import threading
import time
import traceback
from queue import Queue

from dls_pmaclib.dls_pmacremote import (
    PmacEthernetInterface,
    PmacSerialInterface,
    PPmacSshInterface,
)
from PyQt6.QtCore import QCoreApplication, QEvent, QObject, QTimer, pyqtSignal, pyqtSlot

from dls_pmac_control.status_dataclasses import (
    ControllerStatus,
    CurrentCoordinateSystemStatus,
    MotorStatus,
)


class CustomEvent(QEvent):
    _data = None

    def __init__(self, typ, data):
        QEvent.__init__(self, typ)
        self._data = data

    def data(self):
        return self._data


class CommsWorker(QObject):
    update_received = pyqtSignal(object)
    watches_ready = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.CSNum = 1
        self.gen = None
        self.resultQueue = (
            Queue()
        )  # a queue object that stores the results of each polling update
        self.watchesQueue = (
            Queue()
        )  # a queue object that stores the results of each watches update

        self.disablePollingStatusValue = False

        self.max_pollrate = None
        self.lineNumber = 0
        self._watch_window = {}  # Dict containing names and values of watch window variables
        self.lock = (
            threading.Lock()
        )  # Use lock to prevent race condition for watch window

        self.timer = None

    # Give thread own Qt event loop
    # polling every 100ms and slots excute when signals come
    def start(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_func)
        self.timer.start(100)

    @pyqtSlot()
    def stop(self):
        if self.timer:
            self.timer.stop()
        self.finished.emit()

    @pyqtSlot(list)
    def send_series(self, data):
        try:
            self.gen = self.parent.pmac.sendSeries(data)
        except Exception:
            self.send_complete("Couldn't start download")
            traceback.print_exc()

    @pyqtSlot(bool)
    def disable_polling_status(self, data):
        self.disablePollingStatusValue = data

    @pyqtSlot()
    def cancel_send_series(self):
        if self.gen:
            self.gen.close()
            self.send_complete("Download cancelled by the user")

    def add_watch(self, name):
        with self.lock:
            self._watch_window[name] = None

    def remove_watch(self, name):
        with self.lock:
            del self._watch_window[name]

    def clear_watch(self):
        with self.lock:
            self._watch_window.clear()

    def read_watch(self, name):
        return self._watch_window[name]

    def send_tick(self, line_number, err):
        # Post a Qt event with current progress data
        ev = CustomEvent(self.parent.progressEventType, (line_number, err))
        QCoreApplication.postEvent(self.parent, ev)

    def send_complete(self, message):
        self.gen = None
        ev_done = CustomEvent(self.parent.downloadDoneEventType, message)
        QCoreApplication.postEvent(self.parent, ev_done)

    ### NEW CODE - POLLING AS DATACLASSES

    def parsed_poll_response(self, response):

        response_str_list = str(response).rstrip("\x06\r").split("\r")

        if isinstance(self.parent.pmac, PPmacSshInterface):
            bus_under_voltage = bool(response_str_list[4])
            bus_over_voltage = bool(response_str_list[5])
            over_temp = bool(response_str_list[6])
        else:
            bus_under_voltage = None
            bus_over_voltage = None
            over_temp = None

        status = ControllerStatus(
            identifier_i65=int(response_str_list[0]),
            global_status=response_str_list[1],
            coordinate_systems=CurrentCoordinateSystemStatus(
                cs_status=response_str_list[2],
                feedrate=float(response_str_list[3]),
                bus_under_voltage=bus_under_voltage,
                bus_over_voltage=bus_over_voltage,
                over_temp=over_temp,
            ),
        )

        motor_status_sectioning = len(MotorStatus.__annotations__) - 1

        response_motors_list = response_str_list[4:]
        response_motors_list = [
            response_motors_list[i : i + motor_status_sectioning]
            for i in range(0, len(response_motors_list), motor_status_sectioning)
        ]

        motor_no = 1
        for motor_response in response_motors_list:
            if isinstance(self.parent.pmac, PPmacSshInterface):
                overcurrent = float(motor_response[5])
            else:
                overcurrent = None
            status.motors.append(
                MotorStatus(
                    number=motor_no,
                    motor_status=str(motor_response[0]),
                    position=float(motor_response[1]),
                    velocity=float(motor_response[2]),
                    following_error=float(motor_response[3]),
                    i2t_fault_status=float(motor_response[4]),
                    overcurrent=overcurrent,
                )
            )
            motor_no += 1

        return status

    def generate_cmd(self):
        cmd = f"i65???&{self.CSNum}??%"

        # Send a different command for the Power PMAC
        if isinstance(self.parent.pmac, PPmacSshInterface):
            # There has to be a space before the first BrickLV string to avoid its B being interpreted as a 'begin' command
            cmd = f"i65?&{self.CSNum}?% BrickLV.BusUnderVoltage BrickLV.BusOverVoltage BrickLV.OverTemp"
        elif isinstance(self.parent.pmac, PmacEthernetInterface):
            # Add the 7 segment display status query
            cmd = f"i65???&{self.CSNum}??%"
        axes = self.parent.pmac.getNumberOfAxes() + 1

        for motor_no in range(1, axes):
            cmd = cmd + "#" + str(motor_no) + "?PVF "
            # Amplifier status checks only apply to the first 8 axes
            if motor_no < 9:
                if isinstance(self.parent.pmac, PPmacSshInterface):
                    # PowerBrick channels are zero-indexed
                    cmd = (
                        cmd
                        + "BrickLV.Chan["
                        + str(motor_no - 1)
                        + "].I2tFaultStatus BrickLV.Chan["
                        + str(motor_no - 1)
                        + "].OverCurrent"
                    )
                else:
                    # Add a dummy request to keep the request chunks the same length (p99 always returns zero)
                    cmd = cmd + "m" + str(motor_no) + "90 p99"
            else:
                # Use two dummy requests to keep the request chunks the same length (p99 always returns zero)
                cmd = cmd + "p99 p99"

        return cmd

    def poll_status(self) -> None:
        if self.parent.pmac is None:
            return None

        if not self.parent.pmac.isConnectionOpen:
            return None

        cmd = self.generate_cmd()
        (send_command_response, success) = self.parent.pmac.sendCommand(cmd)

        if success:
            parsed_poll_response_status = self.parsed_poll_response(
                send_command_response
            )
            self.update_received.emit(parsed_poll_response_status)

        else:
            print(
                f'WARNING: Could not poll PMAC for motor status ("{send_command_response}")'
            )

    def update_func(self):
        if self.parent.pmac is None or not self.parent.pmac.isConnectionOpen:
            time.sleep(0.1)
            return

        self.poll_status()

        # # Reduce poll rate for serial interface (ignores if poll rate set to
        # # zero)
        if isinstance(self.parent.pmac, PmacSerialInterface) and self.max_pollrate:
            if time.time() - self.parent.pmac.last_comm_time < 1.0 / self.max_pollrate:
                return

        with self.lock:
            # send watch window commands
            value_list_watch = []
            for key in self._watch_window:
                (ret, success) = self.parent.pmac.sendCommand(key)
                ret = ret.rstrip("\x06\r")
                if "error" in ret or "ERR" in ret:
                    ret = "Error"
                # update watches dict
                self._watch_window[key] = ret
                value_list_watch.append(ret)
            self.watchesQueue.put(value_list_watch)

        self.watches_ready.emit()

    ### OLD update_func BELOW FOR REFERENCE ###

    # def updateFunc(self):
    #     try:
    #         # see if the gui wants us to do anything
    #         cmd, data = self.inputQueue.get(block=False)
    #     except Empty:
    #         # nope, nothing to do
    #         pass
    #     else:
    #         # work out what it wants us to do
    #         if cmd == "die":
    #             return True
    #         elif cmd == "sendSeries":
    #             try:
    #                 self.gen = self.parent.pmac.sendSeries(data)
    #             except Exception:
    #                 self.sendComplete("Couldn't start download")
    #                 traceback.print_exc()
    #         elif cmd == "disablePollingStatus":
    #             self.disablePollingStatus = data
    #         elif cmd == "cancelSendSeries":
    #             if self.gen:
    #                 self.gen.close()
    #                 self.sendComplete("Download cancelled by the user")
    #         else:
    #             print(f"WARNING: don't know what to do with cmd {cmd}")
    #     if self.parent.pmac is None or not self.parent.pmac.isConnectionOpen:
    #         time.sleep(0.1)
    #         return
    #     if self.gen:
    #         # should be downloading a text file
    #         try:
    #             (
    #                 wasSuccessful,
    #                 self.lineNumber,
    #                 command,
    #                 pmacResponseStr,
    #             ) = self.gen.__next__()
    #         except StopIteration:
    #             self.sendComplete(
    #                 "Downloaded " + str(self.lineNumber) + " lines from pmc file."
    #             )
    #         else:
    #             err = ""
    #             if not wasSuccessful:
    #                 err = "{}: command '{}' generated '{}'".format(
    #                     self.lineNumber,
    #                     command,
    #                     pmacResponseStr.replace("\r", " ").replace("\x07", ""),
    #                 )
    #             self.sendTick(self.lineNumber, err)
    #         return
    #     if self.disablePollingStatus:
    #         time.sleep(0.1)
    #         return

    #     # Reduce poll rate for serial interface (ignores if poll rate set to
    #     # zero)
    #     if isinstance(self.parent.pmac, PmacSerialInterface) and self.max_pollrate:
    #         if time.time() - self.parent.pmac.last_comm_time < 1.0 / self.max_pollrate:
    #             return
    #     cmd = f"i65???&{self.CSNum}??%"
    #     # Send a different command for the Power PMAC
    #     if isinstance(self.parent.pmac, PPmacSshInterface):
    #         # There has to be a space before the first BrickLV string to avoid its B being interpreted as a 'begin' command
    #         cmd = f"i65?&{self.CSNum}?% BrickLV.BusUnderVoltage BrickLV.BusOverVoltage BrickLV.OverTemp"
    #     elif isinstance(self.parent.pmac, PmacEthernetInterface):
    #         # Add the 7 segment display status query
    #         cmd = f"i65???&{self.CSNum}??%"
    #     axes = self.parent.pmac.getNumberOfAxes() + 1
    #     for motorNo in range(1, axes):
    #         cmd = cmd + "#" + str(motorNo) + "?PVF "
    #         # Amplifier status checks only apply to the first 8 axes
    #         if motorNo < 9:
    #             if isinstance(self.parent.pmac, PPmacSshInterface):
    #                 # PowerBrick channels are zero-indexed
    #                 cmd = (
    #                     cmd
    #                     + "BrickLV.Chan["
    #                     + str(motorNo - 1)
    #                     + "].I2tFaultStatus BrickLV.Chan["
    #                     + str(motorNo - 1)
    #                     + "].OverCurrent"
    #                 )
    #             else:
    #                 # Add a dummy request to keep the request chunks
    #                 # the same length (p99 always returns zero)
    #                 cmd = cmd + "m" + str(motorNo) + "90 p99"
    #         else:
    #             # Use two dummy requests to keep the request chunks
    #             # the same length (p99 always returns zero)
    #             cmd = cmd + "p99 p99"

    #     # send polling command
    #     (retStr, wasSuccessful) = self.parent.pmac.sendCommand(cmd)
    #     with self.lock:
    #         # send watch window commands
    #         valueListWatch = []
    #         for key in self._watch_window:
    #             (ret, success) = self.parent.pmac.sendCommand(key)
    #             ret = ret.rstrip("\x06\r")
    #             if "error" in ret or "ERR" in ret:
    #                 ret = "Error"
    #             # update watches dict
    #             self._watch_window[key] = ret
    #             valueListWatch.append(ret)
    #         self.watchesQueue.put(valueListWatch)

    #     if wasSuccessful:
    #         valueList = retStr.rstrip("\x06\r").split("\r")
    #         # fourth is the PMAC identity
    #         if valueList[0].startswith("\x07"):
    #             # error, probably in buffer
    #             print(f"i65 returned {valueList[0].__repr__()}, sending CLOSE command")
    #             self.parent.pmac.sendCommand("CLOSE")
    #             return

    #         # If we got a malformed response, abort now before writing anything
    #         # to the result queue.
    #         if len(valueList) < 4:
    #             if self.parent.verboseMode:
    #                 print("Received malformed response to poll request: ", valueList)
    #             return

    #         # Identifier i65
    #         self.resultQueue.put([valueList[0], 0, 0, 0, 0, 0, "IDENT"])
    #         # Global status
    #         self.resultQueue.put([valueList[1], 0, 0, 0, 0, 0, "G"])
    #         # CS status
    #         self.resultQueue.put([valueList[2], 0, 0, 0, 0, 0, f"CS{self.CSNum}"])
    #         # Fedrate
    #         self.resultQueue.put([valueList[3], 0, 0, 0, 0, 0, f"FEED{self.CSNum}"])

    #         if isinstance(self.parent.pmac, PPmacSshInterface):
    #             # Brick Under Voltage Status
    #             self.resultQueue.put([valueList[4], 0, 0, 0, 0, 0, "UVOL"])
    #             # Brick Over Voltage Status
    #             self.resultQueue.put([valueList[5], 0, 0, 0, 0, 0, "OVOL"])
    #             # Brick Over Temperature Status
    #             self.resultQueue.put([valueList[6], 0, 0, 0, 0, 0, "OTEMP"])
    #             valueList = valueList[7:]
    #         else:
    #             valueList = valueList[4:]
    #         # All request chunks contain 7 elements
    #         cols = 6
    #         for motorRow, i in enumerate(range(0, len(valueList), cols)):
    #             returnList = valueList[i : i + cols]
    #             returnList.append(motorRow)
    #             self.resultQueue.put(returnList, False)

    #         evUpdatesReady = CustomEvent(self.parent.updatesReadyEventType, None)
    #         QCoreApplication.postEvent(self.parent, evUpdatesReady)
    #     else:
    #         print(f'WARNING: Could not poll PMAC for motor status ("{retStr}")')
    #     time.sleep(0.1)
