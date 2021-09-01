import os
import time
import threading

from numpy import arange
from PyQt5.Qt import QPen
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from qwt import QwtPlotCurve

from dls_pmaccontrol.gatherchannel import LONGWORD, WORD, GatherChannel, dataSources, motorBaseAddrs
from dls_pmaccontrol.ui_formGather import Ui_formGather

# TODO - this needs the logic decoupled from the GUI and moved into pmaclib
#  work has started in pmaclib but currently duplicates code in this module

class myThread(threading.Thread):
    def __init__(self, instance, waittime):
        threading.Thread.__init__(self)
        self.waittime = waittime
        self.instance = instance

    def run(self):
        Gatherform.triggerWait(self.instance,self.waittime)


class Gatherform(QDialog, Ui_formGather):
    def __init__(self, parent, currentMotor=1):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.parent = parent
        if not self.parent:
            raise ValueError(
                "It is now required to provide a parent form for this form"
            )

        self.currentMotor = currentMotor

        # initialize the data lists that will contain
        # the gathered data
        self.numberOfSamples = 0
        self.numberOfChannels = 0
        self.lstChannels = []
        self.oddNumberOfWords = False
        self.numberOfWords = 0

        # Initialize the timing variables for gathering
        self.sampleTime = 0.0  # the sample time per gather sampling (ms)
        self.nServoCyclesGather = 0  # of servo cycles per gather sampling
        self.servoCycleTime = 0.0  # the time of one servo cycle (ms)
        self.nGatherPoints = 0  # the # of data points to sample

        self.lstColours = [Qt.red, Qt.blue, Qt.magenta, Qt.green, Qt.cyan]

        self.lstCheckboxes = [
            self.chkPlot1,
            self.chkPlot2,
            self.chkPlot3,
            self.chkPlot4,
            self.chkPlot5,
        ]
        self.lstSpinboxes = [
            self.spbAxis1,
            self.spbAxis2,
            self.spbAxis3,
            self.spbAxis4,
            self.spbAxis5,
        ]

        self.lstComboboxes = [
            self.cmbDataSource1,
            self.cmbDataSource2,
            self.cmbDataSource3,
            self.cmbDataSource4,
            self.cmbDataSource5,
        ]

        self.lstColourBoxes = [
            self.cmbCol1,
            self.cmbCol2,
            self.cmbCol3,
            self.cmbCol4,
            self.cmbCol5,
        ]

        self.lstCmbYaxis = [
            self.cmbXaxis1,
            self.cmbXaxis2,
            self.cmbXaxis3,
            self.cmbXaxis4,
            self.cmbXaxis5,
        ]

        # initialise the combo-boxes with all the possible data points
        # that can be gathered.
        for cmBox in self.lstComboboxes:
            cmBox.clear()
        for dataPoint in dataSources:
            for cmBox in self.lstComboboxes:
                cmBox.addItem(dataPoint["desc"])      

    def gatherConfig(self):
        # Clear the plot by setting empty plotitems
        for chIndex, ch in enumerate(self.lstChannels):
            ch.qwtCurve.setData([],[])

        # Reset the data channels from class GatherChannel
        self.lstChannels = []

        # Left or right Y axis
        enableRight = False
        enableLeft = False
 
        # use counter to find number of items to gather
        items = 0

        # Specify data to sample
        for index, axisSpinBox in enumerate(self.lstSpinboxes):
            cmBox = self.lstComboboxes[index]
            chkBox = self.lstCheckboxes[index]

            addr_str = dataSources[cmBox.currentIndex()]["addr"]
            gather_addr = "Gather.Addr[%d]" % items
            addr = "Motor[%d].%s" % (axisSpinBox.value(),addr_str)
            cmd = "%s=%s" % (gather_addr, addr)
            if chkBox.isChecked():
                items += 1
                self.parent.pmac.sendCommand(cmd)

                # create a new curve for the qwt plot and instanciate a
                # GatherChannel.

                # print "Set data: %s"%cmd
                curve = QwtPlotCurve("Ch%d" % index)
                curve.attach(self.qwtPlot)
                # curve = self.qwtPlot.insertCurve("Ch%d"%index)
                channel = GatherChannel(self.parent.pmac, curve)
                self.lstChannels.append(channel)
                # Set the colour of the graph
                colour = self.lstColours[self.lstColourBoxes[index].currentIndex()]
                channel.qwtCurve.setPen(QPen(colour))
                # set the left or right Y axis
                if self.lstCmbYaxis[index].currentIndex() == 0:
                    channel.qwtCurve.setYAxis(self.qwtPlot.yLeft)
                    enableLeft = True
                    # self.qwtPlot.setCurveYAxis(channel.qwtCurve,
                    # self.qwtPlot.yLeft)
                elif self.lstCmbYaxis[index].currentIndex() == 1:
                    enableRight = True
                    channel.qwtCurve.setYAxis(self.qwtPlot.yRight)
                    # self.qwtPlot.setCurveYAxis(channel.qwtCurve,
                    # self.qwtPlot.yRight)

        if enableLeft and enableRight:
            self.qwtPlot.enableAxis(self.qwtPlot.yLeft, True)
            self.qwtPlot.enableAxis(self.qwtPlot.yRight, True)
        elif enableLeft:
            self.qwtPlot.enableAxis(self.qwtPlot.yLeft, True)
            self.qwtPlot.enableAxis(self.qwtPlot.yRight, False)
        elif enableRight:
            self.qwtPlot.enableAxis(self.qwtPlot.yLeft, False)
            self.qwtPlot.enableAxis(self.qwtPlot.yRight, True)
        else:
            self.qwtPlot.enableAxis(self.qwtPlot.yLeft, False)
            self.qwtPlot.enableAxis(self.qwtPlot.yRight, False)  
        
        # set the number of items to gather
        self.parent.pmac.sendCommand("Gather.items=%d" % items)
        return True

    def gatherSetup(self, numberOfSamples=1):
        # set the sampling time (in servo cycles)
        self.parent.pmac.sendCommand("Gather.Period=%d" % int(str(self.lneSampleTime.text())))
        # set the number of samples
        self.parent.pmac.sendCommand("Gather.MaxSamples=%d" % int(str(self.lneNumberSamples.text())))
        return

    def triggerWait(self,waittime):
        time.sleep(waittime)
        self.btnCollect.setEnabled(True)

    def gatherTrigger(self):
        self.parent.pmac.sendCommand("Gather.enable=2")
        # gather time in secs
        gather_time = self.sampleTime * self.nGatherPoints / 1000.0
        t = myThread(self,gather_time) 
        t.start()

    def collectData(self):
        # send gathered data to file on ppmac
        tmp_file = "../../var/ftp/usrflash/Temp/gather.txt"
        self.parent.pmac.sendSshCommand("gather -u " + tmp_file)
        time.sleep(0.1)
        # copy file from ppmac to cwd
        gather_file = "./gather.txt"
        try:
            self.parent.pmac.getFile(tmp_file, gather_file)
        except Exception as e:
            print("Error: Could not get gather file from power pmac")
            return

    def parseData(self, lstDataStrings):
        pass # need to write code here

    def plotData(self):
        gather_file = "./gather.txt"
        for chIndex, ch in enumerate(self.lstChannels):
            data = [line.split(' ')[chIndex] for line in open(gather_file).readlines()]
            data = [float(s.strip('/n')) for s in data]
            ch.qwtCurve.setData(arange(len(data)), data)
        self.qwtPlot.replot()

    def calcSampleTime(self):
        cmd = "Sys.ServoPeriod"
        (retStr, status) = self.parent.pmac.sendCommand(cmd)
        self.servoCycleTime = float(retStr)
        #print("self.servoCycleTime is: ",self.servoCycleTime)
        # calculate the actual sample time and frequency of the data
        # gathering function
        #print("self.nServoCyclesGather is: ",self.nServoCyclesGather)
        self.sampleTime = self.nServoCyclesGather * self.servoCycleTime
        #print("self.sampleTime is: ",self.sampleTime)
        realSampleFreq = 1.0 / self.sampleTime
        self.txtLblFreq.setText("%.3f kHz" % realSampleFreq)
        self.txtLblSignalLen.setText("%.2f ms" % (self.sampleTime * self.nGatherPoints))

    # ############## button clicked slots from here
    # #######################################

    def changedTab(self):
        # Get the sample time (in servo cycles unit)
        cmd = "Gather.Period"
        (retStr, status) = self.parent.pmac.sendCommand(cmd)
        newNGatherPoints = int(retStr)
        if not (newNGatherPoints == self.nServoCyclesGather):
            self.nServoCyclesGather = newNGatherPoints
            self.calcSampleTime()
        self.nServoCyclesGather = newNGatherPoints
        self.lneSampleTime.setText(str(self.nServoCyclesGather))

    def servoCyclesChanged(self):
        # Get the # of servo cycles per gather sampling
        self.nServoCyclesGather = int(str(self.lneSampleTime.text()))
        self.nGatherPoints = int(str(self.lneNumberSamples.text()))
        cmd = "Gather.Period=" +  str(self.lneSampleTime.text()) #bem
        self.parent.pmac.sendCommand(cmd) #bem
        self.calcSampleTime()

    def changedNoSamples(self):
        # Get the # of data points to gather
        self.nGatherPoints = int(str(self.lneNumberSamples.text()))
        self.nServoCyclesGather = int(str(self.lneSampleTime.text()))
        cmd = "Gather.MaxSamples=" +  str(self.lneNumberSamples.text()) #bem
        self.parent.pmac.sendCommand(cmd) #bem
        self.calcSampleTime()

    def collectClicked(self):
        self.btnSetup.setEnabled(False)
        self.btnTrigger.setEnabled(False)
        self.btnCollect.setEnabled(False)
        self.btnSave.setEnabled(False)
        self.parseData(self.collectData())
        self.plotData()

        self.btnSetup.setEnabled(True)
        self.btnTrigger.setEnabled(False)
        self.btnCollect.setEnabled(False)
        self.btnSave.setEnabled(True)

    def setupClicked(self):
        # print "formGather.setupClicked(): Not implemented yet"
        self.numberOfSamples = int(str(self.lneNumberSamples.text()))
        self.gatherSetup(self.numberOfSamples)
        self.btnSetup.setEnabled(True)
        self.btnTrigger.setEnabled(True)
        self.btnCollect.setEnabled(False)
        self.btnSave.setEnabled(False)

    def triggerClicked(self):
        # print "formGather.triggerClicked(): Not implemented yet"
        self.btnTrigger.setEnabled(False)
        self.gatherTrigger()
        self.btnSetup.setEnabled(True)
        #self.btnCollect.setEnabled(True)
        self.btnSave.setEnabled(False)

    def applyConfigClicked(self):
        # print "formGather.applyConfigClicked(): Not implemented yet"
        if not self.gatherConfig():
            return
        self.btnSetup.setEnabled(True)
        self.btnTrigger.setEnabled(False)
        self.btnCollect.setEnabled(False)
        self.btnSave.setEnabled(False)

    def saveClicked(self):
        gather_file = "./gather.txt"
        # if gather file does not exist
        if not os.path.isfile(gather_file):
            QMessageBox.information(self, "Error", "No data has been collected yet.")
            return
        #if gather file is empty
        if os.path.getsize(gather_file) == 0:
            QMessageBox.information(self, "Error", "No data has been collected yet.")
            return

        myDialog = QFileDialog(self)
        # myDialog.setShowHiddenFiles(False)
        fileName = myDialog.getSaveFileName(
            caption="Comma seperated data file (*.csv *.CSV)",
            directory=os.path.expanduser("~"),
            options=None,
        )
        if not fileName:
            return
        try:
            fptr = open(str(fileName), "w")
        except Exception:
            QMessageBox.information(
                self,
                "Error",
                "Could not open file %s for writing." % fileName,
                buttons=1,
                p_str_1="OK",
            )
            return

        #dataLists = []
        line = "point,"
        for i, channel in enumerate(self.lstChannels):
            line += "CH%d Axis%d %s," % (
                i,
                channel.axisNo,
                channel.dataSourceInfo["desc"],
            )
            #dataLists.append(channel.scaledData)
        fptr.write(line + "\n")

        '''for lineNo, lineData in enumerate(zip(*dataLists)):
            line = "%d," % lineNo
            for data_point in lineData:
                line += "%f," % data_point
            fptr.write(line + "\n")'''
        fptr.close()
