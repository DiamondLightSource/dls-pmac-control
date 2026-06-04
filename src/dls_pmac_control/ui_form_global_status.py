from PyQt6 import QtCore, QtWidgets


class UiFormGlobalStatus:
    def setup_ui(self, form_global_status):
        form_global_status.setObjectName("formGlobalStatus")
        form_global_status.resize(122, 144)
        self.gridlayout = QtWidgets.QGridLayout(form_global_status)
        self.gridlayout.setContentsMargins(11, 11, 11, 11)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        self.ledGroup = QtWidgets.QGroupBox(form_global_status)
        self.ledGroup.setObjectName("ledGroup")
        self.gridlayout1 = QtWidgets.QGridLayout(self.ledGroup)
        self.gridlayout1.setContentsMargins(11, 11, 11, 11)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")
        self.gridlayout.addWidget(self.ledGroup, 0, 0, 1, 2)

        self.retranslate_ui(form_global_status)
        QtCore.QMetaObject.connectSlotsByName(form_global_status)

    def retranslate_ui(self, form_global_status):
        _translate = QtCore.QCoreApplication.translate
        form_global_status.setWindowTitle(_translate("formGlobalStatus", "Status bits"))
        self.ledGroup.setTitle(_translate("formGlobalStatus", "Global Status"))
