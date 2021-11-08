import PyQt5
import unittest
from mock import patch
import time
import sys
sys.path.append('/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol')
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem
from motor import Controlform
from commsThread import CommsThread
from CSstatus import CSStatusForm, PpmacCSStatusForm
from optparse import OptionParser

app = QApplication(sys.argv)

class CSStatusTest(unittest.TestCase):

    def test_inital_form(self):
        obj = CSStatusForm(None)
        print(ob.parent)
        assert obj.ledGroup.title() == "CS 1"
        obj.close()

    def test_change_cs(self):
        obj = CSStatusForm(None)
        obj.changeCS(2)
        assert obj.parent().commsThread.CSNum == 2
        assert obj.ledGroup.title() == "CS 2"
        obj.close()

    #def test_update_status(self):


class PpmacCSStatusTest(unittest.TestCase):

    def test_inital_form(self):
        obj = PpmacCSStatusForm(None)
        assert obj.ledGroup.title() == "CS 1"
        obj.close()
