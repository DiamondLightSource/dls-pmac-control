import PyQt5
import unittest
from mock import patch
import time
import sys
sys.path.append('/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol')
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem
from motor import Controlform, main
from login import Loginform
from optparse import OptionParser
from ui_formLogin import Ui_Login

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

class WatchesTest(unittest.TestCase):

    @patch("motor.Controlform")
    def test_inital_form(self, mock_control_form):
        obj = Loginform(Controlform(options))
        self.assertEqual(obj.lneUsername.text(),"")
        self.assertEqual(obj.lnePassword.text(),"")
        self.assertTrue(obj.btnCancel.isEnabled())
        self.assertTrue(obj.btnOK.isEnabled())
        obj.close()

    @patch("motor.Controlform")
    def test_ok_clicked(self, mock_control_form):
        obj = Loginform(Controlform(options))
        obj.lneUsername.setText("username")
        obj.lnePassword.setText("password")
        QTest.mouseClick(obj.btnOK, Qt.LeftButton)
        self.assertEqual(obj.username, "username")
        self.assertEqual(obj.password, "password")
        self.assertEqual(obj.lneUsername.text(),"")
        self.assertEqual(obj.lnePassword.text(),"")

    @patch("motor.Controlform")
    def test_cancel_clicked(self, mock_control_form):
        obj = Loginform(Controlform(options))
        obj.lneUsername.setText("username")
        obj.lnePassword.setText("password")
        QTest.mouseClick(obj.btnCancel, Qt.LeftButton)
        self.assertEqual(obj.username, None)
        self.assertEqual(obj.password, None)
        self.assertEqual(obj.lneUsername.text(),"")
        self.assertEqual(obj.lnePassword.text(),"")

