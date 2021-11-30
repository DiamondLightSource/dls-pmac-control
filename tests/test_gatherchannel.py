import unittest

from mock import Mock
from PyQt5.QtWidgets import QMainWindow
from qwt import QwtPlotCurve

from dls_pmaccontrol.gatherchannel import PmacGatherChannel, PpmacGatherChannel


class DummyTestWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.pmac = Mock()
        attrs = {"sendCommand.return_value": ("100\r", True)}
        self.pmac.configure_mock(**attrs)


class DummyTestWidget2(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.pmac = Mock()
        attrs = {"sendCommand.return_value": ("$088\r", True)}
        self.pmac.configure_mock(**attrs)


class PpmacGatherChannelTest(unittest.TestCase):
    def test_init(self):
        curve = QwtPlotCurve("test")
        test_widget = DummyTestWidget()
        obj = PpmacGatherChannel(test_widget.pmac, curve)
        assert obj.pmac == test_widget.pmac
        assert obj.qwtCurve == curve
        assert obj.axisNo is None
        assert obj.descNo is None


class GatherChannelTest(unittest.TestCase):
    def setUp(self):
        self.curve = QwtPlotCurve("test")
        self.test_widget = DummyTestWidget()
        self.obj = PmacGatherChannel(self.test_widget.pmac, self.curve)

    def test_init(self):
        assert self.obj.pmac == self.test_widget.pmac
        assert self.obj.qwtCurve == self.curve
        assert self.obj.axisNo is None
        assert self.obj.strData == []
        assert self.obj.rawData == []
        assert self.obj.scaledData == []
        assert self.obj.pSrcIvar is None
        assert self.obj.srcDataAddr == ""
        assert self.obj.dataWidth is None
        assert self.obj.dataType is None
        assert self.obj.regOffset is None
        assert self.obj.dataSourceInfo is None
        assert self.obj.scalingFactor is None

    def test_setDataGatherPointer(self):
        self.obj.setDataGatherPointer("test_ivar")
        assert self.obj.pSrcIvar == "test_ivar"

    def test_setStrData(self):
        self.obj.setStrData("test_strData")
        assert self.obj.strData == "test_strData"

    def test_strToRaw_no_data(self):
        self.obj.strData = []
        assert self.obj.strToRaw() is False

    def test_strToRaw_longword(self):
        self.obj.strData = ["0x000000000000"]
        self.obj.dataWidth = 48
        assert self.obj.strToRaw() is None
        assert self.obj.rawData == [0]

    def test_strToRaw_word(self):
        self.obj.strData = ["0x000000"]
        self.obj.dataWidth = 24
        assert self.obj.strToRaw() is None
        assert self.obj.rawData == [0]

    def test_getScalingFactor_no_scalingCalc(self):
        self.obj.dataSourceInfo = {}
        assert self.obj.getScalingFactor() is None
        assert self.obj.scalingFactor == 1.0

    def test_getScalingFactor(self):
        self.obj.pmac.return_value = "100\r"
        self.obj.axisNo = 1
        self.obj.dataSourceInfo = {
            "scalingCalc": "1.0/(%d*32.0)",
            "scalingIvars": ("i%d08",),
        }
        assert self.obj.getScalingFactor() is None
        self.assertEqual(self.obj.scalingFactor, 1 / 3200)

    def test_rawToScaled(self):
        self.obj.scalingFactor = 5
        self.obj.rawData = [10]
        assert self.obj.rawToScaled() is None
        assert self.obj.scaledData == [50]


class GatherChannelTestDataInfo(unittest.TestCase):
    def setUp(self):
        self.curve = QwtPlotCurve("test")
        self.test_widget = DummyTestWidget2()
        self.obj = PmacGatherChannel(self.test_widget.pmac, self.curve)

    def test_getDataInfo(self):
        ret = self.obj.getDataInfo()
        assert ret is None
        assert self.obj.dataWidth == 24
        assert self.obj.dataType == int
        assert self.obj.regOffset == 8
        assert self.obj.axisNo == 1
