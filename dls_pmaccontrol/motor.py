#!/bin/env dls-python2.6
#
import sys, os, signal
sys.path.append("/dls_sw/work/common/python/dls_pmaclib")

import types
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Queue import Queue, Empty
from optparse import OptionParser

from formControl import Ui_ControlForm
from dls_pmaclib.dls_pmacremote import *
from dls_pmaclib.dls_pmcpreprocessor import clsPmacParser
from energise import *
from status import *
from axissettings import *
from gather import *
from CSstatus import *
from GlobalStatus import *

# [TODO] Check why there is a segfault when one closes the main window without being disconnected. The fault happens after
#		controlform.remoteDisconnect() has finished. It did happen in previous releases of motorcontrol, too.

class controlform(QMainWindow, Ui_ControlForm):
	def __init__(self, options, parent = None):
		QMainWindow.__init__(self,parent)
		self.setupUi(self)
		
		signal.signal(2, self.signalHandler)

		self.greenLedOn = QPixmap( os.path.join( os.path.dirname(__file__), "greenLedOn.png"))
		self.greenLedOff = QPixmap( os.path.join( os.path.dirname(__file__), "greenLedOff.png"))
		self.redLedOn = QPixmap( os.path.join( os.path.dirname(__file__), "redLedOn.png"))
		self.redLedOff = QPixmap( os.path.join( os.path.dirname(__file__), "redLedOff.png"))
		
		self.pollingStatus = True

		self.lneServer.setText(options.server)
		self.lnePort.setText(options.port)
		self.currentMotor = int(options.defaultAxis)
		self.nAxes = options.nAxes
		
		self.verboseMode = options.verbose
		
		self.connectionProtocol = options.protocol
		if self.connectionProtocol == "ts":
			# use terminal server
			self.rbUseTerminalServer.setChecked(True)
			self.isUsingTerminalServerConnection = True
		elif self.connectionProtocol == "tcpip":
			# use TCP/IP socket connection
			self.rbUseSocket.setChecked(True)
			self.isUsingTerminalServerConnection = False
		else:
			QMessageBox.information(self, "Error", "Wrong connection protocol specified on command line (use \"ts\" or \"tcpip\").")
			sys.exit(-1)

		# This will hold a PmacRemoteInterface once self.remoteConnect() is called
		self.pmac = None

		self.statusScreen = statusform(self, self.currentMotor)
		self.CSStatusScreen = CSStatusForm(self)
		self.GlobalStatusScreen = GlobalStatusForm(self)		
		self.axisSettingsScreen = axissettingsform( self, self.currentMotor )
		self.gatherScreen = gatherform(self, self.currentMotor)
		self.energiseScreen = None

		self.spnJogMotor.setValue( self.currentMotor )
		
		# a few details for use when downloading pmc file
		self.progressEventType = QEvent.Type( QEvent.User + 1 )
		self.downloadDoneEventType = QEvent.Type( QEvent.User + 2 )
		self.updatesReadyEventType = QEvent.Type( QEvent.User + 3 )
		self.progressDialog = None
		self.canceledDownload = False
		
		self.table.setColumnWidth(3, 40)
		self.table.setColumnWidth(4, 40)
		
		self.commands = []
		self.commandsi= 0
		self.lneSend.keyPressEvent = types.MethodType(self.checkHistory,self.lneSend,self.lneSend.__class__)
		self.dirname = "."

                self.lblIdentity.setText('')

	def useTerminalServerConnection(self):
		if self.isUsingTerminalServerConnection == False:
			self.isUsingTerminalServerConnection = True
			# set the server and port fields to defaults for this connection type
			self.lneServer.setText("blxxi-nt-tserv-01")
			self.lnePort.setText("7017")

	def useSocketConnection(self):
		if self.isUsingTerminalServerConnection == True:
			self.isUsingTerminalServerConnection = False
			# set the server and port fields to defaults for this connection type
			self.lneServer.setText("172.23.243.156")
			self.lnePort.setText("1025")

	def checkHistory(self,edit,event):
		if event.key() == Qt.Key_Up:
			if self.commandsi > - len(self.commands):
				self.commandsi -=1
			self.lneSend.setText(self.commands[self.commandsi])
		elif event.key() == Qt.Key_Down:
			if self.commandsi >= -1:
				self.commandsi = 0
				self.lneSend.setText("")
			else:
				self.commandsi +=1
				self.lneSend.setText(self.commands[self.commandsi])			
		QLineEdit.keyPressEvent(edit,event)		
		
	def remoteConnect(self):
		# Create a remote PMAC interface, of the correct type, depending on radio-box selection in the "Connection to PMAC" section
		if self.isUsingTerminalServerConnection:
			self.pmac = PmacTelnetInterface(self, verbose = self.verboseMode, numAxes = self.nAxes)
		elif self.useSocketConnection:
			self.pmac = PmacEthernetInterface(self, verbose = self.verboseMode, numAxes = self.nAxes)

		# Set the server name and port
		serverName = self.lneServer.text()
		serverPort = self.lnePort.text()
		self.pmac.setConnectionParams( serverName, serverPort )
		
		# Connect to the interface/PMAC
		connectionStatus = self.pmac.connect(self.updatesReadyEventType)
		if (connectionStatus):
			# did not connect succesfully...
			QMessageBox.information(self, "Error", connectionStatus)
			return

		# Find out the type of the PMAC
		pmacModelStr = self.pmac.getPmacModel()
		if pmacModelStr:
			self.setWindowTitle('Delta Tau motor controller - %s' % pmacModelStr)
		else:
			QMessageBox.information(self, "Error", "Could not determine PMAC model")
			return

		self.table.setRowCount(self.pmac.getNumberOfAxes())
		self.spnJogMotor.setMaximum(self.pmac.getNumberOfAxes())

		self.btnConnect.setEnabled(False)
		self.lneServer.setEnabled(False)
		self.lnePort.setEnabled(False)
		self.btnGroupProtocol.setEnabled(False)
		self.btnDisconnect.setEnabled(True)
		self.btnJogNeg.setEnabled(True)
		self.btnJogPos.setEnabled(True)
		self.btnJogStop.setEnabled(True)
		self.btnHome.setEnabled(True)
		self.lneSend.setEnabled(True)
		self.btnSend.setEnabled(True)
		self.lneJogTo.setEnabled(True)
		self.lneJogDist.setEnabled(True)
		self.btnJogTo.setEnabled(True)
		self.btnEnergise.setEnabled(not self.pmac.isModelGeobrick())
		self.btnKillAll.setEnabled(True)
		self.btnStatus.setEnabled(True)
		self.btnCSStatus.setEnabled(True)
		self.btnGlobalStatus.setEnabled(True)				
		self.btnSave.setEnabled(not self.pmac.isModelGeobrick()) # [TEMP] 
		self.btnLoadFile.setEnabled(True)
		self.btnSettings.setEnabled(True)
		self.btnKillMotor.setEnabled(True)
		self.chkJogInc.setEnabled(True)
		self.btnPollingStatus.setEnabled(True)
		self.btnGather.setEnabled(True)
		self.table.setEnabled(True)
		self.pixPolling.setPixmap(self.greenLedOn)

	def remoteDisconnect(self):

		# If the PMAC interface has been already defined, make it disconnect (this will do nothing if the interface is not connected)
		if self.pmac:
			self.pmac.disconnect()

		self.setWindowTitle("Delta Tau motor controller")
		self.btnConnect.setEnabled(True)
		self.btnDisconnect.setEnabled(False)
		self.lneServer.setEnabled(True)
		self.lnePort.setEnabled(True)
		self.btnGroupProtocol.setEnabled(True)
		self.btnJogNeg.setEnabled(False)
		self.btnJogPos.setEnabled(False)
		self.btnJogStop.setEnabled(False)
		self.btnHome.setEnabled(False)
		self.lneSend.setEnabled(False)
		self.btnSend.setEnabled(False)
		self.lneJogTo.setEnabled(False)
		self.lneJogDist.setEnabled(False)
		self.btnJogTo.setEnabled(False)
		self.btnEnergise.setEnabled( False )
		self.btnKillAll.setEnabled(False)
		self.btnStatus.setEnabled(False)
		self.btnCSStatus.setEnabled(False)
		self.btnGlobalStatus.setEnabled(False)						
		self.btnSave.setEnabled(False)
		self.btnSettings.setEnabled(False)
		self.btnKillMotor.setEnabled(False)
		self.btnLoadFile.setEnabled(False)
		self.chkJogInc.setEnabled(False)
		self.btnPollingStatus.setEnabled(False)
		self.btnGather.setEnabled(False)
		self.table.setEnabled(False)
		self.pixPolling.setPixmap(self.greenLedOff)
                self.lblIdentity.setText('')
		
		self.axisSettingsScreen.close()
		self.statusScreen.close()
		self.CSStatusScreen.close()
#		self.GlobalStatusScreen.close()		
		self.gatherScreen.close()
		if self.energiseScreen:
			self.energiseScreen.close()

	def jogNeg(self):
		#print "controlform.jogNeg(): Not implemented yet"
		(command, retStr, retStatus) = self.pmac.jogInc(self.currentMotor, "neg", str(self.lneJogDist.text()))
		if self.chkShowAll.isChecked():
			self.txtShell.append(command)
			self.txtShell.append(retStr) # This may need reconsidering... Will not always print the return string.

	# public slot
	def jogPos(self):
		#print "controlform.jogPos(): Not implemented yet"
		(command, retStr, retStatus) = self.pmac.jogInc(self.currentMotor, "pos", str(self.lneJogDist.text()))
		if self.chkShowAll.isChecked():
			self.txtShell.append(command)
			self.txtShell.append(retStr) # This may need reconsidering... Will not always print the return string.

	# public slot

	def jogStop(self):
		#print "controlform.jogStop(): Not implemented yet"
		(command, retStr, retStatus) = self.pmac.jogStop( self.currentMotor )
		if self.chkShowAll.isChecked():
			self.txtShell.append(command)
			self.txtShell.append(retStr) # This may need reconsidering... Will not always print the return string.
		

	# public slot

	def jogHome(self):
		#print "controlform.jogHome(): Not implemented yet"
		(command, retStr, retStatus) = self.pmac.homeCommand( self.currentMotor )
		if self.chkShowAll.isChecked():
			self.txtShell.append(command)
			self.txtShell.append(retStr) # This may need reconsidering... Will not always print the return string.

	# public slot

	def jogGoToPosition(self):
		#print "controlform.jogGoToPosition(): Not implemented yet"
		(command, retStr, retStatus) = self.pmac.jogTo( self.currentMotor, self.lneJogTo.text() )
		if self.chkShowAll.isChecked():
			self.txtShell.append(command)
			self.txtShell.append(retStr) # This may need reconsidering... Will not always print the return string.

	# public slot
	def jogChangeMotor(self,newMotor):
		#print "controlform.jogChangeMotor(int newMotor): Not implemented yet " + str(newMotor)
		self.currentMotor = newMotor
		self.statusScreen.changeAxis( self.currentMotor )
		self.axisSettingsScreen.changeAxis( self.currentMotor )

	# Send a #Xk command to kill the current motor.
	def killMotor(self):
		command = "#%dk"%self.currentMotor
		(returnString, status) = self.pmac.sendCommand( command )
		if self.chkShowAll.isChecked():
			self.txtShell.append(command)
		

	# Send a <CTRL-K> (ASCII 0x0B) command to the PMAC to kill all motion
	# all servo loops will be opened and amplifier enable set false.
	# see TURBO SRM page 289
	def killAllMotors(self):
		#print "killing all motors!"
		command = '\x0B'
		(returnString, status) = self.pmac.sendCommand( command )
		if self.chkShowAll.isChecked():
			self.txtShell.append("CTRL-K")

	def writeShell(self, command, retStr):
		if self.chkShowAll.isChecked():
			if command:
				self.txtShell.append(command)
			appendStr = retStr.strip()
			appendStr = appendStr.replace('\r', ' ')
			self.txtShell.append(appendStr) 

	def dataGather(self):
		self.gatherScreen.show()

	def pmacSave(self):
		answer = QMessageBox.No
		filename = "."
		while filename!=".pmc" and QMessageBox.No == answer:
			filename=str(QFileDialog.getSaveFileName(filename, "*.pmc", self)).replace(".pmc","")+".pmc"
			if os.path.isfile(filename):
				question="%s already exists, would you like to overwrite?"
				answer=QMessageBox.question(self,"File already exists",\
											question%filename,QMessageBox.Yes,\
											QMessageBox.No)
			else:
				answer=QMessageBox.Yes
		if filename!=".pmc":
			command = "i0..8191"
			(returnString, status) = self.pmac.sendCommand( command )
			f = open(filename,"w")
			ivars = enumerate(returnString.split("\r")[:-1])
			f.writelines(["i%s = %s\n"%(i,x) for (i,x) in ivars])
			if self.chkShowAll.isChecked():
				self.txtShell.append("i0..8191")
			QMessageBox.information(self,"Backup I Variables",
						"I variables saved to file: '%s'"%filename)				

	# public slot
	def pmacEnergiseAxis(self):
		self.energiseScreen = energiseform( self.pmac, self )
		self.energiseScreen.show()
		
	def statusScreen(self):
		self.statusScreen.show()		

	def CSStatusScreen(self):
		self.CSStatusScreen.show()
		
	def GlobalStatusScreen(self):
		self.GlobalStatusScreen.show()

	# public slot
	def jogParameters(self):
		self.axisSettingsScreen.show()
		self.axisSettingsScreen.axisUpdate()
		
	# Download a pmc configuration file to the PMAC
	def pmacLoadConfig(self):
		# First get the file from a file dialog
		myDialog = QFileDialog(self)
		fileName = myDialog.getOpenFileName(self, "Load PMC file", self.dirname, "PMAC configuration (*.pmc *.PMC)")
		fileName = str(fileName)
		if (not fileName): return
		self.dirname = os.path.dirname(fileName)		
		
		# A couple of regular expressions for use in parsing the pmc file
		blankLine = re.compile(r'^\s*$')			# match blank lines
		
		# parsing through the file
		pmcLines = []
		pmc = clsPmacParser()
		pmcLines = pmc.parse(fileName)

		# Get rid of all the empty lines, but keep line numbers
		commands = []
		for i, pmcLine in enumerate(pmcLines):
			if not blankLine.match( pmcLine ):
				commands.append(( i+1, pmcLine ))

		# Open up progress dialog and start sending the commands.
		self.progressDialog = QProgressDialog("Downloading PMAC configuration",
							"cancel",
							len(commands)+1,
							self, "download_progress", True)
		self.canceledDownload = False
		self.txtShell.append("Beginning download of pmc file: "+fileName)
		self.pmac.sendSeries( commands, self.progressEventType, self.downloadDoneEventType, self )
	#	print pmcLines		

	def pmacPollingStatus(self):
		# If we are already polling, disable it
		if self.pollingStatus:
			self.pollingStatus = False
			self.pmac.startPollingStatus(False)
			
			self.btnPollingStatus.setText("enable polling")
			
			# Disable all the controls and status displays to indicate that we
			# do not have updates available
			self.table.setEnabled(False)
			self.lblPosition.setEnabled(False)
			self.lblVelo.setEnabled(False)
			self.lblFolErr.setEnabled(False)
			self.pixPolling.setPixmap(self.greenLedOff)			
			
		# else, if we are not polling: start polling!
		else:
			self.pollingStatus = True
			self.pmac.startPollingStatus(True)
			self.btnPollingStatus.setText("disable polling")

			# Re-enable all the disabled labels and controls
			self.table.setEnabled(True)
			self.lblPosition.setEnabled(True)
			self.lblVelo.setEnabled(True)
			self.lblFolErr.setEnabled(True)
			self.pixPolling.setPixmap(self.greenLedOn)

	
	def jogNegContinousStart(self):
		#print "controlform.jogNegContinousStart(): Not implemented yet"
		(command, retStr, retStatus) = self.pmac.jogContinous(self.currentMotor, "neg")
		if self.chkShowAll.isChecked():
			self.txtShell.append(command)
			self.txtShell.append(retStr) # This may need reconsidering... Will not always print the return string.
		
	# public slot
	def jogPosContinousStart(self):
		#print "controlform.jogPosContinousStart(): Not implemented yet"
		(command, retStr, retStatus) = self.pmac.jogContinous(self.currentMotor, "pos")
		if self.chkShowAll.isChecked():
			self.txtShell.append(command)
			self.txtShell.append(retStr) # This may need reconsidering... Will not always print the return string.

	# public slot
	def sendSingleCommand(self):
		#print "controlform.sendSingleCommand(): Not implemented yet"
		command = self.lneSend.text()
		self.commands.append( command )
		self.txtShell.append( command )
		(returnString, status) = self.pmac.sendCommand( command )
		self.txtShell.append( returnString )
		self.commandsi = 0
		self.lneSend.setText("")

	# public slot
	def chooseMotorFromTable(self,a0,a1):
		#print "controlform.chooseMotorFromTable(int row, int col): Not implemented yet" + str(a0)
		self.spnJogMotor.setValue( a0 + 1 )
		

	# public slot
	def jogIncrementally(self,a0):
		#print "controlform.jogIncrementally(bool): Not implemented yet"
		self.lneJogDist.setEnabled(a0)
		if a0:
			self.disconnect(self.btnJogPos,SIGNAL("pressed()"),self.jogPosContinousStart)
			self.disconnect(self.btnJogPos,SIGNAL("released()"),self.jogStop)
			self.disconnect(self.btnJogNeg,SIGNAL("pressed()"),self.jogNegContinousStart)
			self.disconnect(self.btnJogNeg,SIGNAL("released()"),self.jogStop)
			self.connect(self.btnJogNeg,SIGNAL("clicked()"),self.jogNeg)
			self.connect(self.btnJogPos,SIGNAL("clicked()"),self.jogPos)
		else:
			self.connect(self.btnJogPos,SIGNAL("pressed()"),self.jogPosContinousStart)
			self.connect(self.btnJogPos,SIGNAL("released()"),self.jogStop)
			self.connect(self.btnJogNeg,SIGNAL("pressed()"),self.jogNegContinousStart)
			self.connect(self.btnJogNeg,SIGNAL("released()"),self.jogStop)
			self.disconnect(self.btnJogNeg,SIGNAL("clicked()"),self.jogNeg)
			self.disconnect(self.btnJogPos,SIGNAL("clicked()"),self.jogPos)
			
		
	# Called when an event comes out of the polling thread
	# and the jog ribbon.
	def updateMotors(self):
		#print "updating motors..."
		self.pmac.resultQueue.qsize()
		#print "-"
		for queItem in range(0,self.pmac.resultQueue.qsize()):
			try:
				value = self.pmac.resultQueue.get(False)
			except Empty:
				return
			motorRow = value[4]
			# check for special cases
			if type(motorRow) == str:
				if motorRow == "G":
					self.GlobalStatusScreen.updateStatus(int(value[0], 16))
					continue
				if motorRow.startswith("CS"):
					self.CSStatusScreen.updateStatus(int(value[0], 16))
					continue
				if motorRow.startswith("FEED"):
					self.CSStatusScreen.updateFeed(int(round(float(value[0]))))
					continue					
				if motorRow == "IDENT":
					self.updateIdentity(int(value[0]))
					continue					
			#print str(motorRow)
			#print value
			position = str(round(float( value[1]), 1 ))
			velocity = str(round(float( value[2]), 1 ))
			folerr = str(round(float( value[3]), 1 ))

			self.table.setText(motorRow, 0, position )
			self.table.setText(motorRow, 1, velocity )
			self.table.setText(motorRow, 2, folerr )
			#print value[0]
			statusWord = int(value[0], 16)
			loLim = bool(statusWord & 0x400000000000)
			hiLim = bool(statusWord & 0x200000000000)

			
			if hiLim:
				self.table.setPixmap(motorRow, 3, self.redLedOn)
			else:
				self.table.setPixmap(motorRow, 3, self.redLedOff)
			if loLim:
				self.table.setPixmap(motorRow, 4, self.redLedOn)
			else:
				self.table.setPixmap(motorRow, 4, self.redLedOff)
			
			# Update also the jog ribbon
			if motorRow + 1 == self.currentMotor:
				self.lblPosition.setText( position )
				self.lblVelo.setText( velocity )
				self.lblFolErr.setText( folerr )
				if hiLim: self.pixHiLim.setPixmap(self.redLedOn)
				else: self.pixHiLim.setPixmap(self.redLedOff)
				if loLim: self.pixLoLim.setPixmap(self.redLedOn)
				else: self.pixLoLim.setPixmap(self.redLedOff)
				self.statusScreen.updateStatus( statusWord )

		#print "."

        domainNames = ['BL', 'BR', 'BS', 'FE', 'LB', 'LI', 'ME', 'SR',
                       'TBD', 'TBD', 'TBD', 'TBD', 'TBD', 'TBD', 'TBD', 'RSV']
        subdomainLetters = [
            ['I', 'B', 'J', 'C', 'K', 'D', 'L', 'E'],
            ['C', 'S', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['I', 'B', 'J', 'C', 'K', 'D', 'L', 'E'],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['I', 'A', 'J', 'C', 'K', 'R', 'L', 'S'],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''] ]

        def updateIdentity(self, id):
            if not self.btnConnect.isEnabled():
                if id == 0:
                    text = 'Identity not set'
                else:
                    domain = (id >> 20) & 0x0f
                    swVersion = (id >> 13) & 0x7f
                    subdomainNum = (id >> 7) & 0x1f
                    pmacNum = id & 0x1f
                    subdomainLetter = ((id >> 6) & 0x01) | ((id >> 4) & 0x02) | ((id >> 10) & 0x04)
                    text = self.domainNames[domain]
                    if subdomainNum != 0:
                        text += '%02d' % subdomainNum
                        text += self.subdomainLetters[domain][subdomainLetter]
                    if self.pmac.isModelGeobrick():
                        text += ' Geobrick '
                    else:
                        text += ' Pmac '
                    text += '%d' % pmacNum
                self.lblIdentity.setText(text)
		
	def customEvent( self, E ):
		#print "custom event!"
		if E.type() == self.progressEventType:
			#print "Data = " + str(E.data())
			if self.progressDialog.wasCanceled():
				self.canceledDownload = True
				self.txtShell.append("Download of configuration canceled by user.")
			else:
				self.progressDialog.setProgress( E.data() )
				
		elif E.type() == self.downloadDoneEventType:
			(errors, lines) = E.data()
			for err in errors:
				self.txtShell.append("Error in line: "+str(err[0])+" "+err[1])
			self.txtShell.append("Downloaded "+str(lines)+" lines from pmc file.")
			
		elif E.type() == self.updatesReadyEventType:
			#print "updating motors"
			self.updateMotors()
			
	def signalHandler(self, signum, frame):
		if signum == 2:
			print "Closing terminal session..."
			self.pmac.tn.close()
			print "Closing application."
			QApplication.exit(0)	

def main():
	usage = """usage: %prog [options]
%prog is a graphical frontend to the Deltatau motorcontroller known as PMAC."""
	parser = OptionParser(usage)
	parser.add_option(	"-v", "--verbose",
						action="store_true", dest="verbose", default=False,
						help="Print more details (than necessary in most cases...)")
	parser.add_option(	"-o", "--protocol",
						action="store", dest="protocol", default="ts",
						help="Set the connection protocol; use \"ts\" for serial via terminal server (the default), or \"tcpip\" for network TCP/IP connection.")
	parser.add_option(	"-s", "--server",
						action="store", dest="server", default="blxxi-nt-tserv-01",
						help="Set server name (default: blxxi-nt-tserv-01)")
	parser.add_option(	"-p", "--port",
						action="store", dest="port", default="7017",
						help="Set IP port number to connect to (default: 7017)")
	parser.add_option(	"-a", "--axis",
						action="store", dest="defaultAxis", default=1,
						help="Set an axis as a default selected axis when starting up the application (default: 1)")
	parser.add_option(	"-n", "--naxes",
						action="store", dest="nAxes",
						help="Display and poll NAXES axes. Default is 32 for a PMAC, 8 for a geoBrick")
	(options, args) = parser.parse_args()
	
	a = QApplication(sys.argv)
	QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
	w = controlform(options)
	QObject.connect(a, SIGNAL("aboutToQuit()"), w.remoteDisconnect)
	w.show()
	a.exec_()

if __name__ == "__main__":    
	main()
