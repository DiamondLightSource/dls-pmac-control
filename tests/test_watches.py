import PyQt5
import unittest
from mock import patch, Mock
import time
import sys
sys.path.append('/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol')
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from watches import Watchesform, Watch

app = QApplication(sys.argv)

class TestWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.pmac = Mock()
        self.commsThread = Mock()

class WatchesTest(unittest.TestCase):

    def test_inital_form(self):
        test_widget = TestWidget()
        obj = Watchesform(test_widget)
        self.assertTrue(obj.lneVariableName.isEnabled())
        self.assertEqual(obj.lneVariableName.text(),"")
        self.assertTrue(obj.btnAddWatch.isEnabled())
        self.assertTrue(obj.btnRemoveWatch.isEnabled())
        self.assertTrue(obj.btnClose.isEnabled())
        self.assertFalse(obj.panelEditWatch.isEnabled())
        self.assertEqual(obj.table.rowCount(),0)
        obj.close()

    @patch("PyQt5.QtWidgets.QMessageBox.information")
    def test_add_unsafe_watch(self, mock_box):
        test_widget = TestWidget()
        obj = Watchesform(test_widget)
        obj.lneVariableName.setText("jog")
        QTest.mouseClick(obj.btnAddWatch, Qt.LeftButton)
        self.assertRaises(ValueError)
        self.assertFalse(obj.panelEditWatch.isEnabled())
        obj.close()

    @patch("PyQt5.QtWidgets.QMessageBox.information")
    def test_add_invalid_watch(self, mock_box):
        test_widget = TestWidget()
        obj = Watchesform(test_widget)
        obj.lneVariableName.setText("#1j+")
        QTest.mouseClick(obj.btnAddWatch, Qt.LeftButton)
        self.assertRaises(ValueError)
        self.assertFalse(obj.panelEditWatch.isEnabled())
        obj.close()

    @patch("PyQt5.QtWidgets.QMessageBox.information")
    def test_add_existing_watch(self, mock_box):
        test_widget = TestWidget()
        obj = Watchesform(test_widget)
        obj._watches = {"test" : 0}
        obj.lneVariableName.setText("test")
        QTest.mouseClick(obj.btnAddWatch, Qt.LeftButton)
        self.assertRaises(ValueError)
        self.assertFalse(obj.panelEditWatch.isEnabled())
        obj.close()

    @patch("watches.Watchesform.getPolledValue")
    @patch("watches.Watch")
    def test_add_watch(self, mock_watch, mock_get_value):
        test_widget = TestWidget()
        mock_get_value.return_value = "12"
        obj = Watchesform(test_widget)
        obj.lneVariableName.setText("watch")
        QTest.mouseClick(obj.btnAddWatch, Qt.LeftButton) 
        assert obj._watches["watch"] is not None
        self.assertEqual(obj.table.rowCount(),1)
        self.assertEqual(obj.table.item(0,0).text(),"watch")
        self.assertEqual(obj.table.item(0,1).text(),"12")
        self.assertEqual(obj.lneVariableName.text(),"")

    def test_get_watch(self):
        test_widget = TestWidget()
        obj = Watchesform(test_widget)
        obj._watches = {"test" : -1}
        actual_return = obj.getWatch("test")
        expected_return = -1
        self.assertEqual(actual_return, expected_return)
        obj.close()

    def test_get_watch_does_not_exist(self):
        test_widget = TestWidget()
        obj = Watchesform(test_widget)
        with self.assertRaises(ValueError):
            actual_return = obj.getWatch("test")
        obj.close()

    @patch("watches.Watchesform.getPolledValue")
    @patch("watches.Watch")
    def test_remove_watch(self, mock_watch, mock_get_value):
        test_widget = TestWidget()
        #add watch to be removed
        mock_get_value.return_value = "3"
        obj = Watchesform(test_widget)
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

    def test_clear_watches(self):
        test_widget = TestWidget()
        obj = Watchesform(test_widget)
        obj.clearWatches()
        self.assertEqual(obj.table.rowCount(),0)
        assert obj._watches == {}
        self.assertEqual(obj.lneVariableName.text(),"")
        self.assertEqual(obj.lneEditValue.text(),"")
        obj.close()

    @patch("watches.Watchesform.getPolledValue")
    @patch("watches.Watch")
    def test_apply_edit_watch(self, mock_watch, mock_get_value):
        test_widget = TestWidget()
        #add watch to be edited
        mock_get_value.return_value = "-8"
        obj = Watchesform(test_widget)
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
