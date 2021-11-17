import PyQt5
import unittest
from mock import patch
import time
from os import path
import sys

sys.path.append("/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol")
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem
from PyQt5.QtGui import QPixmap
from GlobalStatus import GlobalStatusForm, PpmacGlobalStatusForm

app = QApplication(sys.argv)


class TestWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.greenLedOn = QPixmap(path.join(path.dirname(__file__), "greenLedOn.png"))
        self.greenLedOff = QPixmap(path.join(path.dirname(__file__), "greenLedOff.png"))
        self.redLedOn = QPixmap(path.join(path.dirname(__file__), "redLedOn.png"))
        self.redLedOff = QPixmap(path.join(path.dirname(__file__), "redLedOff.png"))


class GlobalStatusTest(unittest.TestCase):
    @patch("PyQt5.QtWidgets.QLabel.setToolTip")
    @patch("PyQt5.QtWidgets.QLabel.setText")
    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    def test_inital_form(self, mock_pixmap, mock_text, mock_tooltip):
        test_widget = TestWidget()
        obj = GlobalStatusForm(test_widget)
        mock_pixmap.assert_called_with(test_widget.greenLedOff)
        assert mock_text.called
        assert mock_tooltip.called
        assert mock_pixmap.call_count == len(obj.lstLeds)
        assert mock_text.call_count == len(obj.lstLabels)
        assert mock_tooltip.call_count == len(obj.lstLabels)
        obj.close()

    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    def test_update_status_all_off(self, mock_pixmap):
        test_widget = TestWidget()
        obj = GlobalStatusForm(test_widget)
        obj.updateStatus(0)
        mock_pixmap.assert_called_with(test_widget.greenLedOff)
        assert mock_pixmap.call_count == 2 * len(obj.lstLeds)
        obj.close()


class PpmacGlobalStatusTest(unittest.TestCase):
    @patch("PyQt5.QtWidgets.QLabel.setToolTip")
    @patch("PyQt5.QtWidgets.QLabel.setText")
    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    def test_inital_form(self, mock_pixmap, mock_text, mock_tooltip):
        test_widget = TestWidget()
        obj = PpmacGlobalStatusForm(test_widget)
        mock_pixmap.assert_called_with(test_widget.greenLedOff)
        assert mock_text.called
        assert mock_tooltip.called
        assert mock_pixmap.call_count == len(obj.lstLeds)
        assert mock_text.call_count == len(obj.lstLabels)
        assert mock_tooltip.call_count == len(obj.lstLabels)
        obj.close()

    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    def test_update_status_all_off(self, mock_pixmap):
        test_widget = TestWidget()
        obj = PpmacGlobalStatusForm(test_widget)
        obj.updateStatus(0)
        mock_pixmap.assert_called_with(test_widget.greenLedOff)
        assert mock_pixmap.call_count == 2 * len(obj.lstLeds)
        obj.close()
