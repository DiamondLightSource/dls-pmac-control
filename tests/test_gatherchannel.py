import PyQt5
import unittest
from mock import patch, Mock
import time
import sys

sys.path.append("/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol")
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem
from qwt import QwtPlotCurve
from gatherchannel import PpmacGatherChannel, PmacGatherChannel

app = QApplication(sys.argv)


class TestWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.pmac = Mock()
        attrs = {"sendCommand.return_value": ("100\r", True)}
        self.pmac.configure_mock(**attrs)


class TestWidget2(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.pmac = Mock()
        attrs = {"sendCommand.return_value": ("$088\r", True)}
        self.pmac.configure_mock(**attrs)


class PpmacGatherChannel:
    def __init__(self, pmac, qwtCurve):
        self.pmac = pmac
        self.qwtCurve = qwtCurve
        self.axisNo = None
        self.descNo = None


class PpmacGatherChannelTest(unittest.TestCase):
    def test_init(self):
        curve = QwtPlotCurve("test")
        test_widget = TestWidget()
        obj = PpmacGatherChannel(test_widget.pmac, curve)
        assert obj.pmac == test_widget.pmac
        assert obj.qwtCurve == curve
        assert obj.axisNo == None
        assert obj.descNo == None


class GatherChannelTest(unittest.TestCase):
    def setUp(self):
        self.curve = QwtPlotCurve("test")
        self.test_widget = TestWidget()
        self.obj = PmacGatherChannel(self.test_widget.pmac, self.curve)

    def test_init(self):
        assert self.obj.pmac == self.test_widget.pmac
        assert self.obj.qwtCurve == self.curve
        assert self.obj.axisNo == None
        assert self.obj.strData == []
        assert self.obj.rawData == []
        assert self.obj.scaledData == []
        assert self.obj.pSrcIvar == None
        assert self.obj.srcDataAddr == ""
        assert self.obj.dataWidth == None
        assert self.obj.dataType == None
        assert self.obj.regOffset == None
        assert self.obj.dataSourceInfo == None
        assert self.obj.scalingFactor == None

    def test_setDataGatherPointer(self):
        self.obj.setDataGatherPointer("test_ivar")
        assert self.obj.pSrcIvar == "test_ivar"

    def test_setStrData(self):
        self.obj.setStrData("test_strData")
        assert self.obj.strData == "test_strData"

    def test_strToRaw_no_data(self):
        self.obj.strData = []
        assert self.obj.strToRaw() == False

    def test_strToRaw_longword(self):
        self.obj.strData = ["0x000000000000"]
        self.obj.dataWidth = 48
        assert self.obj.strToRaw() == None
        assert self.obj.rawData == [0]

    def test_strToRaw_word(self):
        self.obj.strData = ["0x000000"]
        self.obj.dataWidth = 24
        assert self.obj.strToRaw() == None
        assert self.obj.rawData == [0]

    def test_getScalingFactor_no_scalingCalc(self):
        self.obj.dataSourceInfo = {}
        assert self.obj.getScalingFactor() == None
        assert self.obj.scalingFactor == 1.0

    def test_getScalingFactor(self):
        self.obj.pmac.return_value = "100\r"
        self.obj.axisNo = 1
        self.obj.dataSourceInfo = {
            "scalingCalc": "1.0/(%d*32.0)",
            "scalingIvars": ("i%d08",),
        }
        assert self.obj.getScalingFactor() == None
        self.assertEqual(self.obj.scalingFactor, 1 / 3200)

    def test_rawToScaled(self):
        self.obj.scalingFactor = 5
        self.obj.rawData = [10]
        assert self.obj.rawToScaled() == None
        assert self.obj.scaledData == [50]


class GatherChannelTestDataInfo(unittest.TestCase):
    def setUp(self):
        self.curve = QwtPlotCurve("test")
        self.test_widget = TestWidget2()
        self.obj = PmacGatherChannel(self.test_widget.pmac, self.curve)

    def test_getDataInfo(self):
        ret = self.obj.getDataInfo()
        assert ret == None
        assert self.obj.dataWidth == 24
        assert self.obj.dataType == int
        assert self.obj.regOffset == 8
        assert self.obj.axisNo == 1
