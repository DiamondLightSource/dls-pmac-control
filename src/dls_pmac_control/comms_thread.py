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
        self.resultQueue = Queue()
        self.watchesQueue = Queue()

        # self.inputQueue = Queue() -->> Using slots instead

        # self.updateReadyEvent = None -->> Come back to

        self.disablePollingStatusValue = False

        self.max_pollrate = None
        self.lineNumber = 0
        self._watch_window = {}
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
        ev = CustomEvent(self.parent.progressEventType, (line_number, err))
        QCoreApplication.postEvent(self.parent, ev)

    def send_complete(self, message):
        self.gen = None
        ev_done = CustomEvent(self.parent.downloadDoneEventType, message)
        QCoreApplication.postEvent(self.parent, ev_done)

    ### OLD CODE BELOW - CHANGE? ###

    def update_func(self):
        if self.parent.pmac is None or not self.parent.pmac.isConnectionOpen:
            time.sleep(0.1)
            return
        if self.gen:
            try:
                (
                    was_successful,
                    self.lineNumber,
                    command,
                    pmac_response_str,
                ) = self.gen.__next__()
            except StopIteration:
                self.send_complete(
                    "Downloaded " + str(self.lineNumber) + " lines from pmc file."
                )
            else:
                err = ""
                if not was_successful:
                    err = "{}: command '{}' generated '{}'".format(
                        self.lineNumber,
                        command,
                        pmac_response_str.replace("\r", " ").replace("\x07", ""),
                    )
                self.send_tick(self.lineNumber, err)
            return
        if self.disablePollingStatusValue:
            time.sleep(0.1)
            return

        if isinstance(self.parent.pmac, PmacSerialInterface) and self.max_pollrate:
            if time.time() - self.parent.pmac.last_comm_time < 1.0 / self.max_pollrate:
                return
        cmd = f"i65???&{self.CSNum}??%"
        if isinstance(self.parent.pmac, PPmacSshInterface):
            cmd = f"i65?&{self.CSNum}?% BrickLV.BusUnderVoltage BrickLV.BusOverVoltage BrickLV.OverTemp"
        elif isinstance(self.parent.pmac, PmacEthernetInterface):
            cmd = f"i65???&{self.CSNum}??%"
        axes = self.parent.pmac.getNumberOfAxes() + 1
        for motor_no in range(1, axes):
            cmd = cmd + "#" + str(motor_no) + "?PVF "
            if motor_no < 9:
                if isinstance(self.parent.pmac, PPmacSshInterface):
                    cmd = (
                        cmd
                        + "BrickLV.Chan["
                        + str(motor_no - 1)
                        + "].I2tFaultStatus BrickLV.Chan["
                        + str(motor_no - 1)
                        + "].OverCurrent"
                    )
                else:
                    cmd = cmd + "m" + str(motor_no) + "90 p99"
            else:
                cmd = cmd + "p99 p99"

        (ret_str, was_successful) = self.parent.pmac.sendCommand(cmd)
        with self.lock:
            value_list_watch = []
            for key in self._watch_window:
                (ret, success) = self.parent.pmac.sendCommand(key)
                ret = ret.rstrip("\x06\r")
                if "error" in ret or "ERR" in ret:
                    ret = "Error"
                self._watch_window[key] = ret
                value_list_watch.append(ret)
            self.watchesQueue.put(value_list_watch)

        if was_successful:
            value_list = ret_str.rstrip("\x06\r").split("\r")
            if value_list[0].startswith("\x07"):
                print(f"i65 returned {value_list[0].__repr__()}, sending CLOSE command")
                self.parent.pmac.sendCommand("CLOSE")
                return

            if len(value_list) < 4:
                if self.parent.verboseMode:
                    print("Received malformed response to poll request: ", value_list)
                return

            self.resultQueue.put([value_list[0], 0, 0, 0, 0, 0, "IDENT"])
            self.resultQueue.put([value_list[1], 0, 0, 0, 0, 0, "G"])
            self.resultQueue.put([value_list[2], 0, 0, 0, 0, 0, f"CS{self.CSNum}"])
            self.resultQueue.put([value_list[3], 0, 0, 0, 0, 0, f"FEED{self.CSNum}"])

            if isinstance(self.parent.pmac, PPmacSshInterface):
                self.resultQueue.put([value_list[4], 0, 0, 0, 0, 0, "UVOL"])
                self.resultQueue.put([value_list[5], 0, 0, 0, 0, 0, "OVOL"])
                self.resultQueue.put([value_list[6], 0, 0, 0, 0, 0, "OTEMP"])
                value_list = value_list[7:]
            else:
                value_list = value_list[4:]
            cols = 6
            for motor_row, i in enumerate(range(0, len(value_list), cols)):
                return_list = value_list[i : i + cols]
                return_list.append(motor_row)
                self.resultQueue.put(return_list, False)

            ev_updates_ready = CustomEvent(self.parent.updatesReadyEventType, None)
            QCoreApplication.postEvent(self.parent, ev_updates_ready)
        else:
            print(f'WARNING: Could not poll PMAC for motor status ("{ret_str}")')
        time.sleep(0.1)
