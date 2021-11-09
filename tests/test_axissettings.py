import PyQt5
import unittest
from mock import patch, Mock, call
import time
import sys
sys.path.append('/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol')
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem
from axissettings import Axissettingsform, PpmacAxissettingsform

app = QApplication(sys.argv)

class TestWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.pmac = Mock()
        attrs = {
        "sendCommand.return_value" : ("return",True),
        "getAxisSetupIVars.return_value" : ["value","value","value"],
        "isMacroStationAxis.return_value" : False,
        "getOnboardAxisI7000PlusVars.return_value" : 
                     ["loopSelect","captureOn","captureFlag","outputMode"],
        "getAxisMsIVars.return_value" : 
                     ["loopSelect","captureOn","captureFlag","outputMode"],
        "setAxisMsIVar.return_value" : None,
        "setOnboardAxisI7000PlusIVar.return_value" : None,
        "setAxisSetupIVar.return_value" : None}
        self.pmac.configure_mock(**attrs)

class AxissettingsTest(unittest.TestCase):

    def test_change_axis_not_visible(self):
        test_widget = TestWidget()
        obj = Axissettingsform(test_widget)
        obj.changeAxis(2)
        assert obj.currentMotor == 2
        obj.close()

    @patch("axissettings.Axissettingsform._updateAxisSignalControlsVars")
    @patch("axissettings.Axissettingsform._updateAxisSetupIVars")
    def test_change_axis_visible(self, mock_setup, mock_signal):
        test_widget = TestWidget()
        obj = Axissettingsform(test_widget)
        obj.show()
        obj.changeAxis(2)
        assert obj.currentMotor == 2
        self.assertTrue(mock_setup.called)
        if obj.tabAxisSetup.currentIndex() !=0:
            self.assertTrue(mock_signal.called)
        obj.close()

    @patch("axissettings.Axissettingsform._updateAxisSignalControlsVars")
    @patch("axissettings.Axissettingsform._updateAxisSetupIVars")
    def test_change_tab(self, mock_setup, mock_signal):
        test_widget = TestWidget()
        obj = Axissettingsform(test_widget)
        QTest.mouseClick(obj.tabAxisSetup, Qt.LeftButton)
        assert obj.tabAxisSetup.currentIndex() == 1
        obj.close()

    def test_updateAxisSetupIVars(self):
        test_widget = TestWidget()
        obj = Axissettingsform(test_widget)
        obj._updateAxisSetupIVars([11,16,23])
        assert obj.lneIx11.text() == "value"
        assert obj.lneIx16.text() == "value"
        assert obj.lneIx23.text() == "value"

    def test_updateAxisSignalControlsVars(self):
        test_widget = TestWidget()
        obj = Axissettingsform(test_widget)
        obj._updateAxisSignalControlsVars()
        assert obj.lneLoopSelect.text() == "loopSelect"
        assert obj.lneCaptureOn.text() == "captureOn"
        assert obj.lneCaptureFlag.text() == "captureFlag"
        assert obj.lneOutputMode.text() == "outputMode"

    def test_getAxisSignalControlsVars(self):
        test_widget = TestWidget()
        obj = Axissettingsform(test_widget)
        (ret1,ret2,ret3,ret4) = obj._getAxisSignalControlsVars()
        assert ret1 == "loopSelect" 
        assert ret2 == "captureOn"
        assert ret3 == "captureFlag"
        assert ret4 == "outputMode"

    def test_sendLoopSelect(self):
        test_widget = TestWidget()
        obj = Axissettingsform(test_widget)
        obj.sendLoopSelect()
        self.assertTrue(test_widget.pmac.setOnboardAxisI7000PlusIVar.called)

    def test_sendCaptureOn(self):
        test_widget = TestWidget()
        obj = Axissettingsform(test_widget)
        obj.sendLoopSelect()
        self.assertTrue(test_widget.pmac.setOnboardAxisI7000PlusIVar.called)

    def test_sendCaptureFlag(self):
        test_widget = TestWidget()
        obj = Axissettingsform(test_widget)
        obj.sendLoopSelect()
        self.assertTrue(test_widget.pmac.setOnboardAxisI7000PlusIVar.called)

    def test_sendOutputMode(self):
        test_widget = TestWidget()
        obj = Axissettingsform(test_widget)
        obj.sendLoopSelect()
        self.assertTrue(test_widget.pmac.setOnboardAxisI7000PlusIVar.called)

    @patch("axissettings.Axissettingsform.axisUpdate")
    def test_sendIx(self, mock_update):
        test_widget = TestWidget()
        obj = Axissettingsform(test_widget)
        ivars = [11,12,13,14,15,16,17,19,20,21,22,23,25,26]
        for i in range(len(ivars)):
            exec("obj.sendIx%d()" % ivars[i])
            self.assertTrue(test_widget.pmac.setAxisSetupIVar.called)
            self.assertTrue(mock_update.called)

class PpmacAxissettingsTest(unittest.TestCase):

    def test_change_axis_not_visible(self):
        test_widget = TestWidget()
        obj = PpmacAxissettingsform(test_widget)
        obj.changeAxis(2)
        assert obj.currentMotor == 2
        obj.close()

    @patch("axissettings.PpmacAxissettingsform._updateAxisSetupIVars")
    def test_change_axis_visible(self, mock_setup):
        test_widget = TestWidget()
        obj = PpmacAxissettingsform(test_widget)
        obj.show()
        obj.changeAxis(2)
        assert obj.currentMotor == 2
        self.assertTrue(mock_setup.called)
        obj.close()

    @patch("axissettings.PpmacAxissettingsform._updateAxisSetupIVars")
    def test_change_tab(self, mock_setup):
        test_widget = TestWidget()
        obj = PpmacAxissettingsform(test_widget)
        QTest.mouseClick(obj.tabAxisSetup, Qt.LeftButton)
        assert obj.tabAxisSetup.currentIndex() == 0
        obj.close()

    def test_updateAxisSetupIVars(self):
        test_widget = TestWidget()
        obj = PpmacAxissettingsform(test_widget)
        obj._updateAxisSetupIVars([11,16,23])
        assert obj.lneIx11.text() == "return"
        assert obj.lneIx16.text() == "return"
        assert obj.lneIx23.text() == "return"

    @patch("axissettings.PpmacAxissettingsform.axisUpdate")
    def test_setAxisSetupIVar(self, mock_update):
        test_widget = TestWidget()
        obj = PpmacAxissettingsform(test_widget)
        obj.setAxisSetupIVar(12, 1234)
        self.assertTrue(mock_update.called)

    @patch("axissettings.PpmacAxissettingsform.setAxisSetupIVar")
    @patch("axissettings.PpmacAxissettingsform.axisUpdate")
    def test_sendIx(self, mock_update, mock_setup):
        test_widget = TestWidget()
        obj = PpmacAxissettingsform(test_widget)
        ivars = [11,12,13,14,15,16,17,19,20,21,22,23,25,26]
        for i in range(len(ivars)):
            exec("obj.sendIx%d()" % ivars[i])
            self.assertTrue(mock_setup.called)
            self.assertTrue(mock_update.called)

