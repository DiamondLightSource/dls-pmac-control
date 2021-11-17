import PyQt5
import unittest
from mock import patch
import time
import sys

sys.path.append("/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol")
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow
from ui_formControl import Ui_ControlForm
from motor import Controlform

# need to get slots from motor

app = QApplication(sys.argv)


class GuiWidgetTest(unittest.TestCase):

    testWidget = None
    ui = None

    def setUp(self):
        self.testWidget = QMainWindow()
        self.ui = Ui_ControlForm()
        self.ui.setupUi(self.testWidget)

    def test_initialWidgetsEnabledDisabled(self):

        self.assertTrue(self.ui.btnGroupProtocol.isEnabled())
        self.assertTrue(self.ui.lneServer.isEnabled())
        self.assertTrue(self.ui.lnePort.isEnabled())
        self.assertTrue(self.ui.btnConnect.isEnabled())
        self.assertTrue(self.ui.spnJogMotor.isEnabled())
        self.assertTrue(self.ui.chkShowAll.isEnabled())

        self.assertFalse(self.ui.btnJogNeg.isEnabled())
        self.assertFalse(self.ui.btnHome.isEnabled())
        self.assertFalse(self.ui.btnJogPos.isEnabled())
        self.assertFalse(self.ui.btnJogTo.isEnabled())
        self.assertFalse(self.ui.btnStatus.isEnabled())
        self.assertFalse(self.ui.btnSettings.isEnabled())
        self.assertFalse(self.ui.btnJogStop.isEnabled())
        self.assertFalse(self.ui.lneJogDist.isEnabled())
        self.assertFalse(self.ui.lneJogTo.isEnabled())
        self.assertFalse(self.ui.chkJogInc.isEnabled())
        self.assertFalse(self.ui.btnKillMotor.isEnabled())
        self.assertFalse(self.ui.btnDisconnect.isEnabled())
        self.assertFalse(self.ui.lneSend.isEnabled())
        self.assertFalse(self.ui.btnSend.isEnabled())
        self.assertFalse(self.ui.btnEnergise.isEnabled())
        self.assertFalse(self.ui.btnCSStatus.isEnabled())
        self.assertFalse(self.ui.lnePollRate.isEnabled())
        self.assertFalse(self.ui.btnGlobalStatus.isEnabled())
        self.assertFalse(self.ui.btnKillAll.isEnabled())
        self.assertFalse(self.ui.btnPollingStatus.isEnabled())
        self.assertFalse(self.ui.btnGather.isEnabled())
        self.assertFalse(self.ui.btnWatches.isEnabled())
        self.assertFalse(self.ui.btnLoadFile.isEnabled())

    def test_terminalClicked(self):
        QTest.mouseClick(self.ui.rbUseTerminalServer, Qt.LeftButton)
        self.assertEqual(self.ui.lneServer.text(), "blxxi-nt-tserv-01")
        self.assertEqual(self.ui.lnePort.text(), "7017")

    def test_socketClicked(self):
        QTest.mouseClick(self.ui.rbUseSocket, Qt.LeftButton)
        self.assertEqual(self.ui.lneServer.text(), "10.2.2.28")
        self.assertEqual(self.ui.lnePort.text(), "1025")

    def test_serialClicked(self):
        QTest.mouseClick(self.ui.rbUseSerial, Qt.LeftButton)
        self.assertEqual(self.ui.lneServer.text(), "/dev/ttyUSB0")
        self.assertEqual(self.ui.lnePort.text(), "38400")
        # check that polling frequency box is enabled and is set to 0
        self.assertTrue(self.ui.lnePollRate.isEnabled())
        self.assertEqual(self.ui.lnePollRate.text(), "0")

    def test_sshClicked(self):
        QTest.mouseClick(self.ui.rbUseSsh, Qt.LeftButton)
        self.assertEqual(self.ui.lneServer.text(), "192.168.56.10")
        self.assertEqual(self.ui.lnePort.text(), "22")

    def test_connect_clicked(self):
        QTest.mouseClick(self.ui.btnConnect, Qt.LeftButton)
        # assert remoteConnect called
