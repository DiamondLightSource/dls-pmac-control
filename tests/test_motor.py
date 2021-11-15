import PyQt5
import unittest
from mock import patch, Mock
import time
import sys
sys.path.append('/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol')
from PyQt5.QtCore import Qt, QPoint, QEvent
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from motor import Controlform

app = QApplication(sys.argv)

class TestOptionsTelnet():
    def __init__(self):
        self.verbose = False
        self.protocol = "ts"
        self.server = "test"
        self.port = "123"
        self.defaultAxis = 1
        self.nAxes = 8
        self.timeout = 3.0

class TestOptionsEthernet():
    def __init__(self):
        self.verbose = False
        self.protocol = "tcpip"
        self.server = "test"
        self.port = "123"
        self.defaultAxis = 1
        self.nAxes = 8
        self.timeout = 3.0

class TestOptionsSerial():
    def __init__(self):
        self.verbose = False
        self.protocol = "rs232"
        self.server = "test"
        self.port = "123"
        self.defaultAxis = 1
        self.nAxes = 8
        self.timeout = 3.0

class TestOptionsSsh():
    def __init__(self):
        self.verbose = False
        self.protocol = "ssh"
        self.server = "test"
        self.port = "123"
        self.defaultAxis = 1
        self.nAxes = 8
        self.timeout = 3.0

class MotorTestTelnet(unittest.TestCase):

    @patch("dls_pmaccontrol.status.Statusform")
    @patch("dls_pmaccontrol.status.PpmacStatusform")
    @patch("dls_pmaccontrol.CSstatus.CSStatusForm")
    @patch("dls_pmaccontrol.CSstatus.PpmacCSStatusForm")
    @patch("dls_pmaccontrol.GlobalStatus.GlobalStatusForm")
    @patch("dls_pmaccontrol.GlobalStatus.PpmacGlobalStatusForm")
    @patch("dls_pmaccontrol.axissettings.Axissettingsform")
    @patch("dls_pmaccontrol.axissettings.PpmacAxissettingsform")
    @patch("dls_pmaccontrol.gather.PmacGatherform")
    @patch("dls_pmaccontrol.ppmacgather.PpmacGatherform")
    @patch("dls_pmaccontrol.watches.Watchesform")
    @patch("dls_pmaccontrol.login.Loginform")
    @patch("dls_pmaccontrol.commsThread.CommsThread")
    @patch("PyQt5.QtCore.QEvent")
    @patch("threading.Thread")
    @patch("signal.signal")
    def setUp(self, mock_signal, mock_thread, mock_event, mock_comms, 
            mock_login, mock_watches, mock_ppmacgather, mock_gather, 
            mock_ppmacaxis, mock_axis, mock_ppmacglobal, mock_global,
            mock_ppmaccs, mock_cs, mock_ppmacstatus, mock_status):
        self.options = TestOptionsTelnet()
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

    @patch("PyQt5.QtWidgets.QMessageBox.information")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.setConnectionParams")
    def test_remote_connect_auth_error(self, mock_params, 
                        mock_connect, mock_box):
        mock_connect.return_value = "Invalid username or password"
        ret = self.obj.remoteConnect()
        assert mock_params.called
        assert mock_connect.called
        mock_box.assert_called_with(self.obj, "Error", "Invalid username or password")
        assert ret == None

    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.isModelGeobrick")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.getNumberOfAxes")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.getPmacModel")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.setConnectionParams")
    def test_remote_connect(self, mock_params, mock_connect, mock_model, 
                                     mock_axes, mock_geo, mock_pixmap):
        mock_model.return_value = "test"
        mock_axes.return_value = 8
        mock_geo.return_value = True
        mock_connect.return_value = None
        ret = self.obj.remoteConnect()
        assert mock_params.called
        assert mock_connect.called
        assert mock_model.called
        assert self.obj.windowTitle() == "Delta Tau motor controller - test"
        assert ret == None
        assert self.obj.table.rowCount() == 8
        assert self.obj.spnJogMotor.maximum() == 8
        self.assertFalse(self.obj.btnConnect.isEnabled())
        self.assertFalse(self.obj.lneServer.isEnabled())
        self.assertFalse(self.obj.lnePort.isEnabled())
        self.assertFalse(self.obj.btnGroupProtocol.isEnabled())
        self.assertTrue(self.obj.btnDisconnect.isEnabled())
        self.assertTrue(self.obj.btnJogNeg.isEnabled())
        self.assertTrue(self.obj.btnJogPos.isEnabled())
        self.assertTrue(self.obj.btnJogStop.isEnabled())
        self.assertTrue(self.obj.btnHome.isEnabled())
        self.assertTrue(self.obj.lneSend.isEnabled())
        self.assertTrue(self.obj.btnSend.isEnabled())
        self.assertTrue(self.obj.lneJogTo.isEnabled())
        self.assertTrue(self.obj.lneJogDist.isEnabled())
        self.assertTrue(self.obj.btnJogTo.isEnabled())
        self.assertFalse(self.obj.btnEnergise.isEnabled())
        self.assertTrue(self.obj.btnKillAll.isEnabled())
        self.assertTrue(self.obj.btnStatus.isEnabled())
        self.assertTrue(self.obj.btnCSStatus.isEnabled())
        self.assertTrue(self.obj.btnGlobalStatus.isEnabled())
        self.assertTrue(self.obj.btnLoadFile.isEnabled())
        self.assertTrue(self.obj.btnSettings.isEnabled())
        self.assertTrue(self.obj.btnKillMotor.isEnabled())
        self.assertTrue(self.obj.chkJogInc.isEnabled())
        self.assertTrue(self.obj.btnPollingStatus.isEnabled())
        self.assertTrue(self.obj.btnGather.isEnabled())
        self.assertTrue(self.obj.btnWatches.isEnabled())
        self.assertTrue(self.obj.table.isEnabled())
        self.assertFalse(self.obj.lnePollRate.isEnabled())
        self.assertFalse(self.obj.lblPollRate.isEnabled())
        mock_pixmap.assert_called_with(self.obj.greenLedOn)

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

    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.isModelGeobrick")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.getNumberOfAxes")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.getPmacModel")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.setConnectionParams")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.disconnect")
    def test_remote_disconnect(self, mock_disconnect, mock_params, mock_connect, 
                                mock_model, mock_axes, mock_geo, mock_pixmap):
        # create connection
        mock_model.return_value = "test"
        mock_axes.return_value = 8
        mock_geo.return_value = True
        mock_connect.return_value = None
        self.obj.remoteConnect() 
        # now disconnect
        ret = self.obj.remoteDisconnect()
        assert mock_disconnect.called
        assert self.obj.windowTitle() == "Delta Tau motor controller"
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
        assert self.obj.lblIdentity.text() == ""

    def tearDown(self):
        self.obj.close()

class MotorTestEthernet(unittest.TestCase):

    @patch("dls_pmaccontrol.status.Statusform")
    @patch("dls_pmaccontrol.status.PpmacStatusform")
    @patch("dls_pmaccontrol.CSstatus.CSStatusForm")
    @patch("dls_pmaccontrol.CSstatus.PpmacCSStatusForm")
    @patch("dls_pmaccontrol.GlobalStatus.GlobalStatusForm")
    @patch("dls_pmaccontrol.GlobalStatus.PpmacGlobalStatusForm")
    @patch("dls_pmaccontrol.axissettings.Axissettingsform")
    @patch("dls_pmaccontrol.axissettings.PpmacAxissettingsform")
    @patch("dls_pmaccontrol.gather.PmacGatherform")
    @patch("dls_pmaccontrol.ppmacgather.PpmacGatherform")
    @patch("dls_pmaccontrol.watches.Watchesform")
    @patch("dls_pmaccontrol.login.Loginform")
    @patch("dls_pmaccontrol.commsThread.CommsThread")
    @patch("PyQt5.QtCore.QEvent")
    @patch("threading.Thread")
    @patch("signal.signal")
    def setUp(self, mock_signal, mock_thread, mock_event, mock_comms, 
            mock_login, mock_watches, mock_ppmacgather, mock_gather, 
            mock_ppmacaxis, mock_axis, mock_ppmacglobal, mock_global,
            mock_ppmaccs, mock_cs, mock_ppmacstatus, mock_status):
        self.options = TestOptionsEthernet()
        self.obj = Controlform(self.options)

    def test_initial_state(self):
        assert self.obj.ConnectionType == 1
        assert self.obj.pmac == None
        assert self.obj.powerpmac == None
        assert self.obj.pollingStatus == True
        assert self.obj.isUsingSerial == False
        assert self.obj.lneServer.text() == "test"
        assert self.obj.lnePort.text() == "123"
        assert self.obj.currentMotor == 1
        assert self.obj.nAxes == 8

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

    @patch("PyQt5.QtWidgets.QMessageBox.information")
    @patch("dls_pmaclib.dls_pmacremote.PmacEthernetInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PmacEthernetInterface.setConnectionParams")
    def test_remote_connect_auth_error(self, mock_params, 
                        mock_connect, mock_box):
        mock_connect.return_value = "Invalid username or password"
        ret = self.obj.remoteConnect()
        assert mock_params.called
        assert mock_connect.called
        mock_box.assert_called_with(self.obj, "Error", "Invalid username or password")
        assert ret == None

    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    @patch("dls_pmaclib.dls_pmacremote.PmacEthernetInterface.isModelGeobrick")
    @patch("dls_pmaclib.dls_pmacremote.PmacEthernetInterface.getNumberOfAxes")
    @patch("dls_pmaclib.dls_pmacremote.PmacEthernetInterface.getPmacModel")
    @patch("dls_pmaclib.dls_pmacremote.PmacEthernetInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PmacEthernetInterface.setConnectionParams")
    def test_remote_connect(self, mock_params, mock_connect, mock_model, 
                                     mock_axes, mock_geo, mock_pixmap):
        mock_model.return_value = "test"
        mock_axes.return_value = 8
        mock_geo.return_value = True
        mock_connect.return_value = None
        ret = self.obj.remoteConnect()
        assert mock_params.called
        assert mock_connect.called
        assert mock_model.called
        assert self.obj.windowTitle() == "Delta Tau motor controller - test"
        assert ret == None
        assert self.obj.table.rowCount() == 8
        assert self.obj.spnJogMotor.maximum() == 8
        self.assertFalse(self.obj.btnConnect.isEnabled())
        self.assertFalse(self.obj.lneServer.isEnabled())
        self.assertFalse(self.obj.lnePort.isEnabled())
        self.assertFalse(self.obj.btnGroupProtocol.isEnabled())
        self.assertTrue(self.obj.btnDisconnect.isEnabled())
        self.assertTrue(self.obj.btnJogNeg.isEnabled())
        self.assertTrue(self.obj.btnJogPos.isEnabled())
        self.assertTrue(self.obj.btnJogStop.isEnabled())
        self.assertTrue(self.obj.btnHome.isEnabled())
        self.assertTrue(self.obj.lneSend.isEnabled())
        self.assertTrue(self.obj.btnSend.isEnabled())
        self.assertTrue(self.obj.lneJogTo.isEnabled())
        self.assertTrue(self.obj.lneJogDist.isEnabled())
        self.assertTrue(self.obj.btnJogTo.isEnabled())
        self.assertFalse(self.obj.btnEnergise.isEnabled())
        self.assertTrue(self.obj.btnKillAll.isEnabled())
        self.assertTrue(self.obj.btnStatus.isEnabled())
        self.assertTrue(self.obj.btnCSStatus.isEnabled())
        self.assertTrue(self.obj.btnGlobalStatus.isEnabled())
        self.assertTrue(self.obj.btnLoadFile.isEnabled())
        self.assertTrue(self.obj.btnSettings.isEnabled())
        self.assertTrue(self.obj.btnKillMotor.isEnabled())
        self.assertTrue(self.obj.chkJogInc.isEnabled())
        self.assertTrue(self.obj.btnPollingStatus.isEnabled())
        self.assertTrue(self.obj.btnGather.isEnabled())
        self.assertTrue(self.obj.btnWatches.isEnabled())
        self.assertTrue(self.obj.table.isEnabled())
        self.assertFalse(self.obj.lnePollRate.isEnabled())
        self.assertFalse(self.obj.lblPollRate.isEnabled())
        mock_pixmap.assert_called_with(self.obj.greenLedOn)

    @unittest.skip("not working")
    @patch("motor.Controlform.jogNeg")
    @patch("motor.Controlform.jogPos")
    def test_jog_incrementally_true(self, jog_neg, jog_pos):
        self.obj.jogIncrementally(True)
        self.assertTrue(self.obj.lneJogDist.isEnabled())
        QTest.mouseClick(self.obj.btnJogNeg, Qt.LeftButton)
        assert jog_neg.called
        QTest.mouseClick(self.obj.btnJogPos, Qt.LeftButton)
        assert jog_pos.called
    @unittest.skip("not finished")
    def test_jog_incrementally_false(self):
        self.obj.jogIncrementally(False)
        self.assertFalse(self.obj.lneJogDist.isEnabled())
        QTest.mouseClick(obj.btnJogNeg, Qt.LeftButton)
        QTest.mouseClick(obj.btnJogPos, Qt.LeftButton)

    def tearDown(self):
        self.obj.close()

class MotorTestSerial(unittest.TestCase):

    @patch("dls_pmaccontrol.status.Statusform")
    @patch("dls_pmaccontrol.status.PpmacStatusform")
    @patch("dls_pmaccontrol.CSstatus.CSStatusForm")
    @patch("dls_pmaccontrol.CSstatus.PpmacCSStatusForm")
    @patch("dls_pmaccontrol.GlobalStatus.GlobalStatusForm")
    @patch("dls_pmaccontrol.GlobalStatus.PpmacGlobalStatusForm")
    @patch("dls_pmaccontrol.axissettings.Axissettingsform")
    @patch("dls_pmaccontrol.axissettings.PpmacAxissettingsform")
    @patch("dls_pmaccontrol.gather.PmacGatherform")
    @patch("dls_pmaccontrol.ppmacgather.PpmacGatherform")
    @patch("dls_pmaccontrol.watches.Watchesform")
    @patch("dls_pmaccontrol.login.Loginform")
    @patch("dls_pmaccontrol.commsThread.CommsThread")
    @patch("PyQt5.QtCore.QEvent")
    @patch("threading.Thread")
    @patch("signal.signal")
    def setUp(self, mock_signal, mock_thread, mock_event, mock_comms, 
            mock_login, mock_watches, mock_ppmacgather, mock_gather, 
            mock_ppmacaxis, mock_axis, mock_ppmacglobal, mock_global,
            mock_ppmaccs, mock_cs, mock_ppmacstatus, mock_status):
        self.options = TestOptionsSerial()
        self.obj = Controlform(self.options)

    def test_initial_state(self):
        assert self.obj.ConnectionType == 2
        assert self.obj.pmac == None
        assert self.obj.powerpmac == None
        assert self.obj.pollingStatus == True
        assert self.obj.isUsingSerial == False
        assert self.obj.lneServer.text() == "test"
        assert self.obj.lnePort.text() == "123"
        assert self.obj.currentMotor == 1
        assert self.obj.nAxes == 8

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

    @patch("PyQt5.QtWidgets.QMessageBox.information")
    @patch("dls_pmaclib.dls_pmacremote.PmacSerialInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PmacSerialInterface.setConnectionParams")
    def test_remote_connect_auth_error(self, mock_params, 
                        mock_connect, mock_box):
        mock_connect.return_value = "Invalid username or password"
        ret = self.obj.remoteConnect()
        assert mock_params.called
        assert mock_connect.called
        mock_box.assert_called_with(self.obj, "Error", "Invalid username or password")
        assert ret == None

    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    @patch("dls_pmaclib.dls_pmacremote.PmacSerialInterface.isModelGeobrick")
    @patch("dls_pmaclib.dls_pmacremote.PmacSerialInterface.getNumberOfAxes")
    @patch("dls_pmaclib.dls_pmacremote.PmacSerialInterface.getPmacModel")
    @patch("dls_pmaclib.dls_pmacremote.PmacSerialInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PmacSerialInterface.setConnectionParams")
    def test_remote_connect(self, mock_params, mock_connect, mock_model, 
                                     mock_axes, mock_geo, mock_pixmap):
        mock_model.return_value = "test"
        mock_axes.return_value = 8
        mock_geo.return_value = True
        mock_connect.return_value = None
        ret = self.obj.remoteConnect()
        assert mock_params.called
        assert mock_connect.called
        assert mock_model.called
        assert self.obj.windowTitle() == "Delta Tau motor controller - test"
        assert ret == None
        assert self.obj.table.rowCount() == 8
        assert self.obj.spnJogMotor.maximum() == 8
        self.assertFalse(self.obj.btnConnect.isEnabled())
        self.assertFalse(self.obj.lneServer.isEnabled())
        self.assertFalse(self.obj.lnePort.isEnabled())
        self.assertFalse(self.obj.btnGroupProtocol.isEnabled())
        self.assertTrue(self.obj.btnDisconnect.isEnabled())
        self.assertTrue(self.obj.btnJogNeg.isEnabled())
        self.assertTrue(self.obj.btnJogPos.isEnabled())
        self.assertTrue(self.obj.btnJogStop.isEnabled())
        self.assertTrue(self.obj.btnHome.isEnabled())
        self.assertTrue(self.obj.lneSend.isEnabled())
        self.assertTrue(self.obj.btnSend.isEnabled())
        self.assertTrue(self.obj.lneJogTo.isEnabled())
        self.assertTrue(self.obj.lneJogDist.isEnabled())
        self.assertTrue(self.obj.btnJogTo.isEnabled())
        self.assertFalse(self.obj.btnEnergise.isEnabled())
        self.assertTrue(self.obj.btnKillAll.isEnabled())
        self.assertTrue(self.obj.btnStatus.isEnabled())
        self.assertTrue(self.obj.btnCSStatus.isEnabled())
        self.assertTrue(self.obj.btnGlobalStatus.isEnabled())
        self.assertTrue(self.obj.btnLoadFile.isEnabled())
        self.assertTrue(self.obj.btnSettings.isEnabled())
        self.assertTrue(self.obj.btnKillMotor.isEnabled())
        self.assertTrue(self.obj.chkJogInc.isEnabled())
        self.assertTrue(self.obj.btnPollingStatus.isEnabled())
        self.assertTrue(self.obj.btnGather.isEnabled())
        self.assertTrue(self.obj.btnWatches.isEnabled())
        self.assertTrue(self.obj.table.isEnabled())
        self.assertFalse(self.obj.lnePollRate.isEnabled())
        self.assertFalse(self.obj.lblPollRate.isEnabled())
        mock_pixmap.assert_called_with(self.obj.greenLedOn)

    def tearDown(self):
        self.obj.close()

class MotorTestSsh(unittest.TestCase):

    @patch("dls_pmaccontrol.status.Statusform")
    @patch("dls_pmaccontrol.status.PpmacStatusform")
    @patch("dls_pmaccontrol.CSstatus.CSStatusForm")
    @patch("dls_pmaccontrol.CSstatus.PpmacCSStatusForm")
    @patch("dls_pmaccontrol.GlobalStatus.GlobalStatusForm")
    @patch("dls_pmaccontrol.GlobalStatus.PpmacGlobalStatusForm")
    @patch("dls_pmaccontrol.axissettings.Axissettingsform")
    @patch("dls_pmaccontrol.axissettings.PpmacAxissettingsform")
    @patch("dls_pmaccontrol.gather.PmacGatherform")
    @patch("dls_pmaccontrol.ppmacgather.PpmacGatherform")
    @patch("dls_pmaccontrol.watches.Watchesform")
    @patch("dls_pmaccontrol.login.Loginform")
    @patch("dls_pmaccontrol.commsThread.CommsThread")
    @patch("PyQt5.QtCore.QEvent")
    @patch("threading.Thread")
    @patch("signal.signal")
    def setUp(self, mock_signal, mock_thread, mock_event, mock_comms, 
            mock_login, mock_watches, mock_ppmacgather, mock_gather, 
            mock_ppmacaxis, mock_axis, mock_ppmacglobal, mock_global,
            mock_ppmaccs, mock_cs, mock_ppmacstatus, mock_status):
        self.options = TestOptionsSsh()
        self.obj = Controlform(self.options)

    def test_initial_state(self):
        assert self.obj.ConnectionType == 3
        assert self.obj.pmac == None
        assert self.obj.powerpmac == None
        assert self.obj.pollingStatus == True
        assert self.obj.isUsingSerial == False
        assert self.obj.lneServer.text() == "test"
        assert self.obj.lnePort.text() == "123"
        assert self.obj.currentMotor == 1
        assert self.obj.nAxes == 8

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

    @patch("dls_pmaccontrol.login.Loginform.exec")
    @patch("PyQt5.QtWidgets.QMessageBox.information")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.setConnectionParams")
    def test_remote_connect_auth_error(self, mock_params, 
                        mock_connect, mock_box, mock_exec):
        mock_connect.return_value = "Invalid username or password"
        mock_exec.return_value = True
        ret = self.obj.remoteConnect()
        assert mock_params.called
        assert mock_connect.called
        mock_box.assert_called_with(self.obj, "Error", "Invalid username or password")
        assert ret == None

    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.isModelGeobrick")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.getNumberOfAxes")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.getPmacModel")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.setConnectionParams")
    def test_remote_connect(self, mock_params, mock_connect, mock_model, 
                                     mock_axes, mock_geo, mock_pixmap):
        mock_model.return_value = "test"
        mock_axes.return_value = 8
        mock_geo.return_value = True
        mock_connect.return_value = None
        ret = self.obj.remoteConnect()
        assert mock_params.called
        assert mock_connect.called
        assert mock_model.called
        assert self.obj.windowTitle() == "Delta Tau motor controller - test"
        assert ret == None
        assert self.obj.table.rowCount() == 8
        assert self.obj.spnJogMotor.maximum() == 8
        self.assertFalse(self.obj.btnConnect.isEnabled())
        self.assertFalse(self.obj.lneServer.isEnabled())
        self.assertFalse(self.obj.lnePort.isEnabled())
        self.assertFalse(self.obj.btnGroupProtocol.isEnabled())
        self.assertTrue(self.obj.btnDisconnect.isEnabled())
        self.assertTrue(self.obj.btnJogNeg.isEnabled())
        self.assertTrue(self.obj.btnJogPos.isEnabled())
        self.assertTrue(self.obj.btnJogStop.isEnabled())
        self.assertTrue(self.obj.btnHome.isEnabled())
        self.assertTrue(self.obj.lneSend.isEnabled())
        self.assertTrue(self.obj.btnSend.isEnabled())
        self.assertTrue(self.obj.lneJogTo.isEnabled())
        self.assertTrue(self.obj.lneJogDist.isEnabled())
        self.assertTrue(self.obj.btnJogTo.isEnabled())
        self.assertFalse(self.obj.btnEnergise.isEnabled())
        self.assertTrue(self.obj.btnKillAll.isEnabled())
        self.assertTrue(self.obj.btnStatus.isEnabled())
        self.assertTrue(self.obj.btnCSStatus.isEnabled())
        self.assertTrue(self.obj.btnGlobalStatus.isEnabled())
        self.assertTrue(self.obj.btnLoadFile.isEnabled())
        self.assertTrue(self.obj.btnSettings.isEnabled())
        self.assertTrue(self.obj.btnKillMotor.isEnabled())
        self.assertTrue(self.obj.chkJogInc.isEnabled())
        self.assertTrue(self.obj.btnPollingStatus.isEnabled())
        self.assertTrue(self.obj.btnGather.isEnabled())
        self.assertTrue(self.obj.btnWatches.isEnabled())
        self.assertTrue(self.obj.table.isEnabled())
        self.assertFalse(self.obj.lnePollRate.isEnabled())
        self.assertFalse(self.obj.lblPollRate.isEnabled())
        mock_pixmap.assert_called_with(self.obj.greenLedOn)

    @unittest.skip("not working")
    @patch("queue.Queue")
    def test_update_motors(self, mock_queue):
        attrs = {"qsize.return_value" : 5,
                 "get.return_value" : 0}
        mock_queue.configure_mock(**attrs)
        ret = self.obj.updateMotors()
        assert ret == None
        assert self.obj.lblPosition.text() == "0"
        assert self.obj.lblVelo.text() == "0"
        assert self.obj.lblFolErr.text() == "0"

    @unittest.skip("not working")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.getShortModelName")
    @patch("dls_pmaclib.dls_pmacremote.PmacSshInterface.isModelGeobrick")
    @patch("dls_pmaclib.dls_pmacremote.PmacSshInterface.getNumberOfAxes")
    @patch("dls_pmaclib.dls_pmacremote.PmacSshInterface.getPmacModel")
    @patch("dls_pmaclib.dls_pmacremote.PmacSshInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PmacSshInterface.setConnectionParams")
    def test_update_identity(self, mock_params, mock_connect, mock_model, 
                              mock_axes, mock_geo, mock_short):
        mock_short.return_value = "name"
        # create connection
        mock_model.return_value = "test"
        mock_axes.return_value = 8
        mock_geo.return_value = True
        mock_connect.return_value = None
        self.obj.remoteConnect()
        self.obj.updateIdentity(1)

    def tearDown(self):
        self.obj.close()
