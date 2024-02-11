# -*- coding: utf-8 -*-
import sys

from PyQt5.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QLabel

from dls_pmaccontrol.ui_formGlobalStatus import Ui_formGlobalStatus


class GlobalStatusForm(QDialog, Ui_formGlobalStatus):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.greenLedOn = parent.greenLedOn
        self.greenLedOff = parent.greenLedOff
        self.redLedOn = parent.redLedOn
        self.redLedOff = parent.redLedOff

        ledGroupLayout = self.ledGroup.layout()
        ledGroupLayout.setAlignment(Qt.AlignTop)
        self.lstLeds = []
        self.lstLabels = []
        self.lstLabelTexts = []
        self.lstTooltips = []
        # First Word Returned (X:$000006):
        # Bit 23
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        # Bit 22
        self.lstLabelTexts.append("Real-Time Interrupt Re-entry")
        self.lstTooltips.append(
            """Real-Time Interrupt Re-entry: This bit is
        1 if a real-time interrupt task has taken long enough so
        that it was still executing when the next real-time interrupt came (
        I8+1 servo cycles later). It stays at 1
        until the card is reset, or until this bit is manually changed to 0.
        If motion program calculations cause this
        it is not a serious problem. If PLC 0 causes this (no motion programs
        running) it could be serious."""
        )
        # Bit 21
        self.lstLabelTexts.append("CPU Type Bit 1")
        self.lstTooltips.append(
            """CPU Type Bit 1: This bit is 1 if the Turbo
        PMAC has an Option 5Ex DSP56311 or an Option
        5Fx DSP56321 processor. It is 0 if it has an Option 5Cx DSP56303 or an
        Option 5Dx DSP56309
        processor. In both cases, bit 21 in the second word returned (
        Y:$000006) distinguishes between
        processor types."""
        )
        # Bit 20
        self.lstLabelTexts.append("Servo Error")
        self.lstTooltips.append(
            """Servo Error: This bit is 1 if Turbo PMAC
        could not properly complete its servo routines. This is
        a serious error condition. It is 0 if the servo operations have been
        completing properly."""
        )
        # Bit 19
        self.lstLabelTexts.append("Data Gathering Function On")
        self.lstTooltips.append(
            """Data Gathering Function On: This bit is 1
        when the data gathering function is active; it is 0
        when the function is not active."""
        )
        # Bit 18
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        # Bit 17
        self.lstLabelTexts.append("Data Gather to Start on Trigger")
        self.lstTooltips.append(
            """Data Gather to Start on Trigger: This bit
        is 1 when the data gathering function is set up to start
        on the rising edge of Machine Input 2. It is 0 otherwise. It changes
        from 1 to 0 as soon as the gathering
        function actually starts."""
        )
        # Bit 16
        self.lstLabelTexts.append("Servo Request")
        self.lstTooltips.append("""Servo Request: (Internal use).""")
        # Bit 15
        self.lstLabelTexts.append("Watchdog Timer")
        self.lstTooltips.append("""Watchdog Timer: (Internal use)""")
        # Bit 14
        self.lstLabelTexts.append("Leadscrew Compensation On")
        self.lstTooltips.append(
            """Leadscrew Compensation On: This bit is 1
        if leadscrew compensation is currently active in
        Turbo PMAC. It is 0 if the compensation is not active."""
        )
        # Bit 13
        self.lstLabelTexts.append("Any Memory Checksum Error")
        self.lstTooltips.append(
            """Any Memory Checksum Error: This bit is 1
        if a checksum error has been detected for either the
        Turbo PMAC firmware or the user program buffer space. Bit 12 of this
        word distinguishes between the
        two cases."""
        )
        # Bit 12
        self.lstLabelTexts.append("PROM Checksum Active")
        self.lstTooltips.append(
            """PROM Checksum Active: This bit is 1 if
        Turbo PMAC is currently evaluating a firmware
        checksum (Bit 13 = 0), or has found a firmware checksum error (Bit 13
        = 1). It is 0 if Turbo PMAC is
        evaluating a user program checksum (Bit 13 = 0), or has found a user
        program checksum error (Bit 13 = 1)."""
        )
        # Bit 11
        self.lstLabelTexts.append("DPRAM Error")
        self.lstTooltips.append(
            """DPRAM Error: This bit is 1 if Turbo PMAC
        detected an error in its automatic DPRAM check
        function at power-up/reset due to missing or defective DPRAM. It is 0
        otherwise."""
        )
        # Bit 10
        self.lstLabelTexts.append("Flash Error")
        self.lstTooltips.append(
            """Flash Error: This bit is 1 if Turbo PMAC
        detected a checksum error in reading saved data from
        the flash memory on board reset. It is 0 otherwise.
        Turbo PMAC/PMAC2 Software Reference
        Turbo PMAC On-Line Command Specification 321"""
        )
        # Bit 9
        self.lstLabelTexts.append("Real-Time Interrupt Warning")
        self.lstTooltips.append(
            """Real-Time Interrupt Warning: This bit is 1
        if a real-time interrupt task (motion program or PLC
        0) has taken more than one interrupt period: a possible sign of CPU
        loading problems. It is 0 otherwise."""
        )
        # Bit 8
        self.lstLabelTexts.append("Illegal L-Variable Definition")
        self.lstTooltips.append(
            """Illegal L-Variable Definition: This bit is
        1 if a compiled PLC has failed because it used an Lvariable
        pointer that accessed an illegal M-variable definition. It is 0
        otherwise."""
        )
        # Bit 7
        self.lstLabelTexts.append("Configuration Error")
        self.lstTooltips.append("""Configuration Error: (For internal use)""")
        # Bit 6
        self.lstLabelTexts.append("TWS Variable Parity Error")
        self.lstTooltips.append(
            """TWS Variable Parity Error: This bit is 1
        if the most recent TWS-format M-variable read or
        write operation with a device supporting parity had a parity error; it
        is 0 if the operation with such a
        device had no parity error. The bit status is indeterminate if the
        operation was with a device that does not
        support parity."""
        )
        # Bit 5
        self.lstLabelTexts.append("MACRO Auxiliary Communications Error")
        self.lstTooltips.append(
            """MACRO Auxiliary Communications Error: This
        bit is 1 if the most recent MACRO auxiliary
        read or write command has failed. It is set to 0 at the beginning of
        each MACRO auxiliary read or write
        command."""
        )
        # Bit 4
        self.lstLabelTexts.append("MACRO Ring Check Error")
        self.lstTooltips.append(
            """MACRO Ring Check Error: This bit is 1 if
        the MACRO ring check function is enabled (I80 > 0)
        and Turbo PMAC has either detected at least I81 ring communication
        errors in an I80-servo-cycle period,
        or has failed to detect the receipt of I82 ring sync packets."""
        )
        # Bit 3
        self.lstLabelTexts.append("Phase Clock Missing")
        self.lstTooltips.append(
            """Phase Clock Missing: This bit is set to 1
        if the CPU received no hardware-generated phase clock
        from a source external to it (Servo IC, MACRO IC, or through serial
        port). If this bit is set, no motor may
        be enabled (starting in V1.940). This bit is 0 otherwise."""
        )
        # Bit 2
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        # Bit 1
        self.lstLabelTexts.append("All Cards Addressed")
        self.lstTooltips.append(
            """All Cards Addressed: This bit is set to 1
        if all cards on a serial daisychain have been addressed
        simultaneously with the @@ command. It is 0 otherwise."""
        )
        # Bit 0
        self.lstLabelTexts.append("This Card Addressed")
        self.lstTooltips.append(
            """This Card Addressed: This bit is set to 1
        if this card is on a serial daisychain and has been
        addressed with the @n command. It is 0 otherwise."""
        )
        # Second Word Returned (Y:$000006)
        # Bit 23
        self.lstLabelTexts.append("Turbo Ultralite")
        self.lstTooltips.append(
            """Turbo Ultralite: This bit is 1 if Turbo
        PMAC has detected that it is an Ultralite PMAC2 with no
        Servo ICs on board. It is 0 if Turbo PMAC has detected that it has
        Servo ICs on board."""
        )
        # Bit 22
        self.lstLabelTexts.append("Turbo VME")
        self.lstTooltips.append(
            """Turbo VME: This bit is 1 if Turbo PMAC has
        detected that it has a VME bus interface on board.
        It is 0 otherwise."""
        )
        # Bit 21
        self.lstLabelTexts.append("CPU Type Bit 0")
        self.lstTooltips.append(
            """CPU Type Bit 0: This bit is 1 if the Turbo
        PMAC has an Option 5Dx DSP56309 or an Option 5Fx
        DSP56321 processor. It is 0 if it has an Option 5Cx DSP56303 or an
        Option 5Dx DSP56311 processor. In
        both cases, bit 21 in the first word returned (X:$000006)
        distinguishes between processor types."""
        )
        # Bit 20
        self.lstLabelTexts.append("Binary Rotary Buffers Open")
        self.lstTooltips.append(
            """Binary Rotary Buffers Open: This bit is 1
        if the rotary motion program buffers on Turbo PMAC
        are open for binary-format entry through the DPRAM. It is 0
        otherwise."""
        )
        # Bit 19
        self.lstLabelTexts.append("Motion Buffer Open")
        self.lstTooltips.append(
            """Motion Buffer Open: This bit is 1 if any
        motion program buffer (PROG or ROT) is open for
        entry. It is 0 if none of these buffers is open."""
        )
        # Bit 18
        self.lstLabelTexts.append("ASCII Rotary Buffer Open")
        self.lstTooltips.append(
            """ASCII Rotary Buffer Open: This bit is 1 if
        the rotary motion program buffers on Turbo PMAC
        are open for ASCII-format entry. It is 0 otherwise."""
        )
        # Bit 17
        self.lstLabelTexts.append("PLC Buffer Open")
        self.lstTooltips.append(
            """PLC Buffer Open: This bit is 1 if a PLC
        program buffer is open for entry. It is 0 if none of these
        buffers is open."""
        )
        # Bit 16
        self.lstLabelTexts.append("UMAC System")
        self.lstTooltips.append(
            """UMAC System: This bit is 1 if the Turbo
        PMAC is a 3U Turbo system (UMAC or Stack). It is 0
        otherwise."""
        )
        # Bit 14
        self.lstLabelTexts.append("Kinematics Active")
        self.lstTooltips.append("""Kinematics Active: (For internal use)""")
        # Bit 15
        self.lstLabelTexts.append("Kinematics Active")
        self.lstTooltips.append("""Kinematics Active: (For internal use)""")
        # Bit 13
        self.lstLabelTexts.append("Ring-Master-to-Master Communications")
        self.lstTooltips.append(
            """Ring-Master-to-Master Communications: (For internal use)"""
        )
        # Bit 12
        self.lstLabelTexts.append("Master-to-Ring-Master Communications")
        self.lstTooltips.append(
            """Master-to-Ring-Master Communications: (For internal use)"""
        )
        # Bit 11
        self.lstLabelTexts.append("Fixed Buffer Full")
        self.lstTooltips.append(
            """Fixed Buffer Full: This bit is 1 when no
        fixed motion (PROG) or PLC buffers are open, or
        when one is open but there are less than I18 words available. It is 0
        when one of these buffers is open and
        there are more than I18 words available."""
        )
        # Bit 10
        self.lstLabelTexts.append("(For Internal use)")
        self.lstTooltips.append("""(For Internal use)""")
        # Bit 9
        self.lstLabelTexts.append("(For Internal use)")
        self.lstTooltips.append("""(For Internal use)""")
        # Bit 8
        self.lstLabelTexts.append("(For Internal use)")
        self.lstTooltips.append("""(For Internal use)""")
        # Bit 7
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        # Bit 6
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        # Bit 5
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        # Bit 4
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        # Bit 3
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        # Bit 2
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        # Bit 1
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        # Bit 0
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")

        self.lstLabelTexts.reverse()
        self.lstTooltips.reverse()

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

    def updateStatus(self, statusHexWord):
        for bit in range(0, 48):
            bitMask = 1 << bit
            if bool(statusHexWord & bitMask):
                self.lstLeds[bit].setPixmap(self.greenLedOn)
            else:
                self.lstLeds[bit].setPixmap(self.greenLedOff)


class PpmacGlobalStatusForm(QDialog, Ui_formGlobalStatus):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.greenLedOn = parent.greenLedOn
        self.greenLedOff = parent.greenLedOff
        self.redLedOn = parent.redLedOn
        self.redLedOff = parent.redLedOff

        ledGroupLayout = self.ledGroup.layout()
        ledGroupLayout.setAlignment(Qt.AlignTop)
        self.lstLeds = []
        self.lstLabels = []
        self.lstLabelTexts = []
        self.lstTooltips = []
        # First Word Returned: Bit 31 - Bit 16
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        self.lstLabelTexts.append("(Reserved for future use)")
        self.lstTooltips.append("""(Reserved for future use)""")
        # First Word Returned: Bit 15 - Bit 0
        self.lstLabelTexts.append("CK3WHWChange")
        self.lstTooltips.append("""CK3W module change detected """)
        self.lstLabelTexts.append("CK3WConfigErr (bit 2)")
        self.lstTooltips.append("""CK3W module config error bit 2 """)
        self.lstLabelTexts.append("CK3WConfigErr (bit 1)")
        self.lstTooltips.append("""CK3W module config error bit 1 """)
        self.lstLabelTexts.append("CK3WConfigErr (bit 0)")
        self.lstTooltips.append("""CK3W module config error bit 0 """)
        self.lstLabelTexts.append("FlashSizeErr")
        self.lstTooltips.append("""Insufficient flash memory size error """)
        self.lstLabelTexts.append("BufSizeErr")
        self.lstTooltips.append("""Insufficient user buffer size error """)
        self.lstLabelTexts.append("AbortAll")
        self.lstTooltips.append(""""Abort all" condition  """)
        self.lstLabelTexts.append("NoClocks")
        self.lstTooltips.append("""No system clocks found """)
        self.lstLabelTexts.append("Default")
        self.lstTooltips.append("""Factory default configuration (by cmd or error)  """)
        self.lstLabelTexts.append("FileConfigErr")
        self.lstTooltips.append("""System file configuration error """)
        self.lstLabelTexts.append("HWChangeErr")
        self.lstTooltips.append("""Hardware change detected since save """)
        self.lstLabelTexts.append("ConfigLoadErr")
        self.lstTooltips.append("""Saved configuration load error """)
        self.lstLabelTexts.append("ProjectLoadErr")
        self.lstTooltips.append("""Project load error """)
        self.lstLabelTexts.append("PwrOnFault")
        self.lstTooltips.append("""Power-on/reset load fault (OR of bits 3–6)  """)
        self.lstLabelTexts.append("WDTFault (bit 1)")
        self.lstTooltips.append("""Software watchdog fault bit 1 """)
        self.lstLabelTexts.append("WDTFault (bit 0)")
        self.lstTooltips.append("""Software watchdog fault bit 0 """)

        self.lstLabelTexts.reverse()
        self.lstTooltips.reverse()

        for bit in range(0, 32):
            self.lstLeds.append(QLabel(self.ledGroup))
            self.lstLabels.append(QLabel("bit: " + str(bit), self.ledGroup))

        for bit in range(0, 32):
            if bit < 16:
                row = bit
                ledGroupLayout.addWidget(self.lstLeds[bit], row, 0)
                ledGroupLayout.addWidget(self.lstLabels[bit], row, 1)
            else:
                row = bit - 16
                ledGroupLayout.addWidget(self.lstLeds[bit], row, 2)
                ledGroupLayout.addWidget(self.lstLabels[bit], row, 4)
            self.lstLeds[bit].setPixmap(self.greenLedOff)
            self.lstLabels[bit].setText(self.lstLabelTexts[bit])
            self.lstLabels[bit].setToolTip(self.lstTooltips[bit])

    def updateStatus(self, statusHexWord):
        for bit in range(0, 32):
            bitMask = 1 << bit
            if bool(statusHexWord & bitMask):
                self.lstLeds[bit].setPixmap(self.greenLedOn)
            else:
                self.lstLeds[bit].setPixmap(self.greenLedOff)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a, pyqtSignal("lastWindowClosed()"), a, pyqtSlot("quit()"))  # type: ignore # noqa
    w = GlobalStatusForm(None)
    a.setMainWidget(w)  # type: ignore
    w.show()
    a.exec_loop()  # type: ignore
