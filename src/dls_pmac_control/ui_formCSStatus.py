# Form implementation generated from reading ui file 'src/dls_pmac_control/formCSStatus.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets


class Ui_formCSStatus:
    def setupUi(self, formCSStatus):
        formCSStatus.setObjectName("formCSStatus")
        formCSStatus.resize(433, 311)
        formCSStatus.setSizeGripEnabled(True)
        self.gridLayout_2 = QtWidgets.QGridLayout(formCSStatus)
        self.gridLayout_2.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_2.setSpacing(6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.ctrlGroup = QtWidgets.QGroupBox(formCSStatus)
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
        self.ledGroup = QtWidgets.QGroupBox(formCSStatus)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ledGroup.sizePolicy().hasHeightForWidth())
        self.ledGroup.setSizePolicy(sizePolicy)
        self.ledGroup.setObjectName("ledGroup")
        self.gridlayout = QtWidgets.QGridLayout(self.ledGroup)
        self.gridlayout.setContentsMargins(11, 11, 11, 11)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        self.gridLayout_2.addWidget(self.ledGroup, 1, 0, 1, 1)

        self.retranslateUi(formCSStatus)
        QtCore.QMetaObject.connectSlotsByName(formCSStatus)

    def retranslateUi(self, formCSStatus):
        _translate = QtCore.QCoreApplication.translate
        formCSStatus.setWindowTitle(_translate("formCSStatus", "Status bits"))
        self.ctrlGroup.setTitle(_translate("formCSStatus", "Co-ordinate System"))
        self.textLabel1.setText(_translate("formCSStatus", "CS Number:"))
        self.textLabel1_2.setText(_translate("formCSStatus", "Feed Rate:"))
        self.ledGroup.setTitle(_translate("formCSStatus", "CS Status"))
