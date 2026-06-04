from PyQt6 import QtCore, QtWidgets


class UiFormPpmacCSStatus:
    def setup_ui(self, form_cs_status):
        form_cs_status.setObjectName("formCSStatus")
        form_cs_status.setGeometry(QtCore.QRect(0, 0, 433, 311))
        form_cs_status.setSizeGripEnabled(True)
        self.gridLayout_2 = QtWidgets.QGridLayout(form_cs_status)
        self.gridLayout_2.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_2.setSpacing(6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.ctrlGroup = QtWidgets.QGroupBox(form_cs_status)
        self.ctrlGroup.setObjectName("ctrlGroup")
        self.gridLayout = QtWidgets.QGridLayout(self.ctrlGroup)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.feedSpin = QtWidgets.QSpinBox(self.ctrlGroup)
        self.feedSpin.setMaximum(100)
        self.feedSpin.setProperty("value", 100)
        self.feedSpin.setObjectName("feedSpin")
        self.gridLayout.addWidget(self.feedSpin, 0, 3, 1, 1)
        self.textLabel1 = QtWidgets.QLabel(self.ctrlGroup)
        self.textLabel1.setWordWrap(False)
        self.textLabel1.setObjectName("textLabel1")
        self.gridLayout.addWidget(self.textLabel1, 0, 0, 1, 1)
        self.textLabel1_2 = QtWidgets.QLabel(self.ctrlGroup)
        self.textLabel1_2.setWordWrap(False)
        self.textLabel1_2.setObjectName("textLabel1_2")
        self.gridLayout.addWidget(self.textLabel1_2, 0, 2, 1, 1)
        self.csSpin = QtWidgets.QSpinBox(self.ctrlGroup)
        self.csSpin.setMinimum(1)
        self.csSpin.setMaximum(16)
        self.csSpin.setObjectName("csSpin")
        self.gridLayout.addWidget(self.csSpin, 0, 1, 1, 1)
        self.gridLayout_2.addWidget(self.ctrlGroup, 0, 0, 1, 1)
        self.ledGroup = QtWidgets.QGroupBox(form_cs_status)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.ledGroup.sizePolicy().hasHeightForWidth())
        self.ledGroup.setSizePolicy(size_policy)
        self.ledGroup.setObjectName("ledGroup")
        self.gridlayout = QtWidgets.QGridLayout(self.ledGroup)
        self.gridlayout.setContentsMargins(11, 11, 11, 11)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        self.gridLayout_2.addWidget(self.ledGroup, 1, 0, 1, 1)

        self.retranslate_ui(form_cs_status)
        QtCore.QMetaObject.connectSlotsByName(form_cs_status)

    def retranslate_ui(self, form_cs_status):
        _translate = QtCore.QCoreApplication.translate
        form_cs_status.setWindowTitle(_translate("formPpmacCSStatus", "Status bits"))
        self.ctrlGroup.setTitle(_translate("formPpmacCSStatus", "Co-ordinate System"))
        self.textLabel1.setText(_translate("formPpmacCSStatus", "CS Number:"))
        self.textLabel1_2.setText(_translate("formPpmacCSStatus", "Feed Rate:"))
        self.ledGroup.setTitle(_translate("formPpmacCSStatus", "CS Status"))
