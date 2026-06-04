from PyQt6.QtWidgets import QDialog, QMessageBox

from dls_pmac_control.ui_form_axis_settings import UiFormAxisSettings
from dls_pmac_control.ui_form_ppmac_axis_settings import UiFormPpmacAxisSettings

# Power PMAC I-Variable Equivalents
PpmacVars = {
    "Ix11": "FatalFeLimit",
    "Ix12": "WarnFeLimit",
    "Ix13": "MaxPos",
    "Ix14": "MinPos",
    "Ix15": "AbortTa",
    "Ix16": "MaxSpeed",
    "Ix17": "InvAmax",
    "Ix19": "AbortTs",
    "Ix20": "JogTa",
    "Ix21": "JogTs",
    "Ix22": "JogSpeed",
    "Ix23": "HomeVel",
    "Ix25": "pEncStatus",
    "Ix26": "HomeOffset",
    "Ix30": "Servo.Kp",
    "Ix31": "Servo.Kvfb",
    "Ix32": "Servo.Kvff",
    "Ix33": "Servo.Ki",
    "Ix34": "Servo.SwZvInt",
    "Ix35": "Servo.Kaff",
    "Derivative2": "Servo.Kvifb",
    "VFF2": "Servo.Kviff",
}


class Axissettingsform(QDialog, UiFormAxisSettings):
    def __init__(self, parent=None, current_motor=1, macro_axis_start_index=0):
        QDialog.__init__(self, parent)
        self.setup_ui(self)

        self.currentMotor = current_motor
        self.macroAxisStartIndex = macro_axis_start_index
        self.parent = parent

        self.lneIx11.setToolTip("""Fatal following error [1/16 cts]""")
        self.lneIx12.setToolTip("""Warning following error limit [1/16 cts]""")
        self.lneIx13.setToolTip("""Positive soft limit position [cts]""")
        self.lneIx14.setToolTip("""Negative soft limit position [cts]""")
        self.lneIx15.setToolTip(
            "Decceleration rate on position\nlimit or abort [cts/msec2]"
        )
        self.lneIx16.setToolTip("Maximum velocity in LINEAR motion programs [cts/msec]")
        self.lneIx17.setToolTip("Maximum acceleration in motion programs [cts/msec2]")
        self.lneIx19.setToolTip("Maximum jog/home acceleration [cts/msec2]")
        self.lneIx20.setToolTip("Jog/Home Acceleration Time [msec]")
        self.lneIx21.setToolTip(
            "Jog/Home S-Curve Time [msec]\n(DLS: Try to avoid using this one!)"
        )
        self.lneIx22.setToolTip("Jog velocity [cts/msec]")
        self.lneIx23.setToolTip("Home velocity and direction [cts/msec]")
        self.lneIx24.setToolTip("Flag Mode Control (limits)")
        self.lneIx25.setToolTip("Flag Address")
        self.lneIx26.setToolTip("Home offset [1/16 cts]")

        self.lneIx30.setToolTip("PID Proportional Gain")
        self.lneIx31.setToolTip("PID Derivative Gain")
        self.lneIx32.setToolTip("PID Velocity Feedforward Gain")
        self.lneIx33.setToolTip("PID Integral Gain")
        self.lneIx34.setToolTip("PID Integration Mode [0 or 1]")
        self.lneIx35.setToolTip("PID Acceleration Feedforward Gain")
        self.lneIx65.setToolTip("Deadband Size [1/16 cts]")
        self.lneLoopSelect.setToolTip(
            "Encoder/Timer n Decode Control\n7: Closed loop stepper\n8: Open "
            "loop stepper"
        )
        self.lneCaptureOn.setToolTip(
            """Encoder n Capture Control
            0: Immediate capture
            1: Capture on Index (CHCn) high
            2: Capture on Flag high
            3: Capture on (Index high AND Flag high)
            4: Immediate capture
            5: Capture on Index (CHCn) low
            6: Capture on Flag high
            7: Capture on (Index low AND Flag high)
            8: Immediate capture
            9: Capture on Index (CHCn) high
            10: Capture on Flag low
            11: Capture on (Index high AND Flag low)
            12: Immediate capture
            13: Capture on Index (CHCn) low
            14: Capture on Flag low"""
        )
        self.lneCaptureFlag.setToolTip(
            """Capture n Flag Select Control
            0: Home Flag
            1: positive limit flag
            2: Negative limit flag
            3: User flag"""
        )
        self.lneOutputMode.setToolTip(
            """Output n Mode Select (DLS: use 2 for
            steppers)
            0 = Outputs A & B are PWM; Output C is PWM
            1 = Outputs A & B are DAC; Output C is PWM
            2 = Outputs A & B are PWM; Output C is PFM
            3 = Outputs A & B are DAC; Output C is PFM
            """
        )
        self.definitionIvars = [11, 12, 13, 14, 15, 16, 17, 19]
        self.safetyIvars = [20, 21, 22, 23, 24, 25, 26]
        self.pidIvars = [30, 31, 32, 33, 34, 35, 65]

    def change_axis(self, new_motor):
        self.currentMotor = new_motor
        if self.isVisible():
            self.axis_update()

    # Updates I-variable line edits for this axis and I-variables listed in
    # ivars
    def _update_axis_setup_i_vars(self, ivars):
        ret_lst = self.parent.pmac.getAxisSetupIVars(self.currentMotor, ivars)
        if ret_lst:
            for i, ret_val in enumerate(ret_lst):
                if i < len(ivars):
                    exec(f'self.lneIx{ivars[i]}.setText(str("{ret_val}"))')

    def _update_axis_signal_controls_vars(self):
        (
            loop_select,
            capture_on,
            capture_flag,
            output_mode,
        ) = self._get_axis_signal_controls_vars()
        self.lneLoopSelect.setText(loop_select)
        self.lneCaptureOn.setText(capture_on)
        self.lneCaptureFlag.setText(capture_flag)
        self.lneOutputMode.setText(output_mode)

    def _get_axis_signal_controls_vars(self):
        pmac = self.parent.pmac  # a link to the RemotePmacInterface
        (loop_select, capture_on, capture_flag, output_mode) = [None, None, None, None]
        if pmac.isMacroStationAxis(self.currentMotor):
            result = pmac.getAxisMsIVars(
                self.currentMotor, [910, 912, 913, 916], self.macroAxisStartIndex
            )
            if len(result) == 4:
                (loop_select, capture_on, capture_flag, output_mode) = result
            else:
                error_str = result[0]
                if "ERR008" in result[0]:
                    error_str = "ERR008: MACRO auxiliary communications error."
                QMessageBox.information(self, "Error", error_str)
        else:
            (
                loop_select,
                capture_on,
                capture_flag,
                output_mode,
            ) = pmac.getOnboardAxisI7000PlusVars(self.currentMotor, [0, 2, 3, 6])
        return loop_select, capture_on, capture_flag, output_mode

    def axis_update(self):
        selected_tab_index = self.tabAxisSetup.currentIndex()
        if selected_tab_index == 0:
            # The "definition and safety" tab is selected
            self._update_axis_setup_i_vars(self.definitionIvars + self.safetyIvars)
        else:
            # The "PID and macro" tab is selected
            self._update_axis_setup_i_vars(self.pidIvars)
            self._update_axis_signal_controls_vars()

    def tab_change(self):
        self.axis_update()

    # public slot
    @staticmethod
    def axis_close():
        print("axissettingsform.axisClose(): Not implemented yet")

    def send_ix11(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 11, self.lneIx11.text())
        self.axis_update()

    def send_ix12(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 12, self.lneIx12.text())
        self.axis_update()

    def send_ix13(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 13, self.lneIx13.text())
        self.axis_update()

    def send_ix14(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 14, self.lneIx14.text())
        self.axis_update()

    def send_ix15(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 15, self.lneIx15.text())
        self.axis_update()

    def send_ix16(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 16, self.lneIx16.text())
        self.axis_update()

    def send_ix17(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 17, self.lneIx17.text())
        self.axis_update()

    def send_ix19(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 19, self.lneIx19.text())
        self.axis_update()

    def send_ix20(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 20, self.lneIx20.text())
        self.axis_update()

    def send_ix21(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 21, self.lneIx21.text())
        self.axis_update()

    def send_ix22(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 22, self.lneIx22.text())
        self.axis_update()

    def send_ix23(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 23, self.lneIx23.text())
        self.axis_update()

    def send_ix24(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 24, self.lneIx24.text())
        self.axis_update()

    def send_ix25(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 25, self.lneIx25.text())
        self.axis_update()

    def send_ix26(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 26, self.lneIx26.text())
        self.axis_update()

    def send_ix30(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 30, self.lneIx30.text())
        self.axis_update()

    def send_ix31(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 31, self.lneIx31.text())
        self.axis_update()

    def send_ix32(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 32, self.lneIx32.text())
        self.axis_update()

    def send_ix33(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 33, self.lneIx33.text())
        self.axis_update()

    def send_ix34(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 34, self.lneIx34.text())
        self.axis_update()

    def send_ix35(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 35, self.lneIx35.text())
        self.axis_update()

    def send_ix65(self):
        self.parent.pmac.setAxisSetupIVar(self.currentMotor, 65, self.lneIx65.text())
        self.axis_update()

    def send_loop_select(self):
        pmac = self.parent.pmac
        if pmac.isMacroStationAxis(self.currentMotor):
            pmac.setAxisMsIVar(self.currentMotor, 910, self.lneLoopSelect.text())
        else:
            pmac.setOnboardAxisI7000PlusIVar(
                self.currentMotor, 0, self.lneLoopSelect.text()
            )

    def send_capture_on(self):
        pmac = self.parent.pmac
        if pmac.isMacroStationAxis(self.currentMotor):
            pmac.setAxisMsIVar(self.currentMotor, 912, self.lneCaptureOn.text())
        else:
            pmac.setOnboardAxisI7000PlusIVar(
                self.currentMotor, 2, self.lneCaptureOn.text()
            )

    def send_capture_flag(self):
        pmac = self.parent.pmac
        if pmac.isMacroStationAxis(self.currentMotor):
            pmac.setAxisMsIVar(self.currentMotor, 913, self.lneCaptureFlag.text())
        else:
            pmac.setOnboardAxisI7000PlusIVar(
                self.currentMotor, 3, self.lneCaptureFlag.text()
            )

    def send_output_mode(self):
        pmac = self.parent.pmac
        if pmac.isMacroStationAxis(self.currentMotor):
            pmac.setAxisMsIVar(self.currentMotor, 916, self.lneOutputMode.text())
        else:
            pmac.setOnboardAxisI7000PlusIVar(
                self.currentMotor, 6, self.lneOutputMode.text()
            )


class PpmacAxissettingsform(QDialog, UiFormPpmacAxisSettings):
    def __init__(self, parent=None, current_motor=1):
        QDialog.__init__(self, parent)
        self.setup_ui(self)

        self.currentMotor = current_motor
        self.parent = parent

        self.lneIx11.setToolTip("Fatal (shutdown) following error limit [cts]")
        self.lneIx12.setToolTip("Warning (trigger) following error limit [cts]")
        self.lneIx13.setToolTip("Positive position overtravel limit [cts]")
        self.lneIx14.setToolTip("Negative position overtravel limit [cts]")
        self.lneIx15.setToolTip(
            "Abort deceleration time or inverse rate [msec or msec2/cts]"
        )
        self.lneIx16.setToolTip("Maximum programmed velocity magnitude [cts/msec]")
        self.lneIx17.setToolTip(
            "Inverse of maximum programmed acceleration [msec2/cts]"
        )
        self.lneIx19.setToolTip(
            "Abort S-curve deceleration time or inverse jerk rate  [msec or msec3/cts]"
        )
        self.lneIx20.setToolTip(
            "Jog accel/decel time or inverse rate [msec or msec2/cts]"
        )
        self.lneIx21.setToolTip(
            "Jog accel/decel S-curve time or inverse jerk rate [msec or msec3/cts]"
        )
        self.lneIx22.setToolTip("Jog command velocity magnitude [cts/msec]")
        self.lneIx23.setToolTip("Home-search command signed velocity [cts/msec]")
        self.lneIx25.setToolTip("Motor “parent” input flag pointer")
        self.lneIx26.setToolTip("Position referencing offset [cts]")

        self.definitionIvars = [11, 12, 13, 14, 15, 16, 17, 19]
        self.safetyIvars = [20, 21, 22, 23, 25, 26]
        self.gainIvars = [30, 31, 32, 33, 34, 35]
        self.directCmds = ["Derivative2", "VFF2"]

    def change_axis(self, new_motor):
        self.currentMotor = new_motor
        if self.isVisible():
            self.axis_update()

    def tab_change(self):
        self.axis_update()

    # Updates I-variable line edits for this axis and I-variables listed in
    # ivars
    def _update_axis_setup_i_vars(self, ivars):
        ret_lst = []
        for i in range(len(ivars)):
            var_str = PpmacVars["Ix" + str(ivars[i])]
            cmd = (f"Motor[{self.currentMotor}].") + var_str
            (ret_str, success) = self.parent.pmac.sendCommand(cmd)
            if success:
                ret_lst.append(ret_str.strip("\r"))
            else:
                ret_lst.append("Error")
        if ret_lst:
            for i, ret_val in enumerate(ret_lst):
                exec(f'self.lneIx{ivars[i]}.setText(str("{ret_val}"))')

    def _update_axis_setup_direct_cmds(self, ppmac_cmds):
        ret_lst = []
        for i in range(len(ppmac_cmds)):
            var_str = PpmacVars[str(ppmac_cmds[i])]
            cmd = (f"Motor[{self.currentMotor}].") + var_str
            (ret_str, success) = self.parent.pmac.sendCommand(cmd)
            if success:
                ret_lst.append(ret_str.strip("\r"))
            else:
                ret_lst.append("Error")
        if ret_lst:
            for i, ret_val in enumerate(ret_lst):
                exec(f'self.lne{ppmac_cmds[i]}.setText(str("{ret_val}"))')

    def axis_update(self):
        self._update_axis_setup_i_vars(
            self.definitionIvars + self.safetyIvars + self.gainIvars
        )
        self._update_axis_setup_direct_cmds(self.directCmds)

    def set_axis_setup_i_var(self, i_var_no, new_value):
        var_str = PpmacVars["Ix" + str(i_var_no)]
        self.set_axis_setup_vars(var_str, new_value)

    def set_axis_setup_direct(self, direct_cmd, new_value):
        var_str = PpmacVars[direct_cmd]
        self.set_axis_setup_vars(var_str, new_value)

    def set_axis_setup_vars(self, var_str, new_value):
        cmd = (f"Motor[{self.currentMotor}].") + var_str + (f"={new_value}")
        (ret_str, success) = self.parent.pmac.sendCommand(cmd)
        if success:
            self.axis_update()
        else:
            print(f"cannot set value for Motor[{self.currentMotor}].{var_str}")

    # public slot
    @staticmethod
    def axis_close():
        print("axissettingsform.axisClose(): Not implemented yet")

    def send_ix11(self):
        self.set_axis_setup_i_var(11, self.lneIx11.text())
        self.axis_update()

    def send_ix12(self):
        self.set_axis_setup_i_var(12, self.lneIx12.text())
        self.axis_update()

    def send_ix13(self):
        self.set_axis_setup_i_var(13, self.lneIx13.text())
        self.axis_update()

    def send_ix14(self):
        self.set_axis_setup_i_var(14, self.lneIx14.text())
        self.axis_update()

    def send_ix15(self):
        self.set_axis_setup_i_var(15, self.lneIx15.text())
        self.axis_update()

    def send_ix16(self):
        self.set_axis_setup_i_var(16, self.lneIx16.text())
        self.axis_update()

    def send_ix17(self):
        self.set_axis_setup_i_var(17, self.lneIx17.text())
        self.axis_update()

    def send_ix19(self):
        self.set_axis_setup_i_var(19, self.lneIx19.text())
        self.axis_update()

    def send_ix20(self):
        self.set_axis_setup_i_var(20, self.lneIx20.text())
        self.axis_update()

    def send_ix21(self):
        self.set_axis_setup_i_var(21, self.lneIx21.text())
        self.axis_update()

    def send_ix22(self):
        self.set_axis_setup_i_var(22, self.lneIx22.text())
        self.axis_update()

    def send_ix23(self):
        self.set_axis_setup_i_var(23, self.lneIx23.text())
        self.axis_update()

    def send_ix25(self):
        self.set_axis_setup_i_var(25, self.lneIx25.text())
        self.axis_update()

    def send_ix26(self):
        self.set_axis_setup_i_var(26, self.lneIx26.text())
        self.axis_update()

    def send_ix30(self):
        self.set_axis_setup_i_var(30, self.lneIx30.text())
        self.axis_update()

    def send_ix31(self):
        self.set_axis_setup_i_var(31, self.lneIx31.text())
        self.axis_update()

    def send_ix32(self):
        self.set_axis_setup_i_var(32, self.lneIx32.text())
        self.axis_update()

    def send_ix33(self):
        self.set_axis_setup_i_var(33, self.lneIx33.text())
        self.axis_update()

    def send_ix34(self):
        self.set_axis_setup_i_var(34, self.lneIx34.text())
        self.axis_update()

    def send_ix35(self):
        self.set_axis_setup_i_var(35, self.lneIx35.text())
        self.axis_update()

    def send_derivative2(self):
        self.set_axis_setup_direct("Derivative2", self.lneDerivative2.text())
        self.axis_update()

    def send_vff2(self):
        self.set_axis_setup_direct("VFF2", self.lneVFF2.text())
        self.axis_update()
