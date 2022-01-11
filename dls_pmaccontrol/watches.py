# -*- coding: utf-8 -*-

import re

from PyQt5.QtWidgets import QDialog, QMessageBox, QTableWidgetItem

from dls_pmaccontrol.ui_formWatches import Ui_formWatches

# [TODO] Make sure variable types are not changed when writing to the PMAC
# [TODO] Add warnings when value being edited has changed in
#       the meantime (could use row colouring just like in dls-dependency-checker)
# [TODO] Remove invalid variables from watch window

unsafeCommands = ["save", "kill", "$$$", "$$$**", "out", "reset", "reboot", "jog"]


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
            varName = varName.lower()
            if varName in unsafeCommands:
                raise ValueError("%s is an unsafe command" % varName)
            if re.search(r"[\+\-=\^/]", varName) is not None:
                raise ValueError("%s is not a valid variable" % varName)
            if varName in self._watches:
                raise ValueError("There is already a watch for %s" % varName)
            # create watch object
            watch = Watch(self.parent.pmac, varName)
        except ValueError as e:
            self.panelEditWatch.setEnabled(False)
            QMessageBox.information(self, "Cannot create watch", str(e))
            return
        noRows = self.table.rowCount()
        self.table.insertRow(noRows)  # add a new row
        self.table.setItem(noRows, 0, QTableWidgetItem(varName))  # set variable name
        self._watches[varName] = watch  # add watch object to dict
        self.parent.commsThread.add_watch(varName)  # add to polling thread
        self.updateWatch(noRows)  # update the watch at the new row
        self.lneVariableName.setText("")

    # return watch object
    def getWatch(self, varName):
        varName = varName.lower()
        try:
            watch = self._watches[varName]
        except KeyError:
            raise ValueError('There is no watch for variable "%s"' % varName)
        return watch

    def updateWatch(self, row):
        varName = self.table.item(row, 0).text()
        try:
            self.table.setItem(row, 1, QTableWidgetItem(self.getPolledValue(varName)))
        except ValueError:
            self.table.setItem(row, 1, QTableWidgetItem("Error"))

    def updateCurrentWatch(self):
        row = self.table.currentRow()
        if row >= 0:
            self.updateWatch(row)

    def removeWatch(self):
        row = self.table.currentRow()
        if row is -1:
            return None
        assert type(row) is int
        varName = self.table.item(row, 0).text()
        try:
            del self._watches[varName]
            self.parent.commsThread.remove_watch(varName)
        except KeyError:
            raise ValueError('There is no watch for variable "%s"' % varName)
        try:
            self.table.removeRow(row)
            # self.updateEditWatchPanel()
            self.lneEditValue.setText("")
            self.panelEditWatch.setEnabled(False)
        except ValueError as e:
            QMessageBox.information(self, "Cannot remove watch", str(e))

    def clickTable(self, row, column):
        self.updateEditWatchPanel()

    def selectedVarName(self):
        currRow = self.table.currentRow()
        if currRow is -1:
            return None
        else:
            return self.table.item(currRow, 0).text()

    def updateEditWatchPanel(self):
        if not self.selectedVarName():
            self.panelEditWatch.setEnabled(False)
        else:
            self.panelEditWatch.setEnabled(True)
            # leave only the edit line edit enabled
            self.labelEditValue.setEnabled(True)
            self.lneEditValue.setEnabled(True)
            # set the edit line edit's text
            self.lneEditValue.setText(self.getPolledValue(self.selectedVarName()))

    def applyEditWatch(self):
        watch = self.getWatch(self.selectedVarName())
        try:
            newValueStr = str(self.lneEditValue.text())
            watch.setVariableValue(newValueStr)
            self.updateCurrentWatch()
            self.lneEditValue.setText("")
            self.panelEditWatch.setEnabled(False)
        except (ValueError, IOError) as e:
            self.lneEditValue.setText("")
            self.panelEditWatch.setEnabled(False)
            QMessageBox.information(self, "Cannot change value", str(e))

    def clearWatches(self):
        self.table.setRowCount(0)
        self._watches.clear()
        self.parent.commsThread.clear_watch()
        self.lneVariableName.setText("")
        self.lneEditValue.setText("")

    def getPolledValue(self, varName):
        return self.parent.commsThread.read_watch(varName)


class Watch:
    def __init__(self, pmac, varName):
        self.varName = varName
        self.pmac = pmac
        self.isInt = None
        self.isFloat = None
        self.isHex = None
        # None here, but do set it in the constructor in child classes

    # Get variable value to check whether it is hexadecimal, store that in isHex
    # 		rawStrValue = self._sendPMACCommand(varName)
    # 		assert len(rawStrValue) > 0
    # 		self.isHex = rawStrValue[0] is '$'
    #           self.isFloat = "." in rawStrValue
    #           self.isInt = not self.isHex and not self.isFloat

    def setVariableValue(self, newValue):
        # check type matches before sending command to set variable
        assert type(newValue) in (str, int, float)
        if self.varName[-2:] == "->":
            self._sendPMACCommand("%s%s" % (self.varName, str(newValue)))
        else:
            self._sendPMACCommand("%s=%s" % (self.varName, str(newValue)))

    def _sendPMACCommand(self, command):
        """Send a command to PMAC.
        On success, returns a string with response from the PMAC.
        On I/O failure, or if PMAC returns an ERRxx, throws an exception."""
        # Get response from PMAC; the 2nd returned boolean indicates absence of timeout
        (s, wasNoTimeout) = self.pmac.sendCommand(command)
        if not wasNoTimeout:
            raise IOError("Connection to PMAC timed out")

        # Check whether PMAC doesn't reply with an ERRxx type response
        matchObject = re.match(r"^\x07(ERR\d+)\r$", s)
        if matchObject or "error" in s:
            raise ValueError('Error: cannot set value for "%s"' % self.varName)
