import PyQt5
import unittest
from mock import patch, Mock
import time
import sys
sys.path.append('/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol')
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem
from motor import Controlform
from optparse import OptionParser

app = QApplication(sys.argv)

parser = OptionParser("usage")
parser.add_option("-v", dest="verbose", default=False)
parser.add_option("-o", dest="protocol", default="ts")
parser.add_option("-s", dest="server", default="test server")
parser.add_option("-p", dest="port", default="test port")
parser.add_option("-a", dest="defaultAxis", default=1)
parser.add_option("-n", dest="nAxes", default=8)
parser.add_option("-t", dest="timeout", default=3.0)
(options, args) = parser.parse_args()

class MotorTest(unittest.TestCase):

    def test_initial_state(self):
        obj = Controlform(options)
        assert obj.ConnectionType == 0
        assert obj.pmac == None
        assert obj.powerpmac == None
        assert obj.pollingStatus == True
        assert obj.isUsingSerial == False
        assert obj.lneServer.text() == "test server"
        assert obj.lnePort.text() == "test port"
        assert obj.currentMotor == 1
        assert obj.nAxes == 8
        obj.close()

    def test_useTerminalServerConnection(self):
        obj = Controlform(options)
        obj.ConnectionType = None
        obj.useTerminalServerConnection()
        assert obj.ConnectionType == 0
        assert obj.lneServer.text() == "blxxi-nt-tserv-01"
        assert obj.lnePort.text() == "7017"
        assert obj.textLabel1.text() == "Server:"
        assert obj.textLabel2.text() == "Port:"
        assert obj.lblPolling.text() == "Polling"
        self.assertFalse(obj.lnePollRate.isEnabled())
        self.assertFalse(obj.lblPollRate.isEnabled())

    def test_useSocketConnection(self):
        obj = Controlform(options)
        obj.ConnectionType = None
        obj.useSocketConnection()
        assert obj.ConnectionType == 1
        assert obj.lneServer.text() == "10.2.2.28"
        assert obj.lnePort.text() == "1025"
        assert obj.textLabel1.text() == "IP address:"
        assert obj.textLabel2.text() == "Port:"
        assert obj.lblPolling.text() == "Polling"
        self.assertFalse(obj.lnePollRate.isEnabled())
        self.assertFalse(obj.lblPollRate.isEnabled())

    def test_useSerial(self):
        obj = Controlform(options)
        obj.ConnectionType = None
        obj.useSerial()
        assert obj.ConnectionType == 2
        assert obj.lneServer.text() == "/dev/ttyUSB0"
        assert obj.lnePort.text() == "38400"
        assert obj.textLabel1.text() == "COM port:"
        assert obj.textLabel2.text() == "Baudrate:"
        assert obj.lblPolling.text() == "Polling @"
        assert obj.lnePollRate.text() == "0"
        self.assertTrue(obj.lnePollRate.isEnabled())
        self.assertTrue(obj.lblPollRate.isEnabled())

    def test_useSshConnection(self):
        obj = Controlform(options)
        obj.ConnectionType = None
        obj.useSshConnection()
        assert obj.ConnectionType == 3
        assert obj.lneServer.text() == "192.168.56.10"
        assert obj.lnePort.text() == "22"
        assert obj.textLabel1.text() == "IP address:"
        assert obj.textLabel2.text() == "Port:"
        assert obj.lblPolling.text() == "Polling"
        self.assertFalse(obj.lnePollRate.isEnabled())
        self.assertFalse(obj.lblPollRate.isEnabled())

    def test_checkHistory(self):
        obj = Controlform(options)
        obj.commands = ["cmd1","cmd2","cmd3"]

    '''def checkHistory(self, edit, event):
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
        QLineEdit.keyPressEvent(edit, event)'''



