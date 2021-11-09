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

    def test_inital_form(self):
        test_widget = TestWidget()
        obj = Statusform(test_widget,1)
        assert obj.ledGroup.title() == "Axis 1"
        obj.close()

    def test_change_axis(self):
        test_widget = TestWidget()
        obj = Statusform(test_widget,1)
        obj.changeAxis(5)
        assert obj.currentAxis == 5
        assert obj.ledGroup.title() == "Axis 5"
        obj.close()

    def test_update_status_all_off(self):
        test_widget = TestWidget()
        obj = Statusform(test_widget,1)
        obj.updateStatus(000000000000)
        obj.close()

    def test_update_status_all_on(self):
        test_widget = TestWidget()
        obj = Statusform(test_widget,1)
        obj.updateStatus(111111111111)
        obj.close()

class PpmacStatusTest(unittest.TestCase):

    def test_inital_form(self):
        test_widget = TestWidget()
        obj = PpmacStatusform(test_widget,1)
        assert obj.ledGroup.title() == "Axis 1"
        obj.close()

    def test_change_axis(self):
        test_widget = TestWidget()
        obj = PpmacStatusform(test_widget,1)
        obj.changeAxis(3)
        assert obj.currentAxis == 3
        assert obj.ledGroup.title() == "Axis 3"
        obj.close()

    def test_update_status_all_off(self):
        test_widget = TestWidget()
        obj = PpmacStatusform(test_widget,1)
        obj.updateStatus(0000000000000000)
        obj.close()

    def test_update_status_all_on(self):
        test_widget = TestWidget()
        obj = PpmacStatusform(test_widget,1)
        obj.updateStatus(1111111111111111)
        obj.close()
