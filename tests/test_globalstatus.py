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
from GlobalStatus import GlobalStatusForm, PpmacGlobalStatusForm
from optparse import OptionParser

app = QApplication(sys.argv)


class GlobalStatusTest(unittest.TestCase):

    def test_inital_form(self):
        obj = GlobalStatusForm(None)
        obj.close()

    def test_update_status(self):
        obj = GlobalStatusForm(None)
        obj.updateStatus(000000000000)
        obj.close()

    def test_ppmac_inital_form(self):
        obj = PpmacGlobalStatusForm(None)
        obj.close()

    def test_ppmac_update_status(self):
        obj = PpmacGlobalStatusForm(None)
        obj.updateStatus(0000000000000000)
        obj.close()
