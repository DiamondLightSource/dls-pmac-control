import PyQt5
import unittest
from mock import patch, Mock
import time
import sys
sys.path.append('/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol')
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem
from gather import PmacGatherform
from ppmacgather import PpmacGatherform

app = QApplication(sys.argv)

class TestWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.pmac = Mock()
        self.commsThread = Mock()

class PmacGatherTest(unittest.TestCase):

    def test_initial_state(self):
        test_widget = TestWidget()
        obj = PmacGatherform(test_widget)
        self.assertFalse(obj.btnSetup.isEnabled())
        self.assertFalse(obj.btnTrigger.isEnabled())
        self.assertFalse(obj.btnCollect.isEnabled())
        self.assertFalse(obj.btnSave.isEnabled())
        self.assertTrue(obj.btnApplyConf.isEnabled())
        obj.close()

    def test_gather_config(self):
        test_widget = TestWidget()
        obj = PmacGatherform(test_widget)
        chkboxcentre = QPoint(2,obj.chkPlot1.height()/2)
        QTest.mouseClick(obj.chkPlot1, Qt.LeftButton, pos=chkboxcentre)
        ret = obj.gatherConfig()
        assert ret == True
        obj.close()

    @patch("gather.PmacGatherform.calcSampleTime")
    def test_change_no_samples(self, mock_calc):
        test_widget = TestWidget()
        obj = PmacGatherform(test_widget)
        obj.lneNumberSamples.setText("1000")
        QTest.keyClick(obj.lneNumberSamples, Qt.Key_Enter)
        assert obj.nGatherPoints == 1000
        assert obj.nServoCyclesGather == 10
        obj.close()

    @patch("gather.PmacGatherform.calcSampleTime")
    def test_change_sample_time(self, mock_calc):
        test_widget = TestWidget()
        obj = PmacGatherform(test_widget)
        obj.lneSampleTime.setText("5")
        QTest.keyClick(obj.lneSampleTime, Qt.Key_Enter)
        assert obj.nServoCyclesGather == 5
        assert obj.nGatherPoints == 10
        obj.close()

    def test_click_apply(self):
        test_widget = TestWidget()
        obj = PmacGatherform(test_widget)
        obj.nServoCyclesGather = 10
        obj.nGatherPoints = 100
        obj.gatherConfig = Mock()
        QTest.keyClick(obj.btnApplyConf, Qt.Key_Enter)
        self.assertTrue(obj.btnSetup.isEnabled())
        self.assertFalse(obj.btnTrigger.isEnabled())
        self.assertFalse(obj.btnCollect.isEnabled())
        self.assertFalse(obj.btnSave.isEnabled())
        obj.close()

    @patch("gather.PmacGatherform.gatherSetup")
    def test_setup_clicked(self, mock_setup):
        test_widget = TestWidget()
        obj = PmacGatherform(test_widget)
        obj.btnSetup.setEnabled(True)
        QTest.mouseClick(obj.btnSetup, Qt.LeftButton)
        assert mock_setup.called
        self.assertTrue(obj.btnSetup.isEnabled())
        self.assertTrue(obj.btnTrigger.isEnabled())
        self.assertFalse(obj.btnCollect.isEnabled())
        self.assertFalse(obj.btnSave.isEnabled())

    #def test_gather_setup(self):
     #   test_widget = TestWidget()
      #  obj = PmacGatherform(test_widget)
       # ret = obj.gatherSetup()
        #assert ret == None        
        #obj.close()

    '''def test_collect_data(self):
        test_widget = TestWidget()
        obj = PmacGatherform(test_widget)
        #set up gather
        chkboxcentre = QPoint(2,obj.chkPlot1.height()/2)
        QTest.mouseClick(obj.chkPlot1, Qt.LeftButton, pos=chkboxcentre)
        QTest.mouseClick(obj.btnApplyConf, Qt.LeftButton)
        QTest.mouseClick(obj.btnSetup, Qt.LeftButton)
        QTest.mouseClick(obj.btnTrigger, Qt.LeftButton)
        #then press collect
        QTest.mouseClick(obj.btnCollect, Qt.LeftButton)
        self.assertTrue(obj.btnSave.isEnabled())
        self.assertFalse(obj.btnTrigger.isEnabled())
        self.assertFalse(obj.btnCollect.isEnabled())
        self.assertTrue(obj.btnSave.isEnabled())
        obj.close()'''

    #def test_parse_data(self):
     #   test_widget = TestWidget()
      #  obj = PmacGatherform(test_widget)
       # datastrings = ["test"]
        #obj.parseData(datastrings)
        #obj.close()

    # need to mock self.parent.pmac.sendCommand
    #def test_calc_sample_time(self):
     #   test_widget = TestWidget()
      #  obj = PmacGatherform(test_widget)
       # obj.calcSampleTime()
        #assert obj.servoCycleTime == 1
        #self.assertEqual(obj.sampleTime, obj.nServoCyclesGather)
        #obj.close()

    @patch("gather.PmacGatherform.plotData")
    @patch("gather.PmacGatherform.collectData")
    def test_collect_clicked(self, mock_collect, mock_plot):
        test_widget = TestWidget()
        obj = PmacGatherform(test_widget)
        obj.btnCollect.setEnabled(True)
        QTest.mouseClick(obj.btnCollect, Qt.LeftButton)
        assert mock_collect.called
        assert mock_plot.called
        self.assertTrue(obj.btnSetup.isEnabled())
        self.assertFalse(obj.btnTrigger.isEnabled())
        self.assertFalse(obj.btnCollect.isEnabled())
        self.assertTrue(obj.btnSave.isEnabled())
        obj.close()

    @patch("PyQt5.QtWidgets.QMessageBox.information")
    def test_save_clicked_no_data(self, mock_box):
        test_widget = TestWidget()
        obj = PmacGatherform(test_widget)
        obj.lstChannels = []
        ret = obj.saveClicked()
        assert ret == None
        obj.close()

    #def test_save_clicked

class PpmacGatherTest(unittest.TestCase):

    def test_initial_state(self):
        test_widget = TestWidget()
        obj = PpmacGatherform(test_widget)
        self.assertFalse(obj.btnSetup.isEnabled())
        self.assertFalse(obj.btnTrigger.isEnabled())
        self.assertFalse(obj.btnCollect.isEnabled())
        self.assertFalse(obj.btnSave.isEnabled())
        self.assertTrue(obj.btnApplyConf.isEnabled())
        obj.close()

    @patch("PyQt5.QtWidgets.QMessageBox.information")
    def test_change_no_samples(self, mock_box):
        test_widget = TestWidget()
        obj = PpmacGatherform(test_widget)
        obj.lneNumberSamples.setText("1000")
        QTest.keyClick(obj.lneNumberSamples, Qt.Key_Enter)
        assert obj.nGatherPoints == 1000
        assert obj.nServoCyclesGather == 0 
        obj.close()

    @patch("PyQt5.QtWidgets.QMessageBox.information")
    def test_change_sample_time(self, mock_box):
        test_widget = TestWidget()
        obj = PpmacGatherform(test_widget)
        obj.lneSampleTime.setText("5")
        QTest.keyClick(obj.lneSampleTime, Qt.Key_Enter)
        assert obj.nGatherPoints == 0
        assert obj.nServoCyclesGather == 5 
        obj.close()

    # mock send command
    #def test_gather_config(self):
     #   test_widget = TestWidget()
      #  obj = PpmacGatherform(test_widget)

    def test_click_apply(self):
        test_widget = TestWidget()
        obj = PpmacGatherform(test_widget)
        obj.nServoCyclesGather = 10
        obj.nGatherPoints = 100
        obj.gatherConfig = Mock()
        QTest.keyClick(obj.btnApplyConf, Qt.Key_Enter)
        self.assertTrue(obj.btnSetup.isEnabled())
        self.assertFalse(obj.btnTrigger.isEnabled())
        self.assertFalse(obj.btnCollect.isEnabled())
        self.assertFalse(obj.btnSave.isEnabled())
        obj.close()

    #def test_collect_data

    #def test_plot_data(self):
     #   test_widget = TestWidget()
      #  obj = PpmacGatherform(test_widget)

    #def test_calc_sample_time


    # mock send command
    #@patch("ppmacgather.PpmacGatherform.calcSampleTime")
    #def test_changed_tab(self, mock_calc):
        #test_widget = TestWidget()
        #obj = PpmacGatherform(test_widget)


    @patch("ppmacgather.PpmacGatherform.plotData")
    @patch("ppmacgather.PpmacGatherform.collectData")
    def test_collect_clicked(self, mock_collect, mock_plot):
        test_widget = TestWidget()
        obj = PpmacGatherform(test_widget)
        obj.btnCollect.setEnabled(True)
        QTest.mouseClick(obj.btnCollect, Qt.LeftButton)
        assert mock_collect.called
        assert mock_plot.called
        self.assertTrue(obj.btnSetup.isEnabled())
        self.assertFalse(obj.btnTrigger.isEnabled())
        self.assertFalse(obj.btnCollect.isEnabled())
        self.assertTrue(obj.btnSave.isEnabled())
        obj.close()

    #def test_save_clicked(self):
     #   test_widget = TestWidget()
      #  obj = PpmacGatherform(test_widget)
