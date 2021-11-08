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
from axissettings import Axissettingsform, PpmacAxissettingsform
from optparse import OptionParser

app = QApplication(sys.argv)

class AxissettingsTest(unittest.TestCase):

    def test_change_axis_not_visible(self):
        obj = Axissettingsform()
        obj.changeAxis(2)
        assert obj.currentMotor == 2
        obj.close()

    def test_change_tab(self):
        obj = Axissettingsform()
        QTest.mouseClick(obj.tabAxisSetup, Qt.LeftButton)
        assert obj.tabAxisSetup.currentIndex() == 1
        obj.close()

class PpmacAxissettingsTest(unittest.TestCase):

    def test_change_axis_not_visible(self):
        obj = PpmacAxissettingsform()
        obj.changeAxis(2)
        assert obj.currentMotor == 2
        obj.close()

    def test_change_tab(self):
        obj = PpmacAxissettingsform()
        QTest.mouseClick(obj.tabAxisSetup, Qt.LeftButton)
        assert obj.tabAxisSetup.currentIndex() == 0
        obj.close()

    #def test_updateAxisSetupIVars(self):






