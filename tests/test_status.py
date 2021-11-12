import PyQt5
import unittest
from mock import patch
import time
from os import path
import sys
sys.path.append('/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol')
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem
from PyQt5.QtGui import QPixmap
from status import Statusform, PpmacStatusform

app = QApplication(sys.argv)

class TestWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.greenLedOn = QPixmap(path.join(path.dirname(__file__), "greenLedOn.png"))
        self.greenLedOff = QPixmap(path.join(path.dirname(__file__), "greenLedOff.png"))
        self.redLedOn = QPixmap(path.join(path.dirname(__file__), "redLedOn.png"))
        self.redLedOff = QPixmap(path.join(path.dirname(__file__), "redLedOff.png"))


class StatusTest(unittest.TestCase):

    @patch("PyQt5.QtWidgets.QLabel.setToolTip")
    @patch("PyQt5.QtWidgets.QLabel.setText")
    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    def setUp(self, mock_pixmap, mock_text, mock_tooltip):
        self.test_widget = TestWidget()
        self.obj = Statusform(self.test_widget,1)

    def test_inital_form(self):
        assert self.obj.ledGroup.title() == "Axis 1"

    def test_change_axis(self):
        self.obj.changeAxis(5)
        assert self.obj.currentAxis == 5
        assert self.obj.ledGroup.title() == "Axis 5"

    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    def test_update_status_all_off(self, mock_pixmap):
        self.obj.updateStatus(0)
        mock_pixmap.assert_called_with(self.test_widget.greenLedOff)
        assert mock_pixmap.call_count == len(self.obj.lstLeds)

    def tearDown(self):
        self.obj.close()

class PpmacStatusTest(unittest.TestCase):

    @patch("PyQt5.QtWidgets.QLabel.setToolTip")
    @patch("PyQt5.QtWidgets.QLabel.setText")
    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    def setUp(self, mock_pixmap, mock_text, mock_tooltip):
        self.test_widget = TestWidget()
        self.obj = PpmacStatusform(self.test_widget,1)

    def test_inital_form(self):
        assert self.obj.ledGroup.title() == "Axis 1"

    def test_change_axis(self):
        self.obj.changeAxis(3)
        assert self.obj.currentAxis == 3
        assert self.obj.ledGroup.title() == "Axis 3"

    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    def test_update_status_all_off(self, mock_pixmap):
        self.obj.updateStatus(0)
        mock_pixmap.assert_called_with(self.test_widget.greenLedOff)
        assert mock_pixmap.call_count == len(self.obj.lstLeds)

    def tearDown(self):
        self.obj.close()
