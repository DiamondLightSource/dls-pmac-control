import re

from PyQt6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem

from dls_pmac_control.ui_form_watches import UiFormWatches

# [TODO] Make sure variable types are not changed when writing to the PMAC
# [TODO] Add warnings when value being edited has changed in
#       the meantime (could use row colouring just like in dls-dependency-checker)
# [TODO] Remove invalid variables from watch window

unsafe_commands = ["save", "kill", "$$$", "$$$**", "out", "reset", "reboot", "jog"]


class Watchesform(QDialog, UiFormWatches):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setup_ui(self)
        self.parent = parent
        self._watches = {}

    def add_watch(self):
        var_name = str(self.lneVariableName.text())
        try:
            assert isinstance(var_name, str)
            if var_name.lower() in unsafe_commands:
                raise ValueError(f"{var_name} is an unsafe command")
            if re.search(r"[\+\-=\^/]", var_name) is not None:
                raise ValueError(f"{var_name} is not a valid variable")
            if var_name in self._watches:
                raise ValueError(f"There is already a watch for {var_name}")
            # create watch object
            watch = Watch(self.parent.pmac, var_name)
        except ValueError as e:
            self.panelEditWatch.setEnabled(False)
            QMessageBox.information(self, "Cannot create watch", str(e))
            return
        no_rows = self.table.rowCount()
        self.table.insertRow(no_rows)  # add a new row
        self.table.setItem(no_rows, 0, QTableWidgetItem(var_name))  # set variable name
        self._watches[var_name] = watch  # add watch object to dict
        self.parent.comms_worker.add_watch(var_name)  # add to polling thread
        self.update_watch(no_rows)  # update the watch at the new row
        self.lneVariableName.setText("")

    # return watch object
    def get_watch(self, var_name):
        try:
            watch = self._watches[var_name]
        except KeyError as e:
            print(f'There is no watch for variable "{var_name}"')
            raise ValueError() from e
        return watch

    def update_watch(self, row):
        var_name = self.table.item(row, 0).text()
        try:
            self.table.setItem(
                row, 1, QTableWidgetItem(self.get_polled_value(var_name))
            )
        except ValueError:
            self.table.setItem(row, 1, QTableWidgetItem("Error"))

    def update_current_watch(self):
        row = self.table.currentRow()
        if row >= 0:
            self.update_watch(row)

    def remove_watch(self):
        row = self.table.currentRow()
        if row == -1:
            return None
        assert isinstance(row, int)
        var_name = self.table.item(row, 0).text()
        try:
            del self._watches[var_name]
            self.parent.comms_worker.remove_watch(var_name)
        except KeyError as e:
            print(f'There is no watch for variable "{var_name}"')
            raise ValueError() from e
        try:
            self.table.removeRow(row)
            # self.updateEditWatchPanel()
            self.lneEditValue.setText("")
            self.panelEditWatch.setEnabled(False)
        except ValueError as e:
            QMessageBox.information(self, "Cannot remove watch", str(e))

    def click_table(self, row, column):
        self.update_edit_watch_panel()

    def selected_var_name(self):
        curr_row = self.table.currentRow()
        if curr_row == -1:
            return None
        else:
            return self.table.item(curr_row, 0).text()

    def update_edit_watch_panel(self):
        if not self.selected_var_name():
            self.panelEditWatch.setEnabled(False)
        else:
            self.panelEditWatch.setEnabled(True)
            # leave only the edit line edit enabled
            self.labelEditValue.setEnabled(True)
            self.lneEditValue.setEnabled(True)
            # set the edit line edit's text
            self.lneEditValue.setText(self.get_polled_value(self.selected_var_name()))

    def apply_edit_watch(self):
        watch = self.get_watch(self.selected_var_name())
        try:
            new_value_str = str(self.lneEditValue.text())
            watch.setVariableValue(new_value_str)
            self.update_current_watch()
            self.lneEditValue.setText("")
            self.panelEditWatch.setEnabled(False)
        except (OSError, ValueError) as e:
            self.lneEditValue.setText("")
            self.panelEditWatch.setEnabled(False)
            QMessageBox.information(self, "Cannot change value", str(e))

    def clear_watches(self):
        self.table.setRowCount(0)
        self._watches.clear()
        self.parent.comms_worker.clear_watch()
        self.lneVariableName.setText("")
        self.lneEditValue.setText("")

    def get_polled_value(self, var_name):
        return self.parent.comms_worker.read_watch(var_name)


class Watch:
    def __init__(self, pmac, var_name):
        self.varName = var_name
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

    def set_variable_value(self, new_value):
        # check type matches before sending command to set variable
        assert type(new_value) in (str, int, float)
        if self.varName[-2:] == "->":
            self._send_pmac_command(f"{self.varName}{str(new_value)}")
        else:
            self._send_pmac_command(f"{self.varName}={str(new_value)}")

    def _send_pmac_command(self, command):
        """Send a command to PMAC.
        On success, returns a string with response from the PMAC.
        On I/O failure, or if PMAC returns an ERRxx, throws an exception."""
        # Get response from PMAC; the 2nd returned boolean indicates absence of timeout
        (s, was_no_timeout) = self.pmac.sendCommand(command)
        if not was_no_timeout:
            raise OSError("Connection to PMAC timed out")

        # Check whether PMAC doesn't reply with an ERRxx type response
        match_object = re.match(r"^\x07(ERR\d+)\r$", s)
        if match_object or "error" in s:
            raise ValueError(f'Error: cannot set value for "{self.varName}"')
