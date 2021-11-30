import unittest

from mock import Mock, patch
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QMainWindow

from dls_pmaccontrol.axissettings import Axissettingsform, PpmacAxissettingsform


class DummyTestWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.pmac = Mock()
        attrs = {
            "sendCommand.return_value": ("return", True),
            "getAxisSetupIVars.return_value": ["value", "value", "value"],
            "isMacroStationAxis.return_value": False,
            "getOnboardAxisI7000PlusVars.return_value": [
                "loopSelect",
                "captureOn",
                "captureFlag",
                "outputMode",
            ],
            "getAxisMsIVars.return_value": [
                "loopSelect",
                "captureOn",
                "captureFlag",
                "outputMode",
            ],
            "setAxisMsIVar.return_value": None,
            "setOnboardAxisI7000PlusIVar.return_value": None,
            "setAxisSetupIVar.return_value": None,
        }
        self.pmac.configure_mock(**attrs)


class AxissettingsTest(unittest.TestCase):
    def setUp(self):
        self.test_widget = DummyTestWidget()
        self.obj = Axissettingsform(self.test_widget)

    def test_change_axis_not_visible(self):
        self.obj.changeAxis(2)
        assert self.obj.currentMotor == 2

    @patch(
        "dls_pmaccontrol.axissettings.Axissettingsform._updateAxisSignalControlsVars"
    )
    @patch("dls_pmaccontrol.axissettings.Axissettingsform._updateAxisSetupIVars")
    def test_change_axis_visible(self, mock_setup, mock_signal):
        self.obj.show()
        self.obj.changeAxis(2)
        assert self.obj.currentMotor == 2
        self.assertTrue(mock_setup.called)
        if self.obj.tabAxisSetup.currentIndex() != 0:
            self.assertTrue(mock_signal.called)

    @patch(
        "dls_pmaccontrol.axissettings.Axissettingsform._updateAxisSignalControlsVars"
    )
    @patch("dls_pmaccontrol.axissettings.Axissettingsform._updateAxisSetupIVars")
    def test_change_tab(self, mock_setup, mock_signal):
        QTest.mouseClick(self.obj.tabAxisSetup, Qt.LeftButton)
        assert self.obj.tabAxisSetup.currentIndex() == 1

    def test_updateAxisSetupIVars(self):
        self.obj._updateAxisSetupIVars([11, 16, 23])
        assert self.obj.lneIx11.text() == "value"
        assert self.obj.lneIx16.text() == "value"
        assert self.obj.lneIx23.text() == "value"

    def test_updateAxisSignalControlsVars(self):
        self.obj._updateAxisSignalControlsVars()
        assert self.obj.lneLoopSelect.text() == "loopSelect"
        assert self.obj.lneCaptureOn.text() == "captureOn"
        assert self.obj.lneCaptureFlag.text() == "captureFlag"
        assert self.obj.lneOutputMode.text() == "outputMode"

    def test_getAxisSignalControlsVars(self):
        (ret1, ret2, ret3, ret4) = self.obj._getAxisSignalControlsVars()
        assert ret1 == "loopSelect"
        assert ret2 == "captureOn"
        assert ret3 == "captureFlag"
        assert ret4 == "outputMode"

    def test_sendLoopSelect(self):
        self.obj.sendLoopSelect()
        self.assertTrue(self.test_widget.pmac.setOnboardAxisI7000PlusIVar.called)

    def test_sendCaptureOn(self):
        self.obj.sendLoopSelect()
        self.assertTrue(self.test_widget.pmac.setOnboardAxisI7000PlusIVar.called)

    def test_sendCaptureFlag(self):
        self.obj.sendLoopSelect()
        self.assertTrue(self.test_widget.pmac.setOnboardAxisI7000PlusIVar.called)

    def test_sendOutputMode(self):
        self.obj.sendLoopSelect()
        self.assertTrue(self.test_widget.pmac.setOnboardAxisI7000PlusIVar.called)

    @patch("dls_pmaccontrol.axissettings.Axissettingsform.axisUpdate")
    def test_sendIx(self, mock_update):
        ivars = [11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 25, 26]
        for i in range(len(ivars)):
            exec("self.obj.sendIx%d()" % ivars[i])
            self.assertTrue(self.test_widget.pmac.setAxisSetupIVar.called)
            self.assertTrue(mock_update.called)

    def tearDown(self):
        self.obj.close()


class PpmacAxissettingsTest(unittest.TestCase):
    def setUp(self):
        self.test_widget = DummyTestWidget()
        self.obj = PpmacAxissettingsform(self.test_widget)

    def test_change_axis_not_visible(self):
        self.obj.changeAxis(2)
        assert self.obj.currentMotor == 2

    @patch("dls_pmaccontrol.axissettings.PpmacAxissettingsform._updateAxisSetupIVars")
    def test_change_axis_visible(self, mock_setup):
        self.obj.show()
        self.obj.changeAxis(2)
        assert self.obj.currentMotor == 2
        self.assertTrue(mock_setup.called)

    @patch("dls_pmaccontrol.axissettings.PpmacAxissettingsform._updateAxisSetupIVars")
    def test_change_tab(self, mock_setup):
        QTest.mouseClick(self.obj.tabAxisSetup, Qt.LeftButton)
        assert self.obj.tabAxisSetup.currentIndex() == 0

    def test_updateAxisSetupIVars(self):
        self.obj._updateAxisSetupIVars([11, 16, 23])
        assert self.obj.lneIx11.text() == "return"
        assert self.obj.lneIx16.text() == "return"
        assert self.obj.lneIx23.text() == "return"

    @patch("dls_pmaccontrol.axissettings.PpmacAxissettingsform.axisUpdate")
    def test_setAxisSetupIVar(self, mock_update):
        self.obj.setAxisSetupIVar(12, 1234)
        self.assertTrue(mock_update.called)

    @patch("dls_pmaccontrol.axissettings.PpmacAxissettingsform.setAxisSetupIVar")
    @patch("dls_pmaccontrol.axissettings.PpmacAxissettingsform.axisUpdate")
    def test_sendIx(self, mock_update, mock_setup):
        ivars = [11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 25, 26]
        for i in range(len(ivars)):
            exec("self.obj.sendIx%d()" % ivars[i])
            self.assertTrue(mock_setup.called)
            self.assertTrue(mock_update.called)

    def tearDown(self):
        self.obj.close()
