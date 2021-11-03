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

usage = """usage: %prog [options]
%prog is a graphical frontend to the Deltatau motorcontroller known as PMAC."""
parser = OptionParser(usage)
parser.add_option(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        help="Print more details (than necessary in most " "cases...)",
    )
parser.add_option(
        "-o",
        "--protocol",
        action="store",
        dest="protocol",
        default="ts",
        help='Set the connection protocol; use "ts" for '
        "serial via terminal server (the default), "
        'or "tcpip" for network TCP/IP connection.',
    )
parser.add_option(
        "-s",
        "--server",
        action="store",
        dest="server",
        default="blxxi-nt-tserv-01",
        help="Set server name (default: blxxi-nt-tserv-01)",
    )
parser.add_option(
        "-p",
        "--port",
        action="store",
        dest="port",
        default="7017",
        help="Set IP port number to connect to (default: 7017)",
    )
parser.add_option(
        "-a",
        "--axis",
        action="store",
        dest="defaultAxis",
        default=1,
        help="Set an axis as a default selected axis when "
        "starting up the application (default: 1)",
    )
parser.add_option(
        "-n",
        "--naxes",
        action="store",
        dest="nAxes",
        help="Display and poll NAXES axes. Default is 32 for a "
        "PMAC, 8 for a geoBrick",
    )
parser.add_option(
        "-t",
        "--timeout",
        action="store",
        type="float",
        dest="timeout",
        default=3.0,
        help="Set the communication timeout (default: 3 seconds, " "minimum: 1 second)",
    )
(options, args) = parser.parse_args()

class AxissettingsTest(unittest.TestCase):

    @patch("motor.Controlform")
    def test_inital_form(self, mock_control_form):
        obj = Axissettingsform(Controlform(options))
        obj.close()


    @patch("motor.Controlform")
    def test_change_axis_not_visible(self, mock_control_form):
        obj = Axissettingsform(Controlform(options))
        obj.changeAxis(2)
        assert obj.currentMotor == 2
        obj.close()


    '''@patch("motor.Controlform.pmac.getAxisMsIVars")
    @patch("motor.Controlform.pmac.getAxisSetupIvars")
    @patch("motor.Controlform")
    def test_change_tab(self, mock_control_form, mock_get_ivars, mock_get_ms_ivars):
        mock_get_ivars.return_value = [0,0,0,0,0,0,0,0]
        mock_get_ms_ivars.return_value = (0, 0, 0, 0)
        obj = Axissettingsform(Controlform(options))
        obj.parent = mock_control_form.return_value
        #obj.tabChange()
        print(obj.tabAxisSetup)
        print(obj.tabAxisSetup[1])

        QTest.mouseClick(obj.tabAxisSetup, Qt.LeftButton)
        obj.close()'''













