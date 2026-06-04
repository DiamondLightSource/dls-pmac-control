import unittest
from os import path
from unittest.mock import patch

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow

from dls_pmac_control.status import PpmacStatusform, Statusform


class DummyTestWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.greenLedOn = QPixmap(path.join(path.dirname(__file__), "greenLedOn.png"))
        self.greenLedOff = QPixmap(path.join(path.dirname(__file__), "greenLedOff.png"))
        self.redLedOn = QPixmap(path.join(path.dirname(__file__), "redLedOn.png"))
        self.redLedOff = QPixmap(path.join(path.dirname(__file__), "redLedOff.png"))


class StatusTest(unittest.TestCase):
    @patch("PyQt6.QtWidgets.QLabel.setToolTip")
    @patch("PyQt6.QtWidgets.QLabel.setText")
    @patch("PyQt6.QtWidgets.QLabel.setPixmap")
    def setUp(self, mock_pixmap, mock_text, mock_tooltip):
        self.test_widget = DummyTestWidget()
        self.obj = Statusform(self.test_widget, 1)

    def test_inital_form(self):
        assert self.obj.ledGroup.title() == "Axis 1"

    def test_change_axis(self):
        self.obj.change_axis(5)
        assert self.obj.currentAxis == 5
        assert self.obj.ledGroup.title() == "Axis 5"

    @patch("PyQt6.QtWidgets.QLabel.setPixmap")
    def test_update_status_all_off(self, mock_pixmap):
        self.obj.update_status(0)
        mock_pixmap.assert_called_with(self.test_widget.greenLedOff)
        assert mock_pixmap.call_count == len(self.obj.lstLeds)

    def tearDown(self):
        self.obj.close()


class PpmacStatusTest(unittest.TestCase):
    @patch("PyQt6.QtWidgets.QLabel.setToolTip")
    @patch("PyQt6.QtWidgets.QLabel.setText")
    @patch("PyQt6.QtWidgets.QLabel.setPixmap")
    def setUp(self, mock_pixmap, mock_text, mock_tooltip):
        self.test_widget = DummyTestWidget()
        self.obj = PpmacStatusform(self.test_widget, 1)

    def test_inital_form(self):
        assert self.obj.ledGroup.title() == "Axis 1"

    def test_change_axis(self):
        self.obj.change_axis(3)
        assert self.obj.currentAxis == 3
        assert self.obj.ledGroup.title() == "Axis 3"

    @patch("PyQt6.QtWidgets.QLabel.setPixmap")
    def test_update_status_all_off(self, mock_pixmap):
        self.obj.update_status(0)
        mock_pixmap.assert_called_with(self.test_widget.greenLedOff)
        assert mock_pixmap.call_count == len(self.obj.lstLeds)

    def tearDown(self):
        self.obj.close()
