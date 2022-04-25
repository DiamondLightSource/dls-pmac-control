# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog

from dls_pmaccontrol.ui_formLogin import Ui_Login


class Loginform(QDialog, Ui_Login):
    def __init__(self, parent, username, password):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.parent = parent
        self.username = username
        self.password = password
        self.lneUsername.setText(self.username)
        self.lnePassword.setText(self.password)

    def clickedOK(self):
        self.username = self.lneUsername.text()
        self.password = self.lnePassword.text()
        self.accept()

    def clickedCancel(self):
        self.reject()
