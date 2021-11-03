import PyQt5
import unittest
from mock import patch, Mock
import time
import sys
sys.path.append('/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol')
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem
from motor import Controlform
from commsThread import CommsThread
from gather import PmacGatherform
from ppmacgather import PpmacGatherform
from optparse import OptionParser

app = QApplication(sys.argv)

usage = """usage: %prog [options]
%prog is a graphical frontend to the Deltatau motorcontroller known as PMAC."""
parser = OptionParser(usage)
parser.add_option(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        help="Print more details (than necessary in most " "cases...)",
    )
parser.add_option(
        "-o",
        "--protocol",
        action="store",
        dest="protocol",
        default="ts",
        help='Set the connection protocol; use "ts" for '
        "serial via terminal server (the default), "
        'or "tcpip" for network TCP/IP connection.',
    )
parser.add_option(
        "-s",
        "--server",
        action="store",
        dest="server",
        default="blxxi-nt-tserv-01",
        help="Set server name (default: blxxi-nt-tserv-01)",
    )
parser.add_option(
        "-p",
        "--port",
        action="store",
        dest="port",
        default="7017",
        help="Set IP port number to connect to (default: 7017)",
    )
parser.add_option(
        "-a",
        "--axis",
        action="store",
        dest="defaultAxis",
        default=1,
        help="Set an axis as a default selected axis when "
        "starting up the application (default: 1)",
    )
parser.add_option(
        "-n",
        "--naxes",
        action="store",
        dest="nAxes",
        help="Display and poll NAXES axes. Default is 32 for a "
        "PMAC, 8 for a geoBrick",
    )
parser.add_option(
        "-t",
        "--timeout",
        action="store",
        type="float",
        dest="timeout",
        default=3.0,
        help="Set the communication timeout (default: 3 seconds, " "minimum: 1 second)",
    )
(options, args) = parser.parse_args()

class PmacGatherTest(unittest.TestCase):

    @patch("motor.Controlform")
    def test_initial_state(self, mock_control_form):
        obj = PmacGatherform(Controlform(options))
        self.assertFalse(obj.btnSetup.isEnabled())
        self.assertFalse(obj.btnTrigger.isEnabled())
        self.assertFalse(obj.btnCollect.isEnabled())
        self.assertFalse(obj.btnSave.isEnabled())
        self.assertTrue(obj.btnApplyConf.isEnabled())
        obj.close()

    '''#need to mock sendCommand
    @patch("motor.Controlform")
    def test_gather_config(self, mock_control_form):
        obj = PmacGatherform(Controlform(options))
        chkboxcentre = QPoint(2,obj.chkPlot1.height()/2)
        QTest.mouseClick(obj.chkPlot1, Qt.LeftButton, pos=chkboxcentre)
        ret = obj.gatherConfig()
        assert ret == True'''

    @patch("gather.PmacGatherform.calcSampleTime")
    @patch("motor.Controlform")
    def test_change_no_samples(self, mock_control_form, mock_calc):
        obj = PmacGatherform(Controlform(options))
        obj.lneNumberSamples.setText("1000")
        QTest.keyClick(obj.lneNumberSamples, Qt.Key_Enter)
        assert obj.nGatherPoints == 1000
        assert obj.nServoCyclesGather == 10
        obj.close()

    @patch("gather.PmacGatherform.calcSampleTime")
    @patch("motor.Controlform")
    def test_change_sample_time(self, mock_control_form, mock_calc):
        obj = PmacGatherform(Controlform(options))
        obj.lneSampleTime.setText("5")
        QTest.keyClick(obj.lneSampleTime, Qt.Key_Enter)
        assert obj.nServoCyclesGather == 5
        assert obj.nGatherPoints == 10
        obj.close()

    @patch("motor.Controlform")
    def test_click_apply(self, mock_control_form):
        obj = PmacGatherform(Controlform(options))
        obj.nServoCyclesGather = 10
        obj.nGatherPoints = 100
        obj.gatherConfig = Mock()
        QTest.keyClick(obj.btnApplyConf, Qt.Key_Enter)
        self.assertTrue(obj.btnSetup.isEnabled())
        self.assertFalse(obj.btnTrigger.isEnabled())
        self.assertFalse(obj.btnCollect.isEnabled())
        self.assertFalse(obj.btnSave.isEnabled())
        obj.close()

    '''# need to mock sendCommand
    @patch("motor.Controlform")
    def test_gather_setup(self, mock_control_form):
        obj = PmacGatherform(Controlform(options))
        ret = obj.gatherSetup()
        assert ret == None        
        obj.close()

    # need to mock sendCommand
    @patch("motor.Controlform")
    def test_collect_data(self, mock_control_form):
        obj = PmacGatherform(Controlform(options))
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
        obj.close()

    @patch("motor.Controlform")
    def test_parse_data(self, mock_control_form):
        obj = PmacGatherform(Controlform(options))
        datastrings = ["test"]
        obj.parseData(datastrings)
        obj.close()

    #@patch("motor.Controlform.pmac.sendCommand", return_value=("8388608",None))
    @patch("motor.Controlform")
    def test_calc_sample_time(self, mock_control_form, mock_sendcmd):
        obj = PmacGatherform(Controlform(options))
        obj.calcSampleTime()
        assert obj.servoCycleTime == 1
        self.assertEqual(obj.sampleTime, obj.nServoCyclesGather)
        obj.close()

    @patch("motor.Controlform")
    def test_save_clicked(self, mock_control_form):
        obj = PmacGatherform(Controlform(options))
        obj.saveClicked()
        obj.close()'''

class PpmacGatherTest(unittest.TestCase):

    @patch("motor.Controlform")
    def test_initial_state(self, mock_control_form):
        obj = PpmacGatherform(Controlform(options))
        self.assertFalse(obj.btnSetup.isEnabled())
        self.assertFalse(obj.btnTrigger.isEnabled())
        self.assertFalse(obj.btnCollect.isEnabled())
        self.assertFalse(obj.btnSave.isEnabled())
        self.assertTrue(obj.btnApplyConf.isEnabled())
        obj.close()

    @patch("motor.Controlform")
    def test_change_no_samples(self, mock_control_form):
        obj = PpmacGatherform(Controlform(options))
        obj.lneNumberSamples.setText("1000")
        QTest.keyClick(obj.lneNumberSamples, Qt.Key_Enter)
        assert obj.nGatherPoints == 1000
        assert obj.nServoCyclesGather == 0 
        obj.close()

    @patch("motor.Controlform")
    def test_change_sample_time(self, mock_control_form):
        obj = PpmacGatherform(Controlform(options))
        obj.lneSampleTime.setText("5")
        QTest.keyClick(obj.lneSampleTime, Qt.Key_Enter)
        assert obj.nGatherPoints == 0
        assert obj.nServoCyclesGather == 5 
        obj.close()

    @patch("motor.Controlform")
    def test_gather_config(self, mock_control_form):
        pass

    @patch("motor.Controlform")
    def test_click_apply(self, mock_control_form):
        obj = PpmacGatherform(Controlform(options))
        obj.nServoCyclesGather = 10
        obj.nGatherPoints = 100
        obj.gatherConfig = Mock()
        QTest.keyClick(obj.btnApplyConf, Qt.Key_Enter)
        self.assertTrue(obj.btnSetup.isEnabled())
        self.assertFalse(obj.btnTrigger.isEnabled())
        self.assertFalse(obj.btnCollect.isEnabled())
        self.assertFalse(obj.btnSave.isEnabled())
        obj.close()

    @patch("motor.Controlform")
    def test_plot_data(self, mock_control_form):
        pass

    @patch("motor.Controlform")
    def test_changed_tab(self, mock_control_form):
        pass

    #@patch("ppmacgather.PpmacGatherform.plotData")
    #@patch("ppmacgather.PpmacGatherform.collectData")
    @patch("motor.Controlform")
    def test_collect_clicked(self, mock_control_form):#, mock_collect, mock_plot):
        obj = PpmacGatherform(Controlform(options))
        QTest.mouseClick(obj.btnCollect, Qt.LeftButton)
        #self.assertTrue(obj.btnSetup.isEnabled())
        #self.assertFalse(obj.btnTrigger.isEnabled())
        #self.assertFalse(obj.btnCollect.isEnabled())
        #self.assertTrue(obj.btnSave.isEnabled())
        obj.close()

    @patch("motor.Controlform")
    def test_save_clicked(self, mock_control_form):
        pass







