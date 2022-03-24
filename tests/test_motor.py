import os
import unittest

from mock import Mock, patch
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from dls_pmaccontrol.motor import Controlform


class DummyTestOptionsTelnet:
    def __init__(self):
        self.verbose = False
        self.protocol = "ts"
        self.server = "test"
        self.port = "123"
        self.defaultAxis = 1
        self.nAxes = 8
        self.timeout = 3.0
        self.macroAxisStartIndex = 0
        self.username = "username"
        self.password = "password"


class DummyTestOptionsEthernet:
    def __init__(self):
        self.verbose = False
        self.protocol = "tcpip"
        self.server = "test"
        self.port = "123"
        self.defaultAxis = 1
        self.nAxes = 8
        self.timeout = 3.0
        self.macroAxisStartIndex = 0
        self.username = "username"
        self.password = "password"


class DummyTestOptionsSerial:
    def __init__(self):
        self.verbose = False
        self.protocol = "rs232"
        self.server = "test"
        self.port = "123"
        self.defaultAxis = 1
        self.nAxes = 8
        self.timeout = 3.0
        self.macroAxisStartIndex = 0
        self.username = "username"
        self.password = "password"


class DummyTestOptionsSsh:
    def __init__(self):
        self.verbose = False
        self.protocol = "ssh"
        self.server = "test"
        self.port = "123"
        self.defaultAxis = 1
        self.nAxes = 8
        self.timeout = 3.0
        self.macroAxisStartIndex = 0
        self.username = "username"
        self.password = "password"


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
    def setUp(
        self,
        mock_signal,
        mock_thread,
        mock_event,
        mock_comms,
        mock_login,
        mock_watches,
        mock_ppmacgather,
        mock_gather,
        mock_ppmacaxis,
        mock_axis,
        mock_ppmacglobal,
        mock_global,
        mock_ppmaccs,
        mock_cs,
        mock_ppmacstatus,
        mock_status,
    ):
        self.options = DummyTestOptionsTelnet()
        self.obj = Controlform(self.options)

    def test_initial_state(self):
        assert self.obj.ConnectionType == 0
        assert self.obj.pmac is None
        assert self.obj.powerpmac is None
        assert self.obj.pollingStatus is True
        assert self.obj.isUsingSerial is False
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

    @patch("PyQt5.QtWidgets.QLineEdit.keyPressEvent")
    def test_checkHistory_empty(self, mock_event):
        self.obj.commands = []
        self.obj.commands_i = 0
        self.obj.lneSend.setEnabled(True)
        QTest.keyClick(self.obj.lneSend, Qt.Key_Up)
        assert self.obj.commands_i == 0
        assert self.obj.lneSend.text() == ""
        assert mock_event.called

    @patch("PyQt5.QtWidgets.QLineEdit.keyPressEvent")
    def test_checkHistory_keyup(self, mock_event):
        self.obj.commands = ["cmd1", "cmd2", "cmd3"]
        self.obj.commands_i = 0
        self.obj.lneSend.setEnabled(True)
        QTest.keyClick(self.obj.lneSend, Qt.Key_Up)
        assert self.obj.commands_i == -1
        assert self.obj.lneSend.text() == "cmd3"
        assert mock_event.called

    @patch("PyQt5.QtWidgets.QLineEdit.keyPressEvent")
    def test_checkHistory_keydown(self, mock_event):
        self.obj.commands = ["cmd1", "cmd2", "cmd3"]
        self.obj.commands_i = -1
        self.obj.lneSend.setEnabled(True)
        QTest.keyClick(self.obj.lneSend, Qt.Key_Down)
        assert self.obj.commands_i == 0
        assert self.obj.lneSend.text() == ""
        assert mock_event.called

    @patch("PyQt5.QtWidgets.QMessageBox.information")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.setConnectionParams")
    def test_remote_connect_auth_error(self, mock_params, mock_connect, mock_box):
        mock_connect.return_value = "Invalid username or password"
        ret = self.obj.remoteConnect()
        mock_params.assert_called_with("test", "123")
        assert mock_connect.called
        mock_box.assert_called_with(self.obj, "Error", "Invalid username or password")
        assert ret is None

    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.isModelGeobrick")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.getNumberOfAxes")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.getPmacModel")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.setConnectionParams")
    def test_remote_connect(
        self, mock_params, mock_connect, mock_model, mock_axes, mock_geo, mock_pixmap
    ):
        mock_model.return_value = "test"
        mock_axes.return_value = 8
        mock_geo.return_value = True
        mock_connect.return_value = None
        ret = self.obj.remoteConnect()
        mock_params.assert_called_with("test", "123")
        assert mock_connect.called
        assert mock_model.called
        assert self.obj.windowTitle() == "Delta Tau motor controller - test"
        assert ret is None
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
        self.assertEqual(self.obj.lblIdentity.text(), "")

    def tearDown(self):
        self.obj.close()


class MotorTestTelnetConnectionRequired(unittest.TestCase):
    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.isModelGeobrick")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.getNumberOfAxes")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.getPmacModel")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.setConnectionParams")
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
    def setUp(
        self,
        mock_signal,
        mock_thread,
        mock_event,
        mock_comms,
        mock_login,
        mock_watches,
        mock_ppmacgather,
        mock_gather,
        mock_ppmacaxis,
        mock_axis,
        mock_ppmacglobal,
        mock_global,
        mock_ppmaccs,
        mock_cs,
        mock_ppmacstatus,
        mock_status,
        mock_params,
        mock_connect,
        mock_model,
        mock_axes,
        mock_geo,
        mock_pixmap,
    ):
        self.options = DummyTestOptionsTelnet()
        self.obj = Controlform(self.options)
        mock_model.return_value = "test"
        mock_axes.return_value = 8
        mock_geo.return_value = True
        mock_connect.return_value = None
        self.obj.remoteConnect()

    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.disconnect")
    def test_remote_disconnect(self, mock_disconnect, mock_pixmap):
        self.obj.remoteDisconnect()
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

    @patch("dls_pmaccontrol.motor.Controlform.addToTxtShell")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.jogInc")
    def test_jog_neg(self, mock_joginc, mock_addtxt):
        mock_joginc.return_value = ("cmd", "response", True)
        assert self.obj.jogNeg() is None
        mock_joginc.assert_called_with(
            self.obj.currentMotor, "neg", str(self.obj.lneJogDist.text())
        )

    @patch("dls_pmaccontrol.motor.Controlform.addToTxtShell")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.jogInc")
    def test_jog_pos(self, mock_joginc, mock_addtxt):
        mock_joginc.return_value = ("cmd", "response", True)
        assert self.obj.jogPos() is None
        mock_joginc.assert_called_with(
            self.obj.currentMotor, "pos", str(self.obj.lneJogDist.text())
        )

    @patch("dls_pmaccontrol.motor.Controlform.addToTxtShell")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.jogStop")
    def test_jog_stop(self, mock_jogstop, mock_addtxt):
        mock_jogstop.return_value = ("cmd", "response", True)
        assert self.obj.jogStop() is None
        mock_jogstop.assert_called_with(self.obj.currentMotor)

    @patch("dls_pmaccontrol.motor.Controlform.addToTxtShell")
    @patch("dls_pmaclib.dls_pmacremote.PmacTelnetInterface.homeCommand")
    def test_jog_home(self, mock_home, mock_addtxt):
        mock_home.return_value = ("cmd", "response", True)
        assert self.obj.jogHome() is None
        mock_home.assert_called_with(self.obj.currentMotor)
        mock_addtxt.assert_called_with("cmd", "response")

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
    def setUp(
        self,
        mock_signal,
        mock_thread,
        mock_event,
        mock_comms,
        mock_login,
        mock_watches,
        mock_ppmacgather,
        mock_gather,
        mock_ppmacaxis,
        mock_axis,
        mock_ppmacglobal,
        mock_global,
        mock_ppmaccs,
        mock_cs,
        mock_ppmacstatus,
        mock_status,
    ):
        self.options = DummyTestOptionsEthernet()
        self.obj = Controlform(self.options)

    def test_initial_state(self):
        assert self.obj.ConnectionType == 1
        assert self.obj.pmac is None
        assert self.obj.powerpmac is None
        assert self.obj.pollingStatus is True
        assert self.obj.isUsingSerial is False
        assert self.obj.lneServer.text() == "test"
        assert self.obj.lnePort.text() == "123"
        assert self.obj.currentMotor == 1
        assert self.obj.nAxes == 8

    def test_useSocketConnection(self):
        self.obj.ConnectionType = None
        self.obj.useSocketConnection()
        assert self.obj.ConnectionType == 1
        assert self.obj.lneServer.text() == "172.23.240.97"
        assert self.obj.lnePort.text() == "1025"
        assert self.obj.textLabel1.text() == "IP address:"
        assert self.obj.textLabel2.text() == "Port:"
        assert self.obj.lblPolling.text() == "Polling"
        self.assertFalse(self.obj.lnePollRate.isEnabled())
        self.assertFalse(self.obj.lblPollRate.isEnabled())

    @patch("PyQt5.QtWidgets.QMessageBox.information")
    @patch("dls_pmaclib.dls_pmacremote.PmacEthernetInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PmacEthernetInterface.setConnectionParams")
    def test_remote_connect_auth_error(self, mock_params, mock_connect, mock_box):
        mock_connect.return_value = "Invalid username or password"
        ret = self.obj.remoteConnect()
        mock_params.assert_called_with("test", "123")
        assert mock_connect.called
        mock_box.assert_called_with(self.obj, "Error", "Invalid username or password")
        assert ret is None

    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    @patch("dls_pmaclib.dls_pmacremote.PmacEthernetInterface.isModelGeobrick")
    @patch("dls_pmaclib.dls_pmacremote.PmacEthernetInterface.getNumberOfAxes")
    @patch("dls_pmaclib.dls_pmacremote.PmacEthernetInterface.getPmacModel")
    @patch("dls_pmaclib.dls_pmacremote.PmacEthernetInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PmacEthernetInterface.setConnectionParams")
    def test_remote_connect(
        self, mock_params, mock_connect, mock_model, mock_axes, mock_geo, mock_pixmap
    ):
        mock_model.return_value = "test"
        mock_axes.return_value = 8
        mock_geo.return_value = True
        mock_connect.return_value = None
        ret = self.obj.remoteConnect()
        mock_params.assert_called_with("test", "123")
        assert mock_connect.called
        assert mock_model.called
        assert self.obj.windowTitle() == "Delta Tau motor controller - test"
        assert ret is None
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

    @patch("PyQt5.QtWidgets.QPushButton.released")
    @patch("PyQt5.QtWidgets.QPushButton.pressed")
    @patch("PyQt5.QtWidgets.QPushButton.clicked")
    def test_jog_incrementally_true(self, mock_clicked, mock_pressed, mock_released):
        self.obj.btnJogPos.pressed.connect(self.obj.jogPosContinousStart)
        self.obj.btnJogPos.released.connect(self.obj.jogStop)
        self.obj.btnJogNeg.pressed.connect(self.obj.jogNegContinousStart)
        self.obj.btnJogNeg.released.connect(self.obj.jogStop)
        self.obj.jogIncrementally(True)
        self.assertTrue(self.obj.lneJogDist.isEnabled())
        mock_pressed.disconnect.assert_called_with(self.obj.jogNegContinousStart)
        mock_released.disconnect.assert_called_with(self.obj.jogStop)
        mock_clicked.connect.assert_called_with(self.obj.jogPos)

    @patch("PyQt5.QtWidgets.QPushButton.released")
    @patch("PyQt5.QtWidgets.QPushButton.pressed")
    @patch("PyQt5.QtWidgets.QPushButton.clicked")
    def test_jog_incrementally_false(self, mock_clicked, mock_pressed, mock_released):
        self.obj.btnJogNeg.clicked.connect(self.obj.jogNeg)
        self.obj.btnJogPos.clicked.connect(self.obj.jogPos)
        self.obj.jogIncrementally(False)
        self.assertFalse(self.obj.lneJogDist.isEnabled())
        mock_pressed.connect.assert_called_with(self.obj.jogNegContinousStart)
        mock_released.connect.assert_called_with(self.obj.jogStop)
        mock_clicked.connect.assert_called_with(self.obj.jogPos)

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
    def setUp(
        self,
        mock_signal,
        mock_thread,
        mock_event,
        mock_comms,
        mock_login,
        mock_watches,
        mock_ppmacgather,
        mock_gather,
        mock_ppmacaxis,
        mock_axis,
        mock_ppmacglobal,
        mock_global,
        mock_ppmaccs,
        mock_cs,
        mock_ppmacstatus,
        mock_status,
    ):
        self.options = DummyTestOptionsSerial()
        self.obj = Controlform(self.options)

    def test_initial_state(self):
        assert self.obj.ConnectionType == 2
        assert self.obj.pmac is None
        assert self.obj.powerpmac is None
        assert self.obj.pollingStatus is True
        assert self.obj.isUsingSerial is False
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
    def test_remote_connect_auth_error(self, mock_params, mock_connect, mock_box):
        mock_connect.return_value = "Invalid username or password"
        ret = self.obj.remoteConnect()
        mock_params.assert_called_with("test", "123")
        assert mock_connect.called
        mock_box.assert_called_with(self.obj, "Error", "Invalid username or password")
        assert ret is None

    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    @patch("dls_pmaclib.dls_pmacremote.PmacSerialInterface.isModelGeobrick")
    @patch("dls_pmaclib.dls_pmacremote.PmacSerialInterface.getNumberOfAxes")
    @patch("dls_pmaclib.dls_pmacremote.PmacSerialInterface.getPmacModel")
    @patch("dls_pmaclib.dls_pmacremote.PmacSerialInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PmacSerialInterface.setConnectionParams")
    def test_remote_connect(
        self, mock_params, mock_connect, mock_model, mock_axes, mock_geo, mock_pixmap
    ):
        mock_model.return_value = "test"
        mock_axes.return_value = 8
        mock_geo.return_value = True
        mock_connect.return_value = None
        ret = self.obj.remoteConnect()
        mock_params.assert_called_with("test", "123")
        assert mock_connect.called
        assert mock_model.called
        assert self.obj.windowTitle() == "Delta Tau motor controller - test"
        assert ret is None
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

    @patch("PyQt5.QtWidgets.QFileDialog.getOpenFileName")
    def test_load_config_no_filename(self, mock_dialog):
        test_filename = False, None
        mock_dialog.return_value = test_filename
        assert self.obj.pmacLoadConfig() is None
        assert mock_dialog.called

    @patch("dls_pmaclib.dls_pmcpreprocessor.ClsPmacParser.parse")
    @patch("PyQt5.QtWidgets.QFileDialog.getOpenFileName")
    def test_load_config_no_pmc_lines(self, mock_dialog, mock_parse):
        # create temp file
        test_file = "/tmp/test.txt"
        fh = open(test_file, "w")
        fh.write("#define test P10\ntest = 1")
        fh.close()
        # mock returns filename of temp file
        test_filename = "/tmp/test.txt", None
        mock_dialog.return_value = test_filename
        mock_parse.return_value = False
        assert self.obj.pmacLoadConfig() is None
        assert mock_dialog.called
        assert mock_parse.called
        os.remove(test_file)

    @patch("queue.Queue.put")
    @patch("PyQt5.QtWidgets.QProgressDialog")
    @patch("dls_pmaclib.dls_pmcpreprocessor.ClsPmacParser.parse")
    @patch("PyQt5.QtWidgets.QFileDialog.getOpenFileName")
    def test_load_config(self, mock_dialog, mock_parse, mock_progress, mock_queue):
        # create temp file
        test_file = "/tmp/test.txt"
        fh = open(test_file, "w")
        fh.write("#define test P10\ntest = 1")
        fh.close()
        # mock returns filename of temp file
        test_filename = "/tmp/test.txt", None
        mock_dialog.return_value = test_filename
        mock_parse.return_value = ["#define test P10", "test = 1"]
        assert self.obj.pmacLoadConfig() is None
        assert mock_dialog.called
        assert mock_parse.called
        assert mock_queue.called
        os.remove(test_file)

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
    def setUp(
        self,
        mock_signal,
        mock_thread,
        mock_event,
        mock_comms,
        mock_login,
        mock_watches,
        mock_ppmacgather,
        mock_gather,
        mock_ppmacaxis,
        mock_axis,
        mock_ppmacglobal,
        mock_global,
        mock_ppmaccs,
        mock_cs,
        mock_ppmacstatus,
        mock_status,
    ):
        self.options = DummyTestOptionsSsh()
        self.obj = Controlform(self.options)
        self.obj.commsThread = mock_comms.return_value

    def test_initial_state(self):
        assert self.obj.ConnectionType == 3
        assert self.obj.pmac is None
        assert self.obj.powerpmac is None
        assert self.obj.pollingStatus is True
        assert self.obj.isUsingSerial is False
        assert self.obj.lneServer.text() == "test"
        assert self.obj.lnePort.text() == "123"
        assert self.obj.currentMotor == 1
        assert self.obj.nAxes == 8

    def test_useSshConnection(self):
        self.obj.ConnectionType = None
        self.obj.useSshConnection()
        assert self.obj.ConnectionType == 3
        assert self.obj.lneServer.text() == "172.23.240.97"
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
    def test_remote_connect_auth_error(
        self, mock_params, mock_connect, mock_box, mock_exec
    ):
        mock_connect.return_value = "Invalid username or password"
        mock_exec.return_value = True
        ret = self.obj.remoteConnect()
        mock_params.assert_called_with("test", "123")
        assert mock_connect.called
        mock_box.assert_called_with(self.obj, "Error", "Invalid username or password")
        assert ret is None

    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    @patch("dls_pmaccontrol.login.Loginform.exec")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.isModelGeobrick")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.getNumberOfAxes")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.getPmacModel")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.setConnectionParams")
    def test_remote_connect(
        self,
        mock_params,
        mock_connect,
        mock_model,
        mock_axes,
        mock_geo,
        mock_login,
        mock_pixmap,
    ):
        mock_model.return_value = "test"
        mock_axes.return_value = 8
        mock_geo.return_value = True
        mock_connect.return_value = None
        ret = self.obj.remoteConnect()
        mock_params.assert_called_with("test", "123")
        assert mock_connect.called
        assert mock_model.called
        assert self.obj.windowTitle() == "Delta Tau motor controller - test"
        assert ret is None
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

    def test_update_motors(self):
        attrs = {"resultQueue.return_value": Mock()}
        self.obj.commsThread.configure_mock(**attrs)
        attrs = {"qsize.return_value": 5, "get.return_value": ["0", "0", "0", "0", 0]}
        self.obj.commsThread.resultQueue.configure_mock(**attrs)
        ret = self.obj.updateMotors()
        assert ret is None
        assert self.obj.lblPosition.text() == "0.0"
        assert self.obj.lblVelo.text() == "0.0"
        assert self.obj.lblFolErr.text() == "0.0"

    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.getShortModelName")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.isModelGeobrick")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.getNumberOfAxes")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.getPmacModel")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.connect")
    @patch("dls_pmaclib.dls_pmacremote.PPmacSshInterface.setConnectionParams")
    @patch("dls_pmaccontrol.login.Loginform.exec")
    def test_update_identity(
        self,
        mock_login,
        mock_params,
        mock_connect,
        mock_model,
        mock_axes,
        mock_geo,
        mock_short,
    ):
        mock_short.return_value = "name"
        # create connection
        mock_model.return_value = "test"
        mock_axes.return_value = 8
        mock_geo.return_value = True
        mock_connect.return_value = None
        self.obj.remoteConnect()
        self.obj.updateIdentity(1)
        assert self.obj.lblIdentity.text() == "BL name 1"

    def tearDown(self):
        self.obj.close()
