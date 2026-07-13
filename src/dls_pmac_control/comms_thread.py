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

from dls_pmac_control.status_dataclass import (
    ControllerStatus,
    CoordinateSystemStatus,
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
    finished = pyqtSignal()

    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.CSNum = 1
        self.gen = None
        self.resultQueue = (
            Queue()
        )  # a queue object that stores the results of each polling update
        # of each polling update
        self.watchesQueue = (
            Queue()
        )  # a queue object that stores the results of each watches update

        # self.inputQueue = Queue() -->> Using slots instead

        # self.updateReadyEvent = None -->> Come back to

        self.disablePollingStatusValue = False

        self.max_pollrate = None
        self.lineNumber = 0
        # Dict containing names and values of watch window variables
        self._watch_window = {}
        # Use lock to prevent race condition for watch window
        self.lock = threading.Lock()

    # Give thread own Qt event loop
    # polling every 100ms and slots excute when signals come
    def start(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_func)
        self.timer.start(100)

    def stop(self):
        if hasattr(self, "timer"):
            self.timer.stop()
        self.finished.emit()

    @pyqtSlot()
    def send_series(self, data):
        try:
            self.gen = self.parent.pmac.sendSeries(data)
        except Exception:
            self.send_complete("Couldn't start download")
            traceback.print_exc()

    @pyqtSlot()
    def disable_polling_status(self, data):
        self.disablePollingStatusValue = data

    @pyqtSlot()
    def cancel_send_series(self):
        if self.gen:
            self.gen.close()
            self.send_complete("Download cancelled by the user")

    ### UNCHANGED CODE BELOW - KEEP ###

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
        print("parsed_poll_response \n")
        # print(f"response: {response} \n")
        response_str = response[0]
        # print("response_str: " + repr(response_str))

        response_success = response[1]
        print(f"response_success: {response_success} \n")

        response_str_list = str(response_str).rstrip("\x06\r").split("\r")
        print("response_str_list: " + repr(response_str_list))

        status = ControllerStatus()

        status.coordinate_systems.append(
            CoordinateSystemStatus(
                identifier_i65=int(response_str_list[0]),
                global_status=int(response_str_list[1]),
                cs_status=response_str_list[2],
                feedrate=float(response_str_list[3]),
            )
        )

        response_motors_list = response_str_list[4:]
        response_motors_list = [
            response_motors_list[i : i + 6]
            for i in range(0, len(response_motors_list), 6)
        ]
        print(f"response_motors_list: {response_motors_list}")

        motor_no = 1
        for motor_response in response_motors_list:
            print(f"Motor_response: {motor_response}")
            status.motors.append(
                MotorStatus(
                    number=motor_no,
                    motor_status=str(motor_response[0]),
                    position=float(motor_response[1]),
                    velocity=float(motor_response[2]),
                    following_error=float(motor_response[3]),
                    amplifier_status=float(motor_response[4]),
                )
            )
            motor_no += 1

        print(f"status: {status}")
        return status

    def generate_cmd(self):
        print("generate_cmd \n")
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

        # print(f"cmd: {cmd}")
        return cmd

    def poll_status(self) -> ControllerStatus | None:
        print("poll_status \n")
        if self.parent.pmac is None:
            return None

        if not self.parent.pmac.isConnectionOpen:
            return None

        ###
        cmd = self.generate_cmd()
        return_thing = self.parsed_poll_response(self.parent.pmac.sendCommand(cmd))
        # return self.parsed_poll_response(self.parent.pmac.sendCommand(cmd))
        print(f"parsed poll response: {return_thing}\n")
        return return_thing
        ###

    ### OLD CODE BELOW - CHANGE? ###

    def update_func(self):
        if self.parent.pmac is None or not self.parent.pmac.isConnectionOpen:
            time.sleep(0.1)
            return

        status = self.poll_status()
        print(f"status: {status} \n")
        self.update_received.emit(status)

        # print("parent: ", dir(self.parent))

        # if hasattr(self.parent, "pmac"):
        #     print("\n pmac: ", dir(self.parent.pmac))

        # if self.gen:
        #     # should be downloading a text file
        #     try:
        #         (
        #             was_successful,
        #             self.lineNumber,
        #             command,
        #             pmac_response_str,
        #         ) = self.gen.__next__()
        #     except StopIteration:
        #         self.send_complete(
        #             "Downloaded " + str(self.lineNumber) + " lines from pmc file."
        #         )
        #     else:
        #         err = ""
        #         if not was_successful:
        #             err = "{}: command '{}' generated '{}'".format(
        #                 self.lineNumber,
        #                 command,
        #                 pmac_response_str.replace("\r", " ").replace("\x07", ""),
        #             )
        #         self.send_tick(self.lineNumber, err)
        #     return
        # if self.disablePollingStatusValue:
        #     time.sleep(0.1)
        #     return

        # # Reduce poll rate for serial interface (ignores if poll rate set to
        # # zero)
        # if isinstance(self.parent.pmac, PmacSerialInterface) and self.max_pollrate:
        #     if time.time() - self.parent.pmac.last_comm_time < 1.0 / self.max_pollrate:
        #         return

        # ### GENERATE CMD BELOW ###

        # cmd = self.generate_cmd()
        # (ret_str, was_successful) = self.parent.pmac.sendCommand(
        #     cmd
        # )  ### THIS IS THE RETURNED RESPONSE

        # with self.lock:
        #     # send watch window commands
        #     value_list_watch = []
        #     for key in self._watch_window:
        #         (ret, success) = self.parent.pmac.sendCommand(key)
        #         ret = ret.rstrip("\x06\r")
        #         if "error" in ret or "ERR" in ret:
        #             ret = "Error"
        #         # update watches dict
        #         self._watch_window[key] = ret
        #         value_list_watch.append(ret)
        #     self.watchesQueue.put(value_list_watch)

        # if was_successful:
        #     value_list = ret_str.rstrip("\x06\r").split("\r")
        #     # fourth is the PMAC identity
        #     if value_list[0].startswith("\x07"):
        #         # error, probably in buffer
        #         print(f"i65 returned {value_list[0].__repr__()}, sending CLOSE command")
        #         self.parent.pmac.sendCommand("CLOSE")
        #         return

        #     # If we got a malformed response, abort now before writing anything
        #     # to the result queue.
        #     if len(value_list) < 4:
        #         if self.parent.verboseMode:
        #             print("Received malformed response to poll request: ", value_list)
        #         return

        #     # Identifier i65
        #     self.resultQueue.put([value_list[0], 0, 0, 0, 0, 0, "IDENT"])
        #     # Global status
        #     self.resultQueue.put([value_list[1], 0, 0, 0, 0, 0, "G"])
        #     # CS status
        #     self.resultQueue.put([value_list[2], 0, 0, 0, 0, 0, f"CS{self.CSNum}"])
        #     # Fedrate
        #     self.resultQueue.put([value_list[3], 0, 0, 0, 0, 0, f"FEED{self.CSNum}"])

        #     if isinstance(self.parent.pmac, PPmacSshInterface):
        #         # Brick Under Voltage Status
        #         self.resultQueue.put([value_list[4], 0, 0, 0, 0, 0, "UVOL"])
        #         # Brick Over Voltage Status
        #         self.resultQueue.put([value_list[5], 0, 0, 0, 0, 0, "OVOL"])
        #         # Brick Over Temperature Status
        #         self.resultQueue.put([value_list[6], 0, 0, 0, 0, 0, "OTEMP"])
        #         value_list = value_list[7:]
        #     else:
        #         value_list = value_list[4:]
        #     # All request chunks contain 7 elements
        #     cols = 6
        #     for motor_row, i in enumerate(range(0, len(value_list), cols)):
        #         return_list = value_list[i : i + cols]
        #         return_list.append(motor_row)
        #         self.resultQueue.put(return_list, False)

        #     ev_updates_ready = CustomEvent(self.parent.updatesReadyEventType, None)
        #     QCoreApplication.postEvent(self.parent, ev_updates_ready)
        #     print(f"resultQueue: {list(self.resultQueue.queue)}")
        # else:
        #     print(f'WARNING: Could not poll PMAC for motor status ("{ret_str}")')
        time.sleep(0.1)
