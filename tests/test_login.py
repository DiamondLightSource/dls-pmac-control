import sys
import unittest

from mock import patch
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QWidget

from dls_pmaccontrol.login import Loginform

app = QApplication(sys.argv)
test_widget = QWidget()


class LoginTest(unittest.TestCase):
    def setUp(self):
        self.obj = Loginform(test_widget, "", "")

    def test_inital_form(self):
        self.assertEqual(self.obj.lneUsername.text(), "")
        self.assertEqual(self.obj.lnePassword.text(), "")
        self.assertTrue(self.obj.btnCancel.isEnabled())
        self.assertTrue(self.obj.btnOK.isEnabled())

    @patch("dls_pmaccontrol.login.Loginform.accept")
    def test_ok_clicked(self, mock_accept):
        self.obj.lneUsername.setText("username")
        self.obj.lnePassword.setText("password")
        QTest.mouseClick(self.obj.btnOK, Qt.LeftButton)
        self.assertEqual(self.obj.username, "username")
        self.assertEqual(self.obj.password, "password")
        self.assertEqual(self.obj.lneUsername.text(), "username")
        self.assertEqual(self.obj.lnePassword.text(), "password")
        assert mock_accept.called

    @patch("dls_pmaccontrol.login.Loginform.reject")
    def test_cancel_clicked(self, mock_reject):
        self.obj.lneUsername.setText("username")
        self.obj.lnePassword.setText("password")
        QTest.mouseClick(self.obj.btnCancel, Qt.LeftButton)
        self.assertEqual(self.obj.username, "")
        self.assertEqual(self.obj.password, "")
        self.assertEqual(self.obj.lneUsername.text(), "username")
        self.assertEqual(self.obj.lnePassword.text(), "password")
        assert mock_reject.called

    def tearDown(self):
        self.obj.close()
