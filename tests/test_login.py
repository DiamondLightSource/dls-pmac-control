import PyQt5
import unittest
from mock import patch
import time
import sys
sys.path.append('/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol')
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem
from login import Loginform

app = QApplication(sys.argv)
test_widget = QWidget()

class LoginTest(unittest.TestCase):

    def test_inital_form(self):
        obj = Loginform(test_widget)
        self.assertEqual(obj.lneUsername.text(),"")
        self.assertEqual(obj.lnePassword.text(),"")
        self.assertTrue(obj.btnCancel.isEnabled())
        self.assertTrue(obj.btnOK.isEnabled())
        obj.close()

    def test_ok_clicked(self):
        obj = Loginform(test_widget)
        obj.lneUsername.setText("username")
        obj.lnePassword.setText("password")
        QTest.mouseClick(obj.btnOK, Qt.LeftButton)
        self.assertEqual(obj.username, "username")
        self.assertEqual(obj.password, "password")
        self.assertEqual(obj.lneUsername.text(),"")
        self.assertEqual(obj.lnePassword.text(),"")

    def test_cancel_clicked(self):
        obj = Loginform(test_widget)
        obj.lneUsername.setText("username")
        obj.lnePassword.setText("password")
        QTest.mouseClick(obj.btnCancel, Qt.LeftButton)
        self.assertEqual(obj.username, None)
        self.assertEqual(obj.password, None)
        self.assertEqual(obj.lneUsername.text(),"")
        self.assertEqual(obj.lnePassword.text(),"")

