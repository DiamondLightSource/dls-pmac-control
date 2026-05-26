import re
import sys

from PyQt6.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication, QCheckBox, QDialog, QMessageBox

from dls_pmac_control.ui_form_energise import UiFormEnergise


class PmacIOError(IOError):
    pass


class Energiseform(QDialog, UiFormEnergise):
    def __init__(self, pmac, parent=None):
        QDialog.__init__(self, parent)  # , flags=None)
        self.setup_ui(self)

        self.pmac = pmac
        self.parent = parent
        self.lstCheckBoxes = None

        self.create_check_boxes()
        (self.val7501, self.val7503) = self.read_m750x()
        self.update_screen()

    # Create the 2 columns of check-boxes
    def create_check_boxes(self):
        chk_group_layout = self.chkGroup.layout()
        chk_group_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.lstCheckBoxes = []
        for axis in range(1, 33):
            q_check_box = QCheckBox("chkBox" + str(axis), self.chkGroup)
            q_check_box.setText(str(axis))
            if axis <= 16:
                row = axis - 1
                chk_group_layout.addWidget(q_check_box, row, 0)
            else:
                row = axis - 17
                chk_group_layout.addWidget(q_check_box, row, 1)
            self.lstCheckBoxes.append(q_check_box)

    # Get values of m7501, m7503 from PMAC. This does *not* update
    # self.val7501, self.val7503.
    def read_m750x(self):
        (ret_str, ret_status) = self.pmac.sendCommand("m7501 m7503")
        if not ret_status:
            raise PmacIOError("Cannot read m7501, m7503")
        lst_ret_str = re.split(r"\r", ret_str)
        val7501 = int(lst_ret_str[0])  # just a local variable, not self.var7501
        val7503 = int(lst_ret_str[1])  # just a local variable, not self.var7503
        return val7501, val7503

    # Update the axis energised checkboxes using the values in self.val7501
    # and self.val7503.
    def update_screen(self):
        for axis in range(1, 33):
            if axis <= 16:
                is_axis_checked = bool(self.val7501 & (1 << (axis - 1)))
            else:
                is_axis_checked = bool(self.val7503 & (1 << (axis - 17)))
            self.lstCheckBoxes[axis - 1].setChecked(is_axis_checked)

    # Return True if: the value of self.val7501 is equal to the actual M7501
    # on the PMAC, and
    #                 the value of self.val7503 is equal to the actual M7503
    #                 on the PMAC.
    # During comparisons consider only the 2 LSBs of the variables
    def is_screen_up_to_date(self):
        (val7501, val7503) = self.read_m750x()
        return (self.val7501 & 0x00FFFF == val7501 & 0x00FFFF) and (
            self.val7503 & 0x00FFFF == val7503 & 0x00FFFF
        )

    # public slot
    # Send energise axis command to the pmac.
    # Functionality: create the hex value of the bitmap of axis to energise.
    #                send the command to the pmac
    #                read back the two parts (16 axes per read)
    #                set the corresponding checkboxes to reflect the read
    #                back value.
    def send_command(self):
        # Make sure that self.val7501 and self.val7503 truly reflect the
        # current values of M7501 and M7503 (on the PMAC)
        if not self.is_screen_up_to_date():
            QMessageBox.information(
                self,
                "Error",
                "The screen is out of date, even if "
                "ignoring your changes!\n" + "This may be e.g. due to PLCs running in "
                "the background which de/energised some "
                "motors.\n"
                "To avoid inconsistency, the screen will "
                "reload now. Re-do your changes and submit "
                "again.",
            )
            (self.val7501, self.val7503) = self.read_m750x()
            self.update_screen()
            return

        # Find out new values of m7501, m7503 using current energize bits
        new_val7501 = self.val7501 & 0xFF0000  # keep MSB unchanged
        new_val7503 = self.val7503 & 0xFF0000  # keep MSB unchanged
        for i, axis in enumerate(self.lstCheckBoxes):
            if axis.isChecked():
                if i < 16:
                    new_val7501 = new_val7501 | (1 << i)
                else:
                    new_val7503 = new_val7503 | (1 << (i - 16))
        self.val7501 = new_val7501
        self.val7503 = new_val7503

        # Write m7501, m7503 to the PMAC
        cmd = f"m7501=${self.val7501:x} m7503=${self.val7503:x}"
        (ret_str, ret_status) = self.pmac.sendCommand(cmd)
        if not ret_status:
            QMessageBox.information(self, "Error", "Send command error:\n" + ret_str)
            return

        # Update the shell
        if self.parent.chkShowAll.isChecked():
            self.parent.txtShell.append(cmd)
            self.parent.txtShell.append(ret_str)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a, pyqtSignal("lastWindowClosed()"), a, pyqtSlot("quit()"))  # type: ignore # noqa
    w = Energiseform(None)
    a.setMainWidget(w)  # type: ignore
    w.show()
    a.exec_loop()  # type: ignore
