# -*- coding: utf-8 -*-

import re
import sys

#from formWatches import formWatches
#from pmactelnet import PmacTelnetInterface
#from PyQt4.QtCore import SIGNAL, SLOT
#from PyQt4.QtGui import QApplication, QMessageBox, QObject

from PyQt5.Qt import QPen
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox, QTableWidgetItem
from qwt import QwtPlotCurve

from dls_pmaccontrol.ui_formWatches import Ui_formWatches

# [TODO] Currently allows setting commands as variables
# [TODO] Setting values and reflect changes to PPMAC
# [TODO] Add continuous polling & warnings when value being edited has changed in
#       the meantime (could use row colouring just like in dls-dependency-checker)
# [TODO] Dictionary

class Watchesform(QDialog, Ui_formWatches):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.parent = parent
        self._watches = {}

    def addWatch(self):
        varName = str(self.lneVariableName.text())
        try:
            assert type(varName) is str
            #varName = varName.lower()
            isValidPMACVariableName = False
            (retStr,status) = self.parent.pmac.sendCommand(varName)
            # if no error returned then variable is valid
            if not "error" in retStr: 
                isValidPMACVariableName = True
            if not isValidPMACVariableName:
                raise ValueError('"%s" is not an accepted PMAC variable name' % varName)
            if varName in self._watches:
                raise ValueError("There is already a watch for this variable")
        except ValueError as e:
            QMessageBox.information(self, "Cannot create watch", str(e))
            return

        noRows = self.table.rowCount()
        self.table.insertRow(noRows)  # add a new row
        self.table.setItem(noRows, 0, QTableWidgetItem(varName))  # set variable name column of the new row
        self.updateWatch(noRows)  # update the watch at the new row
        self._watches[varName] = retStr #float(retStr) # add to dict
        self.lneVariableName.setText("")

    def updateWatch(self, row):
        varName = self.table.item(row, 0).text()
        try:
            watch = self.getWatch(varName)
            self.table.setItem(row, 1, QTableWidgetItem("N/A"))
            self.table.setItem(row, 2, QTableWidgetItem(self.getVariableValueStr(varName)))
        except ValueError:
            self.table.setItem(row, 1, QTableWidgetItem("N/A"))
            self.table.setItem(row, 2, QTableWidgetItem("Error"))

    def getVariableValueStr(self,variable):
        assert type(variable) is str
        variable = variable.lower()
        (retStr,status) = self.parent.pmac.sendCommand(variable)
        if not "error" in retStr: 
            return retStr
        else: 
            return "Error"

    def getWatch(self, varName):
        varName = varName.lower()
        try:
            watch = self._watches[varName]
        except KeyError:
            raise ValueError('There is no watch for variable "%s"' % varName)
        return watch

    def updateCurrentWatch(self):
        row = self.table.currentRow()
        print("updateCurrentWatch(): current row is %d" % row)
        if row >= 0:
            self.updateWatch(row)

    def removeWatch(self):
        row = self.table.currentRow()
        assert type(row) is int

        varName = self.table.item(row, 0).text()

        try:
            del self._watches[varName]
        except KeyError:
            raise ValueError('There is no watch for variable "%s"' % varName)
        #print(self._watches)

        try:
            self.table.removeRow(row)
            self.updateEditWatchPanel()
        except ValueError as e:
            QMessageBox.information(self, "Cannot remove watch", str(e))

    def clickTable(self, row, column):
        print("clickTable(%d,%d)" % (row, column))
        self.updateEditWatchPanel()

    def selectedVarName(self):
        currRow = self.table.currentRow()
        if currRow is -1:
            return None
        else:
            return self.table.item(currRow, 0).text()

    def setBitBoxesEnabled(self, isEnabled):
        for i in range(32):
            checkBox = self.__dict__["cb" + str(i)]
            checkBox.setEnabled(isEnabled)

    def updateEditWatchPanel(self):
        if not self.selectedVarName():
            self.panelEditWatch.setEnabled(False)
        else:
            self.panelEditWatch.setEnabled(True)
            watch = self.getWatch(self.selectedVarName())
            #if isinstance(watch, IVariableWatch):
            # leave only the edit line edit enabled; disable the bit fields
            self.labelEditValue.setEnabled(True)
            self.lneEditValue.setEnabled(True)
            self.setBitBoxesEnabled(False)
            # set the edit line edit's text
            self.lneEditValue.setText(self.getVariableValueStr(watch))

    def applyEditWatch(self):
        print("applyEditWatch()")
        watch = self.getWatch(self.selectedVarName())
        #if isinstance(watch, IVariableWatch):
        try:
            newValueStr = str(self.lneEditValue.text())
            print(newValueStr, type(newValueStr))
            watch.setVariableValue(newValueStr)
            self.updateCurrentWatch()
        except (ValueError, IOError) as e:
            QMessageBox.information(self, "Cannot change value", str(e))
