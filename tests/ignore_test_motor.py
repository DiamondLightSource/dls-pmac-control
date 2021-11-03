import PyQt5
import unittest
from mock import patch
import signal
import sys
sys.path.append('/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol')
import motor
from motor import Controlform
from ui_formControl import Ui_ControlForm
import paramiko
import socket
import serial
from optparse import OptionParser
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow


class TestRemoteConnect(unittest.TestCase):

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

    @patch("signal.signal")
    def test_terminal_connect(self, mock_signal):
        obj = Controlform(self.options) # signal handler
        obj.ConnectionType = 0
        print(obj.pmac)

    """def test_ethernet_connect(self):
        obj = Controlform(self.options)
        obj.ConnectionType = 1
        print(obj.pmac)

    def test_serial_connect(self):
        obj = Controlform(self.options)
        obj.ConnectionType = 2
        print(obj.pmac)

    def test_ssh_connect(self):
        obj = Controlform(self.options)
        obj.ConnectionType = 3
        print(obj.pmac)"""
