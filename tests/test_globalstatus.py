import unittest
from os import path
from unittest.mock import patch

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow

from dls_pmac_control.global_status import GlobalStatusForm, PpmacGlobalStatusForm


class DummyTestWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.greenLedOn = QPixmap(path.join(path.dirname(__file__), "greenLedOn.png"))
        self.greenLedOff = QPixmap(path.join(path.dirname(__file__), "greenLedOff.png"))
        self.redLedOn = QPixmap(path.join(path.dirname(__file__), "redLedOn.png"))
        self.redLedOff = QPixmap(path.join(path.dirname(__file__), "redLedOff.png"))


class GlobalStatusTest(unittest.TestCase):
    @patch("PyQt6.QtWidgets.QLabel.setToolTip")
    @patch("PyQt6.QtWidgets.QLabel.setText")
    @patch("PyQt6.QtWidgets.QLabel.setPixmap")
    def test_inital_form(self, mock_pixmap, mock_text, mock_tooltip):
        test_widget = DummyTestWidget()
        obj = GlobalStatusForm(test_widget)
        mock_pixmap.assert_called_with(test_widget.greenLedOff)
        assert mock_text.called
        assert mock_tooltip.called
        assert mock_pixmap.call_count == len(obj.lstLeds)
        assert mock_text.call_count == len(obj.lstLabels)
        assert mock_tooltip.call_count == len(obj.lstLabels)
        obj.close()

    @patch("PyQt6.QtWidgets.QLabel.setPixmap")
    def test_update_status_all_off(self, mock_pixmap):
        test_widget = DummyTestWidget()
        obj = GlobalStatusForm(test_widget)
        obj.update_status(0)
        mock_pixmap.assert_called_with(test_widget.greenLedOff)
        assert mock_pixmap.call_count == 2 * len(obj.lstLeds)
        obj.close()


class PpmacGlobalStatusTest(unittest.TestCase):
    @patch("PyQt6.QtWidgets.QLabel.setToolTip")
    @patch("PyQt6.QtWidgets.QLabel.setText")
    @patch("PyQt6.QtWidgets.QLabel.setPixmap")
    def test_inital_form(self, mock_pixmap, mock_text, mock_tooltip):
        test_widget = DummyTestWidget()
        obj = PpmacGlobalStatusForm(test_widget)
        mock_pixmap.assert_called_with(test_widget.greenLedOff)
        assert mock_text.called
        assert mock_tooltip.called
        assert mock_pixmap.call_count == len(obj.lstLeds)
        assert mock_text.call_count == len(obj.lstLabels)
        assert mock_tooltip.call_count == len(obj.lstLabels)
        obj.close()

    @patch("PyQt6.QtWidgets.QLabel.setPixmap")
    def test_update_status_all_off(self, mock_pixmap):
        test_widget = DummyTestWidget()
        obj = PpmacGlobalStatusForm(test_widget)
        obj.update_status(0)
        mock_pixmap.assert_called_with(test_widget.greenLedOff)
        assert mock_pixmap.call_count == 2 * len(obj.lstLeds)
        obj.close()
