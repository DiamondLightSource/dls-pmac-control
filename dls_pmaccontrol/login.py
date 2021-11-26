# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog

from dls_pmaccontrol.ui_formLogin import Ui_Login


class Loginform(QDialog, Ui_Login):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.parent = parent
        self.username = None
        self.password = None

    def clickedOK(self):
        self.username = self.lneUsername.text()
        self.password = self.lnePassword.text()
        self.lneUsername.setText("")
        self.lnePassword.setText("")
        self.accept()

    def clickedCancel(self):
        self.lneUsername.setText("")
        self.lnePassword.setText("")
        self.reject()
