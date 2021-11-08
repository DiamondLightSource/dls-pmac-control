import PyQt5
import unittest
from mock import patch
import time
import sys
sys.path.append('/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol')
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem
#from motor import Controlform
#from commsThread import CommsThread
from status import Statusform, PpmacStatusform
from optparse import OptionParser

app = QApplication(sys.argv)


class StatusTest(unittest.TestCase):

    def test_inital_form(self):
        obj = Statusform(None,1)
        assert obj.ledGroup.title() == "Axis 1"
        obj.close()

    def test_change_axis(self):
        obj = Statusform(None,1)
        obj.changeAxis(5)
        assert obj.currentAxis == 5
        assert obj.ledGroup.title() == "Axis 5"
        obj.close()

    '''def test_update_status(self):
        obj = Statusform(None,1)
        obj.updateStatus(000000000000)
        obj.close()'''


class PpmacStatusTest(unittest.TestCase):

    def test_inital_form(self):
        obj = PpmacStatusform(None,1)
        assert obj.ledGroup.title() == "Axis 1"
        obj.close()

    def test_change_axis(self):
        obj = PpmacStatusform(None,1)
        obj.changeAxis(3)
        assert obj.currentAxis == 3
        assert obj.ledGroup.title() == "Axis 3"
        obj.close()

    '''def test_update_status(self):
        obj = PpmacStatusform(None,1)
        obj.updateStatus(0000000000000000)
        obj.close()'''






