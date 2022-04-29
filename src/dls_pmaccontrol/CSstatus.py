#!/bin/env dls-python2.6
# -*- coding: utf-8 -*-

import sys

from PyQt5.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QLabel

from dls_pmaccontrol.ui_formCSStatus import Ui_formCSStatus
from dls_pmaccontrol.ui_formPpmacCSStatus import Ui_formPpmacCSStatus

AmpStatusBits = {
    0: "No Error, Not Ready",
    64: "No Error, Ready",
    128: "Bus Under-Voltage Warning",
    192: "Over-Temperature (>70°C)",
    256: "I\u00b2T Warning/Fault, Not Ready",
    320: "I\u00b2T Warning/Fault, Ready",
    384: "Over-Current Fault",
}


class CSStatusForm(QDialog, Ui_formCSStatus):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.csSpin.valueChanged.connect(self.changeCS)
        self.feedSpin.valueChanged.connect(self.setFeed)

        self.greenLedOn = parent.greenLedOn
        self.greenLedOff = parent.greenLedOff
        self.redLedOn = parent.redLedOn
        self.redLedOff = parent.redLedOff
        self._feed = 100

        ledGroupLayout = self.ledGroup.layout()
        ledGroupLayout.setAlignment(Qt.AlignTop)
        self.lstLeds = []
        self.lstLabels = []
        self.lstLabelTexts = []
        self.lstTooltips = []

        # Extracted from manual
        # First Word Returned (X:$002040, X:$0020C0, etc.)
        # Bit 23
        self.lstLabelTexts.append("Z-CS Used in Feedrate Calculations")
        self.lstTooltips.append(
            """Used in Feedrate Calculations: This bit is
        1 if this CS is used in the vector feedrate
        calculations for F-based moves in the coordinate system; it is 0 if
        this CS is not used. See the FRAX
        command."""
        )
        # Bit 22
        self.lstLabelTexts.append("Z-CS Incremental Mode")
        self.lstTooltips.append(
            """Incremental Mode: This bit is 1 if this CS
        is in incremental mode -- moves specified by
        distance from the last programmed point. It is 0 if this CS is in
        absolute mode -- moves specified by end
        position, not distance. See the INC and ABS commands."""
        )
        # Bit 21
        self.lstLabelTexts.append("Y-CS Used in Feedrate Calculations")
        self.lstTooltips.append(self.lstTooltips[-2])
        # Bit 20
        self.lstLabelTexts.append("Y-CS Incremental Mode")
        self.lstTooltips.append(self.lstTooltips[-2])
        # Bit 19
        self.lstLabelTexts.append("X-CS Used in Feedrate Calculations")
        self.lstTooltips.append(self.lstTooltips[-2])
        # Bit 18
        self.lstLabelTexts.append("X-CS Incremental Mode")
        self.lstTooltips.append(self.lstTooltips[-2])
        # Bit 17
        self.lstLabelTexts.append("W-CS Used in Feedrate Calculations")
        self.lstTooltips.append(self.lstTooltips[-2])
        # Bit 16
        self.lstLabelTexts.append("W-CS Incremental Mode")
        self.lstTooltips.append(self.lstTooltips[-2])
        # Bit 15
        self.lstLabelTexts.append("V-CS Used in Feedrate Calculations")
        self.lstTooltips.append(self.lstTooltips[-2])
        # Bit 14
        self.lstLabelTexts.append("V-CS Incremental Mode")
        self.lstTooltips.append(self.lstTooltips[-2])
        # Bit 13
        self.lstLabelTexts.append("U-CS Used in Feedrate Calculations")
        self.lstTooltips.append(self.lstTooltips[-2])
        # Bit 12
        self.lstLabelTexts.append("U-CS Incremental Mode")
        self.lstTooltips.append(self.lstTooltips[-2])
        # Bit 11
        self.lstLabelTexts.append("C-CS Used in Feedrate Calculations")
        self.lstTooltips.append(self.lstTooltips[-2])
        # Bit 10
        self.lstLabelTexts.append("C-CS Incremental Mode")
        self.lstTooltips.append(self.lstTooltips[-2])
        # Bit 9
        self.lstLabelTexts.append("B-CS Used in Feedrate Calculations")
        self.lstTooltips.append(self.lstTooltips[-2])
        # Bit 8
        self.lstLabelTexts.append("B-CS Incremental Mode")
        self.lstTooltips.append(self.lstTooltips[-2])
        # Bit 7
        self.lstLabelTexts.append("A-CS Used in Feedrate Calculations")
        self.lstTooltips.append(self.lstTooltips[-2])
        # Bit 6
        self.lstLabelTexts.append("A-CS Incremental Mode")
        self.lstTooltips.append(self.lstTooltips[-2])
        # Bit 5
        self.lstLabelTexts.append("Radius Vector Incremental Mode")
        self.lstTooltips.append(
            """Radius Vector Incremental Mode: This bit is
        1 if circle move radius vectors are specified incrementally
        (i.e. from the move start point to the arc center). It is 0 if
        circle move radius vectors are specified absolutely (i.e. from
        the XYZ origin to the arc center). See the INC (R) and ABS (R)
        commands."""
        )
        # Bit 4
        self.lstLabelTexts.append("Continuous Motion Request")
        self.lstTooltips.append(
            """Continuous Motion Request: This bit is 1
        if the coordinate system has requested of it a
        continuous set of moves (e.g. with an R command). It is 0 if this is
        not the case (e.g. not running
        program, Isx92=1, or running under an S command)."""
        )
        # Bit 3
        self.lstLabelTexts.append("Move-Specified-by-Time Mode")
        self.lstTooltips.append(
            """Move-Specified-by-Time Mode: This bit is 1
        if programmed moves in this coordinate system are
        currently specified by time (TM or TA), and the move speed is derived.
        It is 0 if programmed moves in
        this coordinate system are currently specified by feedrate (speed; F)
        and the move time is derived."""
        )
        # Bit 2
        self.lstLabelTexts.append("Continuous Motion Mode")
        self.lstTooltips.append(
            """Continuous Motion Mode: This bit is 1 if
        the coordinate system is in a sequence of moves that it
        is blending together without stops in between. It is 0 if it is not
        currently in such a sequence, for whatever
        reason."""
        )
        # Bit 1
        self.lstLabelTexts.append("Single-Step Mode")
        self.lstTooltips.append(
            """Single-Step Mode: This bit is 1 if the
        motion program currently executing in this coordinate
        system has been told to step one move or block of moves, or if it has
        been given a Q (Quit) command. It
        is 0 if the motion program is executing a program by a R (run)
        command, or if it is not executing a motion
        program at all."""
        )
        # Bit 0
        self.lstLabelTexts.append("Running Program")
        self.lstTooltips.append(
            """Running Program: This bit is 1 if the
        coordinate system is currently executing a motion
        program. It is 0 if the C.S. is not currently executing a motion
        program. Note that it becomes 0 as soon
        as it has calculated the last move and reached the final RETURN
        statement in the program, even if the
        motors are still executing the last move or two that have been
        calculated. Compare to the motor Running
        Program status bit."""
        )
        # Second Word Returned (Y:$00203F, Y:$0020BF, etc.)
        # Bit 23
        self.lstLabelTexts.append("Lookahead in Progress")
        self.lstTooltips.append(
            """Lookahead in Progress: This bit is 1 when
        the coordinate system is actively computing and/or
        executing a move sequence using the multi-block lookahead function. It
        is 0 otherwise."""
        )
        # Bit 22
        self.lstLabelTexts.append("Run-Time Error")
        self.lstTooltips.append(
            """Run-Time Error: This bit is 1 when the
        coordinate system has stopped a motion program due to
        an error encountered while executing the program (e.g. jump to
        non-existent label, insufficient calculation
        time, etc.) It is 0 otherwise. The run-time error code word (
        Y:$002x14) shows the cause of a run-time
        error."""
        )
        # Bit 21
        self.lstLabelTexts.append("Move In Stack")
        self.lstTooltips.append("""Move In Stack: (For internal use)""")
        # Bit 20
        self.lstLabelTexts.append("Amplifier Fault Error")
        self.lstTooltips.append(
            """Amplifier Fault Error: This bit is 1 when
        any motor in the coordinate system has been killed due
        to receiving an amplifier fault signal. It is 0 at other times,
        changing from 1 to 0 when the offending
        motor is re-enabled."""
        )
        # Bit 19
        self.lstLabelTexts.append("Fatal Following Error")
        self.lstTooltips.append(
            """Fatal Following Error: This bit is 1 when
        any motor in the coordinate system has been killed
        due to exceeding its fatal following error limit (Ixx11). It is 0 at
        other times. The change from 1 to 0
        occurs when the offending motor is re-enabled."""
        )
        # Bit 18
        self.lstLabelTexts.append("Warning Following Error")
        self.lstTooltips.append(
            """Warning Following Error: This bit is 1
        when any motor in the coordinate system has exceeded
        its warning following error limit (Ixx12). It stays at 1 if a motor
        has been killed due to fatal following
        error limit. It is 0 at all other times. The change from 1 to 0 occurs
        when the offending motor's following
        error is reduced to under the limit, or if killed on fatal following
        error as well, when it is re-enabled."""
        )
        # Bit 17
        self.lstLabelTexts.append("In Position")
        self.lstTooltips.append(
            """In Position: This bit is 1 when all motors
        in the coordinate system are in position. Five
        conditions must apply for all of these motors for this to be true:,
        the loops must be closed, the desired
        velocity must be zero for all motors, the coordinate system cannot be
        in any timed move (even zero
        distance) or DWELL, all motors must have a following error smaller
        than their respective Ixx28 in-position
        bands, and the above conditions must have been satisfied for (Ixx88+1)
        consecutive scans."""
        )
        # Bit 16
        self.lstLabelTexts.append("Rotary Buffer Request")
        self.lstTooltips.append(
            """Rotary Buffer Request: This bit is 1 when
        a rotary buffer exists for the coordinate system and
        enough program lines have been sent to it so that the buffer contains
        at least I17 lines ahead of what has
        been calculated. Once this bit has been set to 1 it will not be set to
        0 until there are less than I16 program
        lines ahead of what has been calculated. The PR command may be used to
        find the current number of
        program lines ahead of what has been calculated."""
        )
        # Bit 15
        self.lstLabelTexts.append("Delayed Calculation Flag")
        self.lstTooltips.append("""Delayed Calculation Flag: (for internal use)""")
        # Bit 14
        self.lstLabelTexts.append("End of Block Stop")
        self.lstTooltips.append(
            """End of Block Stop: This bit is 1 when a
        motion program running in the currently addressed
        Coordinate System is stopped using the ' / ' command from a segmented
        move (Linear or Circular mode
        with Isx13 > 0)."""
        )
        # Bit 13
        self.lstLabelTexts.append("Synchronous M-variable One-Shot")
        self.lstTooltips.append(
            """Synchronous M-variable One-Shot: (for internal use)"""
        )
        # Bit 12
        self.lstLabelTexts.append("Dwell Move Buffered")
        self.lstTooltips.append("""Dwell Move Buffered: (for internal use)""")
        # Bit 11
        self.lstLabelTexts.append("Cutter Comp Outside Corner")
        self.lstTooltips.append(
            """Cutter Comp Outside Corner: This bit is 1
        when the coordinate system is executing an added
        outside corner move with cutter compensation on. It is 0 otherwise."""
        )
        # Bit 10
        self.lstLabelTexts.append("Cutter Comp Move Stop Request")
        self.lstTooltips.append(
            """Cutter Comp Move Stop Request: This bit is
        1 when the coordinate system is executing moves
        with cutter compensation enabled, and has been asked to stop move
        execution. This is primarily for
        internal use."""
        )
        # Bit 9
        self.lstLabelTexts.append("Cutter Comp Move Buffered")
        self.lstTooltips.append(
            """Cutter Comp Move Buffered: This bit is 1
        when the coordinate system is executing moves with
        cutter compensation enabled, and the next move has been calculated and
        buffered. This is primarily for
        internal use."""
        )
        # Bit 8
        self.lstLabelTexts.append("Pre-jog Move Flag")
        self.lstTooltips.append(
            """Pre-jog Move Flag: This bit is 1 when any
        motor in the coordinate system is executing a jog
        move to "pre-jog" position (J= command). It is 0 otherwise."""
        )
        # Bit 7
        self.lstLabelTexts.append("Segmented Move in Progress")
        self.lstTooltips.append(
            """Segmented Move in Progress: This bit is 1
        when the coordinate system is executing motion
        program moves in segmentation mode (Isx13>0). It is 0 otherwise. This
        is primarily for internal use."""
        )
        # Bit 6
        self.lstLabelTexts.append("Segmented Move Acceleration")
        self.lstTooltips.append(
            """Segmented Move Acceleration: This bit is 1
        when the coordinate system is executing motion
        program moves in segmentation mode (Isx13>0) and accelerating from a
        stop. It is 0 otherwise. This is
        primarily for internal use."""
        )
        # Bit 5
        self.lstLabelTexts.append("Segmented Move Stop Request")
        self.lstTooltips.append(
            """Segmented Move Stop Request: This bit is 1
        when the coordinate system is executing motion
        program move in segmentation mode (Isx13>0) and it is decelerating to
        a stop. It is 0 otherwise. This is
        primarily for internal use."""
        )
        # Bit 4
        self.lstLabelTexts.append("PVT/SPLINE Move Mode")
        self.lstTooltips.append(
            """PVT/SPLINE Move Mode: This bit is 1 if
        this coordinate system is in either PVT move mode or
        SPLINE move mode. (If bit 0 of this word is 0, this means PVT mode; if
        bit 0 is 1, this means SPLINE
        mode.) This bit is 0 if the coordinate system is in a different move
        mode (LINEAR, CIRCLE, or
        RAPID). See the table below."""
        )
        # Bit 3
        self.lstLabelTexts.append("2D Cutter Comp Left/3D Cutter Comp On")
        self.lstTooltips.append(
            """2D Cutter Comp Left/3D Cutter Comp On:
        With bit 2 equal to 1, this bit is 1 if the coordinate
        system has 2D cutter compensation on, compensating to the left when
        looking in the direction of motion.
        It is 0 if 2D compensation is to the right. With bit 2 equal to 0,
        this bit is 1 if the coordinate system has
        3D cutter compensation on. It is 0 if no cutter compensation is on."""
        )
        # Bit 2
        self.lstLabelTexts.append("2D Cutter Comp On")
        self.lstTooltips.append(
            """2D Cutter Comp On: This bit is 1 if the
        coordinate system has 2D cutter compensation on. It is
        0 if 2D cutter compensation is off (but 3D cutter compensation may be
        on if bit 3 is 1)."""
        )
        # Bit 1
        self.lstLabelTexts.append(r"CCW Circle\Rapid Mode")
        self.lstTooltips.append(
            r"""CCW Circle\Rapid Mode: When bit 0 is 1 and
        bit 4 is 0, this bit is set to 0 if the coordinate
        system is in CIRCLE1 (clockwise arc) move mode and 1 if the coordinate
        system is in CIRCLE2
        (counterclockwise arc) move mode. If both bits 0 and 4 are 0, this bit
        is set to 1 if the coordinate system
        is in RAPID move mode. Otherwise this bit is 0. See the table
        below."""
        )
        # Bit 0
        self.lstLabelTexts.append("CIRCLE/SPLINE Move Mode")
        self.lstTooltips.append(
            """CIRCLE/SPLINE Move Mode: This bit is 1 if
        the coordinate system is in either CIRCLE or
        SPLINE move mode. (If bit 4 of this word is 0, this means CIRCLE mode;
        if bit 4 is 1, this means
        SPLINE mode.) This bit is 0 if the coordinate system is in a different
        move mode (LINEAR, PVT, or
        RAPID.). See the table below."""
        )
        # Third Word Returned (Y:$002040, Y:$0020C0, etc.)
        # Bit 23
        self.lstLabelTexts.append("Lookahead Buffer Wrap")
        self.lstTooltips.append(
            """Lookahead Buffer Wrap: This bit is 1 when
        the lookahead buffer for the coordinate system is
        active and has wrapped around since the beginning of the current
        continuous motion sequence, meaning
        that retrace back to the beginning of the sequence is no longer
        possible. It is 0 otherwise."""
        )
        # Bit 22
        self.lstLabelTexts.append("Lookahead Lookback Active")
        self.lstTooltips.append("""Lookahead Lookback Active: (For internal use)""")
        # Bit 21
        self.lstLabelTexts.append("Lookahead Buffer End")
        self.lstTooltips.append("""Lookahead Buffer End: (For internal use)""")
        # Bit 20
        self.lstLabelTexts.append("Lookahead Synchronous M-variable")
        self.lstTooltips.append(
            """Lookahead Synchronous M-variable: (For internal use)"""
        )
        # Bit 19
        self.lstLabelTexts.append("Lookahead Synchronous M-variable Overflow")
        self.lstTooltips.append(
            """Lookahead Synchronous M-variable Overflow:
        This bit is 1 if the program has attempted to put
        more synchronous M-variable assignments into the lookahead buffer than
        the buffer has room for. If this
        bit is set, one or more synchronous M-variable assignments have failed
        to execute or will fail to execute."""
        )
        # Bit 18
        self.lstLabelTexts.append("Lookahead Buffer Direction")
        self.lstTooltips.append(
            """Lookahead Buffer Direction: This bit is 1
        if the lookahead buffer is executing in the reverse
        direction, or has executed a quick stop from the reverse direction. It
        is 0 if the lookahead buffer is
        executing in the forward direction, has executed a quick stop for the
        forward direction, or is not executing."""
        )
        # Bit 17
        self.lstLabelTexts.append("Lookahead Buffer Stop")
        self.lstTooltips.append(
            """Lookahead Buffer Stop: This bit is 1 if
        the lookahead buffer execution is stopping due to a
        quick-stop command or request. It is 0 otherwise."""
        )
        # Bit 16
        self.lstLabelTexts.append("Lookahead Buffer Change")
        self.lstTooltips.append(
            """Lookahead Buffer Change: This bit is 1 if
        the lookahead buffer is currently changing state
        between forward and reverse direction, or between executing and
        stopped. It is 0 otherwise.
        Fifteenth character returned:"""
        )
        # Bit 15
        self.lstLabelTexts.append("Lookahead Buffer Last Segment")
        self.lstTooltips.append(
            """Lookahead Buffer Last Segment: This bit is
        1 if the lookahead buffer is currently executing the
        last segment before the end of a sequence. It is 0 otherwise."""
        )
        # Bit 14
        self.lstLabelTexts.append("Lookahead Buffer Recalculate")
        self.lstTooltips.append(
            """Lookahead Buffer Recalculate: This bit is
        1 if the lookahead buffer is recalculating segments
        already in the buffer due to a change in the state of the buffer. It
        is 0 otherwise."""
        )
        # Bit 13
        self.lstLabelTexts.append("Lookahead Buffer Flush")
        self.lstTooltips.append(
            """Lookahead Buffer Flush: This bit is 1 if
        the lookahead buffer is executing segments but not
        adding any new segments. It is 0 otherwise."""
        )
        # Bit 12
        self.lstLabelTexts.append("Lookahead Buffer Last Move")
        self.lstTooltips.append(
            """Lookahead Buffer Last Move: This bit is 1
        if the last programmed move in the buffer has
        reached speed. It is 0 otherwise."""
        )
        # Bit 11
        self.lstLabelTexts.append("Lookahead Buffer Single-Segment Request")
        self.lstTooltips.append(
            """Lookahead Buffer Single-Segment Request:
        This bit can be set to 1 by the user as part of a
        request to change the state of the lookahead buffer. It should be set
        to 1 to request the buffer to move
        only a single segment from a stopped state (in either direction). It
        should be set to 0 otherwise. Turbo
        PMAC leaves this bit in the state of the last request, even after the
        request has been processed."""
        )
        # Bit 10
        self.lstLabelTexts.append("Lookahead Buffer Change Request")
        self.lstTooltips.append(
            """Lookahead Buffer Change Request: This bit
        can be set to 1 by the user to request a change in
        the state of the lookahead buffer. It remains at 1 until the Turbo
        PMAC processes the change, at which
        time Turbo PMAC changes it to 0."""
        )
        # Bit 9
        self.lstLabelTexts.append("Lookahead Buffer Movement Request")
        self.lstTooltips.append(
            """Lookahead Buffer Movement Request: This
        bit can be set by the user as part of a request to
        change the state of the lookahead buffer. It should be set to 1 to
        request the buffer to operate (in either the
        forward or reverse direction); it should be set to 0 to request the
        buffer to execute a quick stop. Turbo
        PMAC leaves this bit in the state of the last request, even after the
        request has been processed."""
        )
        # Bit 8
        self.lstLabelTexts.append("Lookahead Buffer Direction Request")
        self.lstTooltips.append(
            """Lookahead Buffer Direction Request: This
        bit can be set by the user as part of a request to
        change the state of the lookahead buffer. It should be set to 1 to
        request operation in the reverse direction;
        it should be set to 0 to request operation in the forward direction.
        Its state does not matter in a request to
        execute a quick stop. Turbo PMAC leaves this bit in the state of the
        last request, even after the request
        has been processed."""
        )
        # Bit 7
        self.lstLabelTexts.append("Reserved for future use" "")
        self.lstTooltips.append("""Reserved for future use""")
        # Bit 6
        self.lstLabelTexts.append("Reserved for future use" "")
        self.lstTooltips.append("""Reserved for future use""")
        # Bit 5
        self.lstLabelTexts.append("Reserved for future use" "")
        self.lstTooltips.append("""Reserved for future use""")
        # Bit 4
        self.lstLabelTexts.append("Reserved for future use" "")
        self.lstTooltips.append("""Reserved for future use""")
        # Bit 3
        self.lstLabelTexts.append("Radius Error")
        self.lstTooltips.append(
            """Radius Error: This bit is 1 when a motion
        program has been stopped because it was asked to do
        an arc move whose distance was more than twice the radius (by an
        amount greater than Ixx96)."""
        )
        # Bit 2
        self.lstLabelTexts.append("Program Resume Error")
        self.lstTooltips.append(
            """Program Resume Error: This bit is 1 when
        the user has tried to resume program operation after
        a feed-hold or quick-stop, but one or more of the motors in the
        coordinate system are not at the location of
        the feed-hold or quick-stop. It is 0 otherwise."""
        )
        # Bit 1
        self.lstLabelTexts.append("Desired Position Limit Stop")
        self.lstTooltips.append(
            """Desired Position Limit Stop: This bit is 1
        if the motion program in the coordinate system has
        stopped due to the desired position of a motor exceeding a limit."""
        )
        # Bit 0
        self.lstLabelTexts.append("In-Program PMATCH")
        self.lstTooltips.append(
            """In-Program PMATCH: This bit is 1 if Turbo
        PMAC is executing the PMATCH function
        automatically, as at the end of a move-until-trigger. It is 0
        otherwise. This bit is primarily for internal use."""
        )

        # Here are all the labels for the CSStatus bits defined.
        self.lstLabelTexts.reverse()
        self.lstTooltips.reverse()

        for word in range(1, 4):
            for bit in range(0, 24):
                i = 24 * (word - 1) + bit
                self.lstLeds.append(QLabel(self.ledGroup))
                self.lstLabels.append(
                    QLabel("Word%s Bit%s" % (word + 1, bit), self.ledGroup)
                )
                ledGroupLayout.addWidget(self.lstLeds[i], bit, word * 2)
                ledGroupLayout.addWidget(self.lstLabels[i], bit, word * 2 + 1)
                self.lstLeds[i].setPixmap(self.greenLedOff)
                self.lstLabels[i].setText(self.lstLabelTexts[i])
                self.lstLabels[i].setToolTip(self.lstTooltips[i])

    def changeCS(self, CS):
        self.parent().commsThread.CSNum = CS
        self.ledGroup.setTitle("CS " + str(CS))

    def updateFeed(self, feed):
        self._feed = feed
        # Check for integer overflow before updating
        if not self.feedSpin.hasFocus() and (abs(feed) < 2**32):
            self.feedSpin.setValue(feed)

    def setFeed(self, feed):
        if feed != self._feed:
            self.parent().pmac.sendCommand(
                "&%d%%%d" % (self.parent().commsThread.CSNum, feed)
            )

    def updateStatus(self, CSStatusHexWord):
        for bit in range(0, 72):
            bitMask = 1 << bit
            if bool(CSStatusHexWord & bitMask):
                self.lstLeds[bit].setPixmap(self.greenLedOn)
            else:
                self.lstLeds[bit].setPixmap(self.greenLedOff)

    def updateAmpStatus(self, value):
        if value in AmpStatusBits:
            strVal = AmpStatusBits[value]
        else:
            strVal = "Unknown status"
        self.lneAmpStatus.setText(strVal)


class PpmacCSStatusForm(QDialog, Ui_formPpmacCSStatus):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.csSpin.valueChanged.connect(self.changeCS)
        self.feedSpin.valueChanged.connect(self.setFeed)

        self.greenLedOn = parent.greenLedOn
        self.greenLedOff = parent.greenLedOff
        self.redLedOn = parent.redLedOn
        self.redLedOff = parent.redLedOff
        self._feed = 100

        ledGroupLayout = self.ledGroup.layout()
        ledGroupLayout.setAlignment(Qt.AlignTop)
        self.lstLeds = []
        self.lstLabels = []
        self.lstLabelTexts = []
        self.lstTooltips = []

        # Extracted from manual
        # Word 0: Bit 31 - Bit 0
        self.lstLabelTexts.append("TriggerMove")
        self.lstTooltips.append(
            """Trigger search move in progress (any motor in C.S.)"""
        )
        self.lstLabelTexts.append("HomeInprogress")
        self.lstTooltips.append("""Home search move in progress (any motor in C.S.)""")
        self.lstLabelTexts.append("MinusLimit")
        self.lstTooltips.append("""Hardware negative limit set (any motor in C.S.)""")
        self.lstLabelTexts.append("PlusLimit")
        self.lstTooltips.append("""Hardware positive limit set (any motor in C.S.)""")
        self.lstLabelTexts.append("FeWarn")
        self.lstTooltips.append("""Warning following error (any motor in C.S.)""")
        self.lstLabelTexts.append("FeFatal")
        self.lstTooltips.append("""Fatal following error (any motor in C.S.)""")
        self.lstLabelTexts.append("LimitStop")
        self.lstTooltips.append("""Stopped on hardware limit (any motor in C.S.)""")
        self.lstLabelTexts.append("AmpFault")
        self.lstTooltips.append("""Amplifier fault (any motor in C.S.)""")
        self.lstLabelTexts.append("SoftMinusLimit")
        self.lstTooltips.append("""Software negative limit set (any motor in C.S.)""")
        self.lstLabelTexts.append("SoftPlusLimit")
        self.lstTooltips.append("""Software positive limit set (any motor in C.S.)""")
        self.lstLabelTexts.append("I2tFault")
        self.lstTooltips.append(
            """Integrated current (I2T) fault (any motor in C.S.)"""
        )
        self.lstLabelTexts.append("TriggerNotFound")
        self.lstTooltips.append("""Trigger not found (any motor in C.S.)""")
        self.lstLabelTexts.append("AmpWarn")
        self.lstTooltips.append("""Amp warning (any motor in C.S.)""")
        self.lstLabelTexts.append("EncLoss")
        self.lstTooltips.append("""Encoder loss error (any motor in C.S.)""")
        self.lstLabelTexts.append("AuxFault")
        self.lstTooltips.append("""Auxiliary fault error (any motor in C.S.)""")
        self.lstLabelTexts.append("TimerEnabled")
        self.lstTooltips.append("""Move timer enabled""")
        self.lstLabelTexts.append("HomeComplete")
        self.lstTooltips.append("""Home complete (any motor in C.S.)""")
        self.lstLabelTexts.append("DesVelZero")
        self.lstTooltips.append("""Desired velocity zero (any motor in C.S.)""")
        self.lstLabelTexts.append("ClosedLoop")
        self.lstTooltips.append("""Closed-loop mode (any motor in C.S.)""")
        self.lstLabelTexts.append("AmpEna")
        self.lstTooltips.append("""Amplifier enabled (any motor in C.S.)""")
        self.lstLabelTexts.append("InPos")
        self.lstTooltips.append("""In position (any motor in C.S.)""")
        self.lstLabelTexts.append("InterlockStop")
        self.lstTooltips.append("""Stopped on interlock (any motor in C.S.)""")
        self.lstLabelTexts.append("BlockRequest")
        self.lstTooltips.append("""Block request flag set""")
        self.lstLabelTexts.append("TimersEnabled")
        self.lstTooltips.append("""Timers enabled""")
        self.lstLabelTexts.append("RadiusError (bit 1) / ErrorStatus (bit 7)")
        self.lstTooltips.append(
            """XX/YY/ZZ-axis circle radius error / Error word bit 7 """
        )
        self.lstLabelTexts.append("RadiusError (bit 0) / ErrorStatus (bit 6)")
        self.lstTooltips.append("""X/Y/Z-axis circle radius error / Error word bit 6""")
        self.lstLabelTexts.append("SoftLimit / ErrorStatus (bit 5)")
        self.lstTooltips.append(
            """Stopped on software position limit (any motor in C.S.) /
 Error word bit 5"""
        )
        self.lstLabelTexts.append("RunTimeError / ErrorStatus (bit 4)")
        self.lstTooltips.append("""Run time error / Error word bit 4""")
        self.lstLabelTexts.append("PvtError / ErrorStatus (bit 3)")
        self.lstTooltips.append("""PVT mode error / Error word bit 3""")
        self.lstLabelTexts.append("LinToPvtError / ErrorStatus (bit 2)")
        self.lstTooltips.append("""Linear-to-PVT mode error / Error word bit 2 """)
        self.lstLabelTexts.append("ErrorStatus (bit 1)")
        self.lstTooltips.append("""Buffer error / Error word bit 1 """)
        self.lstLabelTexts.append("ErrorStatus (bit 0)")
        self.lstTooltips.append(
            """Synchronous assignment buffer error / Error word bit 0"""
        )

        # Word 1: Bit 31 - Bit 0
        self.lstLabelTexts.append("Csolve")
        self.lstTooltips.append(
            """Valid coordinate system axis definition for PMATCH """
        )
        self.lstLabelTexts.append("LinToPvtBuf")
        self.lstTooltips.append("""Linear-to-PVT move buffered""")
        self.lstLabelTexts.append("FeedHold (bit 1)")
        self.lstTooltips.append("""Feed hold accel/decel """)
        self.lstLabelTexts.append("FeedHold (bit 0)")
        self.lstTooltips.append("""Feed hold time base source""")
        self.lstLabelTexts.append("BlockActive")
        self.lstTooltips.append("""Block active""")
        self.lstLabelTexts.append("ContMotion")
        self.lstTooltips.append("""Continuous motion request""")
        self.lstLabelTexts.append("CCMode (bit 1)")
        self.lstTooltips.append("""Cutter comp mode bit 1""")
        self.lstLabelTexts.append("CCMode (bit 0)")
        self.lstTooltips.append("""Cutter comp mode bit 0""")
        self.lstLabelTexts.append("MoveMode (bit 1)")
        self.lstTooltips.append(
            """Move mode bit 1 (=0 for blended and spline, 1 for rapid and pvt
 modes) """
        )
        self.lstLabelTexts.append("MoveMode (bit 0)")
        self.lstTooltips.append(
            """Move mode bit 0 (=0 for blended and pvt, 1 for rapid and spline
 modes) """
        )
        self.lstLabelTexts.append("SegMove (bit 1)")
        self.lstTooltips.append("""Segmented PVT-mode move in progress""")
        self.lstLabelTexts.append("SegMove (bit 0)")
        self.lstTooltips.append("""Segmented linear-mode move in progress""")
        self.lstLabelTexts.append("SegMoveAccel")
        self.lstTooltips.append("""First segment move""")
        self.lstLabelTexts.append("SegMoveDecel")
        self.lstTooltips.append("""Last segment move""")
        self.lstLabelTexts.append("SegEnabled")
        self.lstTooltips.append("""Segmentation enabled""")
        self.lstLabelTexts.append("SegStopReq")
        self.lstTooltips.append("""Segment stop request""")
        self.lstLabelTexts.append("LookAheadWrap / LHStatus (bit 7) ")
        self.lstTooltips.append("""Lookahead wrap""")
        self.lstLabelTexts.append("LookAheadLookBack / LHStatus (bit 6) ")
        self.lstTooltips.append("""Lookahead lookback""")
        self.lstLabelTexts.append("LookAheadDir / LHStatus (bit 5) ")
        self.lstTooltips.append("""Lookahead direction""")
        self.lstLabelTexts.append("LookAheadStop / LHStatus (bit 4)")
        self.lstTooltips.append("""Lookahead stop""")
        self.lstLabelTexts.append("LookAheadChange / LHStatus (bit 3)")
        self.lstTooltips.append("""Lookahead change""")
        self.lstLabelTexts.append("LookAheadReCalc / LHStatus (bit 2) ")
        self.lstTooltips.append("""Lookahead recalculation""")
        self.lstLabelTexts.append("LookAheadFlush / LHStatus (bit 1) ")
        self.lstTooltips.append("""Lookahead flush""")
        self.lstLabelTexts.append("LookAheadActive / LHStatus (bit 0) ")
        self.lstTooltips.append("""Lookahead active""")
        self.lstLabelTexts.append("CCAddedArc")
        self.lstTooltips.append("""Cutter comp added arc""")
        self.lstLabelTexts.append("CCOffReq")
        self.lstTooltips.append("""Cutter comp turn-off request""")
        self.lstLabelTexts.append("reserved")
        self.lstTooltips.append("""(Reserved)""")
        self.lstLabelTexts.append("CCMoveType (bit 1)")
        self.lstTooltips.append("""Cutter comp move type bit 1""")
        self.lstLabelTexts.append("CCMoveType (bit 0)")
        self.lstTooltips.append("""Cutter comp move type bit 0""")
        self.lstLabelTexts.append("CC3Active")
        self.lstTooltips.append("""3D cutter comp active""")
        self.lstLabelTexts.append("SharpCornerStop")
        self.lstTooltips.append("""Blending disabled for sharp corner""")
        self.lstLabelTexts.append("AddedDwellDis")
        self.lstTooltips.append("""Added dwell disable """)
        # Here are all the labels for the CSStatus bits defined.
        self.lstLabelTexts.reverse()
        self.lstTooltips.reverse()

        for word in range(1, 5):
            for bit in range(0, 16):
                i = 16 * (word - 1) + bit
                self.lstLeds.append(QLabel(self.ledGroup))
                self.lstLabels.append(
                    QLabel("Word%s Bit%s" % (word + 1, bit), self.ledGroup)
                )
                ledGroupLayout.addWidget(self.lstLeds[i], bit, word * 2)
                ledGroupLayout.addWidget(self.lstLabels[i], bit, word * 2 + 1)
                self.lstLeds[i].setPixmap(self.greenLedOff)
                self.lstLabels[i].setText(self.lstLabelTexts[i])
                self.lstLabels[i].setToolTip(self.lstTooltips[i])

    def changeCS(self, CS):
        self.parent().commsThread.CSNum = CS
        self.ledGroup.setTitle("CS " + str(CS))

    def updateFeed(self, feed):
        self._feed = feed
        if not self.feedSpin.hasFocus():
            self.feedSpin.setValue(feed)

    def setFeed(self, feed):
        if feed != self._feed:
            self.parent().pmac.sendCommand(
                "&%d%%%d" % (self.parent().commsThread.CSNum, feed)
            )

    def updateStatus(self, CSStatusHexWord):
        for bit in range(0, 64):
            bitMask = 1 << bit
            if bool(CSStatusHexWord & bitMask):
                self.lstLeds[bit].setPixmap(self.greenLedOn)
            else:
                self.lstLeds[bit].setPixmap(self.greenLedOff)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a, pyqtSignal("lastWindowClosed()"), a, pyqtSlot("quit()"))  # type: ignore # noqa
    w = CSStatusForm(None)
    a.setMainWidget(w)  # type: ignore
    w.show()
    a.exec_loop()  # type: ignore
