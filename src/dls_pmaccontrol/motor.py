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
from PyQt5.QtCore import QEvent, Qt, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressDialog,
    QTableWidgetItem,
)

from dls_pmaccontrol.axissettings import Axissettingsform, PpmacAxissettingsform
from dls_pmaccontrol.commsThread import CommsThread
from dls_pmaccontrol.CSstatus import CSStatusForm, PpmacCSStatusForm
from dls_pmaccontrol.energise import Energiseform
from dls_pmaccontrol.gather import PmacGatherform
from dls_pmaccontrol.GlobalStatus import GlobalStatusForm, PpmacGlobalStatusForm
from dls_pmaccontrol.login import Loginform
from dls_pmaccontrol.ppmacgather import PpmacGatherform
from dls_pmaccontrol.status import PpmacStatusform, Statusform
from dls_pmaccontrol.ui_formControl import Ui_ControlForm
from dls_pmaccontrol.watches import Watchesform

from . import __version__

# from optparse import OptionParser

if __name__ == "__main__":
    pass


class Controlform(QMainWindow, Ui_ControlForm):
    def __init__(self, options, parent=None):
        signal.signal(2, self.signalHandler)
        # setup signals

        QMainWindow.__init__(self, parent)
        self.setupUi(self)
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

        self.statusScreen = Statusform(self, self.currentMotor)
        self.ppmacstatusScreen = PpmacStatusform(self, self.currentMotor)
        self.CSStatusScreen = CSStatusForm(self)
        self.PpmacCSStatusScreen = PpmacCSStatusForm(self)
        self.GlobalStatusScreen = GlobalStatusForm(self)
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
        self.commsThread = CommsThread(self)

        self.spnJogMotor.setValue(self.currentMotor)

        # a few details for use when downloading pmc file
        self.progressEventType = QEvent.User + 1
        self.downloadDoneEventType = QEvent.User + 2
        self.updatesReadyEventType = QEvent.User + 3
        self.progressDialog = None
        self.canceledDownload = False

        self.table.setColumnWidth(3, 40)
        self.table.setColumnWidth(4, 40)
        self.table.cellDoubleClicked.connect(self.chooseMotorFromTable)

        self.commands = []
        self.commands_i = 0
        self.lneSend.keyPressEvent = types.MethodType(self.checkHistory, self.lneSend)
        self.dirname = "."

        self.lblIdentity.setText("")
        self.txtShell.clear()

    def useTerminalServerConnection(self):
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

    def useSocketConnection(self):
        if self.ConnectionType != 1:
            self.ConnectionType = 1
            # set the server and port fields to defaults for this connection
            # type
            self.lneServer.setText("172.23.240.97")
            self.lnePort.setText("1025")
            self.textLabel1.setText("IP address:")
            self.textLabel2.setText("Port:")
            self.lblPolling.setText("Polling")
            self.lnePollRate.setEnabled(False)
            self.lblPollRate.setEnabled(False)

    def useSerial(self):
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

    def useSshConnection(self):
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

    def checkHistory(self, edit, event):
        if event.key() == Qt.Key_Up:
            if len(self.commands) == 0:
                self.commands_i = 0
                self.lneSend.setText("")
            elif self.commands_i > -len(self.commands):
                self.commands_i -= 1
                self.lneSend.setText(self.commands[self.commands_i])
            else:
                self.lneSend.setText(self.commands[self.commands_i])
        elif event.key() == Qt.Key_Down:
            if self.commands_i >= -1:
                self.commands_i = 0
                self.lneSend.setText("")
            else:
                self.commands_i += 1
                self.lneSend.setText(self.commands[self.commands_i])
        QLineEdit.keyPressEvent(edit, event)

    def remoteConnect(self):
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
            self.commsThread.max_pollrate = pollrate
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
        self.txtShell.append("Connecting to %s %s" % (server_name, server_port))

        # Connect to the interface/PMAC
        # Show login window if ssh connection
        if self.ConnectionType == 3:
            # use exec instead of show to wait until login is done
            is_clickedOK = self.login.exec()
            if not is_clickedOK:
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
            self.setWindowTitle("Delta Tau motor controller - %s" % pmac_model_str)
        else:
            QMessageBox.information(self, "Error", "Could not determine PMAC model")
            return

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
        enableEnergise = (
            not self.pmac.isModelGeobrick() and not self.ConnectionType == 3
        )
        self.btnEnergise.setEnabled(enableEnergise)
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

    def remoteDisconnect(self):
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
        self.statusScreen.close()
        self.ppmacstatusScreen.close()
        self.CSStatusScreen.close()
        self.PpmacCSStatusScreen.close()
        self.GlobalStatusScreen.close()
        self.PpmacGlobalStatusScreen.close()
        self.pmacgatherScreen.close()
        self.ppmacgatherScreen.close()
        self.watchesScreen.clearWatches()
        self.watchesScreen.close()
        try:
            self.energiseScreen.close()
        except Exception:
            pass

    def jogNeg(self):
        (command, retStr, retStatus) = self.pmac.jogInc(
            self.currentMotor, "neg", str(self.lneJogDist.text())
        )
        self.addToTxtShell(command, retStr)

    # public slot
    def jogPos(self):
        (command, retStr, retStatus) = self.pmac.jogInc(
            self.currentMotor, "pos", str(self.lneJogDist.text())
        )
        self.addToTxtShell(command, retStr)

    # public slot

    def jogStop(self):
        (command, retStr, retStatus) = self.pmac.jogStop(self.currentMotor)
        self.addToTxtShell(command, retStr)

    # public slot

    def jogHome(self):
        (command, retStr, retStatus) = self.pmac.homeCommand(self.currentMotor)
        self.addToTxtShell(command, retStr)

    # public slot

    def jogGoToPosition(self):
        (command, retStr, retStatus) = self.pmac.jogTo(
            self.currentMotor, self.lneJogTo.text()
        )
        self.addToTxtShell(command, retStr)

    # public slot
    def jogChangeMotor(self, newMotor):
        self.currentMotor = newMotor
        self.statusScreen.changeAxis(self.currentMotor)
        self.ppmacstatusScreen.changeAxis(self.currentMotor)
        self.axisSettingsScreen.changeAxis(self.currentMotor)
        self.ppmacaxisSettingsScreen.changeAxis(self.currentMotor)

    # Send a #Xk command to kill the current motor.
    def killMotor(self):
        command = "#%dk" % self.currentMotor
        (returnString, status) = self.pmac.sendCommand(command)
        self.addToTxtShell(command)

    # Send a <CTRL-K> (ASCII 0x0B) command to the PMAC to kill all motion
    # all servo loops will be opened and amplifier enable set false.
    # see TURBO SRM page 289
    def killAllMotors(self):
        # print "killing all motors!"
        command = "\x0B"
        (returnString, status) = self.pmac.sendCommand(command)
        self.addToTxtShell("CTRL-K")

    def dataGather(self):
        # if power pmac
        # if self.ConnectionType == 3:
        if isinstance(self.pmac, PPmacSshInterface):
            self.ppmacgatherScreen.show()
        else:
            self.pmacgatherScreen.show()

    # public slot
    def watches(self):
        self.watchesScreen.show()

    def pmacEnergiseAxis(self):
        self.energiseScreen = Energiseform(self.pmac, self)
        self.energiseScreen.show()

    def statusScreen(self):
        # if power pmac
        if isinstance(self.pmac, PPmacSshInterface):
            self.ppmacstatusScreen.show()
        else:
            self.statusScreen.show()

    def CSStatusScreen(self):
        # if power pmac
        if isinstance(self.pmac, PPmacSshInterface):
            self.PpmacCSStatusScreen.show()
        else:
            self.CSStatusScreen.show()

    def GlobalStatusScreen(self):
        # if power pmac
        if isinstance(self.pmac, PPmacSshInterface):
            self.PpmacGlobalStatusScreen.show()
        else:
            self.GlobalStatusScreen.show()

    # public slot
    def jogParameters(self):
        if isinstance(self.pmac, PPmacSshInterface):
            self.ppmacaxisSettingsScreen.show()
            self.ppmacaxisSettingsScreen.axisUpdate()
        else:
            self.axisSettingsScreen.show()
            self.axisSettingsScreen.axisUpdate()

    # Download a pmc configuration file to the PMAC
    def pmacLoadConfig(self):
        # First get the file from a file dialog
        myDialog = QFileDialog(self)
        q_file = myDialog.getOpenFileName(
            self, "Load PMC file", self.dirname, "PMAC configuration (*.pmc *.PMC)"
        )
        fileName, _ = q_file
        if not fileName:
            return
        self.dirname = path.dirname(str(fileName))

        # A couple of regular expressions for use in parsing the pmc file
        blankLine = re.compile(r"^\s*$")  # match blank lines

        # parsing through the file
        pmc = ClsPmacParser()
        pmcLines = pmc.parse(fileName)

        if pmcLines:
            # Get rid of all the empty lines, but keep line numbers
            commands = []
            for i, pmcLine in enumerate(pmcLines):
                if not blankLine.match(pmcLine):
                    commands.append((i + 1, pmcLine))

            # Prepend two close commands and a delete gather to the front of
            # any pmc file uploaded. This ensures that any open PLC buffers
            # are closed before an upload and that the gather buffer is
            # erased to make memory available for the new PLC. Two close
            # commands are sent to ensure that we leave any nested statements
            # (first close) before then closing the buffer (second close).
            # Dummy line numbers of zero are paired with each command to
            # match the formatting and to not disrupt the real line numbering
            closeCommands = [(0, "CLOSE"), (0, "CLOSE"), (0, "DELETE GATHER")]
            commands = closeCommands + commands

            # Open up progress dialog and start sending the commands.
            self.canceledDownload = False
            self.progressDialog = QProgressDialog(
                "Downloading PMAC configuration", "cancel", 0, len(pmcLines), self
            )
            self.progressDialog.setWindowModality(Qt.ApplicationModal)
            self.progressDialog.canceled.connect(self.cancel)
            self.txtShell.append("Beginning download of pmc file: " + fileName)
            self.commsThread.inputQueue.put(("sendSeries", commands))

    def cancel(self):
        self.canceledDownload = True
        self.commsThread.inputQueue.put(("cancelSendSeries", ""))

    def pmacPollingStatus(self):
        # If we are already polling, disable it
        if self.pollingStatus:
            self.pollingStatus = False
            self.commsThread.inputQueue.put(("disablePollingStatus", True))

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
            self.commsThread.inputQueue.put(("disablePollingStatus", False))
            self.btnPollingStatus.setText("disable polling")

            # Re-enable all the disabled labels and controls
            self.table.setEnabled(True)
            self.lblPosition.setEnabled(True)
            self.lblVelo.setEnabled(True)
            self.lblFolErr.setEnabled(True)
            self.pixPolling.setPixmap(self.greenLedOn)

    def jogNegContinousStart(self):
        # print "controlform.jogNegContinousStart(): Not implemented yet"
        (command, retStr, retStatus) = self.pmac.jogContinous(self.currentMotor, "neg")
        self.addToTxtShell(command, retStr)

    # public slot
    def jogPosContinousStart(self):
        # print "controlform.jogPosContinousStart(): Not implemented yet"
        (command, retStr, retStatus) = self.pmac.jogContinous(self.currentMotor, "pos")
        self.addToTxtShell(command, retStr)

    # public slot
    def sendSingleCommand(self):
        # print "controlform.sendSingleCommand(): Not implemented yet"
        command = self.lneSend.text()
        if len(self.commands) == 0 or self.commands[-1] != command:
            self.commands.append(command)
        (retStr, status) = self.pmac.sendCommand(command)
        self.addToTxtShell(command, retStr, False)
        self.commands_i = 0
        self.lneSend.setText("")

    @pyqtSlot(int, int, name="chooseMotorFromTable")
    def chooseMotorFromTable(self, a0):
        self.spnJogMotor.setValue(a0 + 1)

    # public slot
    def jogIncrementally(self, a0):  # a0 is True if 'jog inc' box checked
        self.lneJogDist.setEnabled(a0)
        if a0:
            self.btnJogPos.pressed.disconnect(self.jogPosContinousStart)
            self.btnJogPos.released.disconnect(self.jogStop)
            self.btnJogNeg.pressed.disconnect(self.jogNegContinousStart)
            self.btnJogNeg.released.disconnect(self.jogStop)
            self.btnJogNeg.clicked.connect(self.jogNeg)
            self.btnJogPos.clicked.connect(self.jogPos)
        else:
            self.btnJogPos.pressed.connect(self.jogPosContinousStart)
            self.btnJogPos.released.connect(self.jogStop)
            self.btnJogNeg.pressed.connect(self.jogNegContinousStart)
            self.btnJogNeg.released.connect(self.jogStop)
            self.btnJogNeg.clicked.disconnect(self.jogNeg)
            self.btnJogPos.clicked.disconnect(self.jogPos)

    def __item(self, row, col):
        item = self.table.item(row, col)
        if not item:
            item = QTableWidgetItem()
            self.table.setItem(row, col, item)
            item.setFlags(Qt.ItemIsEnabled)
        return item

    def addToTxtShell(self, command, retStr=None, chkShowAll=True):
        if chkShowAll is False or self.chkShowAll.isChecked():
            self.txtShell.append(command)
            if retStr is not None:
                self.txtShell.append(
                    retStr.rstrip("\x06").lstrip("\x07").replace("\r", " ")
                )

    # Called when an event comes out of the polling thread
    # and the jog ribbon.
    def updateMotors(self):

        self.commsThread.resultQueue.qsize()
        for queItem in range(0, self.commsThread.resultQueue.qsize()):
            try:
                value = self.commsThread.resultQueue.get(False)
            except Empty:
                return

            try:
                motorRow = value[4]
                # check for special cases
                if type(motorRow) == str:
                    if isinstance(self.pmac, PPmacSshInterface):
                        if motorRow == "G":
                            self.PpmacGlobalStatusScreen.updateStatus(
                                int(value[0].strip("$"), 16)
                            )
                            continue
                        if motorRow.startswith("CS"):
                            self.PpmacCSStatusScreen.updateStatus(
                                int(value[0].strip("$"), 16)
                            )
                            continue
                        if motorRow.startswith("FEED"):
                            self.PpmacCSStatusScreen.updateFeed(
                                int(round(float(value[0])))
                            )
                            continue
                        if motorRow == "IDENT":
                            self.updateIdentity(int(value[0]))
                            continue
                    else:
                        if motorRow == "G":
                            self.GlobalStatusScreen.updateStatus(int(value[0], 16))
                            continue
                        if motorRow.startswith("CS"):
                            self.CSStatusScreen.updateStatus(int(value[0], 16))
                            continue
                        if motorRow.startswith("FEED"):
                            self.CSStatusScreen.updateFeed(int(round(float(value[0]))))
                            continue
                        if motorRow == "IDENT":
                            self.updateIdentity(int(value[0]))
                            continue
                        if motorRow.startswith("M90"):
                            self.CSStatusScreen.updateAmpStatus(int(value[0]) & 448)
                            continue

                position = str(round(float(value[1]), 1))
                velocity = str(round(float(value[2]), 1))
                folerr = str(round(float(value[3]), 1))

                self.__item(motorRow, 0).setText(position)
                self.__item(motorRow, 1).setText(velocity)
                self.__item(motorRow, 2).setText(folerr)

                statusWord = int(value[0].strip("$"), 16)

                # define high and low limits for power pmac
                if isinstance(self.pmac, PPmacSshInterface):
                    loLim = bool(statusWord & 0x2000000000000000)  # MinusLimit
                    hiLim = bool(statusWord & 0x1000000000000000)  # PlusLimit
                    loLimSoft = bool(statusWord & 0x0080000000000000)  # SoftMinusLimit
                    hiLimSoft = bool(statusWord & 0x0040000000000000)  # SoftPlusLimit

                # define high and low limits for pmac
                else:
                    loLim = bool(statusWord & 0x400000000000)  # negative end limit set
                    hiLim = bool(statusWord & 0x200000000000)  # positive end limit set
                    loLimSoft = False
                    hiLimSoft = False

                # set limit indicators in polling table
                if hiLim:
                    self.__item(motorRow, 3).setIcon(QIcon(self.redLedOn))
                elif hiLimSoft:
                    self.__item(motorRow, 3).setIcon(QIcon(self.amberLedOn))
                else:
                    self.__item(motorRow, 3).setIcon(QIcon(self.redLedOff))
                if loLim:
                    self.__item(motorRow, 4).setIcon(QIcon(self.redLedOn))
                elif loLimSoft:
                    self.__item(motorRow, 4).setIcon(QIcon(self.amberLedOn))
                else:
                    self.__item(motorRow, 4).setIcon(QIcon(self.redLedOff))

                # Update also the jog ribbon
                if motorRow + 1 == self.currentMotor:
                    self.lblPosition.setText(position)
                    self.lblVelo.setText(velocity)
                    self.lblFolErr.setText(folerr)
                    if hiLim:
                        self.pixHiLim.setPixmap(self.redLedOn)
                    elif hiLimSoft:
                        self.pixHiLim.setPixmap(self.amberLedOn)
                    else:
                        self.pixHiLim.setPixmap(self.redLedOff)
                    if loLim:
                        self.pixLoLim.setPixmap(self.redLedOn)
                    elif loLimSoft:
                        self.pixLoLim.setPixmap(self.amberLedOn)
                    else:
                        self.pixLoLim.setPixmap(self.redLedOff)
                    self.statusScreen.updateStatus(statusWord)
                    self.ppmacstatusScreen.updateStatus(statusWord)

            except (ValueError, IndexError):
                # Catch the exception and continue, since there may be other
                # updates waiting in the queue.
                if self.verboseMode:
                    print("Update request received invalid response: ", value)

    domainNames = [
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
    subdomainLetters = [
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

    def updateIdentity(self, id):
        if not self.btnConnect.isEnabled():
            if id == 0:
                text = "Identity not set"
            else:
                domain = (id >> 20) & 0x0F
                # swVersion = (id >> 13) & 0x7F
                subdomainNum = (id >> 7) & 0x1F
                pmacNum = id & 0x1F
                subdomainLetter = (
                    ((id >> 6) & 0x01) | ((id >> 4) & 0x02) | ((id >> 10) & 0x04)
                )
                text = self.domainNames[domain]
                if subdomainNum != 0:
                    text += "%02d" % subdomainNum
                    text += self.subdomainLetters[domain][subdomainLetter]
                text += " %s " % self.pmac.getShortModelName()
                text += "%d" % pmacNum
            self.lblIdentity.setText(text)

    def updateWatches(self):
        self.commsThread.watchesQueue.qsize()
        for queItem in range(0, self.commsThread.watchesQueue.qsize()):
            try:
                value = self.commsThread.watchesQueue.get(False)
            except Empty:
                return
            for n in range(len(value)):
                if "." in value[n]:
                    value[n] = round(float(value[n]), 1)
                self.watchesScreen.table.setItem(n, 1, QTableWidgetItem(str(value[n])))

    def customEvent(self, E):
        if E.type() == self.progressEventType:
            (lines, err) = E.data()
            self.progressDialog.setValue(lines)
            if err:
                self.txtShell.append(err)
        elif E.type() == self.downloadDoneEventType:
            self.progressDialog.setValue(self.progressDialog.maximum())
            self.txtShell.append(str(E.data()))
        elif E.type() == self.updatesReadyEventType:
            self.updateMotors()
            self.updateWatches()

    def signalHandler(self, signum, frame):
        if signum == 2:  # SIGINT
            print("Closing connection...")
            self.pmac.disconnect()
            print("Closing application.")
            QApplication.exit(0)

    def die(self):
        self.remoteDisconnect()
        self.commsThread.inputQueue.put(("die", ""))


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
        help="Print more details (than necessary in most " "cases...)",
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
        help="Display and poll NAXES axes. Default is 32 for a "
        "PMAC, 8 for a geoBrick",
    )
    parser.add_option(
        "-t",
        "--timeout",
        action="store",
        type="float",
        dest="timeout",
        default=3.0,
        help="Set the communication timeout (default: 3 seconds, " "minimum: 1 second)",
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
    app.exec_()


if __name__ == "__main__":
    main()
