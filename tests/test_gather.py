import os
import unittest

from mock import Mock, patch
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QMainWindow
from qwt import QwtPlotCurve

from dls_pmaccontrol.gather import PmacGatherform
from dls_pmaccontrol.ppmacgather import PpmacGatherform


class DummyTestWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.pmac = Mock()
        # self.commsThread = Mock()


class DummyTestGatherChannel:
    def __init__(self, pmac, qwtCurve):
        self.axisNo = None
        self.pmac = pmac
        self.strData = []
        self.rawData = []
        self.scaledData = []
        self.pSrcIvar = None
        self.srcDataAddr = ""
        self.dataWidth = None
        self.dataType = None
        self.regOffset = None
        self.dataSourceInfo = None
        self.scalingFactor = None
        self.qwtCurve = qwtCurve

    def setDataGatherPointer(self, ivar):
        self.pSrcIvar = ivar
        return

    def getDataInfo(self):
        self.dataWidth = 24
        self.dataType = int
        return

    def setStrData(self, x):
        self.setStrData_called = True
        return

    def strToRaw(self):
        self.strToRaw_called = True
        return

    def rawToScaled(self):
        self.rawToScaled_called = True
        return


class PmacGatherTest(unittest.TestCase):
    def setUp(self):
        self.test_widget = DummyTestWidget()
        self.obj = PmacGatherform(self.test_widget)

    def test_initial_state(self):
        self.assertFalse(self.obj.btnSetup.isEnabled())
        self.assertFalse(self.obj.btnTrigger.isEnabled())
        self.assertFalse(self.obj.btnCollect.isEnabled())
        self.assertFalse(self.obj.btnSave.isEnabled())
        self.assertTrue(self.obj.btnApplyConf.isEnabled())

    def test_gather_config(self):
        mid = QPoint(2, int(self.obj.chkPlot1.height() / 2))
        QTest.mouseClick(self.obj.chkPlot1, Qt.LeftButton, pos=mid)
        assert self.obj.gatherConfig() is True

    def test_gather_setup(self):
        attrs = {"sendCommand.return_value": ("$010101", True)}
        self.obj.parent.pmac.configure_mock(**attrs)
        for i in range(3):
            curve = QwtPlotCurve("TestCh%d" % i)
            test_channel = DummyTestGatherChannel(self.obj.parent.pmac, curve)
            self.obj.lstChannels.append(test_channel)
        assert self.obj.gatherSetup() is None
        assert self.obj.numberOfChannels == 3
        assert self.obj.lstChannels[0].dataWidth == 24
        assert self.obj.lstChannels[1].dataWidth == 24
        assert self.obj.lstChannels[2].dataWidth == 24
        assert self.obj.lstChannels[0].dataType == int
        assert self.obj.lstChannels[1].dataType == int
        assert self.obj.lstChannels[2].dataType == int

    @patch("dls_pmaccontrol.gather.PmacGatherform.calcSampleTime")
    def test_change_no_samples(self, mock_calc):
        self.obj.lneNumberSamples.setText("1000")
        QTest.keyClick(self.obj.lneNumberSamples, Qt.Key_Enter)
        assert self.obj.nGatherPoints == 1000
        assert self.obj.nServoCyclesGather == 10

    @patch("dls_pmaccontrol.gather.PmacGatherform.calcSampleTime")
    def test_change_sample_time(self, mock_calc):
        self.obj.lneSampleTime.setText("5")
        QTest.keyClick(self.obj.lneSampleTime, Qt.Key_Enter)
        assert self.obj.nServoCyclesGather == 5
        assert self.obj.nGatherPoints == 10

    def test_click_apply(self):
        self.obj.nServoCyclesGather = 10
        self.obj.nGatherPoints = 100
        self.obj.gatherConfig = Mock()
        QTest.keyClick(self.obj.btnApplyConf, Qt.Key_Enter)
        self.assertTrue(self.obj.btnSetup.isEnabled())
        self.assertFalse(self.obj.btnTrigger.isEnabled())
        self.assertFalse(self.obj.btnCollect.isEnabled())
        self.assertFalse(self.obj.btnSave.isEnabled())

    @patch("dls_pmaccontrol.gather.PmacGatherform.gatherSetup")
    def test_setup_clicked(self, mock_setup):
        self.obj.btnSetup.setEnabled(True)
        QTest.mouseClick(self.obj.btnSetup, Qt.LeftButton)
        assert mock_setup.called
        self.assertTrue(self.obj.btnSetup.isEnabled())
        self.assertTrue(self.obj.btnTrigger.isEnabled())
        self.assertFalse(self.obj.btnCollect.isEnabled())
        self.assertFalse(self.obj.btnSave.isEnabled())

    def test_collect_data(self):
        response = "ret1\rret2\rret3\r"
        attrs = {"sendCommand.return_value": (response, True)}
        self.obj.parent.pmac.configure_mock(**attrs)
        ret = self.obj.collectData()
        assert ret == ["", "ret1", "", "ret2", "", "ret3"]

    def test_parse_data(self):
        # set up test channel
        curve = QwtPlotCurve("TestCh")
        test_channel = DummyTestGatherChannel(self.obj.parent.pmac, curve)
        self.obj.lstChannels.append(test_channel)
        datastrings = ["test"]
        self.obj.parseData(datastrings)
        assert self.obj.lstChannels[0].setStrData_called is True
        assert self.obj.lstChannels[0].strToRaw_called is True
        assert self.obj.lstChannels[0].rawToScaled_called is True

    def test_calc_sample_time(self):
        self.obj.nServoCyclesGather = 1
        self.obj.nGatherPoints = 1
        attrs = {"sendCommand.return_value": ("$8388608\x0D", True)}
        self.obj.parent.pmac.configure_mock(**attrs)
        self.obj.calcSampleTime()
        assert self.obj.servoCycleTime == 1.0
        assert self.obj.sampleTime == 1.0

    @patch("dls_pmaccontrol.gather.PmacGatherform.plotData")
    @patch("dls_pmaccontrol.gather.PmacGatherform.collectData")
    def test_collect_clicked(self, mock_collect, mock_plot):
        self.obj.btnCollect.setEnabled(True)
        QTest.mouseClick(self.obj.btnCollect, Qt.LeftButton)
        assert mock_collect.called
        assert mock_plot.called
        self.assertTrue(self.obj.btnSetup.isEnabled())
        self.assertFalse(self.obj.btnTrigger.isEnabled())
        self.assertFalse(self.obj.btnCollect.isEnabled())
        self.assertTrue(self.obj.btnSave.isEnabled())

    @patch("PyQt5.QtWidgets.QMessageBox.information")
    def test_save_clicked_no_data(self, mock_box):
        self.obj.lstChannels = []
        ret = self.obj.saveClicked()
        assert ret is None

    @patch("PyQt5.QtWidgets.QFileDialog.getSaveFileName")
    def test_save_clicked(self, mock_dialog):
        # create temp file
        test_file = "/tmp/test.txt"
        fh = open(test_file, "w")
        fh.write("")
        fh.close()
        # mock returns filename of temp file
        test_filename = "/tmp/test.txt", None
        mock_dialog.return_value = test_filename
        # set up test channel
        curve = QwtPlotCurve("TestCh")
        test_channel = DummyTestGatherChannel(self.obj.parent.pmac, curve)
        self.obj.lstChannels.append(test_channel)
        self.obj.lstChannels[0].axisNo = 1
        self.obj.lstChannels[0].dataSourceInfo = {"desc": "Test desc"}
        # click save
        self.obj.btnSave.setEnabled(True)
        QTest.mouseClick(self.obj.btnSave, Qt.LeftButton)
        assert mock_dialog.called
        # assert file contents are as expected
        with open(test_file) as f:
            lines = f.readlines()
        assert lines == ["point,CH0 Axis1 Test desc,\n"]
        os.remove(test_file)

    def tearDown(self):
        self.obj.close()


class PpmacGatherTest(unittest.TestCase):
    def setUp(self):
        self.test_widget = DummyTestWidget()
        self.obj = PpmacGatherform(self.test_widget)

    def test_initial_state(self):
        self.assertFalse(self.obj.btnSetup.isEnabled())
        self.assertFalse(self.obj.btnTrigger.isEnabled())
        self.assertFalse(self.obj.btnCollect.isEnabled())
        self.assertFalse(self.obj.btnSave.isEnabled())
        self.assertTrue(self.obj.btnApplyConf.isEnabled())

    @patch("PyQt5.QtWidgets.QMessageBox.information")
    def test_change_no_samples(self, mock_box):
        self.obj.lneNumberSamples.setText("1000")
        QTest.keyClick(self.obj.lneNumberSamples, Qt.Key_Enter)
        assert self.obj.nGatherPoints == 1000
        assert self.obj.nServoCyclesGather == 0

    @patch("PyQt5.QtWidgets.QMessageBox.information")
    def test_change_sample_time(self, mock_box):
        self.obj.lneSampleTime.setText("5")
        QTest.keyClick(self.obj.lneSampleTime, Qt.Key_Enter)
        assert self.obj.nGatherPoints == 0
        assert self.obj.nServoCyclesGather == 5

    def test_gather_config(self):
        assert self.obj.gatherConfig() is True
        self.test_widget.pmac.sendCommand.assert_called_with("Gather.items=0")

    def test_gather_config_chkbox_checked(self):
        self.obj.lstCheckboxes[0].setChecked(True)
        assert self.obj.gatherConfig() is True
        self.test_widget.pmac.sendCommand.assert_called_with("Gather.items=1")

    @patch("dls_pmaccontrol.ppmacgather.PpmacGatherform.gatherConfig")
    def test_click_apply(self, mock_config):
        mock_config.return_value = True
        self.obj.nServoCyclesGather = 10
        self.obj.nGatherPoints = 100
        QTest.keyClick(self.obj.btnApplyConf, Qt.Key_Enter)
        assert mock_config.called
        self.assertTrue(self.obj.btnSetup.isEnabled())
        self.assertFalse(self.obj.btnTrigger.isEnabled())
        self.assertFalse(self.obj.btnCollect.isEnabled())
        self.assertFalse(self.obj.btnSave.isEnabled())

    def test_collect_data(self):
        assert self.obj.collectData() is None
        tmp_file = "../../var/ftp/usrflash/Temp/gather.txt"
        gather_file = "./gather.txt"
        cmd = "gather -u " + tmp_file
        self.test_widget.pmac.sendSshCommand.assert_called_with(cmd)
        self.test_widget.pmac.getFile.assert_called_with(tmp_file, gather_file)

    @patch("qwt.QwtPlot.replot")
    def test_plot_data(self, mock_replot):
        # create temp file
        test_file = "./gather.txt"
        fh = open(test_file, "w")
        fh.write("test")
        fh.close()
        assert self.obj.plotData() is None
        assert mock_replot.called
        os.remove(test_file)

    def test_calc_sample_time(self):
        self.obj.nServoCyclesGather = 1
        self.obj.nGatherPoints = 1
        attrs = {"sendCommand.return_value": ("1", True)}
        self.obj.parent.pmac.configure_mock(**attrs)
        self.obj.calcSampleTime()
        assert self.obj.servoCycleTime == 1.0
        assert self.obj.sampleTime == 1.0

    @patch("dls_pmaccontrol.ppmacgather.PpmacGatherform.calcSampleTime")
    def test_changed_tab(self, mock_calc):
        attrs = {"sendCommand.return_value": ("10", True)}
        self.obj.parent.pmac.configure_mock(**attrs)
        self.obj.nServoCyclesGather = 1
        self.obj.nGatherPoints = 1
        self.obj.changedTab()
        assert mock_calc.call_count == 2
        assert self.obj.nServoCyclesGather == 10
        assert self.obj.lneSampleTime.text() == "10"
        assert self.obj.nGatherPoints == 10
        assert self.obj.lneNumberSamples.text() == "10"

    @patch("dls_pmaccontrol.ppmacgather.PpmacGatherform.plotData")
    @patch("dls_pmaccontrol.ppmacgather.PpmacGatherform.collectData")
    def test_collect_clicked(self, mock_collect, mock_plot):
        self.obj.btnCollect.setEnabled(True)
        QTest.mouseClick(self.obj.btnCollect, Qt.LeftButton)
        assert mock_collect.called
        assert mock_plot.called
        self.assertTrue(self.obj.btnSetup.isEnabled())
        self.assertFalse(self.obj.btnTrigger.isEnabled())
        self.assertFalse(self.obj.btnCollect.isEnabled())
        self.assertTrue(self.obj.btnSave.isEnabled())

    @patch("PyQt5.QtWidgets.QFileDialog.getSaveFileName")
    def test_save_clicked(self, mock_dialog):
        # create temp file
        test_file = "/tmp/test.txt"
        fh = open(test_file, "w")
        fh.write("")
        fh.close()
        # mock returns filename of temp file
        test_filename = "/tmp/test.txt", None
        mock_dialog.return_value = test_filename
        # set up test channel
        curve = QwtPlotCurve("TestCh")
        test_channel = DummyTestGatherChannel(self.obj.parent.pmac, curve)
        test_channel.descNo = 0
        test_channel.Data = [0]
        self.obj.lstChannels.append(test_channel)
        self.obj.lstChannels[0].axisNo = 1
        self.obj.lstChannels[0].dataSourceInfo = {"desc": "Test desc"}
        # click save
        self.obj.btnSave.setEnabled(True)
        QTest.mouseClick(self.obj.btnSave, Qt.LeftButton)
        assert mock_dialog.called
        # assert file contents are as expected
        with open(test_file) as f:
            lines = f.readlines()
        expected = [
            "point,CH0, Axis 1, Motor present desired position, \n",
            "0,0.000000,\n",
        ]
        assert lines == expected
        os.remove(test_file)

    def tearDown(self):
        self.obj.close()
