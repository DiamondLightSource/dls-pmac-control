# -*- coding: utf-8 -*-

import sys

from PyQt5.Qt import QApplication
from PyQt5.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QDialog, QLabel

from dls_pmaccontrol.ui_formStatus import Ui_formStatus


class Statusform(QDialog, Ui_formStatus):
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
        # Bits 0 - 47
        self.lstLabelTexts.append("In position")
        self.lstLabelTexts.append("Warning Following Error")
        self.lstLabelTexts.append("Fatal Following Error")
        self.lstLabelTexts.append("Amplifier Fault Error")

        self.lstLabelTexts.append("Backlash Direction Flag")
        self.lstLabelTexts.append("I2T Amplifier Fault Error")
        self.lstLabelTexts.append("Integrated Fatal Following Error")
        self.lstLabelTexts.append("Trigger Move")

        self.lstLabelTexts.append("Phasing Reference Error")
        self.lstLabelTexts.append("Phasing Search/Read Active")
        self.lstLabelTexts.append("Home Complete")
        self.lstLabelTexts.append("Stopped on Position Limit")

        self.lstLabelTexts.append("Stopped on Desired Position Limit")
        self.lstLabelTexts.append("Foreground In-Position")
        self.lstLabelTexts.append("reserved for future use")
        self.lstLabelTexts.append("Assigned to C.S.")

        self.lstLabelTexts.append("Coordinate Definition bit 0")
        self.lstLabelTexts.append("Coordinate Definition bit 1")
        self.lstLabelTexts.append("Coordinate Definition bit 2")
        self.lstLabelTexts.append("Coordinate Definition bit 3")

        self.lstLabelTexts.append("(C.S. -1) Number (LSB)")
        self.lstLabelTexts.append("(C.S. -1) Number")
        self.lstLabelTexts.append("(C.S. -1) Number")
        self.lstLabelTexts.append("(C.S. -1) Number (MSB)")

        self.lstLabelTexts.append("Maximum Rapid Speed")
        self.lstLabelTexts.append("Alternate Command-Output Mode")
        self.lstLabelTexts.append("Software Position Capture")
        self.lstLabelTexts.append("Error Trigger")

        self.lstLabelTexts.append("Following Enabled")
        self.lstLabelTexts.append("Following Offset Mode")
        self.lstLabelTexts.append("Phased Motor")
        self.lstLabelTexts.append("Alternate Source/Destination")

        self.lstLabelTexts.append("User-Written Servo Enable")
        self.lstLabelTexts.append("User-Written Phase Enable")
        self.lstLabelTexts.append("Home Search in Progress")
        self.lstLabelTexts.append("Block Request")

        self.lstLabelTexts.append("Abort Deceleration")
        self.lstLabelTexts.append("Desired velocity zero")
        self.lstLabelTexts.append("Data block error")
        self.lstLabelTexts.append("Dwell in progress")

        self.lstLabelTexts.append("Integration mode")
        self.lstLabelTexts.append("Move timer active")
        self.lstLabelTexts.append("Open loop mode")
        self.lstLabelTexts.append("Amplifier enabled")

        self.lstLabelTexts.append("Ext. servo algorithm enabled")
        self.lstLabelTexts.append("Positive limit set")
        self.lstLabelTexts.append("Negative limit set")
        self.lstLabelTexts.append("Motor activated")

        self.lstTooltips.append(
            """In Position: This bit is 1 when five
        conditions are satisfied: the loop is closed, the desired
velocity zero bit is 1 (which requires closed-loop control and no commanded
move); the
program timer is off (not currently executing any move, DWELL, or DELAY),
the magnitude of
the following error is smaller than Ix28.and the first four conditions have
been satisfied for
(I7+1) consecutive scans."""
        )
        self.lstTooltips.append(
            """Warning Following Error: This bit is 1 if
        the following error for the motor exceeds its warning
following error limit (Ix12). It stays at 1 if the motor is killed due to
fatal following error. It is
0 at all other times, changing from 1 to 0 when the motor’s following error
reduces to under the
limit, or if killed, is re-enabled. """
        )
        self.lstTooltips.append(
            """Fatal Following Error: This bit is 1 if
        this motor has been disabled because it exceeded its fatal
following error limit (Ix11) or because it exceeded its integrated following
error limit (Ix63; in
which case bit 6 is also set). It is 0 at all other times, becoming 0 again
when the motor is reenabled. """
        )
        self.lstTooltips.append(
            """Amplifier Fault Error: This bit is 1 if
        this motor has been disabled because of an amplifier fault
signal, even if the amplifier fault signal has gone away, or if this motor
has been disabled due to
an I2T integrated current fault (in which case bit 5 is also set). It is 0 at
all other times,
becoming 0 again when the motor is re-enabled. """
        )
        self.lstTooltips.append(
            """Backlash Direction Flag: This bit is 1 if
        backlash has been activated in the negative direction.
It is 0 otherwise. """
        )
        self.lstTooltips.append(
            """I2T Amplifier Fault Error: This bit is 1
        if this motor has been disabled by an integrated current
fault. The amplifier fault bit (bit 3) will also be set in this case. Bit 5
is 0 at all other times,
becoming 0 again when the motor is re-enabled. """
        )
        self.lstTooltips.append(
            """Integrated Fatal Following Error: This bit
        is 1 if this motor has been disabled due to an
integrated following error fault, as set by Ix11 and Ix63. The fatal
following error bit (bit 2)
will also be set in this case. Bit 6 is zero at all other times, becoming 0
again when the motor is
re-enabled. """
        )
        self.lstTooltips.append(
            """Trigger Move: This bit is set to 1 at the
        beginning of a jog-until-trigger or motion program
move-until-trigger. It is set to 0 at the end of the move if the trigger has
been found, but
remains at 1 if the move ends with no trigger found. This bit is useful to
determine whether the
move was successful in finding the trigger. """
        )
        self.lstTooltips.append(
            """Phasing Reference Error: This bit is set
        to 1 on power-up/reset for a PMAC-commutated (Ixx01
bit 0 = 1) synchronous motor. It is also set to 1 at the beginning of a
phasing search move or phasing
absolute position read for such a motor. It is set to 0 on the successful
completion of a phasing search
move or phasing absolute position read. If this bit is 1,
the position/velocity servo loop cannot be closed
for this motor.
This bit is set to 1 if the phasing search move for a Turbo PMAC-commutated
motor has failed due to
amplifier fault, overtravel limit, or lack of detected motion. It is set to 0
if the phasing search move did
not fail by any of these conditions (not an absolute guarantee of a
successful phasing search). """
        )
        self.lstTooltips.append(
            """Phasing Search/Read Active: This bit is
        set to 1 if the phasing search move or phasing absolute
position read is currently ongoing for the motor. It is set to 0 otherwise. """
        )
        self.lstTooltips.append(
            """Home Complete: This bit, set to 0 on
        power-up or reset, becomes 1 when the homing move
successfully locates the home trigger. At this point in time the motor is
usually decelerating to a
stop or moving to an offset from the trigger determined by Ix26. If a second
homing move is
done, this bit is set to 0 at the beginning of the move, and only becomes 1
again if that homing
move successfully locates the home trigger. Use the Desired Velocity Zero bit
and/or the In
Position bit to monitor for the end of motor motion. """
        )
        self.lstTooltips.append(
            """Stopped on Position Limit: This bit is 1
        if this motor has stopped because of either a software
or a hardware position (overtravel) limit, even if the condition that caused
the stop has gone
away. It is 0 at all other times, even when into a limit but moving out of
it. """
        )

        self.lstTooltips.append(
            """Stopped on Desired Position Limit: This
        bit is 1 if the motor has stopped because the desired
position has exceeded the software overtravel limit parameters (Ixx24 bit 15
must be 1 to enable this
function). It is 0 otherwise. """
        )
        self.lstTooltips.append(
            """Foreground In-Position: This bit is 1 when
        the foreground in-position checking is enabled with
I13=1 and when four conditions are satisfied: the loop is closed, the desired
velocity zero bit is 1 (which
requires closed-loop control and no commanded move); the program timer is off
(not currently executing
any move, DWELL, or DELAY), and the magnitude of the following error is
smaller than Ixx28. It is 0
otherwise. """
        )
        self.lstTooltips.append("""(Reserved for future use) """)
        self.lstTooltips.append(
            """Assigned to C.S.: This bit is 1 when the
        motor has been assigned to an axis in any coordinate
system through an axis definition statement. It is 0 when the motor is not
assigned to an axis in any
coordinate system. """
        )

        self.lstTooltips.append(
            """Coordinate Definition: These four bits
        tell what axis or axes this motor has been
assigned to in an axis definition statement. The following values are
currently used:
0: No definition
1: Assigned to A-axis
2: Assigned to B-axis
3: Assigned to C-axis
4: Assigned to UVW axes
5: Assigned to I (inverse kinematic)
7: Assigned to XYZ axes """
        )
        self.lstTooltips.append(
            """Coordinate Definition: These four bits
        tell what axis or axes this motor has been
assigned to in an axis definition statement. The following values are
currently used:
0: No definition
1: Assigned to A-axis
2: Assigned to B-axis
3: Assigned to C-axis
4: Assigned to UVW axes
5: Assigned to I (inverse kinematic)
7: Assigned to XYZ axes """
        )
        self.lstTooltips.append(
            """Coordinate Definition: These four bits
        tell what axis or axes this motor has been
assigned to in an axis definition statement. The following values are
currently used:
0: No definition
1: Assigned to A-axis
2: Assigned to B-axis
3: Assigned to C-axis
4: Assigned to UVW axes
5: Assigned to I (inverse kinematic)
7: Assigned to XYZ axes"""
        )
        self.lstTooltips.append(
            """Coordinate Definition: These four bits
        tell what axis or axes this motor has been
assigned to in an axis definition statement. The following values are
currently used:
0: No definition
1: Assigned to A-axis
2: Assigned to B-axis
3: Assigned to C-axis
4: Assigned to UVW axes
5: Assigned to I (inverse kinematic)
7: Assigned to XYZ axes """
        )

        self.lstTooltips.append(
            """(C.S. - 1) Number: These three bits
        together hold a value equal to the (Coordinate System
number minus one) to which the motor is assigned. Bit 22 is the MSB, and bit
20 is the LSB.
For instance, if the motor is assigned to an axis in C. S. 6, these bits
would hold a value of 5: bit
22 =1, bit 21 = 0, and bit 20 = 1. """
        )
        self.lstTooltips.append(
            """(C.S. - 1) Number: These three bits
        together hold a value equal to the (Coordinate System
number minus one) to which the motor is assigned. Bit 22 is the MSB, and bit
20 is the LSB.
For instance, if the motor is assigned to an axis in C. S. 6, these bits
would hold a value of 5: bit
22 =1, bit 21 = 0, and bit 20 = 1. """
        )
        self.lstTooltips.append(
            """(C.S. - 1) Number: These three bits
        together hold a value equal to the (Coordinate System
number minus one) to which the motor is assigned. Bit 22 is the MSB, and bit
20 is the LSB.
For instance, if the motor is assigned to an axis in C. S. 6, these bits
would hold a value of 5: bit
22 =1, bit 21 = 0, and bit 20 = 1. """
        )
        self.lstTooltips.append(
            """(C.S. - 1) Number: These three bits
        together hold a value equal to the (Coordinate System
number minus one) to which the motor is assigned. Bit 22 is the MSB, and bit
20 is the LSB.
For instance, if the motor is assigned to an axis in C. S. 6, these bits
would hold a value of 5: bit
22 =1, bit 21 = 0, and bit 20 = 1. """
        )

        self.lstTooltips.append(
            """Maximum Rapid Speed: This bit is 1 when
        Ixx90 is set to 1 and the motor uses its Ixx16
maximum speed parameter for RAPID moves. It is 0 when Ixx90 is set to 0 and
the motor uses its Ixx22
jog speed parameter for RAPID moves. """
        )
        self.lstTooltips.append(
            """Alternate Command-Output Mode: This bit is
        1 when Ixx96 is set to 1 and the motor’s
commands are output in the alternate mode. If Ixx01 bit 0 is 1, this means
that open-loop directmicrostepping
commutation is performed instead of the normal closed-loop commutation. If
Ixx01 bit 0
is 0, this means that the motor’s non-commutated output is formatted as a
sign-and-magnitude signal pair,
instead of a single bipolar signal output. This bit is 0 when Ixx96 is set to
0 and the motor’s commands
are output in the standard mode. """
        )
        self.lstTooltips.append(
            """Software Position Capture: This bit is 1
        when Ixx97 bit 0 is set to 1 and the motor’s triggered
moves use a software-captured position as the reference for the post-trigger
move. It is 0 when Ixx97 bit
0 is set to 0 and the motor’s triggered moves use the hardware-captured
counter position as the reference
for the post-trigger move. """
        )
        self.lstTooltips.append(
            """Error Trigger: This bit is 1 when Ixx97
        bit 1 is set to 1 and the motor’s triggered moves trigger
on the warning following error limit being exceeded. Itis 0 when Ixx97 bit 1
is set to 0 and the motor’s
triggered moves trigger on a specified input flag state. """
        )

        self.lstTooltips.append(
            """Following Enabled: This bit is 1 when
        Ixx06 bit 0 is 1 and position following for this axis is
enabled; it is 0 when Ixx06 bit 0is 0 and position following is disabled.
Sixth character returned: """
        )
        self.lstTooltips.append(
            """Following Offset Mode: This bit is 1 when
        Ixx06 bit 1 is 1 and position following is executed in
“offset mode”, in which the motor’s programming reference position moves with
the following. This bit
is 0 when Ixx06 bit 1 is 0 and position following is executed in “normal
mode”, in which the motor’s
programming reference does not move with the following. """
        )
        self.lstTooltips.append(
            """Phased Motor: This bit is 1 when Ixx01 bit
        0 is 1 and this motor is being commutated by Turbo
PMAC; it is 0 when Ixx01 bit 0 is 0 and this motor is not being commutated by
Turbo PMAC. """
        )
        self.lstTooltips.append(
            """Alternate Source/Destination: This bit is
        1 when Ixx01 bit 1 is 1 and an alternate source or
destination for the motor algorithms is used. If Ixx01 bit 0 is 0, this means
that the motor writes its
command to an X-register instead of the standard Y-register. If Ixx01 bit 0
is 1, this means that the motor
reads its commutation feedback from a Y-register instead of the standard
X-register. This bit is 0 when
Ixx01 bit 1 is 0, and the standard source or destination is used for the
motor. """
        )

        self.lstTooltips.append(
            """User-Written Servo Enable: This bit is 1
        when Ixx59 bit 0 for the motor is set to 1 and the motor
executes the user-written servo routine instead of the normal servo routine.
It is 0 when Ixx59 bit 0 is 0
and the motor executes the normal servo routine. """
        )
        self.lstTooltips.append(
            """User-Written Phase Enable: This bit is 1
        when Ixx59 bit 1 for the motor is set to 1 and the motor
executes the user-written phase routine instead of the normal phase routine.
It is 0 when Ixx59 bit 1 is 0
and the motor executes the normal phase routine. """
        )
        self.lstTooltips.append(
            """Home Search in Progress: This bit is set
        to 1 when the motor is in a move searching for a
trigger: a homing search move, a jog-until trigger, or a motion program
move-until-trigger. It
becomes 1 as soon as the calculations for the move have started, and becomes
zero again as
soon as the trigger has been found, or if the move is stopped by some other
means. This is not
a good bit to observe to see if the full move is complete, because it will be
0 during the posttrigger
portion of the move. Use the Home Complete and Desired Velocity Zero bits
instead. """
        )
        self.lstTooltips.append(
            """Block Request: This bit is 1 when the
        motor has just entered a new move section, and is
requesting that the upcoming section be calculated. It is 0 otherwise. It is
primarily for internal
use. """
        )

        self.lstTooltips.append(
            """Abort Deceleration: This bit is 1 if the
        motor is decelerating due to an Abort command, or due
to hitting hardware or software position (overtravel) limits. It is 0
otherwise. It changes from 1
to 0 when the commanded deceleration to zero velocity finishes. """
        )
        self.lstTooltips.append(
            """Desired Velocity Zero: This bit is 1 if
        the motor is in closed-loop control and the commanded
velocity is zero (i.e. it is trying to hold position). It is zero either if
the motor is in closed-loop
mode with non-zero commanded velocity, or if it is in open-loop mode. """
        )
        self.lstTooltips.append(
            """Data Block Error: This bit is 1 when move
        execution has been aborted because the data for the
next move section was not ready in time. This is due to insufficient
calculation time. It is 0
otherwise. It changes from 1 to 0 when another move sequence is started. This
is related to the
Run Time Error Coordinate System status bit. """
        )
        self.lstTooltips.append(
            """Dwell in Progress: This bit is 1 when the
        motor’s coordinate system is executing a DWELL
instruction. It is 0 otherwise. """
        )
        self.lstTooltips.append(
            """Integration Mode: This bit is 1 when Ix34
        is 1 and the servo loop integrator is only active when
desired velocity is zero. It is 0 when Ix34 is 0 and the servo loop
integrator is always active. """
        )
        self.lstTooltips.append(
            """Running Definite-Time Move: This bit is 1
        when the motor is executing any move with a
predefined end-point and end-time. This includes any motion program move
dwell or delay,
any jog-to-position move, and the portion of a homing search move after the
trigger has been
found. It is 0 otherwise. It changes from 1 to 0 when execution of the
commanded move
finishes. """
        )
        self.lstTooltips.append(
            """Open Loop Mode: This bit is 1 when the
        servo loop for the motor is open, either with outputs
enabled or disabled (killed). (Refer to Amplifier Enabled status bit to
distinguish between the
two cases.) It is 0 when the servo loop is closed (under position control,
always with outputs
enabled). """
        )
        self.lstTooltips.append(
            """Phased Motor: This bit is 1 when Ix01 is 1
        and this motor is being commutated by PMAC; it is
0 when Ix01 is 0 and this motor is not being commutated by PMAC. """
        )
        self.lstTooltips.append(
            """Handwheel Enabled: This bit is 1 when Ix06
        is 1 and position following for this axis is
enabled; it is 0 when Ix06 is 0 and position following is disabled. """
        )
        self.lstTooltips.append(
            """Positive End Limit Set: This bit is 1 when
        motor actual position is greater than the software
positive position limit (Ix13), or when the hardware limit on this end (-LIMn
-- note!) has been
tripped; it is 0 otherwise. If the motor is deactivated (bit 23 of the first
motor status word set to
zero) or killed (bit 14 of the second motor status word set to zero) this bit
is not updated. """
        )
        self.lstTooltips.append(
            """Negative End Limit Set: This bit is 1 when
        motor actual position is less than the software
negative position limit (Ix14), or when the hardware limit on this end (+LIMn
-- note!) has
been tripped; it is 0 otherwise. If the motor is deactivated (bit 23 of the
first motor status word
set to zero) or killed (bit 14 of the second motor status word set to zero)
this bit is not updated. """
        )
        self.lstTooltips.append(
            """Motor Activated: This bit is 1 when Ix00
        is 1 and the motor calculations are active; it is 0 when
Ix00 is 0 and motor calculations are deactivated. """
        )
        self.lstTooltips.append(""" """)
        self.lstTooltips.append(""" """)
        self.lstTooltips.append(""" """)
        self.lstTooltips.append(""" """)

        for bit in range(0, 48):
            self.lstLeds.append(QLabel(self.ledGroup))
            self.lstLabels.append(QLabel("bit: " + str(bit), self.ledGroup))

        for bit in range(0, 48):
            if bit < 24:
                row = bit
                ledGroupLayout.addWidget(self.lstLeds[bit], row, 0)
                ledGroupLayout.addWidget(self.lstLabels[bit], row, 1)
            else:
                row = bit - 24
                ledGroupLayout.addWidget(self.lstLeds[bit], row, 2)
                ledGroupLayout.addWidget(self.lstLabels[bit], row, 4)

            self.lstLeds[bit].setPixmap(self.greenLedOff)
            self.lstLabels[bit].setText(self.lstLabelTexts[bit])
            self.lstLabels[bit].setToolTip(self.lstTooltips[bit])

    def changeAxis(self, axis):
        self.currentAxis = axis
        self.ledGroup.setTitle("Axis " + str(axis))

    def updateStatus(self, statusHexWord):
        for bit in range(0, 48):
            bitMask = 1 << bit
            if bool(statusHexWord & bitMask):
                self.lstLeds[bit].setPixmap(self.greenLedOn)
            else:
                self.lstLeds[bit].setPixmap(self.greenLedOff)


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
        # Word 1: Bits 0 - 31
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

        # Word 0: Bits 0 -31

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
        self.lstTooltips.append(
            """Soft limit direction: This bit is set to 1 if the most recent move stopped,
 modified, or rejected due to a software position limit was affected because of
 the negative soft limit. It is 0 if such move was limited by the positive soft
 limit, or if no suchlimiting has occurred since power-on/reset. """
        )

        self.lstTooltips.append(
            """Backlash direction: This bit is 1 if the motor’s backlash function is enabled and
 the motor is executing or has most recently executed a position move in the negative
 direction. It is 0 otherwise. """
        )
        self.lstTooltips.append(
            """Servo output limited: This bit is 1 if the motor’s servo output command
 value is presently saturated to the magnitude of Motor[x].MaxDac.
 It is 0 otherwise. """
        )
        self.lstTooltips.append(
            """Stopped on software position limit: This bit is 1 if the motor has stopped, or
 if the present move will be stopped, because it reached or will reach either
 its positive or negative software overtravel limit, even if it is presently
 not in that limit. It is 0 at all other times, including when into a limit,
 but moving out of it. """
        )
        self.lstTooltips.append(
            """Motor used in PMATCH calculations: This bit is set to 1 if this motor’s
 position is used to calculate axis positions in a coordinate-system “pmatch” (position
 match) function (at motion-program start, pmatch command execution, axis
 position/velocity/following-error query). It is 0 when the motor has a “null”
 definition or a redundant axis definition, and so is not used in these calculations."""
        )

        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append("""{Reserved for future use} """)

        self.lstTooltips.append(
            """Spindle definition bit 0: This bit is set to 1 if this motor is defined
 as a spindle axis and uses either the defined coordinate system’s time base (S)
 or a fixed %100 time base (S1). It is set to 0 if the motor is not defined as a
 spindle axis, or if it is defined as a spindle axis using C.S. 0’s time base (S0). """
        )
        self.lstTooltips.append(
            """Spindle definition bit 1: This bit is set to 1 if this motor is defined
 as a spindle axis and uses either C.S. 0’s time base (S0) or a fixed %100 time
 base (S1). It is set to 0 if the motor is not defined as a spindle axis, or if
 it is defined as a spindle axis using the defined coordinate system’s time
 base (S). """
        )
        self.lstTooltips.append(
            """Gantry homing complete: This bit is set to 1 if this motor is a follower
 in a leader/follower gantry system, the home triggers for both leader and follower
 motors have been found, and the skew between motors has been fully removed. It is 0
 otherwise. """
        )
        self.lstTooltips.append(
            """Trigger Speed Select: This bit is set to 1 during a move-until-trigger
 if the move is done at the velocity specified by Motor[x].MaxSpeed. It is set to 0 if
 the move is done at the velocity specified by Motor[x].JogSpeed. """
        )

        self.lstTooltips.append(
            """Phase reference established: This bit is set to 0 on power-up/reset for
 a motor (Motor[x].PhaseCtrl bit 0 or bit 2 = 1) commutated by Power PMAC that is
 synchronous (Motor[x].DtOverRotorTc = 0.0). It is set to 1 if a phase reference is
 properly established for the motor, either with a phasing-search move, or an absolute
 position read. """
        )
        self.lstTooltips.append(
            """Block request flag set: This bit is set to 1 if the motor has just
 entered a new move section, and is requesting that the equations for the next upcoming
 move section for the motion queue be calculated. It is 0 otherwise. It is primarily
 for internal use. """
        )
        self.lstTooltips.append(
            """Stopped on interlock: This bit is set to 1 if the motor has been stopped
 from executing a commanded move because Motor[x].MinusInterlock or
 Motor[x].PlusInterlock was set. It is 0 otherwise. """
        )
        self.lstTooltips.append(
            """In position: This bit is set to 1 when all of the conditions for
 “in position” are satisified: the motor is closed-loop, the desired velocity is zero,
 the move timer is not active (no move, dwell, or delay being executed, the magnitude
 of the following error is less than or equal to Motor[x].InPosBand, and all of these
 conditions have been true for (Motor[x].InPosTime – 1) consecutive servo cycles. It
 is 0 otherwise. """
        )

        self.lstTooltips.append(
            """Amplifier Enabled: This bit is set to 1 if the motor is enabled
 (in closed-loop or open-loop control). Note that there does not need to be an active
 amplifier-enable output signal in this case. This bit is 0 if the motor is disabled."""
        )
        self.lstTooltips.append(
            """Closed-loop mode: This bit is set to 1 if the motor is in closed-loop
 control. It is zero if the motor is in open-loop mode (enabled or disabled). """
        )
        self.lstTooltips.append(
            """Desired velocity zero: This bit is set to 1 if the motor is in closed-loop
 control and the commanded velocity is zero (i.e. it is trying to hold position), or it
 is in open-loop mode (enabled or disabled) with the actual velocity exactly equal to
 zero. It is zero either if the motor is in closed-loop mode with non-zero commanded
 velocity, or if it is in open-loop mode with non-zero actual velocity."""
        )
        self.lstTooltips.append(
            """Position reference established: This bit is set to 1 if a position
 reference is properly established for the motor, either with a homing-search move,
 or an absolute position read. It is automatically set to 0 at power-up/reset, and
 at the beginning of a homing-search move. In a homing-search move, it is set to 1
 when the pre-specified trigger condition is found, which is before the post-trigger
 portion of the move is complete. """
        )

        self.lstTooltips.append("""{Reserved for future use} """)
        self.lstTooltips.append(
            """Auxiliary fault error: This bit is 1 if the motor has been disabled
 because an auxiliary fault error has been detected. It is 0 at all other times,
 becoming 0 again when the motor is re-enabled."""
        )
        self.lstTooltips.append(
            """Encoder loss error: This bit is 1 if the motor has been disabled
 because an encoder loss error has been detected. It is 0 at all other times,
 becoming 0 again when the motor is re-enabled. """
        )
        self.lstTooltips.append(
            """Amplifier warning: This bit is set to 1 if Motor[x].AmpFaultLevel
 bit 1 (value 2) is set to 1, requiring two consecutive readings of the amplifier
 fault bit in its specified fault state to trigger an error, and there has been one
 reading of the amplifier fault bit in its fault state. """
        )

        self.lstTooltips.append(
            """Trigger not found: This bit is set to 1 if a jog-until-trigger or
 program rapid-mode move-until-trigger ends without the pre-specified trigger
 condition being found. This is not an error condition, but subsequent actions will
 often depend on whether this bit is set or not. It is 0 at all other times,
 changing back to 0 when the next move is started. """
        )
        self.lstTooltips.append(
            """Integrated current (I2T) fault: This bit is set to 1 when the motor
 has been disabled from exceeding its integrated current limit as set by
 Motor[x].I2tTrip. The amplifier fault bit (bit 24) will also be set in this case.
 It will be 0 at all other times, becoming 0 when the motor is re-enabled. (Note
 that if the amplifier faults due to its own integrated current fault calculations,
 this bit will not be set.) """
        )
        self.lstTooltips.append(
            """Software positive limit set: This bit is set to 1 when the motor has
 reached or exceeded its positive software limit as set by Motor[x].MaxPos (which must
 be greater than Motor[x].MinPos to be active). It is 0 otherwise, even if the motor
 is still stopped from having hit this limit previously. """
        )
        self.lstTooltips.append(
            """Software negative limit set: This bit is set to 1 when the motor has
 reached or exceeded its negative software limit as set by Motor[x].MinPos (which must
 be less than Motor[x].MaxPos to be active). It is 0 otherwise, even if the motor is
 still stopped from having hit this limit previously. """
        )

        self.lstTooltips.append(
            """Amplifier fault error: This bit is 1 if the motor has been disabled
 because of an amplifier fault error, even if the amplifier fault signal condition is
 no longer present, or because of a calculated “I2T” integrated current fault
 (in which case bit 21 is also set). It is 0 at all other times, becoming 0 again when
 the motor is re-enabled. """
        )
        self.lstTooltips.append(
            """Stopped on hardware position limit: This bit is 1 if the motor has
 stopped because it hit either its positive or negative hardware overtravel limit,
 even if it is presently not in that limit. It is 0 at all other times, including
 when into a limit, but moving out of it. """
        )
        self.lstTooltips.append(
            """Fatal following error: This bit is 1 if the motor has been disabled
 because the magnitude of the following error for the motor has exceeded its fatal
 following error limit as set by Motor[x].FatalFeLimit. It is 0 at all other times,
 becoming 0 again when the motor is re-enabled.  """
        )
        self.lstTooltips.append(
            """Warning following error: This bit is 1 if the magnitude of the
 following error for the motor exceeds its warning following error limit as set by
 Motor[x].WarnFeLimit. It is 0 if the magnitude of the following error is less than
 this limit, or if the motor has been disabled due to exceeding its fatal following
 error limit. """
        )

        self.lstTooltips.append(
            """Hardware positive limit set: This bit is set to 1 when the motor is
 presently in its positive hardware limit. It is 0 otherwise, even if the motor is
 still stopped from having hit this limit previously. """
        )
        self.lstTooltips.append(
            """Hardware negative limit set: This bit is set to 1 when the motor is
 presently in its negative hardware limit. It is 0 otherwise, even if the motor is
 still stopped from having hit this limit previously. """
        )
        self.lstTooltips.append(
            """Home search move in progress: This bit is set to 1 at the beginning of
 a homing search move. It is set to 0 when the pre-specified trigger condition is
 found and the post-trigger move is started, or when the move ends without a trigger
 being found. """
        )
        self.lstTooltips.append(
            """Trigger search move in progress: This bit is set to 1 at the beginning
 of a move-until-trigger (homing search, jog-until-trigger, program rapid-mode
 move-until-trigger). It is set to 0 when the pre-specified trigger condition is found
 and the post-trigger move is started, or when the move ends without a trigger being
 found. """
        )

        for bit in range(0, 64):
            self.lstLeds.append(QLabel(self.ledGroup))
            self.lstLabels.append(QLabel("bit: " + str(bit), self.ledGroup))

        for bit in range(0, 64):
            if bit < 16:
                row = bit
                ledGroupLayout.addWidget(self.lstLeds[bit], row, 0)
                ledGroupLayout.addWidget(self.lstLabels[bit], row, 1)
            elif bit < 32:
                row = bit - 16
                ledGroupLayout.addWidget(self.lstLeds[bit], row, 2)
                ledGroupLayout.addWidget(self.lstLabels[bit], row, 3)
            elif bit < 48:
                row = bit - 32
                ledGroupLayout.addWidget(self.lstLeds[bit], row, 4)
                ledGroupLayout.addWidget(self.lstLabels[bit], row, 5)
            else:
                row = bit - 48
                ledGroupLayout.addWidget(self.lstLeds[bit], row, 6)
                ledGroupLayout.addWidget(self.lstLabels[bit], row, 7)

            self.lstLeds[bit].setPixmap(self.greenLedOff)
            self.lstLabels[bit].setText(self.lstLabelTexts[bit])
            self.lstLabels[bit].setToolTip(self.lstTooltips[bit])

    def changeAxis(self, axis):
        self.currentAxis = axis
        self.ledGroup.setTitle("Axis " + str(axis))

    def updateStatus(self, statusHexWord):
        for bit in range(0, 64):
            bitMask = 1 << bit
            if bool(statusHexWord & bitMask):
                self.lstLeds[bit].setPixmap(self.greenLedOn)
            else:
                self.lstLeds[bit].setPixmap(self.greenLedOff)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a, pyqtSignal("lastWindowClosed()"), a, pyqtSlot("quit()"))  # type: ignore # noqa
    w = Statusform(None, None)
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
