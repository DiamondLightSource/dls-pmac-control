# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dls_pmac_control/formPpmacAxisSettings.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_formPpmacAxisSettings(object):
    def setupUi(self, formPpmacAxisSettings):
        formPpmacAxisSettings.setObjectName("formPpmacAxisSettings")
        formPpmacAxisSettings.resize(580, 688)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(formPpmacAxisSettings.sizePolicy().hasHeightForWidth())
        formPpmacAxisSettings.setSizePolicy(sizePolicy)
        formPpmacAxisSettings.setMaximumSize(QtCore.QSize(1024, 768))
        self.gridLayout_3 = QtWidgets.QGridLayout(formPpmacAxisSettings)
        self.gridLayout_3.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_3.setSpacing(6)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.btnUpdate = QtWidgets.QPushButton(formPpmacAxisSettings)
        self.btnUpdate.setObjectName("btnUpdate")
        self.gridLayout_3.addWidget(self.btnUpdate, 2, 0, 1, 1)
        self.textLabel1 = QtWidgets.QLabel(formPpmacAxisSettings)
        self.textLabel1.setWordWrap(False)
        self.textLabel1.setObjectName("textLabel1")
        self.gridLayout_3.addWidget(self.textLabel1, 0, 0, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(185, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 2, 1, 1, 1)
        self.btnClose = QtWidgets.QPushButton(formPpmacAxisSettings)
        self.btnClose.setObjectName("btnClose")
        self.gridLayout_3.addWidget(self.btnClose, 2, 2, 1, 1)
        self.tabAxisSetup = QtWidgets.QTabWidget(formPpmacAxisSettings)
        self.tabAxisSetup.setEnabled(True)
        self.tabAxisSetup.setObjectName("tabAxisSetup")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_2.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_2.setSpacing(6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox2 = QtWidgets.QGroupBox(self.tab)
        self.groupBox2.setObjectName("groupBox2")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox2)
        self.formLayout.setContentsMargins(11, 11, 11, 11)
        self.formLayout.setSpacing(6)
        self.formLayout.setObjectName("formLayout")
        self.textLabel2_9 = QtWidgets.QLabel(self.groupBox2)
        self.textLabel2_9.setWordWrap(False)
        self.textLabel2_9.setObjectName("textLabel2_9")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.textLabel2_9)
        self.textLabel2_2_2 = QtWidgets.QLabel(self.groupBox2)
        self.textLabel2_2_2.setWordWrap(False)
        self.textLabel2_2_2.setObjectName("textLabel2_2_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.textLabel2_2_2)
        self.textLabel2_3_2 = QtWidgets.QLabel(self.groupBox2)
        self.textLabel2_3_2.setWordWrap(False)
        self.textLabel2_3_2.setObjectName("textLabel2_3_2")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.textLabel2_3_2)
        self.textLabel2_4_2 = QtWidgets.QLabel(self.groupBox2)
        self.textLabel2_4_2.setWordWrap(False)
        self.textLabel2_4_2.setObjectName("textLabel2_4_2")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.textLabel2_4_2)
        self.textLabel2_6_2 = QtWidgets.QLabel(self.groupBox2)
        self.textLabel2_6_2.setWordWrap(False)
        self.textLabel2_6_2.setObjectName("textLabel2_6_2")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole, self.textLabel2_6_2)
        self.textLabel2_7_2 = QtWidgets.QLabel(self.groupBox2)
        self.textLabel2_7_2.setWordWrap(False)
        self.textLabel2_7_2.setObjectName("textLabel2_7_2")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.LabelRole, self.textLabel2_7_2)
        self.lneIx20 = QtWidgets.QLineEdit(self.groupBox2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lneIx20.sizePolicy().hasHeightForWidth())
        self.lneIx20.setSizePolicy(sizePolicy)
        self.lneIx20.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx20.setMaximumSize(QtCore.QSize(32222, 32767))
        self.lneIx20.setObjectName("lneIx20")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.lneIx20)
        self.lneIx21 = QtWidgets.QLineEdit(self.groupBox2)
        self.lneIx21.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx21.setMaximumSize(QtCore.QSize(32222, 32767))
        self.lneIx21.setObjectName("lneIx21")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.SpanningRole, self.lneIx21)
        self.lneIx22 = QtWidgets.QLineEdit(self.groupBox2)
        self.lneIx22.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx22.setMaximumSize(QtCore.QSize(32222, 32767))
        self.lneIx22.setObjectName("lneIx22")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.SpanningRole, self.lneIx22)
        self.lneIx23 = QtWidgets.QLineEdit(self.groupBox2)
        self.lneIx23.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx23.setMaximumSize(QtCore.QSize(32222, 32767))
        self.lneIx23.setObjectName("lneIx23")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.SpanningRole, self.lneIx23)
        self.lneIx25 = QtWidgets.QLineEdit(self.groupBox2)
        self.lneIx25.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx25.setMaximumSize(QtCore.QSize(32222, 32767))
        self.lneIx25.setObjectName("lneIx25")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.SpanningRole, self.lneIx25)
        self.lneIx26 = QtWidgets.QLineEdit(self.groupBox2)
        self.lneIx26.setMinimumSize(QtCore.QSize(0, 0))
        self.lneIx26.setMaximumSize(QtCore.QSize(32222, 32767))
        self.lneIx26.setObjectName("lneIx26")
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.SpanningRole, self.lneIx26)
        self.gridLayout_2.addWidget(self.groupBox2, 0, 1, 1, 1)
        self.groupBox1 = QtWidgets.QGroupBox(self.tab)
        self.groupBox1.setObjectName("groupBox1")
        self.formLayout_2 = QtWidgets.QFormLayout(self.groupBox1)
        self.formLayout_2.setContentsMargins(11, 11, 11, 11)
        self.formLayout_2.setSpacing(6)
        self.formLayout_2.setObjectName("formLayout_2")
        self.lneIx15 = QtWidgets.QLineEdit(self.groupBox1)
        self.lneIx15.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx15.setMaximumSize(QtCore.QSize(31222, 32767))
        self.lneIx15.setObjectName("lneIx15")
        self.formLayout_2.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.lneIx15)
        self.textLabel2 = QtWidgets.QLabel(self.groupBox1)
        self.textLabel2.setWordWrap(False)
        self.textLabel2.setObjectName("textLabel2")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.textLabel2)
        self.lneIx11 = QtWidgets.QLineEdit(self.groupBox1)
        self.lneIx11.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx11.setMaximumSize(QtCore.QSize(31222, 32767))
        self.lneIx11.setObjectName("lneIx11")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lneIx11)
        self.lneIx12 = QtWidgets.QLineEdit(self.groupBox1)
        self.lneIx12.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx12.setMaximumSize(QtCore.QSize(31222, 32767))
        self.lneIx12.setObjectName("lneIx12")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lneIx12)
        self.lneIx13 = QtWidgets.QLineEdit(self.groupBox1)
        self.lneIx13.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx13.setMaximumSize(QtCore.QSize(31222, 32767))
        self.lneIx13.setObjectName("lneIx13")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.lneIx13)
        self.textLabel2_2 = QtWidgets.QLabel(self.groupBox1)
        self.textLabel2_2.setWordWrap(False)
        self.textLabel2_2.setObjectName("textLabel2_2")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.textLabel2_2)
        self.textLabel2_3 = QtWidgets.QLabel(self.groupBox1)
        self.textLabel2_3.setWordWrap(False)
        self.textLabel2_3.setObjectName("textLabel2_3")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.textLabel2_3)
        self.textLabel2_4 = QtWidgets.QLabel(self.groupBox1)
        self.textLabel2_4.setWordWrap(False)
        self.textLabel2_4.setObjectName("textLabel2_4")
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.textLabel2_4)
        self.lneIx14 = QtWidgets.QLineEdit(self.groupBox1)
        self.lneIx14.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx14.setMaximumSize(QtCore.QSize(31222, 32767))
        self.lneIx14.setObjectName("lneIx14")
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.lneIx14)
        self.textLabel2_5 = QtWidgets.QLabel(self.groupBox1)
        self.textLabel2_5.setWordWrap(False)
        self.textLabel2_5.setObjectName("textLabel2_5")
        self.formLayout_2.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.textLabel2_5)
        self.textLabel2_6 = QtWidgets.QLabel(self.groupBox1)
        self.textLabel2_6.setWordWrap(False)
        self.textLabel2_6.setObjectName("textLabel2_6")
        self.formLayout_2.setWidget(8, QtWidgets.QFormLayout.LabelRole, self.textLabel2_6)
        self.lneIx16 = QtWidgets.QLineEdit(self.groupBox1)
        self.lneIx16.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx16.setMaximumSize(QtCore.QSize(31222, 32767))
        self.lneIx16.setObjectName("lneIx16")
        self.formLayout_2.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.lneIx16)
        self.textLabel2_7 = QtWidgets.QLabel(self.groupBox1)
        self.textLabel2_7.setWordWrap(False)
        self.textLabel2_7.setObjectName("textLabel2_7")
        self.formLayout_2.setWidget(9, QtWidgets.QFormLayout.LabelRole, self.textLabel2_7)
        self.lneIx17 = QtWidgets.QLineEdit(self.groupBox1)
        self.lneIx17.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx17.setMaximumSize(QtCore.QSize(31222, 32767))
        self.lneIx17.setObjectName("lneIx17")
        self.formLayout_2.setWidget(9, QtWidgets.QFormLayout.FieldRole, self.lneIx17)
        self.textLabel2_8 = QtWidgets.QLabel(self.groupBox1)
        self.textLabel2_8.setWordWrap(False)
        self.textLabel2_8.setObjectName("textLabel2_8")
        self.formLayout_2.setWidget(10, QtWidgets.QFormLayout.LabelRole, self.textLabel2_8)
        self.lneIx19 = QtWidgets.QLineEdit(self.groupBox1)
        self.lneIx19.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx19.setMaximumSize(QtCore.QSize(31222, 32767))
        self.lneIx19.setObjectName("lneIx19")
        self.formLayout_2.setWidget(10, QtWidgets.QFormLayout.FieldRole, self.lneIx19)
        self.gridLayout_2.addWidget(self.groupBox1, 0, 0, 1, 1)
        self.tabAxisSetup.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.groupBox1_2 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox1_2.setGeometry(QtCore.QRect(10, 20, 271, 330))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox1_2.sizePolicy().hasHeightForWidth())
        self.groupBox1_2.setSizePolicy(sizePolicy)
        self.groupBox1_2.setObjectName("groupBox1_2")
        self.formLayout_3 = QtWidgets.QFormLayout(self.groupBox1_2)
        self.formLayout_3.setContentsMargins(11, 11, 11, 11)
        self.formLayout_3.setSpacing(6)
        self.formLayout_3.setObjectName("formLayout_3")
        self.textLabel2_10 = QtWidgets.QLabel(self.groupBox1_2)
        self.textLabel2_10.setWordWrap(False)
        self.textLabel2_10.setObjectName("textLabel2_10")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.textLabel2_10)
        self.lneIx30 = QtWidgets.QLineEdit(self.groupBox1_2)
        self.lneIx30.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx30.setMaximumSize(QtCore.QSize(32233, 32767))
        self.lneIx30.setObjectName("lneIx30")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lneIx30)
        self.textLabel2_2_3 = QtWidgets.QLabel(self.groupBox1_2)
        self.textLabel2_2_3.setWordWrap(False)
        self.textLabel2_2_3.setObjectName("textLabel2_2_3")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.textLabel2_2_3)
        self.lneIx31 = QtWidgets.QLineEdit(self.groupBox1_2)
        self.lneIx31.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx31.setMaximumSize(QtCore.QSize(32233, 32767))
        self.lneIx31.setObjectName("lneIx31")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lneIx31)
        self.textLabel2_3_3 = QtWidgets.QLabel(self.groupBox1_2)
        self.textLabel2_3_3.setWordWrap(False)
        self.textLabel2_3_3.setObjectName("textLabel2_3_3")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.textLabel2_3_3)
        self.lneDerivative2 = QtWidgets.QLineEdit(self.groupBox1_2)
        self.lneDerivative2.setMinimumSize(QtCore.QSize(60, 0))
        self.lneDerivative2.setMaximumSize(QtCore.QSize(32233, 32767))
        self.lneDerivative2.setObjectName("lneDerivative2")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lneDerivative2)
        self.textLabel2_4_3 = QtWidgets.QLabel(self.groupBox1_2)
        self.textLabel2_4_3.setWordWrap(False)
        self.textLabel2_4_3.setObjectName("textLabel2_4_3")
        self.formLayout_3.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.textLabel2_4_3)
        self.lneIx33 = QtWidgets.QLineEdit(self.groupBox1_2)
        self.lneIx33.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx33.setMaximumSize(QtCore.QSize(32233, 32767))
        self.lneIx33.setObjectName("lneIx33")
        self.formLayout_3.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.lneIx33)
        self.textLabel2_5_3 = QtWidgets.QLabel(self.groupBox1_2)
        self.textLabel2_5_3.setWordWrap(False)
        self.textLabel2_5_3.setObjectName("textLabel2_5_3")
        self.formLayout_3.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.textLabel2_5_3)
        self.lneIx32 = QtWidgets.QLineEdit(self.groupBox1_2)
        self.lneIx32.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx32.setMaximumSize(QtCore.QSize(32233, 32767))
        self.lneIx32.setObjectName("lneIx32")
        self.formLayout_3.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.lneIx32)
        self.textLabel2_10_2 = QtWidgets.QLabel(self.groupBox1_2)
        self.textLabel2_10_2.setWordWrap(False)
        self.textLabel2_10_2.setObjectName("textLabel2_10_2")
        self.formLayout_3.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.textLabel2_10_2)
        self.lneVFF2 = QtWidgets.QLineEdit(self.groupBox1_2)
        self.lneVFF2.setMinimumSize(QtCore.QSize(60, 0))
        self.lneVFF2.setMaximumSize(QtCore.QSize(32233, 32767))
        self.lneVFF2.setObjectName("lneVFF2")
        self.formLayout_3.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.lneVFF2)
        self.textLabel2_10_2_2 = QtWidgets.QLabel(self.groupBox1_2)
        self.textLabel2_10_2_2.setWordWrap(False)
        self.textLabel2_10_2_2.setObjectName("textLabel2_10_2_2")
        self.formLayout_3.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.textLabel2_10_2_2)
        self.lneIx35 = QtWidgets.QLineEdit(self.groupBox1_2)
        self.lneIx35.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx35.setMaximumSize(QtCore.QSize(32233, 32767))
        self.lneIx35.setObjectName("lneIx35")
        self.formLayout_3.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.lneIx35)
        self.groupBox1_2_2 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox1_2_2.setGeometry(QtCore.QRect(290, 20, 260, 81))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox1_2_2.sizePolicy().hasHeightForWidth())
        self.groupBox1_2_2.setSizePolicy(sizePolicy)
        self.groupBox1_2_2.setObjectName("groupBox1_2_2")
        self.formLayout_4 = QtWidgets.QFormLayout(self.groupBox1_2_2)
        self.formLayout_4.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_4.setContentsMargins(11, 11, 11, 11)
        self.formLayout_4.setSpacing(6)
        self.formLayout_4.setObjectName("formLayout_4")
        self.lLoopSelect = QtWidgets.QLabel(self.groupBox1_2_2)
        self.lLoopSelect.setWordWrap(False)
        self.lLoopSelect.setObjectName("lLoopSelect")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.lLoopSelect)
        self.lneIx34 = QtWidgets.QLineEdit(self.groupBox1_2_2)
        self.lneIx34.setMinimumSize(QtCore.QSize(60, 0))
        self.lneIx34.setMaximumSize(QtCore.QSize(32222, 32767))
        self.lneIx34.setObjectName("lneIx34")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lneIx34)
        spacerItem1 = QtWidgets.QSpacerItem(30, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout_4.setItem(2, QtWidgets.QFormLayout.SpanningRole, spacerItem1)
        self.tabAxisSetup.addTab(self.tab_2, "")
        self.gridLayout_3.addWidget(self.tabAxisSetup, 1, 0, 1, 3)

        self.retranslateUi(formPpmacAxisSettings)
        self.tabAxisSetup.setCurrentIndex(0)
        self.btnUpdate.clicked.connect(formPpmacAxisSettings.axisUpdate)
        self.btnClose.clicked.connect(formPpmacAxisSettings.close)
        self.lneIx17.returnPressed.connect(formPpmacAxisSettings.sendIx17)
        self.lneIx16.returnPressed.connect(formPpmacAxisSettings.sendIx16)
        self.lneIx12.returnPressed.connect(formPpmacAxisSettings.sendIx12)
        self.lneIx13.returnPressed.connect(formPpmacAxisSettings.sendIx13)
        self.lneIx19.returnPressed.connect(formPpmacAxisSettings.sendIx19)
        self.lneIx20.returnPressed.connect(formPpmacAxisSettings.sendIx20)
        self.lneIx23.returnPressed.connect(formPpmacAxisSettings.sendIx23)
        self.lneIx21.returnPressed.connect(formPpmacAxisSettings.sendIx21)
        self.lneIx22.returnPressed.connect(formPpmacAxisSettings.sendIx22)
        self.lneIx26.returnPressed.connect(formPpmacAxisSettings.sendIx26)
        self.tabAxisSetup.currentChanged['int'].connect(formPpmacAxisSettings.tabChange)
        self.lneIx11.returnPressed.connect(formPpmacAxisSettings.sendIx11)
        self.lneIx14.returnPressed.connect(formPpmacAxisSettings.sendIx14)
        self.lneIx25.returnPressed.connect(formPpmacAxisSettings.sendIx25)
        self.lneIx15.returnPressed.connect(formPpmacAxisSettings.sendIx15)
        self.lneIx30.returnPressed.connect(formPpmacAxisSettings.sendIx30)
        self.lneIx31.returnPressed.connect(formPpmacAxisSettings.sendIx31)
        self.lneIx32.returnPressed.connect(formPpmacAxisSettings.sendIx32)
        self.lneIx33.returnPressed.connect(formPpmacAxisSettings.sendIx33)
        self.lneIx34.returnPressed.connect(formPpmacAxisSettings.sendIx34)
        self.lneIx35.returnPressed.connect(formPpmacAxisSettings.sendIx35)
        self.lneIx11.returnPressed.connect(formPpmacAxisSettings.sendIx11)
        self.lneDerivative2.returnPressed.connect(formPpmacAxisSettings.sendDerivative2)
        self.lneVFF2.returnPressed.connect(formPpmacAxisSettings.sendVFF2)
        QtCore.QMetaObject.connectSlotsByName(formPpmacAxisSettings)
        formPpmacAxisSettings.setTabOrder(self.btnUpdate, self.btnClose)

    def retranslateUi(self, formPpmacAxisSettings):
        _translate = QtCore.QCoreApplication.translate
        formPpmacAxisSettings.setWindowTitle(_translate("formPpmacAxisSettings", "Axis setup"))
        self.btnUpdate.setText(_translate("formPpmacAxisSettings", "update"))
        self.textLabel1.setText(_translate("formPpmacAxisSettings", "Note this screen does not update continuously.\n"
"Hit the update button to read out the current values from pmac.\n"
"Write demand values in the text fields and hit enter to send."))
        self.btnClose.setText(_translate("formPpmacAxisSettings", "close"))
        self.groupBox2.setTitle(_translate("formPpmacAxisSettings", "Safety I variables"))
        self.textLabel2_9.setText(_translate("formPpmacAxisSettings", "Motor[x].JogTa:"))
        self.textLabel2_2_2.setText(_translate("formPpmacAxisSettings", "Motor[x].JogTs:"))
        self.textLabel2_3_2.setText(_translate("formPpmacAxisSettings", "Motor[x].JogSpeed:"))
        self.textLabel2_4_2.setText(_translate("formPpmacAxisSettings", "Motor[x].HomeVel:"))
        self.textLabel2_6_2.setText(_translate("formPpmacAxisSettings", "Motor[x].pEncStatus:"))
        self.textLabel2_7_2.setText(_translate("formPpmacAxisSettings", "Motor[x].HomeOffset:"))
        self.groupBox1.setTitle(_translate("formPpmacAxisSettings", "Definition I variables"))
        self.textLabel2.setText(_translate("formPpmacAxisSettings", "Motor[x].FatalFeLimit:"))
        self.textLabel2_2.setText(_translate("formPpmacAxisSettings", "Motor[x].WarnFeLimit:"))
        self.textLabel2_3.setText(_translate("formPpmacAxisSettings", "Motor[x].MaxPos:"))
        self.textLabel2_4.setText(_translate("formPpmacAxisSettings", "Motor[x].MinPos:"))
        self.textLabel2_5.setText(_translate("formPpmacAxisSettings", "Motor[x].AbortTa:"))
        self.textLabel2_6.setText(_translate("formPpmacAxisSettings", "Motor[x].MaxSpeed:"))
        self.textLabel2_7.setText(_translate("formPpmacAxisSettings", "Motor[x].InvAmax:"))
        self.textLabel2_8.setText(_translate("formPpmacAxisSettings", "Motor[x].AbortTs:"))
        self.tabAxisSetup.setTabText(self.tabAxisSetup.indexOf(self.tab), _translate("formPpmacAxisSettings", "definition and safety"))
        self.groupBox1_2.setTitle(_translate("formPpmacAxisSettings", "Gains"))
        self.textLabel2_10.setText(_translate("formPpmacAxisSettings", "Proportional:"))
        self.textLabel2_2_3.setText(_translate("formPpmacAxisSettings", "Derivative 1:"))
        self.textLabel2_3_3.setText(_translate("formPpmacAxisSettings", "Derivative 2:"))
        self.textLabel2_4_3.setText(_translate("formPpmacAxisSettings", "Integral:"))
        self.textLabel2_5_3.setText(_translate("formPpmacAxisSettings", "Vel. Feedforward 1:"))
        self.textLabel2_10_2.setText(_translate("formPpmacAxisSettings", "Vel. Feedforward 2:"))
        self.textLabel2_10_2_2.setText(_translate("formPpmacAxisSettings", "Accel. Feedforward:"))
        self.groupBox1_2_2.setTitle(_translate("formPpmacAxisSettings", "Other Servo Settings"))
        self.lLoopSelect.setText(_translate("formPpmacAxisSettings", "Integrator Mode:"))
        self.tabAxisSetup.setTabText(self.tabAxisSetup.indexOf(self.tab_2), _translate("formPpmacAxisSettings", "PID and macro"))


