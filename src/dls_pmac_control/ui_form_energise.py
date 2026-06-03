from PyQt6 import QtCore, QtWidgets


class UiFormEnergise:
    def setup_ui(self, form_energise):
        form_energise.setObjectName("formEnergise")
        form_energise.resize(192, 252)
        self.gridlayout = QtWidgets.QGridLayout(form_energise)
        self.gridlayout.setContentsMargins(11, 11, 11, 11)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        self.btnSend = QtWidgets.QPushButton(form_energise)
        self.btnSend.setObjectName("btnSend")
        self.gridlayout.addWidget(self.btnSend, 1, 0, 1, 1)
        self.btnClose = QtWidgets.QPushButton(form_energise)
        self.btnClose.setObjectName("btnClose")
        self.gridlayout.addWidget(self.btnClose, 1, 1, 1, 1)
        self.chkGroup = QtWidgets.QGroupBox(form_energise)
        self.chkGroup.setObjectName("chkGroup")
        self.gridlayout1 = QtWidgets.QGridLayout(self.chkGroup)
        self.gridlayout1.setContentsMargins(11, 11, 11, 11)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")
        self.gridlayout.addWidget(self.chkGroup, 0, 0, 1, 2)

        self.retranslate_ui(form_energise)
        self.btnClose.clicked.connect(form_energise.close)
        self.btnSend.clicked.connect(form_energise.send_command)
        QtCore.QMetaObject.connectSlotsByName(form_energise)

    def retranslate_ui(self, form_energise):
        _translate = QtCore.QCoreApplication.translate
        form_energise.setWindowTitle(_translate("formEnergise", "Energise axis"))
        self.btnSend.setText(_translate("formEnergise", "send"))
        self.btnClose.setText(_translate("formEnergise", "close"))
        self.chkGroup.setTitle(_translate("formEnergise", "Axis"))
