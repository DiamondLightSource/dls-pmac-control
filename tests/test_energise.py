import PyQt5
import unittest
from mock import patch, Mock, call
import time
import sys
sys.path.append('/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol')
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem, QCheckBox
from energise import Energiseform

app = QApplication(sys.argv)

class TestWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.pmac = Mock()
        self.commsThread = Mock()
        self.chkShowAll = QCheckBox(self)
        attrs = {"sendCommand.return_value" : ("0\r5",True)}
        self.pmac.configure_mock(**attrs)

class EnergiseTest(unittest.TestCase):

    @patch("energise.Energiseform.updateScreen")
    @patch("energise.Energiseform.readM750x")
    @patch("energise.Energiseform.createCheckBoxes")
    def setUp(self, mock_boxes, mock_read, mock_update):
        mock_read.return_value = (0,0)
        self.test_widget = TestWidget()
        self.obj = Energiseform(self.test_widget.pmac, self.test_widget)

    def test_initial_form(self):
        assert self.obj.pmac == self.test_widget.pmac
        assert self.obj.parent == self.test_widget
        assert self.obj.lstCheckBoxes == None

    def test_readM750x(self):
        (val1, val2) = self.obj.readM750x()
        assert val1 == 0
        assert val2 == 5

    def test_update_screen(self):
        self.obj.createCheckBoxes()
        self.obj.val7501 = 1
        self.obj.val7503 = 3
        self.obj.updateScreen()

    @patch("energise.Energiseform.readM750x")
    def test_isScreenUpToDate(self, mock_read):
        mock_read.return_value = (0x00FFFF,0x00FFFF)
        self.obj.val7501 = 0x00FFFF
        self.obj.val7503 = 0x00FFFF
        assert self.obj.isScreenUpToDate() == True

    @patch("energise.Energiseform.updateScreen")
    @patch("energise.Energiseform.readM750x")
    @patch("PyQt5.QtWidgets.QMessageBox.information")
    @patch("energise.Energiseform.isScreenUpToDate")
    def test_sendCommand_outofdate(self, mock_screen, 
                mock_box, mock_read, mock_update):
        mock_screen.return_value = False
        mock_read.return_value = (None,None)
        self.obj.sendCommand()
        assert mock_screen.called
        assert mock_box.called
        assert mock_read.called
        assert mock_screen.called

    @patch("energise.Energiseform.isScreenUpToDate")
    def test_sendCommand_uptodate(self, mock_screen):
        mock_screen.return_value = True
        self.obj.val7501 = 0xFF0000
        self.obj.val7503 = 0xFF0000
        self.obj.createCheckBoxes()
        self.obj.sendCommand()
        assert mock_screen.called










