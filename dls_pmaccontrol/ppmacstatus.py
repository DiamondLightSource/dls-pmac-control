# -*- coding: utf-8 -*-

import sys

from PyQt5.Qt import QApplication
from PyQt5.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QDialog, QLabel

from dls_pmaccontrol.ui_formStatus import Ui_formStatus


class PpmacStatusform(QDialog, Ui_formStatus):
    def __init__(self, parent, axis):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.currentAxis = axis
        self.greenLedOn = parent.greenLedOn
        self.greenLedOff = parent.greenLedOff
        self.redLedOn = parent.redLedOn
        self.redLedOff = parent.redLedOff

        self.ledGroup.setTitle("Axis " + str(axis))

        ledGroupLayout = self.ledGroup.layout()
        ledGroupLayout.setAlignment(Qt.AlignTop)
        self.lstLeds = []
        self.lstLabels = []
        self.lstLabelTexts = []
        self.lstTooltips = []

        # Here are all the labels for the status bits defined.
        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")

        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")

        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")

        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")

        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")

        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")

        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("SoftLimitDir")

        self.lstLabelTexts.append("BlDir")
        self.lstLabelTexts.append("DacLimit")
        self.lstLabelTexts.append("SoftLimit")
        self.lstLabelTexts.append("Csolve")

        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("reserved")

        self.lstLabelTexts.append("SpindleMotor bit 0")
        self.lstLabelTexts.append("SpindleMotor bit 1")
        self.lstLabelTexts.append("GantryHomed")
        self.lstLabelTexts.append("TriggerSpeedSel")

        self.lstLabelTexts.append("PhaseFound")
        self.lstLabelTexts.append("BlockRequest")
        self.lstLabelTexts.append("InterlockStop")
        self.lstLabelTexts.append("InPos")

        self.lstLabelTexts.append("AmpEna")
        self.lstLabelTexts.append("ClosedLoop")
        self.lstLabelTexts.append("DesVelZero")
        self.lstLabelTexts.append("HomeComplete")

        self.lstLabelTexts.append("reserved")
        self.lstLabelTexts.append("AuxFault")
        self.lstLabelTexts.append("EncLoss")
        self.lstLabelTexts.append("AmpWarn")

        self.lstLabelTexts.append("TriggerNotFound")
        self.lstLabelTexts.append("I2tFault")
        self.lstLabelTexts.append("SoftPlusLimit")
        self.lstLabelTexts.append("SoftMinusLimit")

        self.lstLabelTexts.append("AmpFault")
        self.lstLabelTexts.append("LimitStop")
        self.lstLabelTexts.append("FeFatal")
        self.lstLabelTexts.append("FeWarn")

        self.lstLabelTexts.append("PlusLimit")
        self.lstLabelTexts.append("MinusLimit")
        self.lstLabelTexts.append("HomeInProgress")
        self.lstLabelTexts.append("TriggerMove")

        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)

        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)

        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)

        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)

        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)

        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)

        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""Soft limit direction: This bit is set to 1 if the most recent move stopped, 
modified, or rejected due to a software position limit was affected because of the negative soft 
limit. It is 0 if such move was limited by the positive soft limit, or if no such limiting has occurred 
since power-on/reset. """)

        self.lstTooltips.append("""Backlash direction: This bit is 1 if the motor’s backlash function is enabled and 
the motor is executing or has most recently executed a position move in the negative direction. It 
is 0 otherwise. """)
        self.lstTooltips.append("""Servo output limited: This bit is 1 if the motor’s servo output command 
value is presently saturated to the magnitude of Motor[x].MaxDac. It is 0 otherwise. """)
        self.lstTooltips.append("""Stopped on software position limit: This bit is 1 if the motor has stopped, or 
if the present move will be stopped, because it reached or will reach either its positive or negative 
software overtravel limit, even if it is presently not in that limit. It is 0 at all other times, including 
when into a limit, but moving out of it. """)
        self.lstTooltips.append("""Motor used in PMATCH calculations: This bit is set to 1 if this motor’s 
position is used to calculate axis positions in a coordinate-system “pmatch” (position match) 
function (at motion-program start, pmatch command execution, axis 
position/velocity/following-error query). It is 0 when the motor has a “null” definition or a 
redundant axis definition, and so is not used in these calculations. """)

        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)

        self.lstTooltips.append("""Spindle definition bit 0: This bit is set to 1 if this motor is defined 
as a spindle axis and uses either the defined coordinate system’s time base (S) or a fixed %100 time base (S1). It is set to 0 if the motor is not defined as a spindle axis, or if it is defined as a 
spindle axis using C.S. 0’s time base (S0). """)
        self.lstTooltips.append("""Spindle definition bit 1: This bit is set to 1 if this motor is defined 
as a spindle axis and uses either C.S. 0’s time base (S0) or a fixed %100 time base (S1). It is set 
to 0 if the motor is not defined as a spindle axis, or if it is defined as a spindle axis using the 
defined coordinate system’s time base (S). """)
        self.lstTooltips.append("""Gantry homing complete: This bit is set to 1 if this motor is a follower 
in a leader/follower gantry system, the home triggers for both leader and follower motors have 
been found, and the skew between motors has been fully removed. It is 0 otherwise. """)
        self.lstTooltips.append("""Trigger Speed Select: This bit is set to 1 during a move-until-trigger 
if the move is done at the velocity specified by Motor[x].MaxSpeed. It is set to 0 if the move is 
done at the velocity specified by Motor[x].JogSpeed. """)

        self.lstTooltips.append("""Phase reference established: This bit is set to 0 on power-up/reset for a 
motor (Motor[x].PhaseCtrl bit 0 or bit 2 = 1) commutated by Power PMAC that is synchronous 
(Motor[x].DtOverRotorTc = 0.0). It is set to 1 if a phase reference is properly established for 
the motor, either with a phasing-search move, or an absolute position read. """)
        self.lstTooltips.append("""Block request flag set: This bit is set to 1 if the motor has just entered a 
new move section, and is requesting that the equations for the next upcoming move section for 
the motion queue be calculated. It is 0 otherwise. It is primarily for internal use. """)
        self.lstTooltips.append("""Stopped on interlock: This bit is set to 1 if the motor has been stopped 
from executing a commanded move because Motor[x].MinusInterlock or 
Motor[x].PlusInterlock was set. It is 0 otherwise. """)
        self.lstTooltips.append("""In position: This bit is set to 1 when all of the conditions for “in position” are 
satisified: the motor is closed-loop, the desired velocity is zero, the move timer is not active (no 
move, dwell, or delay being executed, the magnitude of the following error is less than or equal to 
Motor[x].InPosBand, and all of these conditions have been true for (Motor[x].InPosTime – 1) 
consecutive servo cycles. It is 0 otherwise. """)
        
        self.lstTooltips.append("""Amplifier Enabled: This bit is set to 1 if the motor is enabled (in closed-loop 
or open-loop control). Note that there does not need to be an active amplifier-enable output signal 
in this case. This bit is 0 if the motor is disabled. """)
        self.lstTooltips.append("""Closed-loop mode: This bit is set to 1 if the motor is in closed-loop 
control. It is zero if the motor is in open-loop mode (enabled or disabled). """)
        self.lstTooltips.append("""Desired velocity zero: This bit is set to 1 if the motor is in closed-loop 
control and the commanded velocity is zero (i.e. it is trying to hold position), or it is in open-loop 
mode (enabled or disabled) with the actual velocity exactly equal to zero. It is zero either if the 
motor is in closed-loop mode with non-zero commanded velocity, or if it is in open-loop mode 
with non-zero actual velocity. """)
        self.lstTooltips.append("""Position reference established: This bit is set to 1 if a position 
reference is properly established for the motor, either with a homing-search move, or an absolute 
position read. It is automatically set to 0 at power-up/reset, and at the beginning of a homing-
search move. In a homing-search move, it is set to 1 when the pre-specified trigger condition is 
found, which is before the post-trigger portion of the move is complete. """)

        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""Auxiliary fault error: This bit is 1 if the motor has been disabled because an 
auxiliary fault error has been detected. It is 0 at all other times, becoming 0 again when the motor 
is re-enabled. """)
        self.lstTooltips.append("""Encoder loss error: This bit is 1 if the motor has been disabled because an 
encoder loss error has been detected. It is 0 at all other times, becoming 0 again when the motor is 
re-enabled. """)
        self.lstTooltips.append("""Amplifier warning: This bit is set to 1 if Motor[x].AmpFaultLevel bit 1 
(value 2) is set to 1, requiring two consecutive readings of the amplifier fault bit in its specified 
fault state to trigger an error, and there has been one reading of the amplifier fault bit in its fault 
state. """)

        self.lstTooltips.append("""Trigger not found: This bit is set to 1 if a jog-until-trigger or 
program rapid-mode move-until-trigger ends without the pre-specified trigger condition being 
found. This is not an error condition, but subsequent actions will often depend on whether this bit 
is set or not. It is 0 at all other times, changing back to 0 when the next move is started. """)
        self.lstTooltips.append("""Integrated current (I2T) fault: This bit is set to 1 when the motor has been 
disabled from exceeding its integrated current limit as set by Motor[x].I2tTrip. The amplifier 
fault bit (bit 24) will also be set in this case. It will be 0 at all other times, becoming 0 when the 
motor is re-enabled. (Note that if the amplifier faults due to its own integrated current fault 
calculations, this bit will not be set.) """)
        self.lstTooltips.append("""Software positive limit set: This bit is set to 1 when the motor has 
reached or exceeded its positive software limit as set by Motor[x].MaxPos (which must be 
greater than Motor[x].MinPos to be active). It is 0 otherwise, even if the motor is still stopped 
from having hit this limit previously. """)
        self.lstTooltips.append("""Software negative limit set: This bit is set to 1 when the motor has 
reached or exceeded its negative software limit as set by Motor[x].MinPos (which must be less 
than Motor[x].MaxPos to be active). It is 0 otherwise, even if the motor is still stopped from 
having hit this limit previously. """)

        self.lstTooltips.append("""Amplifier fault error: This bit is 1 if the motor has been disabled because of 
an amplifier fault error, even if the amplifier fault signal condition is no longer present, or because of a calculated “I2T” integrated current fault (in which case bit 21 is also set). It is 0 at all other times, becoming 0 again when the motor is re-enabled. """)
        self.lstTooltips.append("""Stopped on hardware position limit: This bit is 1 if the motor has stopped 
because it hit either its positive or negative hardware overtravel limit, even if it is presently not in 
that limit. It is 0 at all other times, including when into a limit, but moving out of it. """)
        self.lstTooltips.append("""Fatal following error: This bit is 1 if the motor has been disabled because the 
magnitude of the following error for the motor has exceeded its fatal following error limit as set 
by Motor[x].FatalFeLimit. It is 0 at all other times, becoming 0 again when the motor is re-
enabled.  """)
        self.lstTooltips.append("""Warning following error: This bit is 1 if the magnitude of the following error 
for the motor exceeds its warning following error limit as set by Motor[x].WarnFeLimit. It is 0 
if the magnitude of the following error is less than this limit, or if the motor has been disabled due 
to exceeding its fatal following error limit. """)

        self.lstTooltips.append("""Hardware positive limit set: This bit is set to 1 when the motor is presently in its positive hardware limit. It is 0 otherwise, even if the motor is still stopped from having hit this limit previously. """)
        self.lstTooltips.append("""Hardware negative limit set: This bit is set to 1 when the motor is presently in its negative hardware limit. It is 0 otherwise, even if the motor is still stopped from having hit this limit previously. """)
        self.lstTooltips.append("""Home search move in progress: This bit is set to 1 at the beginning of a homing search move. It is set to 0 when the pre-specified trigger condition is found and the post-trigger move is started, or when the move ends without a trigger being found. """)
        self.lstTooltips.append("""Trigger search move in progress: This bit is set to 1 at the beginning of a move-until-trigger (homing search, jog-until-trigger, program rapid-mode move-until-trigger). It is set to 0 when the pre-specified trigger condition is found and the post-trigger move is started, or when the move ends without a trigger being found. """)

        for bit in range(0, 64):
            self.lstLeds.append(QLabel(self.ledGroup))
            self.lstLabels.append(QLabel("bit: " + str(bit), self.ledGroup))

        for bit in range(0, 64):
            if bit < 32:
                row = bit
                ledGroupLayout.addWidget(self.lstLeds[bit], row, 0)
                ledGroupLayout.addWidget(self.lstLabels[bit], row, 1)
            else:
                row = bit - 32
                ledGroupLayout.addWidget(self.lstLeds[bit], row, 2)
                ledGroupLayout.addWidget(self.lstLabels[bit], row, 4)

            self.lstLeds[bit].setPixmap(self.greenLedOff)
            self.lstLabels[bit].setText(self.lstLabelTexts[bit])
            self.lstLabels[bit].setToolTip(self.lstTooltips[bit])

    def changeAxis(self, axis):
        self.currentAxis = axis
        self.ledGroup.setTitle("Axis " + str(axis))

    def updateStatus(self, statusHexWord):
        # print "update status: dec = " + str(statusHexWord)
        for bit in range(0, 64):
            bitMask = 1 << bit
            if bool(statusHexWord & bitMask):
                self.lstLeds[bit].setPixmap(self.greenLedOn)
            else:
                self.lstLeds[bit].setPixmap(self.greenLedOff)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a, pyqtSignal("lastWindowClosed()"), a, pyqtSlot("quit()"))
    w = Statusform(None, None)
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
