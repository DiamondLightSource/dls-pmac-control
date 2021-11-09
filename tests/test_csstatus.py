import PyQt5
import unittest
from mock import patch, Mock
import time
from os import path
import sys
sys.path.append('/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol')
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem
from PyQt5.QtGui import QPixmap
from CSstatus import CSStatusForm, PpmacCSStatusForm

app = QApplication(sys.argv)

class TestWidget(QMainWindow):
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

    def test_inital_form(self):
        test_widget = TestWidget()
        obj = CSStatusForm(test_widget)
        assert obj.ledGroup.title() == "CS Status"
        assert obj._feed == 100
        obj.close()

    def test_change_cs(self):
        test_widget = TestWidget()
        obj = CSStatusForm(test_widget)
        QTest.keyClick(obj.csSpin, Qt.Key_Up)
        assert obj.ledGroup.title() == ("CS %d" % obj.csSpin.value())
        obj.close()

    def test_update_feed(self):
        test_widget = TestWidget()
        obj = CSStatusForm(test_widget)
        obj.updateFeed(50)
        assert obj._feed == 50
        obj.close()

    def test_set_feed(self):
        test_widget = TestWidget()
        obj = CSStatusForm(test_widget)
        QTest.keyClick(obj.feedSpin, Qt.Key_Down)
        assert obj.feedSpin.value() == 99
        obj.close()

    def test_update_status(self):
        test_widget = TestWidget()
        obj = CSStatusForm(test_widget)
        #obj.updateStatus()
        #assert
        obj.close()

class PpmacCSStatusTest(unittest.TestCase):

    def test_inital_form(self):
        test_widget = TestWidget()
        obj = PpmacCSStatusForm(test_widget)
        assert obj.ledGroup.title() == "CS Status"
        assert obj._feed == 100
        obj.close()

    def test_change_cs(self):
        test_widget = TestWidget()
        obj = PpmacCSStatusForm(test_widget)
        QTest.keyClick(obj.csSpin, Qt.Key_Up)
        assert obj.ledGroup.title() == ("CS %d" % obj.csSpin.value())
        obj.close()

    def test_update_feed(self):
        test_widget = TestWidget()
        obj = PpmacCSStatusForm(test_widget)
        obj.updateFeed(50)
        assert obj._feed == 50
        obj.close()

    def test_set_feed(self):
        test_widget = TestWidget()
        obj = PpmacCSStatusForm(test_widget)
        QTest.keyClick(obj.feedSpin, Qt.Key_Down)
        assert obj.feedSpin.value() == 99
        obj.close()

    def test_update_status(self):
        test_widget = TestWidget()
        obj = PpmacCSStatusForm(test_widget)
        #obj.updateStatus()
        #assert
        obj.close()
