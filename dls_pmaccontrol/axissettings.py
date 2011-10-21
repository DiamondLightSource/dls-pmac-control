# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from formAxisSettings import Ui_formAxisSettings

class axissettingsform(QDialog, Ui_formAxisSettings):

	def __init__(self, parent = None, currentMotor = 1):
		QDialog.__init__(self,parent)
		self.setupUi(self)
		
		self.currentMotor = currentMotor
		self.parent = parent
		
		self.lneIx11.setToolTip("""Fatal following error [1/16 cts]""")
		self.lneIx12.setToolTip("""Warning following error limit [1/16 cts]""")
		self.lneIx13.setToolTip("""Positive soft limit position [cts]""")
		self.lneIx14.setToolTip("""Negative soft limit position [cts]""")
		self.lneIx15.setToolTip("Decceleration rate on position\nlimit or abort [cts/msec2]")
		self.lneIx16.setToolTip("Maximum velocity in LINEAR motion programs [cts/msec]")
		self.lneIx17.setToolTip("Maximum acceleration in motion programs [cts/msec2]")
		self.lneIx19.setToolTip("Maximum jog/home acceleration [cts/msec2]")
		self.lneIx20.setToolTip("Jog/Home Acceleration Time [msec]")
		self.lneIx21.setToolTip("Jog/Home S-Curve Time [msec]\n(DLS: Try to avoid using this one!)")
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
		self.lneLoopSelect.setToolTip("Encoder/Timer n Decode Control\n7: Closed loop stepper\n8: Open loop stepper")
		self.lneCaptureOn.setToolTip("""Encoder n Capture Control
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
14: Capture on Flag low
""")
		self.lneCaptureFlag.setToolTip("""Capture n Flag Select Control
0: Home Flag
1: positive limit flag
2: Negative limit flag
3: User flag""")
		self.lneOutputMode.setToolTip("""Output n Mode Select (DLS: use 2 for steppers)
0 = Outputs A & B are PWM; Output C is PWM
1 = Outputs A & B are DAC; Output C is PWM
2 = Outputs A & B are PWM; Output C is PFM
3 = Outputs A & B are DAC; Output C is PFM
""")
		self.definitionIvars = [11, 12, 13, 14, 15, 16, 17, 19]
		self.safetyIvars = [20, 21, 22, 23, 24, 25, 26]
		self.pidIvars = [30, 31, 32, 33, 34, 35, 65]
		
	def changeAxis(self, newMotor):
		self.currentMotor = newMotor
		if self.isVisible():
			self.axisUpdate()

	# Updates I-variable line edits for this axis and I-variables listed in ivars
	def _updateAxisSetupIVars(self, ivars):
		retLst = self.parent.pmac.getAxisSetupIVars(self.currentMotor, ivars)
		if retLst:
			for i, retVal in enumerate(retLst):
				exec("self.lneIx%d.setText(str(\"%s\"))" % (ivars[i], retVal))

	def _updateAxisSignalControlsVars(self):
		(loopSelect, captureOn, captureFlag, outputMode) = self._getAxisSignalControlsVars()
		self.lneLoopSelect.setText(loopSelect)
		self.lneCaptureOn.setText(captureOn)
		self.lneCaptureFlag.setText(captureFlag)
		self.lneOutputMode.setText(outputMode)

	def _getAxisSignalControlsVars(self):
		pmac = self.parent.pmac  # a link to the RemotePmacInterface
 		if pmac.isMacroStationAxis(self.currentMotor):
			(loopSelect, captureOn, captureFlag, outputMode) = pmac.getAxisMsIVars(self.currentMotor, [910,912,913,916])
 		else:
			(loopSelect, captureOn, captureFlag, outputMode) = pmac.getOnboardAxisI7000PlusVars(self.currentMotor, [0,2,3,6])
		return (loopSelect, captureOn, captureFlag, outputMode)
	
	def axisUpdate(self):
		selectedTabIndex = self.tabAxisSetup.currentIndex()
		if selectedTabIndex == 0:
			# The "definition and safety" tab is selected
			self._updateAxisSetupIVars(self.definitionIvars + self.safetyIvars)
		else:
			# The "PID and macro" tab is selected
			self._updateAxisSetupIVars(self.pidIvars)
			self._updateAxisSignalControlsVars()
	
	def tabChange(self):
		self.axisUpdate()

	# public slot
	def axisClose(self):
		print "axissettingsform.axisClose(): Not implemented yet"
		
	def sendIx11(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 11, self.lneIx11.text())
		self.axisUpdate()

	def sendIx12(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 12, self.lneIx12.text())
		self.axisUpdate()		

	def sendIx13(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 13, self.lneIx13.text())
		self.axisUpdate()

	def sendIx14(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 14, self.lneIx14.text())
		self.axisUpdate()

	def sendIx15(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 15, self.lneIx15.text())
		self.axisUpdate()

	def sendIx16(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 16, self.lneIx16.text())
		self.axisUpdate()

	def sendIx17(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 17, self.lneIx17.text())
		self.axisUpdate()

	def sendIx19(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 19, self.lneIx19.text())
		self.axisUpdate()

	def sendIx20(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 20, self.lneIx20.text())
		self.axisUpdate()

	def sendIx21(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 21, self.lneIx21.text())
		self.axisUpdate()

	def sendIx22(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 22, self.lneIx22.text())
		self.axisUpdate()

	def sendIx23(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 23, self.lneIx23.text())
		self.axisUpdate()

	def sendIx24(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 24, self.lneIx24.text())
		self.axisUpdate()

	def sendIx25(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 25, self.lneIx25.text())
		self.axisUpdate()

	def sendIx26(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 26, self.lneIx26.text())
		self.axisUpdate()

	def sendIx30(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 30, self.lneIx30.text())
		self.axisUpdate()

	def sendIx31(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 31, self.lneIx31.text())
		self.axisUpdate()

	def sendIx32(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 32, self.lneIx32.text())
		self.axisUpdate()

	def sendIx33(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 33, self.lneIx33.text())
		self.axisUpdate()

	def sendIx34(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 34, self.lneIx34.text())
		self.axisUpdate()

	def sendIx35(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 35, self.lneIx35.text())
		self.axisUpdate()

	def sendIx65(self):
		self.parent.pmac.setAxisSetupIVar(self.currentMotor, 65, self.lneIx65.text())
		self.axisUpdate()

	def sendLoopSelect(self):
		pmac = self.parent.pmac
		if pmac.isMacroStationAxis(self.currentMotor):
			pmac.setAxisMsIVar(self.currentMotor, 910, self.lneLoopSelect.text())
		else:
			pmac.setOnboardAxisI7000PlusIVar(self.currentMotor, 0, self.lneLoopSelect.text())

	def sendCaptureOn(self):
		pmac = self.parent.pmac
		if pmac.isMacroStationAxis(self.currentMotor):
			pmac.setAxisMsIVar(self.currentMotor, 912, self.lneCaptureOn.text())
		else:
			pmac.setOnboardAxisI7000PlusIVar(self.currentMotor, 2, self.lneCaptureOn.text())

	def sendCaptureFlag(self):
		pmac = self.parent.pmac
		if pmac.isMacroStationAxis(self.currentMotor):
			pmac.setAxisMsIVar(self.currentMotor, 913, self.lneCaptureFlag.text())
		else:
			pmac.setOnboardAxisI7000PlusIVar(self.currentMotor, 3, self.lneCaptureFlag.text())

	def sendOutputMode(self):
		pmac = self.parent.pmac
		if pmac.isMacroStationAxis(self.currentMotor):
			pmac.setAxisMsIVar(self.currentMotor, 916, self.lneOutputMode.text())
		else:
			pmac.setOnboardAxisI7000PlusIVar(self.currentMotor, 6, self.lneOutputMode.text())
## \file
# \section License
# Author: Diamond Light Source, Copyright 2011
#
# 'dls_pmaccontrol' is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'dls_pmaccontrol' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with 'dls_pmaccontrol'.  If not, see http://www.gnu.org/licenses/.
