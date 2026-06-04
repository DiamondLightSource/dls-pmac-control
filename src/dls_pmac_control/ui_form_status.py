from PyQt6 import QtCore, QtWidgets


class UiFormStatus:
    def setup_ui(self, form_status):
        form_status.setObjectName("formStatus")
        form_status.resize(99, 189)
        self.gridlayout = QtWidgets.QGridLayout(form_status)
        self.gridlayout.setContentsMargins(11, 11, 11, 11)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        self.ledGroup = QtWidgets.QGroupBox(form_status)
        self.ledGroup.setObjectName("ledGroup")
        self.gridlayout1 = QtWidgets.QGridLayout(self.ledGroup)
        self.gridlayout1.setContentsMargins(11, 11, 11, 11)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")
        self.gridlayout.addWidget(self.ledGroup, 0, 0, 1, 2)

        self.retranslate_ui(form_status)
        QtCore.QMetaObject.connectSlotsByName(form_status)

    def retranslate_ui(self, form_status):
        _translate = QtCore.QCoreApplication.translate
        form_status.setWindowTitle(_translate("formStatus", "Status bits"))
        self.ledGroup.setTitle(_translate("formStatus", "Axis"))
