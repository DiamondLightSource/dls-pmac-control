import PyQt5
import unittest
from mock import patch
import time
import sys
sys.path.append('/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol')
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem
from motor import Controlform
from commsThread import CommsThread
from watches import Watchesform, Watch
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


class WatchesTest(unittest.TestCase):

    @patch("motor.Controlform")
    def test_inital_form(self, mock_control_form):
        obj = Watchesform(Controlform(options))
        self.assertTrue(obj.lneVariableName.isEnabled())
        self.assertEqual(obj.lneVariableName.text(),"")
        self.assertTrue(obj.btnAddWatch.isEnabled())
        self.assertTrue(obj.btnRemoveWatch.isEnabled())
        self.assertTrue(obj.btnClose.isEnabled())
        self.assertFalse(obj.panelEditWatch.isEnabled())
        self.assertEqual(obj.table.rowCount(),0)
        obj.close()

    @patch("motor.Controlform")
    def test_add_unsafe_watch(self, mock_control_form):
        obj = Watchesform(Controlform(options))
        obj.lneVariableName.setText("jog")
        QTest.mouseClick(obj.btnAddWatch, Qt.LeftButton)
        self.assertRaises(ValueError)
        self.assertFalse(obj.panelEditWatch.isEnabled())
        obj.close()

    @patch("motor.Controlform")
    def test_add_invalid_watch(self, mock_control_form):
        obj = Watchesform(Controlform(options))
        obj.lneVariableName.setText("#1j+")
        QTest.mouseClick(obj.btnAddWatch, Qt.LeftButton)
        self.assertRaises(ValueError)
        self.assertFalse(obj.panelEditWatch.isEnabled())
        obj.close()

    @patch("motor.Controlform")
    def test_add_existing_watch(self, mock_control_form):
        obj = Watchesform(Controlform(options))
        obj._watches = {"test" : 0}
        obj.lneVariableName.setText("test")
        QTest.mouseClick(obj.btnAddWatch, Qt.LeftButton)
        self.assertRaises(ValueError)
        self.assertFalse(obj.panelEditWatch.isEnabled())
        obj.close()

    @patch("watches.Watchesform.getPolledValue")
    @patch("commsThread.CommsThread")
    @patch("watches.Watch")
    @patch("motor.Controlform")
    def test_add_watch(self, mock_control_form, mock_watch, mock_comms, mock_get_value):
        mock_get_value.return_value = "12"
        obj = Watchesform(Controlform(options))
        obj.lneVariableName.setText("watch")
        QTest.mouseClick(obj.btnAddWatch, Qt.LeftButton) 
        assert obj._watches["watch"] is not None
        self.assertEqual(obj.table.rowCount(),1)
        self.assertEqual(obj.table.item(0,0).text(),"watch")
        self.assertEqual(obj.table.item(0,1).text(),"12")
        self.assertEqual(obj.lneVariableName.text(),"")
  
    @patch("motor.Controlform")
    def test_get_watch(self, mock_control_form):
        obj = Watchesform(Controlform(options))
        obj._watches = {"test" : -1}
        actual_return = obj.getWatch("test")
        expected_return = -1
        self.assertEqual(actual_return, expected_return)
        obj.close()

    @patch("motor.Controlform")
    def test_get_watch_does_not_exist(self, mock_control_form):
        obj = Watchesform(Controlform(options))
        with self.assertRaises(ValueError):
            actual_return = obj.getWatch("test")
        obj.close()

    @patch("watches.Watchesform.getPolledValue")
    @patch("commsThread.CommsThread")
    @patch("watches.Watch")
    @patch("motor.Controlform")
    def test_remove_watch(self, mock_control_form, mock_watch, mock_comms, mock_get_value):
        #add watch to be removed
        mock_get_value.return_value = "3"
        obj = Watchesform(Controlform(options))
        obj.lneVariableName.setText("remove_me")
        QTest.mouseClick(obj.btnAddWatch, Qt.LeftButton) 
        #click on table item and click remove watch
        QTest.mouseClick(obj.table.viewport(), Qt.LeftButton)
        QTest.mouseClick(obj.btnRemoveWatch, Qt.LeftButton)
        assert obj.table.rowCount() == 0
        assert obj._watches == {}
        self.assertEqual(obj.lneEditValue.text(),"")
        self.assertFalse(obj.panelEditWatch.isEnabled())
        obj.close()

    @patch("commsThread.CommsThread")
    @patch("motor.Controlform")
    def test_clear_watches(self, mock_control_form, mock_comms):
        obj = Watchesform(Controlform(options))
        obj.clearWatches()
        self.assertEqual(obj.table.rowCount(),0)
        assert obj._watches == {}
        self.assertEqual(obj.lneVariableName.text(),"")
        self.assertEqual(obj.lneEditValue.text(),"")
        obj.close()

    @patch("watches.Watchesform.getPolledValue")
    @patch("commsThread.CommsThread")
    @patch("watches.Watch")
    @patch("motor.Controlform")
    def test_apply_edit_watch(self, mock_control_form, mock_watch, mock_comms, mock_get_value):
        #add watch to be edited
        mock_get_value.return_value = "-8"
        obj = Watchesform(Controlform(options))
        obj.lneVariableName.setText("edit_me")
        QTest.mouseClick(obj.btnAddWatch, Qt.LeftButton)
        #click on table item and edit
        QTest.mouseClick(obj.table.viewport(), Qt.LeftButton)
        obj.lneEditValue.setText("-8")
        QTest.mouseClick(obj.btnApplyChanges, Qt.LeftButton)
        assert obj._watches["edit_me"] is not None
        self.assertEqual(obj.table.rowCount(),1)
        self.assertEqual(obj.table.item(0,0).text(),"edit_me")
        self.assertEqual(obj.table.item(0,1).text(),"-8")
        self.assertEqual(obj.lneVariableName.text(),"")
        self.assertEqual(obj.lneEditValue.text(),"")
        self.assertFalse(obj.panelEditWatch.isEnabled())
