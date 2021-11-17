# -*- coding: utf-8 -*-

import re
import sys

from PyQt5.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QCheckBox, QDialog, QMessageBox

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
