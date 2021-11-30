import unittest

from mock import Mock, patch
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QMainWindow

from dls_pmaccontrol.watches import Watchesform


class DummyTestWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.pmac = Mock()
        self.commsThread = Mock()


class WatchesTest(unittest.TestCase):
    def setUp(self):
        self.test_widget = DummyTestWidget()
        self.obj = Watchesform(self.test_widget)

    def test_inital_form(self):
        self.assertTrue(self.obj.lneVariableName.isEnabled())
        self.assertEqual(self.obj.lneVariableName.text(), "")
        self.assertTrue(self.obj.btnAddWatch.isEnabled())
        self.assertTrue(self.obj.btnRemoveWatch.isEnabled())
        self.assertTrue(self.obj.btnClose.isEnabled())
        self.assertFalse(self.obj.panelEditWatch.isEnabled())
        self.assertEqual(self.obj.table.rowCount(), 0)

    @patch("PyQt5.QtWidgets.QMessageBox.information")
    def test_add_unsafe_watch(self, mock_box):
        self.obj.lneVariableName.setText("jog")
        QTest.mouseClick(self.obj.btnAddWatch, Qt.LeftButton)
        error_msg = "jog is an unsafe command"
        self.assertRaises(ValueError, msg=error_msg)
        self.assertFalse(self.obj.panelEditWatch.isEnabled())
        mock_box.assert_called_with(self.obj, "Cannot create watch", error_msg)

    @patch("PyQt5.QtWidgets.QMessageBox.information")
    def test_add_invalid_watch(self, mock_box):
        self.obj.lneVariableName.setText("#1j+")
        QTest.mouseClick(self.obj.btnAddWatch, Qt.LeftButton)
        error_msg = "#1j+ is not a valid variable"
        self.assertRaises(ValueError, msg=error_msg)
        self.assertFalse(self.obj.panelEditWatch.isEnabled())
        mock_box.assert_called_with(self.obj, "Cannot create watch", error_msg)

    @patch("PyQt5.QtWidgets.QMessageBox.information")
    def test_add_existing_watch(self, mock_box):
        self.obj._watches = {"test": 0}
        self.obj.lneVariableName.setText("test")
        QTest.mouseClick(self.obj.btnAddWatch, Qt.LeftButton)
        error_msg = "There is already a watch for test"
        self.assertRaises(ValueError, msg=error_msg)
        self.assertFalse(self.obj.panelEditWatch.isEnabled())
        mock_box.assert_called_with(self.obj, "Cannot create watch", error_msg)

    @patch("dls_pmaccontrol.watches.Watchesform.getPolledValue")
    @patch("dls_pmaccontrol.watches.Watch")
    def test_add_watch(self, mock_watch, mock_get_value):
        mock_get_value.return_value = "12"
        self.obj.lneVariableName.setText("watch")
        QTest.mouseClick(self.obj.btnAddWatch, Qt.LeftButton)
        assert self.obj._watches["watch"] is not None
        self.assertEqual(self.obj.table.rowCount(), 1)
        self.assertEqual(self.obj.table.item(0, 0).text(), "watch")
        self.assertEqual(self.obj.table.item(0, 1).text(), "12")
        self.assertEqual(self.obj.lneVariableName.text(), "")
        mock_watch.assert_called_with(self.obj.parent.pmac, "watch")
        mock_get_value.assert_called_with("watch")

    def test_get_watch(self):
        self.obj._watches = {"test": -1}
        assert self.obj.getWatch("test") == -1

    def test_get_watch_does_not_exist(self):
        error_msg = 'There is no watch for variable "test"'
        self.assertRaises(ValueError, msg=error_msg)

    @patch("dls_pmaccontrol.watches.Watchesform.getPolledValue")
    @patch("dls_pmaccontrol.watches.Watch")
    def test_remove_watch(self, mock_watch, mock_get_value):
        # add watch to be removed
        mock_get_value.return_value = "3"
        self.obj.lneVariableName.setText("remove_me")
        QTest.mouseClick(self.obj.btnAddWatch, Qt.LeftButton)
        # click on table item and click remove watch
        QTest.mouseClick(self.obj.table.viewport(), Qt.LeftButton)
        QTest.mouseClick(self.obj.btnRemoveWatch, Qt.LeftButton)
        assert self.obj.table.rowCount() == 0
        assert self.obj._watches == {}
        assert self.obj.lneEditValue.text() == ""
        self.assertFalse(self.obj.panelEditWatch.isEnabled())
        mock_watch.assert_called_with(self.obj.parent.pmac, "remove_me")
        mock_get_value.assert_called_with("remove_me")

    def test_clear_watches(self):
        self.obj.clearWatches()
        self.assertEqual(self.obj.table.rowCount(), 0)
        assert self.obj._watches == {}
        self.assertEqual(self.obj.lneVariableName.text(), "")
        self.assertEqual(self.obj.lneEditValue.text(), "")

    @patch("dls_pmaccontrol.watches.Watchesform.getPolledValue")
    @patch("dls_pmaccontrol.watches.Watch")
    def test_apply_edit_watch(self, mock_watch, mock_get_value):
        # add watch to be edited
        mock_get_value.return_value = "-8"
        self.obj.lneVariableName.setText("edit_me")
        QTest.mouseClick(self.obj.btnAddWatch, Qt.LeftButton)
        # click on table item and edit
        QTest.mouseClick(self.obj.table.viewport(), Qt.LeftButton)
        self.obj.lneEditValue.setText("-8")
        QTest.mouseClick(self.obj.btnApplyChanges, Qt.LeftButton)
        assert self.obj._watches["edit_me"] is not None
        self.assertEqual(self.obj.table.rowCount(), 1)
        self.assertEqual(self.obj.table.item(0, 0).text(), "edit_me")
        self.assertEqual(self.obj.table.item(0, 1).text(), "-8")
        self.assertEqual(self.obj.lneVariableName.text(), "")
        self.assertEqual(self.obj.lneEditValue.text(), "")
        self.assertFalse(self.obj.panelEditWatch.isEnabled())
        mock_watch.assert_called_with(self.obj.parent.pmac, "edit_me")
        mock_get_value.assert_called_with("edit_me")

    def tearDown(self):
        self.obj.close()
