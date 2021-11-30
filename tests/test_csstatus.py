import unittest
from os import path

from mock import Mock, patch
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QMainWindow

from dls_pmaccontrol.CSstatus import CSStatusForm, PpmacCSStatusForm


class DummyTestWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.greenLedOn = QPixmap(path.join(path.dirname(__file__), "greenLedOn.png"))
        self.greenLedOff = QPixmap(path.join(path.dirname(__file__), "greenLedOff.png"))
        self.redLedOn = QPixmap(path.join(path.dirname(__file__), "redLedOn.png"))
        self.redLedOff = QPixmap(path.join(path.dirname(__file__), "redLedOff.png"))
        self.pmac = Mock()
        self.commsThread = Mock()
        self.commsThread.CSNum = 1


class CSStatusTest(unittest.TestCase):
    @patch("PyQt5.QtWidgets.QLabel.setToolTip")
    @patch("PyQt5.QtWidgets.QLabel.setText")
    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    def setUp(self, mock_pixmap, mock_text, mock_tooltip):
        self.test_widget = DummyTestWidget()
        self.obj = CSStatusForm(self.test_widget)

    def test_inital_form(self):
        assert self.obj.ledGroup.title() == "CS Status"
        assert self.obj._feed == 100

    def test_change_cs(self):
        QTest.keyClick(self.obj.csSpin, Qt.Key_Up)
        assert self.obj.ledGroup.title() == ("CS %d" % self.obj.csSpin.value())

    def test_update_feed(self):
        self.obj.updateFeed(50)
        assert self.obj._feed == 50
        assert self.obj.feedSpin.value() == 50

    def test_set_feed(self):
        QTest.keyClick(self.obj.feedSpin, Qt.Key_Down)
        assert self.obj.feedSpin.value() == 99

    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    def test_update_status_all_off(self, mock_pixmap):
        self.obj.updateStatus(0)
        mock_pixmap.assert_called_with(self.test_widget.greenLedOff)
        assert mock_pixmap.call_count == len(self.obj.lstLeds)

    def tearDown(self):
        self.obj.close()


class PpmacCSStatusTest(unittest.TestCase):
    @patch("PyQt5.QtWidgets.QLabel.setToolTip")
    @patch("PyQt5.QtWidgets.QLabel.setText")
    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    def setUp(self, mock_pixmap, mock_text, mock_tooltip):
        self.test_widget = DummyTestWidget()
        self.obj = PpmacCSStatusForm(self.test_widget)

    def test_inital_form(self):
        assert self.obj.ledGroup.title() == "CS Status"
        assert self.obj._feed == 100

    def test_change_cs(self):
        QTest.keyClick(self.obj.csSpin, Qt.Key_Up)
        assert self.obj.ledGroup.title() == ("CS %d" % self.obj.csSpin.value())

    def test_update_feed(self):
        self.obj.updateFeed(50)
        assert self.obj._feed == 50
        assert self.obj.feedSpin.value() == 50

    def test_set_feed(self):
        QTest.keyClick(self.obj.feedSpin, Qt.Key_Down)
        assert self.obj.feedSpin.value() == 99

    @patch("PyQt5.QtWidgets.QLabel.setPixmap")
    def test_update_status_all_off(self, mock_pixmap):
        self.obj.updateStatus(0)
        mock_pixmap.assert_called_with(self.test_widget.greenLedOff)
        assert mock_pixmap.call_count == len(self.obj.lstLeds)

    def tearDown(self):
        self.obj.close()
