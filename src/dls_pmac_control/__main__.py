import re
import signal
import sys
import types
from optparse import OptionParser
from os import path
from queue import Empty

from dls_pmaclib.dls_pmacremote import (
    PmacEthernetInterface,
    PmacSerialInterface,
    PmacTelnetInterface,
    PPmacSshInterface,
)
from dls_pmaclib.dls_pmcpreprocessor import ClsPmacParser
from PyQt6.QtCore import QEvent, Qt, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressDialog,
    QTableWidgetItem,
)
from typing_extensions import override

from dls_pmac_control import __version__
from dls_pmac_control.axissettings import Axissettingsform, PpmacAxissettingsform
from dls_pmac_control.comms_thread import CommsWorker
from dls_pmac_control.cs_status import CSStatusForm, PpmacCSStatusForm
from dls_pmac_control.energise import Energiseform
from dls_pmac_control.gather import PmacGatherform
from dls_pmac_control.global_status import GlobalStatusForm, PpmacGlobalStatusForm
from dls_pmac_control.login import Loginform
from dls_pmac_control.ppmacgather import PpmacGatherform
from dls_pmac_control.status import PpmacStatusform, Statusform
from dls_pmac_control.status_dataclass import ControllerStatus
from dls_pmac_control.ui_form_control import UiControlForm
from dls_pmac_control.watches import Watchesform


class Controlform(QMainWindow, UiControlForm):
    stop_worker_signal = pyqtSignal()
    send_series_signal = pyqtSignal(list)
    cancel_send_series_signal = pyqtSignal()
    disable_polling_status_signal = pyqtSignal(bool)

    def __init__(self, options, parent=None):
        super().__init__(parent)

        signal.signal(2, self.signal_handler)
        # setup signals

        self.setup_ui(self)
        # self.parent = parent

        self.greenLedOn = QPixmap(path.join(path.dirname(__file__), "greenLedOn.png"))
        self.greenLedOff = QPixmap(path.join(path.dirname(__file__), "greenLedOff.png"))
        self.redLedOn = QPixmap(path.join(path.dirname(__file__), "redLedOn.png"))
        self.redLedOff = QPixmap(path.join(path.dirname(__file__), "redLedOff.png"))
        self.amberLedOn = QPixmap(path.join(path.dirname(__file__), "led-amber.png"))

        self.pollingStatus = True
        self.isUsingSerial = False

        self.lneServer.setText(options.server)
        self.lnePort.setText(options.port)
        self.currentMotor = int(options.defaultAxis)
        self.nAxes = options.nAxes
        self.macroAxisStartIndex = int(options.macroAxisStartIndex)

        self.username = options.username
        self.password = options.password

        self.verboseMode = options.verbose

        self.connectionProtocol = options.protocol
        if self.connectionProtocol == "ts":
            # use terminal server
            self.rbUseTerminalServer.setChecked(True)
            self.ConnectionType = 0
        elif self.connectionProtocol == "tcpip":
            # use TCP/IP socket connection
            self.rbUseSocket.setChecked(True)
            self.ConnectionType = 1
        elif self.connectionProtocol == "rs232":
            # use serial connection
            self.rbUseSerial.setChecked(True)
            self.ConnectionType = 2
        elif self.connectionProtocol == "ssh":
            # use ssh
            self.rbUseSsh.setChecked(True)
            self.ConnectionType = 3
        else:
            QMessageBox.information(
                self,
                "Error",
                "Wrong connection protocol specified on "
                'command line (use "ts" or "tcpip").',
            )
            sys.exit(-1)

        self.connectionTimeout = max(options.timeout, 1)

        # This will hold a PmacRemoteInterface once self.remoteConnect() is
        # called
        self.pmac = None
        self.powerpmac = None

        self.status_screen = Statusform(self, self.currentMotor)
        self.ppmacstatusScreen = PpmacStatusform(self, self.currentMotor)
        self.cs_status_screen = CSStatusForm(self)
        self.PpmacCSStatusScreen = PpmacCSStatusForm(self)
        self.global_status_screen = GlobalStatusForm(self)
        self.PpmacGlobalStatusScreen = PpmacGlobalStatusForm(self)
        self.axisSettingsScreen = Axissettingsform(
            self, self.currentMotor, self.macroAxisStartIndex
        )
        self.ppmacaxisSettingsScreen = PpmacAxissettingsform(self, self.currentMotor)
        self.pmacgatherScreen = PmacGatherform(self, self.currentMotor)
        self.ppmacgatherScreen = PpmacGatherform(self, self.currentMotor)
        self.watchesScreen = Watchesform(self)
        self.login = Loginform(self, self.username, self.password)
        # self.energiseScreen = Energiseform(self.pmac,self)

        # set up threading
        self.comms_thread = QThread()
        self.comms_worker = CommsWorker(self)
        self.comms_worker.moveToThread(self.comms_thread)

        self.send_series_signal.connect(self.comms_worker.send_series)
        self.cancel_send_series_signal.connect(self.comms_worker.cancel_send_series)
        self.disable_polling_status_signal.connect(
            self.comms_worker.disable_polling_status
        )

        self.comms_thread.started.connect(self.comms_worker.start)
        self.comms_worker.update_received.connect(self.start_updating_motors)
        self.comms_worker.watches_ready.connect(self.update_watches)

        self.comms_worker.finished.connect(self.comms_thread.quit)
        self.comms_thread.finished.connect(self.comms_worker.deleteLater)
        self.comms_thread.finished.connect(self.comms_thread.deleteLater)

        self.stop_worker_signal.connect(self.comms_worker.stop)
        self.comms_thread.start()

        self.spnJogMotor.setValue(self.currentMotor)

        # a few details for use when downloading pmc file
        self.progressEventType = QEvent.Type.User + 1
        self.downloadDoneEventType = QEvent.Type.User + 2
        self.updatesReadyEventType = QEvent.Type.User + 3
        self.progressDialog = None
        self.canceledDownload = False

        self.table.setColumnWidth(3, 40)
        self.table.setColumnWidth(4, 40)
        self.table.cellDoubleClicked.connect(self.choose_motor_from_table)

        self.commands = []
        self.commands_i = 0
        self.lneSend.keyPressEvent = types.MethodType(self.check_history, self.lneSend)
        self.dirname = "."

        self.lblIdentity.setText("")
        self.txtShell.clear()

    # Calculate servo cycle time in kHz
    def calculate_servo_cycle_time(self):
        if isinstance(self.pmac, PPmacSshInterface):
            cmd = "Sys.ServoPeriod"  # in msec
        else:
            cmd = "I10"  # in 1 / 2^23 msec
        (ret_str, status) = self.pmac.sendCommand(cmd)
        ivar_i10 = float(ret_str.strip("$")[:-1])
        if isinstance(self.pmac, PPmacSshInterface):
            self.servoCycleTime = 1.0 / ivar_i10
        else:
            self.servoCycleTime = 8388608.0 / ivar_i10

    def use_terminal_server_connection(self):
        if self.ConnectionType != 0:
            self.ConnectionType = 0
            # set the server and port fields to defaults for this connection
            # type
            self.lneServer.setText("blxxi-nt-tserv-01")
            self.lnePort.setText("7017")
            self.textLabel1.setText("Server:")
            self.textLabel2.setText("Port:")
            self.lblPolling.setText("Polling")
            self.lnePollRate.setEnabled(False)
            self.lblPollRate.setEnabled(False)

    def use_socket_connection(self):
        if self.ConnectionType != 1:
            self.ConnectionType = 1
            # set the server and port fields to defaults for this connection
            # type
            self.lneServer.setText("172.23.171.103")  # was 172.23.240.97
            self.lnePort.setText("1025")
            self.textLabel1.setText("IP address:")
            self.textLabel2.setText("Port:")
            self.lblPolling.setText("Polling")
            self.lnePollRate.setEnabled(False)
            self.lblPollRate.setEnabled(False)

    def use_serial(self):
        if self.ConnectionType != 2:
            self.ConnectionType = 2
            self.isUsingSerial = False
            # set the server and port fields to defaults for this connection
            # type
            self.lneServer.setText("/dev/ttyUSB0")
            self.lnePort.setText("38400")
            self.textLabel1.setText("COM port:")
            self.textLabel2.setText("Baudrate:")
            self.lblPolling.setText("Polling @")
            self.lnePollRate.setEnabled(True)
            self.lnePollRate.setText("0")
            self.lblPollRate.setEnabled(True)

    def use_ssh_connection(self):
        if self.ConnectionType != 3:
            self.ConnectionType = 3
            # set the server and port fields to defaults for this connection
            # type
            self.lneServer.setText("172.23.240.97")
            self.lnePort.setText("22")
            self.textLabel1.setText("IP address:")
            self.textLabel2.setText("Port:")
            # self.textLabel3.setText("Username:")
            # self.textLabel4.setText("Password:")
            self.lblPolling.setText("Polling")
            self.lnePollRate.setEnabled(False)
            self.lblPollRate.setEnabled(False)

    def check_history(self, edit, event):
        if event.key() == Qt.Key.Key_Up:
            if len(self.commands) == 0:
                self.commands_i = 0
                self.lneSend.setText("")
            elif self.commands_i > -len(self.commands):
                self.commands_i -= 1
                self.lneSend.setText(self.commands[self.commands_i])
            else:
                self.lneSend.setText(self.commands[self.commands_i])
        elif event.key() == Qt.Key.Key_Down:
            if self.commands_i >= -1:
                self.commands_i = 0
                self.lneSend.setText("")
            else:
                self.commands_i += 1
                self.lneSend.setText(self.commands[self.commands_i])
        QLineEdit.keyPressEvent(edit, event)

    def remote_connect(self):
        # Create a remote PMAC interface, of the correct type, depending on
        # radio-box selection in the "Connection to PMAC" section
        if self.ConnectionType == 0:
            self.pmac = PmacTelnetInterface(
                self,
                verbose=self.verboseMode,
                numAxes=self.nAxes,
                timeout=self.connectionTimeout,
            )
        elif self.ConnectionType == 1:
            self.pmac = PmacEthernetInterface(
                self,
                verbose=self.verboseMode,
                numAxes=self.nAxes,
                timeout=self.connectionTimeout,
            )
        elif self.ConnectionType == 2:
            try:
                pollrate = float(self.lnePollRate.text())
            except ValueError:
                pollrate = False
            self.comms_worker.max_pollrate = pollrate
            self.pmac = PmacSerialInterface(
                self,
                verbose=self.verboseMode,
                numAxes=self.nAxes,
                timeout=self.connectionTimeout,
            )
        elif self.ConnectionType == 3:
            self.pmac = PPmacSshInterface(
                self,
                verbose=self.verboseMode,
                numAxes=self.nAxes,
                timeout=self.connectionTimeout,
            )

        # Set the server name and port
        server_name = self.lneServer.text()
        server_port = self.lnePort.text()
        self.pmac.setConnectionParams(server_name, server_port)
        self.txtShell.append(f"Connecting to {server_name} {server_port}")

        # Connect to the interface/PMAC
        # Show login window if ssh connection
        if self.ConnectionType == 3:
            # use exec instead of show to wait until login is done
            is_clicked_ok = self.login.exec()
            if not is_clicked_ok:
                return
            else:
                # try to connect again
                connection_status = self.pmac.connect(
                    username=self.login.username, password=self.login.password
                )
                if connection_status:
                    QMessageBox.information(self, "Error", connection_status)
                    return
        else:
            connection_status = self.pmac.connect()

        if connection_status:
            QMessageBox.information(self, "Error", connection_status)
            return

        # Find out the type of the PMAC
        pmac_model_str = self.pmac.getPmacModel()
        if pmac_model_str:
            self.setWindowTitle(f"Delta Tau motor controller - {pmac_model_str}")
        else:
            QMessageBox.information(self, "Error", "Could not determine PMAC model")
            return

        self.calculate_servo_cycle_time()

        self.table.setRowCount(self.pmac.getNumberOfAxes())
        self.spnJogMotor.setMaximum(self.pmac.getNumberOfAxes())

        self.btnConnect.setEnabled(False)
        self.lneServer.setEnabled(False)
        self.lnePort.setEnabled(False)
        self.btnGroupProtocol.setEnabled(False)
        self.btnDisconnect.setEnabled(True)
        self.btnJogNeg.setEnabled(True)
        self.btnJogPos.setEnabled(True)
        self.btnJogStop.setEnabled(True)
        self.btnHome.setEnabled(True)
        self.lneSend.setEnabled(True)
        self.btnSend.setEnabled(True)
        self.lneJogTo.setEnabled(True)
        self.lneJogDist.setEnabled(True)
        self.btnJogTo.setEnabled(True)
        self.btnEnergise.setEnabled(False)
        # disable energise button for geobrick and power pmac
        enable_energise = (
            not self.pmac.isModelGeobrick() and not self.ConnectionType == 3
        )
        self.btnEnergise.setEnabled(enable_energise)
        self.btnKillAll.setEnabled(True)
        self.btnStatus.setEnabled(True)
        self.btnCSStatus.setEnabled(True)
        self.btnGlobalStatus.setEnabled(True)
        self.btnLoadFile.setEnabled(True)
        self.btnSettings.setEnabled(True)
        self.btnKillMotor.setEnabled(True)
        self.chkJogInc.setEnabled(True)
        self.btnPollingStatus.setEnabled(True)
        self.btnGather.setEnabled(True)
        self.btnWatches.setEnabled(True)
        self.table.setEnabled(True)
        self.lnePollRate.setEnabled(False)
        self.lblPollRate.setEnabled(False)
        self.pixPolling.setPixmap(self.greenLedOn)

    def remote_disconnect(self):
        # If the PMAC interface has been already defined, make it disconnect
        # (this will do nothing if the interface is not connected)
        if self.pmac:
            self.txtShell.append("Disconnected")
            self.pmac.disconnect()

        self.setWindowTitle("Delta Tau motor controller")
        self.btnConnect.setEnabled(True)
        self.btnDisconnect.setEnabled(False)
        self.lneServer.setEnabled(True)
        self.lnePort.setEnabled(True)
        self.btnGroupProtocol.setEnabled(True)
        self.btnJogNeg.setEnabled(False)
        self.btnJogPos.setEnabled(False)
        self.btnJogStop.setEnabled(False)
        self.btnHome.setEnabled(False)
        self.lneSend.setEnabled(False)
        self.btnSend.setEnabled(False)
        self.lneJogTo.setEnabled(False)
        self.lneJogDist.setEnabled(False)
        self.btnJogTo.setEnabled(False)
        self.btnEnergise.setEnabled(False)
        self.btnKillAll.setEnabled(False)
        self.btnStatus.setEnabled(False)
        self.btnCSStatus.setEnabled(False)
        self.btnGlobalStatus.setEnabled(False)
        self.btnSettings.setEnabled(False)
        self.btnKillMotor.setEnabled(False)
        self.btnLoadFile.setEnabled(False)
        self.chkJogInc.setEnabled(False)
        self.btnPollingStatus.setEnabled(False)
        self.btnGather.setEnabled(False)
        self.btnWatches.setEnabled(False)
        self.table.setEnabled(False)
        self.pixPolling.setPixmap(self.greenLedOff)
        self.lblIdentity.setText("")

        self.axisSettingsScreen.close()
        self.ppmacaxisSettingsScreen.close()
        self.status_screen.close()
        self.ppmacstatusScreen.close()
        self.cs_status_screen.close()
        self.PpmacCSStatusScreen.close()
        self.global_status_screen.close()
        self.PpmacGlobalStatusScreen.close()
        self.pmacgatherScreen.close()
        self.ppmacgatherScreen.close()
        self.watchesScreen.clear_watches()
        self.watchesScreen.close()
        try:
            self.energiseScreen.close()
        except Exception:
            pass

    def jog_neg(self):
        (command, ret_str, ret_status) = self.pmac.jogInc(
            self.currentMotor, "neg", str(self.lneJogDist.text())
        )
        self.add_to_txt_shell(command, ret_str)

    # public slot
    def jog_pos(self):
        (command, ret_str, ret_status) = self.pmac.jogInc(
            self.currentMotor, "pos", str(self.lneJogDist.text())
        )
        self.add_to_txt_shell(command, ret_str)

    # public slot

    def jog_stop(self):
        (command, ret_str, ret_status) = self.pmac.jogStop(self.currentMotor)
        self.add_to_txt_shell(command, ret_str)

    # public slot

    def jog_home(self):
        (command, ret_str, ret_status) = self.pmac.homeCommand(self.currentMotor)
        self.add_to_txt_shell(command, ret_str)

    # public slot

    def jog_go_to_position(self):
        (command, ret_str, ret_status) = self.pmac.jogTo(
            self.currentMotor, self.lneJogTo.text()
        )
        self.add_to_txt_shell(command, ret_str)

    # public slot
    def jog_change_motor(self, new_motor):
        self.currentMotor = new_motor
        self.status_screen.change_axis(self.currentMotor)
        self.ppmacstatusScreen.change_axis(self.currentMotor)
        self.axisSettingsScreen.change_axis(self.currentMotor)
        self.ppmacaxisSettingsScreen.change_axis(self.currentMotor)

    # Send a #Xk command to kill the current motor.
    def kill_motor(self):
        command = f"#{self.currentMotor}k"
        (return_string, status) = self.pmac.sendCommand(command)
        self.add_to_txt_shell(command)

    # Send a <CTRL-K> (ASCII 0x0B) command to the PMAC to kill all motion
    # all servo loops will be opened and amplifier enable set false.
    # see TURBO SRM page 289
    def kill_all_motors(self):
        # print "killing all motors!"
        command = "\x0b"
        (return_string, status) = self.pmac.sendCommand(command)
        self.add_to_txt_shell("CTRL-K")

    def data_gather(self):
        # if power pmac
        # if self.ConnectionType == 3:
        if isinstance(self.pmac, PPmacSshInterface):
            self.ppmacgatherScreen.show()
        else:
            self.pmacgatherScreen.show()

    # public slot
    def watches(self):
        self.watchesScreen.show()

    def pmac_energise_axis(self):
        self.energiseScreen = Energiseform(self.pmac, self)
        self.energiseScreen.show()

    def status_screen(self):
        # if power pmac
        if isinstance(self.pmac, PPmacSshInterface):
            self.ppmacstatusScreen.show()
        else:
            self.status_screen.show()

    def cs_status_screen(self):
        # if power pmac
        if isinstance(self.pmac, PPmacSshInterface):
            self.PpmacCSStatusScreen.show()
        else:
            self.cs_status_screen.show()

    def global_status_screen(self):
        # if power pmac
        if isinstance(self.pmac, PPmacSshInterface):
            self.PpmacGlobalStatusScreen.show()
        else:
            self.global_status_screen.show()

    # public slot
    def jog_parameters(self):
        if isinstance(self.pmac, PPmacSshInterface):
            self.ppmacaxisSettingsScreen.show()
            self.ppmacaxisSettingsScreen.axis_update()
        else:
            self.axisSettingsScreen.show()
            self.axisSettingsScreen.axis_update()

    # Download a pmc configuration file to the PMAC
    def pmac_load_config(self):
        # First get the file from a file dialog
        my_dialog = QFileDialog(self)
        q_file = my_dialog.getOpenFileName(
            self, "Load PMC file", self.dirname, "PMAC configuration (*.pmc *.PMC)"
        )
        file_name, _ = q_file
        if not file_name:
            return
        self.dirname = path.dirname(str(file_name))

        # A couple of regular expressions for use in parsing the pmc file
        blank_line = re.compile(r"^\s*$")  # match blank lines

        # parsing through the file
        pmc = ClsPmacParser()
        pmc_lines = pmc.parse(file_name)

        if pmc_lines:
            # Get rid of all the empty lines, but keep line numbers
            commands = []
            for i, pmc_line in enumerate(pmc_lines):
                if not blank_line.match(pmc_line):
                    commands.append((i + 1, pmc_line))

            # Prepend two close commands and a delete gather to the front of
            # any pmc file uploaded. This ensures that any open PLC buffers
            # are closed before an upload and that the gather buffer is
            # erased to make memory available for the new PLC. Two close
            # commands are sent to ensure that we leave any nested statements
            # (first close) before then closing the buffer (second close).
            # Dummy line numbers of zero are paired with each command to
            # match the formatting and to not disrupt the real line numbering
            close_commands = [(0, "CLOSE"), (0, "CLOSE"), (0, "DELETE GATHER")]
            commands = close_commands + commands

            # Open up progress dialog and start sending the commands.
            self.canceledDownload = False
            self.progressDialog = QProgressDialog(
                "Downloading PMAC configuration", "cancel", 0, len(pmc_lines), self
            )
            self.progressDialog.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.progressDialog.canceled.connect(self.cancel)
            self.txtShell.append("Beginning download of pmc file: " + file_name)
            self.send_series_signal.emit(commands)

    def cancel(self):
        self.canceledDownload = True
        self.cancel_send_series_signal.emit()

    def pmac_polling_status(self):
        # If we are already polling, disable it
        if self.pollingStatus:
            self.pollingStatus = False
            self.disable_polling_status_signal.emit(True)

            self.btnPollingStatus.setText("enable polling")

            # Disable all the controls and status displays to indicate that we
            # do not have updates available
            self.table.setEnabled(False)
            self.lblPosition.setEnabled(False)
            self.lblVelo.setEnabled(False)
            self.lblFolErr.setEnabled(False)
            self.pixPolling.setPixmap(self.greenLedOff)

        # else, if we are not polling: start polling!
        else:
            self.pollingStatus = True
            self.disable_polling_status_signal.emit(False)
            self.btnPollingStatus.setText("disable polling")

            # Re-enable all the disabled labels and controls
            self.table.setEnabled(True)
            self.lblPosition.setEnabled(True)
            self.lblVelo.setEnabled(True)
            self.lblFolErr.setEnabled(True)
            self.pixPolling.setPixmap(self.greenLedOn)

    def jog_neg_continous_start(self):
        # print "controlform.jogNegContinousStart(): Not implemented yet"
        (command, ret_str, ret_status) = self.pmac.jogContinous(
            self.currentMotor, "neg"
        )
        self.add_to_txt_shell(command, ret_str)

    # public slot
    def jog_pos_continous_start(self):
        # print "controlform.jogPosContinousStart(): Not implemented yet"
        (command, ret_str, ret_status) = self.pmac.jogContinous(
            self.currentMotor, "pos"
        )
        self.add_to_txt_shell(command, ret_str)

    # public slot
    def send_single_command(self):
        # print "controlform.sendSingleCommand(): Not implemented yet"
        command = self.lneSend.text()
        if len(self.commands) == 0 or self.commands[-1] != command:
            self.commands.append(command)
        (ret_str, status) = self.pmac.sendCommand(command)
        self.add_to_txt_shell(command, ret_str, False)
        self.commands_i = 0
        self.lneSend.setText("")

    @pyqtSlot(int, int, name="chooseMotorFromTable")
    def choose_motor_from_table(self, a0):
        self.spnJogMotor.setValue(a0 + 1)

    # public slot
    def jog_incrementally(self, a0):  # a0 is True if 'jog inc' box checked
        self.lneJogDist.setEnabled(a0)
        if a0:
            self.btnJogPos.pressed.disconnect(self.jog_pos_continous_start)
            self.btnJogPos.released.disconnect(self.jog_stop)
            self.btnJogNeg.pressed.disconnect(self.jog_neg_continous_start)
            self.btnJogNeg.released.disconnect(self.jog_stop)
            self.btnJogNeg.clicked.connect(self.jog_neg)
            self.btnJogPos.clicked.connect(self.jog_pos)
        else:
            self.btnJogPos.pressed.connect(self.jog_pos_continous_start)
            self.btnJogPos.released.connect(self.jog_stop)
            self.btnJogNeg.pressed.connect(self.jog_neg_continous_start)
            self.btnJogNeg.released.connect(self.jog_stop)
            self.btnJogNeg.clicked.disconnect(self.jog_neg)
            self.btnJogPos.clicked.disconnect(self.jog_pos)

    def __item(self, row, col):
        item = self.table.item(row, col)
        if not item:
            item = QTableWidgetItem()
            self.table.setItem(row, col, item)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        return item

    def add_to_txt_shell(self, command, ret_str=None, chk_show_all=True):
        if chk_show_all is False or self.chkShowAll.isChecked():
            self.txtShell.append(command)
            if ret_str is not None:
                self.txtShell.append(
                    ret_str.rstrip("\x06").lstrip("\x07").replace("\r", " ")
                )

    def start_updating_motors(self, status: ControllerStatus):
        print("start_updating_motors")
        print(f"The data that's been passed is {status} \n")
        print(f"The cs is {status.coordinate_systems} \n")
        print(f"The motors are {status.motors} \n")

        under_voltage = False
        over_voltage = False
        over_temperature = False

        try:
            # if isinstance(self.pmac, PPmacSshInterface):
            self.update_identity(status.coordinate_systems[0].identifier_i65)
            self.PpmacGlobalStatusScreen.update_status(
                status.coordinate_systems[0].global_status
            )
            self.PpmacCSStatusScreen.update_status(
                int(status.coordinate_systems[0].cs_status, 16)
            )
            self.PpmacCSStatusScreen.update_feed(
                int(round(float(status.coordinate_systems[0].feedrate)))
            )

            i2t_fault = False
            over_current = False

            for motor_row in status.motors:
                print(f"motor_row: {motor_row}\n")
                self.__item(motor_row.number - 1, 0).setText(str(motor_row.position))
                if isinstance(self.pmac, PPmacSshInterface):
                    self.__item(motor_row.number - 1, 1).setText(
                        str(motor_row.velocity)
                    )
                else:
                    self.__item(motor_row.number - 1, 1).setText(
                        str(round(float(motor_row.velocity) * self.servoCycleTime, 1))
                    )
                self.__item(motor_row.number - 1, 2).setText(
                    str(motor_row.following_error)
                )

                if motor_row.number - 1 < 8:
                    if isinstance(self.pmac, PPmacSshInterface):
                        if int(motor_row.amplifier_status) > 0:
                            i2t_fault = True
                        # if int(value[5]) > 0:
                        #     over_current = True
                    elif isinstance(self.pmac, PmacEthernetInterface):
                        amp_status = (int(motor_row.amplifier_status) & 448) >> 6
                        if amp_status == 5:
                            i2t_fault = True
                        elif amp_status == 6:
                            over_current = True
                        if motor_row.number - 1 < 4:
                            if amp_status == 2:
                                under_voltage = True
                            elif amp_status == 3:
                                over_temperature = True
                            elif amp_status == 4:
                                over_voltage = True

                status_word = int(motor_row.motor_status.strip("$"), 16)

                # define high and low limits for power pmac
                if isinstance(self.pmac, PPmacSshInterface):
                    lo_lim = bool(status_word & 0x2000000000000000)  # MinusLimit
                    hi_lim = bool(status_word & 0x1000000000000000)  # PlusLimit
                    lo_lim_soft = bool(
                        status_word & 0x0080000000000000
                    )  # SoftMinusLimit
                    hi_lim_soft = bool(
                        status_word & 0x0040000000000000
                    )  # SoftPlusLimit

                # define high and low limits for pmac
                else:
                    lo_lim = bool(
                        status_word & 0x400000000000
                    )  # negative end limit set
                    hi_lim = bool(
                        status_word & 0x200000000000
                    )  # positive end limit set
                    lo_lim_soft = False
                    hi_lim_soft = False

                # set limit indicators in polling table
                if hi_lim:
                    self.__item(motor_row.number - 1, 3).setIcon(QIcon(self.redLedOn))
                elif hi_lim_soft:
                    self.__item(motor_row.number - 1, 3).setIcon(QIcon(self.amberLedOn))
                else:
                    self.__item(motor_row.number - 1, 3).setIcon(QIcon(self.redLedOff))
                if lo_lim:
                    self.__item(motor_row.number - 1, 4).setIcon(QIcon(self.redLedOn))
                elif lo_lim_soft:
                    self.__item(motor_row.number - 1, 4).setIcon(QIcon(self.amberLedOn))
                else:
                    self.__item(motor_row.number - 1, 4).setIcon(QIcon(self.redLedOff))

                # set amplifier status indicators in polling table
                if i2t_fault:
                    self.__item(motor_row.number - 1, 5).setIcon(QIcon(self.redLedOn))
                else:
                    self.__item(motor_row.number - 1, 5).setIcon(QIcon(self.redLedOff))
                if over_current:
                    self.__item(motor_row.number - 1, 6).setIcon(QIcon(self.redLedOn))
                else:
                    self.__item(motor_row.number - 1, 6).setIcon(QIcon(self.redLedOff))

                # Update also the jog ribbon
                if motor_row.number == self.currentMotor:
                    self.lblPosition.setText(str(motor_row.position))
                    self.lblVelo.setText(str(motor_row.velocity))
                    self.lblFolErr.setText(str(motor_row.following_error))
                    if hi_lim:
                        self.pixHiLim.setPixmap(self.redLedOn)
                    elif hi_lim_soft:
                        self.pixHiLim.setPixmap(self.amberLedOn)
                    else:
                        self.pixHiLim.setPixmap(self.redLedOff)
                    if lo_lim:
                        self.pixLoLim.setPixmap(self.redLedOn)
                    elif lo_lim_soft:
                        self.pixLoLim.setPixmap(self.amberLedOn)
                    else:
                        self.pixLoLim.setPixmap(self.redLedOff)
                    self.status_screen.update_status(status_word)
                    self.ppmacstatusScreen.update_status(status_word)

            # set controller status indicators on main window
            if under_voltage:
                self.pixUnderVoltage.setPixmap(self.redLedOn)
            else:
                self.pixUnderVoltage.setPixmap(self.redLedOff)
            if over_voltage:
                self.pixOverVoltage.setPixmap(self.redLedOn)
            else:
                self.pixOverVoltage.setPixmap(self.redLedOff)
            if over_temperature:
                self.pixOverTemperature.setPixmap(self.redLedOn)
            else:
                self.pixOverTemperature.setPixmap(self.redLedOff)

        except (ValueError, IndexError):
            # Catch the exception and continue, since there may be other
            # updates waiting in the queue.
            if self.verboseMode:
                print(f"Update request received invalid response: {status}")
                print(f"Update request received invalid response: {status}")

    domain_names = [
        "BL",
        "BR",
        "BS",
        "FE",
        "LB",
        "LI",
        "ME",
        "SR",
        "LA",
        "TBD",
        "TBD",
        "TBD",
        "TBD",
        "TBD",
        "TBD",
        "RSV",
    ]
    subdomain_letters = [
        ["I", "B", "J", "C", "K", "D", "L", "E"],
        ["C", "S", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["I", "B", "J", "C", "K", "D", "L", "E"],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["D", "P", "C", "T", "M", "G", "", ""],
        ["I", "A", "J", "C", "K", "R", "L", "S"],
        ["R", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
    ]

    def update_identity(self, id):
        if not self.btnConnect.isEnabled():
            if id == 0:
                text = "Identity not set"
            else:
                domain = (id >> 20) & 0x0F
                # swVersion = (id >> 13) & 0x7F
                subdomain_num = (id >> 7) & 0x1F
                pmac_num = id & 0x1F
                subdomain_letter = (
                    ((id >> 6) & 0x01) | ((id >> 4) & 0x02) | ((id >> 10) & 0x04)
                )
                text = self.domain_names[domain]
                if subdomain_num != 0:
                    text += f"{subdomain_num:02d}"
                    text += self.subdomain_letters[domain][subdomain_letter]
                text += f" {self.pmac.getShortModelName()} "
                text += f"{pmac_num:d}"
            self.lblIdentity.setText(text)

    def update_watches(self):
        self.comms_worker.watchesQueue.qsize()
        for _que_item in range(0, self.comms_worker.watchesQueue.qsize()):
            try:
                value = self.comms_worker.watchesQueue.get(False)
            except Empty:
                return
            for n in range(len(value)):
                if "." in value[n]:
                    value[n] = round(float(value[n]), 1)
                self.watchesScreen.table.setItem(n, 1, QTableWidgetItem(str(value[n])))

    @override
    def customEvent(self, E):
        if E.type() == self.progressEventType:
            (lines, err) = E.data()
            self.progressDialog.setValue(lines)
            if err:
                self.txtShell.append(err)
        elif E.type() == self.downloadDoneEventType:
            self.progressDialog.setValue(self.progressDialog.maximum())
            self.txtShell.append(str(E.data()))

    def signal_handler(self, signum, frame):
        if signum == 2:  # SIGINT
            print("Closing connection...")
            self.pmac.disconnect()
            print("Closing application.")
            QApplication.exit(0)

    def die(self):
        self.stop_worker_signal.emit()
        self.comms_thread.quit()
        self.comms_thread.wait()

        self.remote_disconnect()


# Main function in the pmaccontrol application.
def main():
    usage = """usage: %prog [options]
%prog is a graphical frontend to the Deltatau motorcontroller known as PMAC."""
    parser = OptionParser(usage)
    parser.add_option(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        help="Print more details (than necessary in most cases...)",
    )
    parser.add_option(
        "-o",
        "--protocol",
        action="store",
        dest="protocol",
        default="ts",
        help='Set the connection protocol; use "ts" for '
        "serial via terminal server (the default), "
        'or "tcpip" for network TCP/IP connection.',
    )
    parser.add_option(
        "-s",
        "--server",
        action="store",
        dest="server",
        default="blxxi-nt-tserv-01",
        help="Set server name (default: blxxi-nt-tserv-01)",
    )
    parser.add_option(
        "-p",
        "--port",
        action="store",
        dest="port",
        default="7017",
        help="Set IP port number to connect to (default: 7017)",
    )
    parser.add_option(
        "--username",
        action="store",
        dest="username",
        default="root",
        help="Set the SSH username (default: root)",
    )
    parser.add_option(
        "--password",
        action="store",
        dest="password",
        default="deltatau",
        help="Set the SSH password (default: deltatau)",
    )
    parser.add_option(
        "-a",
        "--axis",
        action="store",
        dest="defaultAxis",
        default=1,
        help="Set an axis as a default selected axis when "
        "starting up the application (default: 1)",
    )
    parser.add_option(
        "-m",
        "--macroAxisStartIndex",
        action="store",
        dest="macroAxisStartIndex",
        default=0,
        help="Set the first macro axis (default: 0)",
    )
    parser.add_option(
        "-n",
        "--naxes",
        action="store",
        dest="nAxes",
        help="Display and poll NAXES axes. Default is 32 for a PMAC, 8 for a GeoBrick",
    )
    parser.add_option(
        "-t",
        "--timeout",
        action="store",
        type="float",
        dest="timeout",
        default=3.0,
        help="Set the communication timeout (default: 3 seconds, minimum: 1 second)",
    )
    parser.add_option(
        "--version",
        action="store_true",
        help="get the version of dls-pmac-control",
    )
    (options, args) = parser.parse_args()

    if options.version:
        print(__version__)
        exit(0)

    app = QApplication(sys.argv)
    app.lastWindowClosed.connect(app.quit)
    win = Controlform(options)
    app.aboutToQuit.connect(win.die)
    win.show()
    win.splitter.moveSplitter(180, 1)
    # catch CTRL-C
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.exec()


if __name__ == "__main__":
    main()
