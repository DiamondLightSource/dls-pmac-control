from PyQt6.QtWidgets import QDialog

from dls_pmac_control.ui_formLogin import UiLogin


class Loginform(QDialog, UiLogin):
    def __init__(self, parent, username, password):
        QDialog.__init__(self, parent)
        self.setup_ui(self)
        self.parent = parent
        self.username = username
        self.password = password
        self.lneUsername.setText(self.username)
        self.lnePassword.setText(self.password)

    def clicked_ok(self):
        self.username = self.lneUsername.text()
        self.password = self.lnePassword.text()
        self.accept()

    def clicked_cancel(self):
        self.reject()
