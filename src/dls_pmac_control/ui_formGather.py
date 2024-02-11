
# Form implementation generated from reading ui file 'dls_pmac_control/formGather.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from qwt import QwtPlot


class Ui_formGather:
    def setupUi(self, formGather):
        formGather.setObjectName("formGather")
        formGather.resize(608, 429)
        formGather.setMinimumSize(QtCore.QSize(600, 400))
        self.gridlayout = QtWidgets.QGridLayout(formGather)
        self.gridlayout.setContentsMargins(11, 11, 11, 11)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        self.tabWidget2 = QtWidgets.QTabWidget(formGather)
        self.tabWidget2.setObjectName("tabWidget2")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridlayout1 = QtWidgets.QGridLayout(self.tab)
        self.gridlayout1.setContentsMargins(11, 11, 11, 11)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")
        self.qwtPlot = QwtPlot(self.tab)
        self.qwtPlot.setProperty("autoReplot", True)
        self.qwtPlot.setProperty("canvasBackground", QtGui.QColor(255, 255, 255))
        self.qwtPlot.setProperty("yRightAxis", True)
        self.qwtPlot.setObjectName("qwtPlot")
        self.gridlayout1.addWidget(self.qwtPlot, 0, 0, 1, 5)
        spacerItem = QtWidgets.QSpacerItem(
            200, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridlayout1.addItem(spacerItem, 1, 3, 1, 1)
        self.btnSetup = QtWidgets.QPushButton(self.tab)
        self.btnSetup.setEnabled(False)
        self.btnSetup.setObjectName("btnSetup")
        self.gridlayout1.addWidget(self.btnSetup, 1, 0, 1, 1)
        self.btnSave = QtWidgets.QPushButton(self.tab)
        self.btnSave.setEnabled(False)
        self.btnSave.setObjectName("btnSave")
        self.gridlayout1.addWidget(self.btnSave, 1, 4, 1, 1)
        self.btnTrigger = QtWidgets.QPushButton(self.tab)
        self.btnTrigger.setEnabled(False)
        self.btnTrigger.setObjectName("btnTrigger")
        self.gridlayout1.addWidget(self.btnTrigger, 1, 1, 1, 1)
        self.btnCollect = QtWidgets.QPushButton(self.tab)
        self.btnCollect.setEnabled(False)
        self.btnCollect.setObjectName("btnCollect")
        self.gridlayout1.addWidget(self.btnCollect, 1, 2, 1, 1)
        self.qWidget = QtWidgets.QWidget(self.tab)
        self.qWidget.setObjectName("qWidget")
        self.gridlayout1.addWidget(self.qWidget, 0, 0, 1, 5)
        self.tabWidget2.addTab(self.tab, "")
        self.tab1 = QtWidgets.QWidget()
        self.tab1.setObjectName("tab1")
        self.gridlayout2 = QtWidgets.QGridLayout(self.tab1)
        self.gridlayout2.setContentsMargins(11, 11, 11, 11)
        self.gridlayout2.setSpacing(6)
        self.gridlayout2.setObjectName("gridlayout2")
        self.textLabel2 = QtWidgets.QLabel(self.tab1)
        self.textLabel2.setWordWrap(False)
        self.textLabel2.setObjectName("textLabel2")
        self.gridlayout2.addWidget(self.textLabel2, 0, 0, 1, 1)
        self.lneNumberSamples = QtWidgets.QLineEdit(self.tab1)
        self.lneNumberSamples.setMinimumSize(QtCore.QSize(60, 0))
        self.lneNumberSamples.setMaximumSize(QtCore.QSize(100, 32767))
        self.lneNumberSamples.setObjectName("lneNumberSamples")
        self.gridlayout2.addWidget(self.lneNumberSamples, 0, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(
            60, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridlayout2.addItem(spacerItem1, 0, 5, 1, 1)
        self.lneSampleTime = QtWidgets.QLineEdit(self.tab1)
        self.lneSampleTime.setMinimumSize(QtCore.QSize(60, 0))
        self.lneSampleTime.setMaximumSize(QtCore.QSize(100, 32767))
        self.lneSampleTime.setObjectName("lneSampleTime")
        self.gridlayout2.addWidget(self.lneSampleTime, 0, 4, 1, 1)
        self.textLabel2_2 = QtWidgets.QLabel(self.tab1)
        self.textLabel2_2.setWordWrap(False)
        self.textLabel2_2.setObjectName("textLabel2_2")
        self.gridlayout2.addWidget(self.textLabel2_2, 0, 3, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridlayout2.addItem(spacerItem2, 0, 2, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(
            20, 50, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.gridlayout2.addItem(spacerItem3, 4, 2, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(
            460, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridlayout2.addItem(spacerItem4, 3, 1, 1, 5)
        self.btnApplyConf = QtWidgets.QPushButton(self.tab1)
        self.btnApplyConf.setObjectName("btnApplyConf")
        self.gridlayout2.addWidget(self.btnApplyConf, 3, 0, 1, 1)
        self.groupBox3 = QtWidgets.QGroupBox(self.tab1)
        self.groupBox3.setObjectName("groupBox3")
        self.gridlayout3 = QtWidgets.QGridLayout(self.groupBox3)
        self.gridlayout3.setContentsMargins(11, 11, 11, 11)
        self.gridlayout3.setSpacing(6)
        self.gridlayout3.setObjectName("gridlayout3")
        self.chkPlot1 = QtWidgets.QCheckBox(self.groupBox3)
        self.chkPlot1.setFocusPolicy(QtCore.Qt.NoFocus)
        self.chkPlot1.setText("")
        self.chkPlot1.setObjectName("chkPlot1")
        self.gridlayout3.addWidget(self.chkPlot1, 0, 0, 1, 1)
        self.spbAxis1 = QtWidgets.QSpinBox(self.groupBox3)
        self.spbAxis1.setFocusPolicy(QtCore.Qt.NoFocus)
        self.spbAxis1.setMinimum(1)
        self.spbAxis1.setMaximum(32)
        self.spbAxis1.setObjectName("spbAxis1")
        self.gridlayout3.addWidget(self.spbAxis1, 0, 1, 1, 1)
        self.chkPlot2 = QtWidgets.QCheckBox(self.groupBox3)
        self.chkPlot2.setFocusPolicy(QtCore.Qt.NoFocus)
        self.chkPlot2.setText("")
        self.chkPlot2.setObjectName("chkPlot2")
        self.gridlayout3.addWidget(self.chkPlot2, 1, 0, 1, 1)
        self.spbAxis2 = QtWidgets.QSpinBox(self.groupBox3)
        self.spbAxis2.setFocusPolicy(QtCore.Qt.NoFocus)
        self.spbAxis2.setMinimum(1)
        self.spbAxis2.setMaximum(32)
        self.spbAxis2.setObjectName("spbAxis2")
        self.gridlayout3.addWidget(self.spbAxis2, 1, 1, 1, 1)
        self.spbAxis3 = QtWidgets.QSpinBox(self.groupBox3)
        self.spbAxis3.setFocusPolicy(QtCore.Qt.NoFocus)
        self.spbAxis3.setMinimum(1)
        self.spbAxis3.setMaximum(32)
        self.spbAxis3.setObjectName("spbAxis3")
        self.gridlayout3.addWidget(self.spbAxis3, 2, 1, 1, 1)
        self.chkPlot3 = QtWidgets.QCheckBox(self.groupBox3)
        self.chkPlot3.setFocusPolicy(QtCore.Qt.NoFocus)
        self.chkPlot3.setText("")
        self.chkPlot3.setObjectName("chkPlot3")
        self.gridlayout3.addWidget(self.chkPlot3, 2, 0, 1, 1)
        self.spbAxis4 = QtWidgets.QSpinBox(self.groupBox3)
        self.spbAxis4.setFocusPolicy(QtCore.Qt.NoFocus)
        self.spbAxis4.setMinimum(1)
        self.spbAxis4.setMaximum(32)
        self.spbAxis4.setObjectName("spbAxis4")
        self.gridlayout3.addWidget(self.spbAxis4, 3, 1, 1, 1)
        self.chkPlot4 = QtWidgets.QCheckBox(self.groupBox3)
        self.chkPlot4.setFocusPolicy(QtCore.Qt.NoFocus)
        self.chkPlot4.setText("")
        self.chkPlot4.setObjectName("chkPlot4")
        self.gridlayout3.addWidget(self.chkPlot4, 3, 0, 1, 1)
        self.spbAxis5 = QtWidgets.QSpinBox(self.groupBox3)
        self.spbAxis5.setFocusPolicy(QtCore.Qt.NoFocus)
        self.spbAxis5.setMinimum(1)
        self.spbAxis5.setMaximum(32)
        self.spbAxis5.setObjectName("spbAxis5")
        self.gridlayout3.addWidget(self.spbAxis5, 4, 1, 1, 1)
        self.chkPlot5 = QtWidgets.QCheckBox(self.groupBox3)
        self.chkPlot5.setFocusPolicy(QtCore.Qt.NoFocus)
        self.chkPlot5.setText("")
        self.chkPlot5.setObjectName("chkPlot5")
        self.gridlayout3.addWidget(self.chkPlot5, 4, 0, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(
            170, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridlayout3.addItem(spacerItem5, 0, 5, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(
            170, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridlayout3.addItem(spacerItem6, 1, 5, 1, 1)
        spacerItem7 = QtWidgets.QSpacerItem(
            170, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridlayout3.addItem(spacerItem7, 2, 5, 1, 1)
        spacerItem8 = QtWidgets.QSpacerItem(
            170, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridlayout3.addItem(spacerItem8, 3, 5, 1, 1)
        spacerItem9 = QtWidgets.QSpacerItem(
            170, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridlayout3.addItem(spacerItem9, 4, 5, 1, 1)
        self.cmbDataSource1 = QtWidgets.QComboBox(self.groupBox3)
        self.cmbDataSource1.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmbDataSource1.setObjectName("cmbDataSource1")
        self.gridlayout3.addWidget(self.cmbDataSource1, 0, 4, 1, 1)
        self.cmbDataSource2 = QtWidgets.QComboBox(self.groupBox3)
        self.cmbDataSource2.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmbDataSource2.setObjectName("cmbDataSource2")
        self.gridlayout3.addWidget(self.cmbDataSource2, 1, 4, 1, 1)
        self.cmbDataSource3 = QtWidgets.QComboBox(self.groupBox3)
        self.cmbDataSource3.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmbDataSource3.setObjectName("cmbDataSource3")
        self.gridlayout3.addWidget(self.cmbDataSource3, 2, 4, 1, 1)
        self.cmbDataSource4 = QtWidgets.QComboBox(self.groupBox3)
        self.cmbDataSource4.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmbDataSource4.setObjectName("cmbDataSource4")
        self.gridlayout3.addWidget(self.cmbDataSource4, 3, 4, 1, 1)
        self.cmbDataSource5 = QtWidgets.QComboBox(self.groupBox3)
        self.cmbDataSource5.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmbDataSource5.setObjectName("cmbDataSource5")
        self.gridlayout3.addWidget(self.cmbDataSource5, 4, 4, 1, 1)
        self.cmbCol1 = QtWidgets.QComboBox(self.groupBox3)
        self.cmbCol1.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmbCol1.setObjectName("cmbCol1")
        self.cmbCol1.addItem("")
        self.cmbCol1.addItem("")
        self.cmbCol1.addItem("")
        self.cmbCol1.addItem("")
        self.cmbCol1.addItem("")
        self.gridlayout3.addWidget(self.cmbCol1, 0, 3, 1, 1)
        self.cmbCol2 = QtWidgets.QComboBox(self.groupBox3)
        self.cmbCol2.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmbCol2.setObjectName("cmbCol2")
        self.cmbCol2.addItem("")
        self.cmbCol2.addItem("")
        self.cmbCol2.addItem("")
        self.cmbCol2.addItem("")
        self.cmbCol2.addItem("")
        self.gridlayout3.addWidget(self.cmbCol2, 1, 3, 1, 1)
        self.cmbCol3 = QtWidgets.QComboBox(self.groupBox3)
        self.cmbCol3.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmbCol3.setObjectName("cmbCol3")
        self.cmbCol3.addItem("")
        self.cmbCol3.addItem("")
        self.cmbCol3.addItem("")
        self.cmbCol3.addItem("")
        self.cmbCol3.addItem("")
        self.gridlayout3.addWidget(self.cmbCol3, 2, 3, 1, 1)
        self.cmbCol4 = QtWidgets.QComboBox(self.groupBox3)
        self.cmbCol4.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmbCol4.setObjectName("cmbCol4")
        self.cmbCol4.addItem("")
        self.cmbCol4.addItem("")
        self.cmbCol4.addItem("")
        self.cmbCol4.addItem("")
        self.cmbCol4.addItem("")
        self.gridlayout3.addWidget(self.cmbCol4, 3, 3, 1, 1)
        self.cmbCol5 = QtWidgets.QComboBox(self.groupBox3)
        self.cmbCol5.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmbCol5.setObjectName("cmbCol5")
        self.cmbCol5.addItem("")
        self.cmbCol5.addItem("")
        self.cmbCol5.addItem("")
        self.cmbCol5.addItem("")
        self.cmbCol5.addItem("")
        self.gridlayout3.addWidget(self.cmbCol5, 4, 3, 1, 1)
        self.cmbXaxis1 = QtWidgets.QComboBox(self.groupBox3)
        self.cmbXaxis1.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmbXaxis1.setObjectName("cmbXaxis1")
        self.cmbXaxis1.addItem("")
        self.cmbXaxis1.addItem("")
        self.gridlayout3.addWidget(self.cmbXaxis1, 0, 2, 1, 1)
        self.cmbXaxis2 = QtWidgets.QComboBox(self.groupBox3)
        self.cmbXaxis2.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmbXaxis2.setObjectName("cmbXaxis2")
        self.cmbXaxis2.addItem("")
        self.cmbXaxis2.addItem("")
        self.gridlayout3.addWidget(self.cmbXaxis2, 1, 2, 1, 1)
        self.cmbXaxis3 = QtWidgets.QComboBox(self.groupBox3)
        self.cmbXaxis3.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmbXaxis3.setObjectName("cmbXaxis3")
        self.cmbXaxis3.addItem("")
        self.cmbXaxis3.addItem("")
        self.gridlayout3.addWidget(self.cmbXaxis3, 2, 2, 1, 1)
        self.cmbXaxis4 = QtWidgets.QComboBox(self.groupBox3)
        self.cmbXaxis4.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmbXaxis4.setObjectName("cmbXaxis4")
        self.cmbXaxis4.addItem("")
        self.cmbXaxis4.addItem("")
        self.gridlayout3.addWidget(self.cmbXaxis4, 3, 2, 1, 1)
        self.cmbXaxis5 = QtWidgets.QComboBox(self.groupBox3)
        self.cmbXaxis5.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmbXaxis5.setObjectName("cmbXaxis5")
        self.cmbXaxis5.addItem("")
        self.cmbXaxis5.addItem("")
        self.gridlayout3.addWidget(self.cmbXaxis5, 4, 2, 1, 1)
        self.gridlayout2.addWidget(self.groupBox3, 2, 0, 1, 6)
        spacerItem10 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridlayout2.addItem(spacerItem10, 1, 5, 1, 1)
        spacerItem11 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridlayout2.addItem(spacerItem11, 1, 2, 1, 1)
        self.textLabel1 = QtWidgets.QLabel(self.tab1)
        self.textLabel1.setWordWrap(False)
        self.textLabel1.setObjectName("textLabel1")
        self.gridlayout2.addWidget(self.textLabel1, 1, 3, 1, 1)
        self.txtLblFreq = QtWidgets.QLabel(self.tab1)
        self.txtLblFreq.setWordWrap(False)
        self.txtLblFreq.setObjectName("txtLblFreq")
        self.gridlayout2.addWidget(self.txtLblFreq, 1, 4, 1, 1)
        self.txtLblSignalLen = QtWidgets.QLabel(self.tab1)
        self.txtLblSignalLen.setWordWrap(False)
        self.txtLblSignalLen.setObjectName("txtLblSignalLen")
        self.gridlayout2.addWidget(self.txtLblSignalLen, 1, 1, 1, 1)
        self.textLabel1_2 = QtWidgets.QLabel(self.tab1)
        self.textLabel1_2.setWordWrap(False)
        self.textLabel1_2.setObjectName("textLabel1_2")
        self.gridlayout2.addWidget(self.textLabel1_2, 1, 0, 1, 1)
        self.tabWidget2.addTab(self.tab1, "")
        self.gridlayout.addWidget(self.tabWidget2, 0, 0, 1, 1)

        self.retranslateUi(formGather)
        self.tabWidget2.setCurrentIndex(0)
        self.cmbCol2.setCurrentIndex(1)
        self.cmbCol3.setCurrentIndex(2)
        self.cmbCol4.setCurrentIndex(3)
        self.cmbCol5.setCurrentIndex(4)
        self.btnCollect.clicked.connect(formGather.collectClicked)
        self.btnSave.clicked.connect(formGather.saveClicked)
        self.btnTrigger.clicked.connect(formGather.triggerClicked)
        self.btnApplyConf.clicked.connect(formGather.applyConfigClicked)
        self.btnSetup.clicked.connect(formGather.setupClicked)
        self.tabWidget2.currentChanged["int"].connect(formGather.changedTab)
        self.lneSampleTime.returnPressed.connect(formGather.servoCyclesChanged)
        self.lneNumberSamples.returnPressed.connect(formGather.changedNoSamples)
        QtCore.QMetaObject.connectSlotsByName(formGather)
        formGather.setTabOrder(self.tabWidget2, self.btnSetup)
        formGather.setTabOrder(self.btnSetup, self.btnTrigger)
        formGather.setTabOrder(self.btnTrigger, self.btnCollect)
        formGather.setTabOrder(self.btnCollect, self.btnSave)
        formGather.setTabOrder(self.btnSave, self.lneNumberSamples)
        formGather.setTabOrder(self.lneNumberSamples, self.lneSampleTime)
        formGather.setTabOrder(self.lneSampleTime, self.btnApplyConf)
        formGather.setTabOrder(self.btnApplyConf, self.chkPlot1)
        formGather.setTabOrder(self.chkPlot1, self.spbAxis1)
        formGather.setTabOrder(self.spbAxis1, self.cmbXaxis1)
        formGather.setTabOrder(self.cmbXaxis1, self.cmbCol1)
        formGather.setTabOrder(self.cmbCol1, self.cmbDataSource1)
        formGather.setTabOrder(self.cmbDataSource1, self.chkPlot2)
        formGather.setTabOrder(self.chkPlot2, self.spbAxis2)
        formGather.setTabOrder(self.spbAxis2, self.cmbXaxis2)
        formGather.setTabOrder(self.cmbXaxis2, self.cmbCol2)
        formGather.setTabOrder(self.cmbCol2, self.cmbDataSource2)
        formGather.setTabOrder(self.cmbDataSource2, self.chkPlot3)
        formGather.setTabOrder(self.chkPlot3, self.spbAxis3)
        formGather.setTabOrder(self.spbAxis3, self.cmbXaxis3)
        formGather.setTabOrder(self.cmbXaxis3, self.cmbCol3)
        formGather.setTabOrder(self.cmbCol3, self.cmbDataSource3)
        formGather.setTabOrder(self.cmbDataSource3, self.chkPlot4)
        formGather.setTabOrder(self.chkPlot4, self.spbAxis4)
        formGather.setTabOrder(self.spbAxis4, self.cmbXaxis4)
        formGather.setTabOrder(self.cmbXaxis4, self.cmbCol4)
        formGather.setTabOrder(self.cmbCol4, self.cmbDataSource4)
        formGather.setTabOrder(self.cmbDataSource4, self.chkPlot5)
        formGather.setTabOrder(self.chkPlot5, self.spbAxis5)
        formGather.setTabOrder(self.spbAxis5, self.cmbXaxis5)
        formGather.setTabOrder(self.cmbXaxis5, self.cmbCol5)
        formGather.setTabOrder(self.cmbCol5, self.cmbDataSource5)

    def retranslateUi(self, formGather):
        _translate = QtCore.QCoreApplication.translate
        formGather.setWindowTitle(_translate("formGather", "Data Gather"))
        self.qwtPlot.setProperty("title", _translate("formGather", "data gather"))
        self.btnSetup.setText(_translate("formGather", "setup"))
        self.btnSave.setText(_translate("formGather", "save data..."))
        self.btnTrigger.setText(_translate("formGather", "trigger"))
        self.btnCollect.setText(_translate("formGather", "collect"))
        self.tabWidget2.setTabText(
            self.tabWidget2.indexOf(self.tab), _translate("formGather", "gather")
        )
        self.textLabel2.setText(_translate("formGather", "# of samples:"))
        self.lneNumberSamples.setText(_translate("formGather", "10"))
        self.lneSampleTime.setText(_translate("formGather", "10"))
        self.textLabel2_2.setText(
            _translate("formGather", "sample time [servo cycles]")
        )
        self.btnApplyConf.setText(_translate("formGather", "Apply"))
        self.groupBox3.setTitle(_translate("formGather", "configure data gathering "))
        self.cmbCol1.setItemText(0, _translate("formGather", "red"))
        self.cmbCol1.setItemText(1, _translate("formGather", "blue"))
        self.cmbCol1.setItemText(2, _translate("formGather", "magenta"))
        self.cmbCol1.setItemText(3, _translate("formGather", "green"))
        self.cmbCol1.setItemText(4, _translate("formGather", "cyan"))
        self.cmbCol2.setItemText(0, _translate("formGather", "red"))
        self.cmbCol2.setItemText(1, _translate("formGather", "blue"))
        self.cmbCol2.setItemText(2, _translate("formGather", "magenta"))
        self.cmbCol2.setItemText(3, _translate("formGather", "green"))
        self.cmbCol2.setItemText(4, _translate("formGather", "cyan"))
        self.cmbCol3.setItemText(0, _translate("formGather", "red"))
        self.cmbCol3.setItemText(1, _translate("formGather", "blue"))
        self.cmbCol3.setItemText(2, _translate("formGather", "magenta"))
        self.cmbCol3.setItemText(3, _translate("formGather", "green"))
        self.cmbCol3.setItemText(4, _translate("formGather", "cyan"))
        self.cmbCol4.setItemText(0, _translate("formGather", "red"))
        self.cmbCol4.setItemText(1, _translate("formGather", "blue"))
        self.cmbCol4.setItemText(2, _translate("formGather", "magenta"))
        self.cmbCol4.setItemText(3, _translate("formGather", "green"))
        self.cmbCol4.setItemText(4, _translate("formGather", "cyan"))
        self.cmbCol5.setItemText(0, _translate("formGather", "red"))
        self.cmbCol5.setItemText(1, _translate("formGather", "blue"))
        self.cmbCol5.setItemText(2, _translate("formGather", "magenta"))
        self.cmbCol5.setItemText(3, _translate("formGather", "green"))
        self.cmbCol5.setItemText(4, _translate("formGather", "cyan"))
        self.cmbXaxis1.setItemText(0, _translate("formGather", "left"))
        self.cmbXaxis1.setItemText(1, _translate("formGather", "right"))
        self.cmbXaxis2.setItemText(0, _translate("formGather", "left"))
        self.cmbXaxis2.setItemText(1, _translate("formGather", "right"))
        self.cmbXaxis3.setItemText(0, _translate("formGather", "left"))
        self.cmbXaxis3.setItemText(1, _translate("formGather", "right"))
        self.cmbXaxis4.setItemText(0, _translate("formGather", "left"))
        self.cmbXaxis4.setItemText(1, _translate("formGather", "right"))
        self.cmbXaxis5.setItemText(0, _translate("formGather", "left"))
        self.cmbXaxis5.setItemText(1, _translate("formGather", "right"))
        self.textLabel1.setText(_translate("formGather", "sample frequency [kHz]:"))
        self.txtLblFreq.setText(_translate("formGather", "kHz"))
        self.txtLblSignalLen.setText(_translate("formGather", "ms"))
        self.textLabel1_2.setText(_translate("formGather", "signal length:"))
        self.tabWidget2.setTabText(
            self.tabWidget2.indexOf(self.tab1), _translate("formGather", "configure")
        )
