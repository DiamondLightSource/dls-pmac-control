import PyQt5
import unittest
from mock import patch, Mock
import time
import sys
sys.path.append('/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol')
from PyQt5.QtCore import Qt, QPoint, QEvent
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem
from motor import Controlform

from dls_pmaclib.dls_pmacremote import (
    PmacEthernetInterface,
    PmacSerialInterface,
    PmacTelnetInterface,
    PPmacSshInterface)

app = QApplication(sys.argv)

class TestOptions():
    def __init__(self):
        self.verbose = False
        self.protocol = "ts"
        self.server = "test"
        self.port = "123"
        self.defaultAxis = 1
        self.nAxes = 8
        self.timeout = 3.0 

class MotorTest(unittest.TestCase):

    @patch("status.Statusform")
    @patch("status.PpmacStatusform")
    @patch("CSstatus.CSStatusForm")
    @patch("CSstatus.PpmacCSStatusForm")
    @patch("GlobalStatus.GlobalStatusForm")
    @patch("GlobalStatus.PpmacGlobalStatusForm")
    @patch("axissettings.Axissettingsform")
    @patch("axissettings.PpmacAxissettingsform")
    @patch("gather.PmacGatherform")
    @patch("ppmacgather.PpmacGatherform")
    @patch("watches.Watchesform")
    @patch("login.Loginform")
    @patch("commsThread.CommsThread")
    @patch("PyQt5.QtCore.QEvent")
    @patch("threading.Thread")
    @patch("signal.signal")
    def setUp(self, mock_signal, mock_thread, mock_event, mock_comms, 
            mock_login, mock_watches, mock_ppmacgather, mock_gather, 
            mock_ppmacaxis, mock_axis, mock_ppmacglobal, mock_global,
            mock_ppmaccs, mock_cs, mock_ppmacstatus, mock_status):
        self.options = TestOptions()
        self.obj = Controlform(self.options)

    def test_initial_state(self):
        assert self.obj.ConnectionType == 0
        assert self.obj.pmac == None
        assert self.obj.powerpmac == None
        assert self.obj.pollingStatus == True
        assert self.obj.isUsingSerial == False
        assert self.obj.lneServer.text() == "test"
        assert self.obj.lnePort.text() == "123"
        assert self.obj.currentMotor == 1
        assert self.obj.nAxes == 8

    def test_useTerminalServerConnection(self):
        self.obj.ConnectionType = None
        self.obj.useTerminalServerConnection()
        assert self.obj.ConnectionType == 0
        assert self.obj.lneServer.text() == "blxxi-nt-tserv-01"
        assert self.obj.lnePort.text() == "7017"
        assert self.obj.textLabel1.text() == "Server:"
        assert self.obj.textLabel2.text() == "Port:"
        assert self.obj.lblPolling.text() == "Polling"
        self.assertFalse(self.obj.lnePollRate.isEnabled())
        self.assertFalse(self.obj.lblPollRate.isEnabled())

    def test_useSocketConnection(self):
        self.obj.ConnectionType = None
        self.obj.useSocketConnection()
        assert self.obj.ConnectionType == 1
        assert self.obj.lneServer.text() == "10.2.2.28"
        assert self.obj.lnePort.text() == "1025"
        assert self.obj.textLabel1.text() == "IP address:"
        assert self.obj.textLabel2.text() == "Port:"
        assert self.obj.lblPolling.text() == "Polling"
        self.assertFalse(self.obj.lnePollRate.isEnabled())
        self.assertFalse(self.obj.lblPollRate.isEnabled())

    def test_useSerial(self):
        self.obj.ConnectionType = None
        self.obj.useSerial()
        assert self.obj.ConnectionType == 2
        assert self.obj.lneServer.text() == "/dev/ttyUSB0"
        assert self.obj.lnePort.text() == "38400"
        assert self.obj.textLabel1.text() == "COM port:"
        assert self.obj.textLabel2.text() == "Baudrate:"
        assert self.obj.lblPolling.text() == "Polling @"
        assert self.obj.lnePollRate.text() == "0"
        self.assertTrue(self.obj.lnePollRate.isEnabled())
        self.assertTrue(self.obj.lblPollRate.isEnabled())

    def test_useSshConnection(self):
        self.obj.ConnectionType = None
        self.obj.useSshConnection()
        assert self.obj.ConnectionType == 3
        assert self.obj.lneServer.text() == "192.168.56.10"
        assert self.obj.lnePort.text() == "22"
        assert self.obj.textLabel1.text() == "IP address:"
        assert self.obj.textLabel2.text() == "Port:"
        assert self.obj.lblPolling.text() == "Polling"
        self.assertFalse(self.obj.lnePollRate.isEnabled())
        self.assertFalse(self.obj.lblPollRate.isEnabled())

    @unittest.skip("checkHistory not being called")
    @patch("PyQt5.QtWidgets.QLineEdit.keyPressEvent")
    def test_checkHistory_empty(self, mock_event):
        obj.commands = []
        obj.commands_i = 0
        QTest.keyClick(obj.lneSend, Qt.Key_Up)
        assert obj.commands_i == 0
        assert obj.lneSend.text() == ""
        #assert mock_event.called

    @unittest.skip("checkHistory not being called")
    @patch("PyQt5.QtWidgets.QLineEdit.keyPressEvent")
    def test_checkHistory_keyup(self, mock_event):
        obj.commands = ["cmd1","cmd2","cmd3"]
        obj.commands_i = 0
        QTest.keyClick(obj.lneSend, Qt.Key_Up)
        assert obj.commands_i == -1
        assert obj.lneSend.text() == "cmd3"
        #assert mock_event.called

    @unittest.skip("checkHistory not being called")
    @patch("PyQt5.QtWidgets.QLineEdit.keyPressEvent")
    def test_checkHistory_keydown(self, mock_event):
        self.obj.commands = ["cmd1","cmd2","cmd3"]
        self.obj.commands_i = -1
        #self.obj.show()
        #self.obj.lneSend.setFocus()
        #QTest.mouseClick(self.obj.lneSend, Qt.LeftButton)
        QTest.keyClick(self.obj.lneSend, Qt.Key_Up)
        #self.event = self.obj.lneSend.keyPressEvent
        #self.event.key = Qt.Key_Up
        #event = QKeyEvent(self.obj.lneSend.keyPressEvent, 16777235)
        #self.obj.checkHistory(self.obj.lneSend, event)
        #self.obj.checkHistory(self.obj.lneSend, self.obj.lneSend.keyPressEvent)
        #self.obj.lneSend.keyPressEvent(Qt.Key_Up)
        assert self.obj.commands_i == 0
        assert self.obj.lneSend.text() == "cmd1"
        assert mock_event.called

    #@unittest.skip("need to mock setConnectionParams")
    #@patch("motor.Controlform.pmac")
    @patch.object(PmacTelnetInterface, "connect")
    @patch.object(PmacTelnetInterface, "setConnectionParams")
    #@patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface")
    def test_remote_connect_telnet(self, mock_params, mock_connect):
        mock_params.return_value = None
        mock_connect.return_value = False
        #attrs = {"setConnectionParams" : "this is a test", "connect" : False}
        #mock_class.configure_mock(**attrs)
        self.obj.connectionType = 0
        self.obj.remoteConnect()
        #print(self.obj.pmac.setConnectionParams())
        #assert mock_class.called

    #def test_remote_connect_ethernet(self, mock_params, mock_connect):
    #def test_remote_connect_serial(self, mock_params, mock_connect):
    #def test_remote_connect_ssh(self, mock_params, mock_connect):

    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    def test_remote_disconnect_pmac_none(self, mock_pixmap):
        self.obj.pmac = None
        self.obj.remoteDisconnect()
        self.assertEqual(self.obj.windowTitle(), "Delta Tau motor controller")
        self.assertTrue(self.obj.btnConnect.isEnabled())
        self.assertFalse(self.obj.btnDisconnect.isEnabled())
        self.assertTrue(self.obj.lneServer.isEnabled())
        self.assertTrue(self.obj.lnePort.isEnabled())
        self.assertTrue(self.obj.btnGroupProtocol.isEnabled())
        self.assertFalse(self.obj.btnJogNeg.isEnabled())
        self.assertFalse(self.obj.btnJogPos.isEnabled())
        self.assertFalse(self.obj.btnJogStop.isEnabled())
        self.assertFalse(self.obj.btnHome.isEnabled())
        self.assertFalse(self.obj.lneSend.isEnabled())
        self.assertFalse(self.obj.btnSend.isEnabled())
        self.assertFalse(self.obj.lneJogTo.isEnabled())
        self.assertFalse(self.obj.lneJogDist.isEnabled())
        self.assertFalse(self.obj.btnJogTo.isEnabled())
        self.assertFalse(self.obj.btnEnergise.isEnabled())
        self.assertFalse(self.obj.btnKillAll.isEnabled())
        self.assertFalse(self.obj.btnStatus.isEnabled())
        self.assertFalse(self.obj.btnCSStatus.isEnabled())
        self.assertFalse(self.obj.btnGlobalStatus.isEnabled())
        self.assertFalse(self.obj.btnSettings.isEnabled())
        self.assertFalse(self.obj.btnKillMotor.isEnabled())
        self.assertFalse(self.obj.btnLoadFile.isEnabled())
        self.assertFalse(self.obj.chkJogInc.isEnabled())
        self.assertFalse(self.obj.btnPollingStatus.isEnabled())
        self.assertFalse(self.obj.btnGather.isEnabled())
        self.assertFalse(self.obj.btnWatches.isEnabled())
        self.assertFalse(self.obj.table.isEnabled())
        mock_pixmap.assert_called_with(self.obj.greenLedOff)
        self.assertEqual(self.obj.lblIdentity.text(),"")

    def tearDown(self):
        self.obj.close()
