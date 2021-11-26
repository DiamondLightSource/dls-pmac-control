import os
import threading
import time

from numpy import arange
from PyQt5.Qt import QPen
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from qwt import QwtPlotCurve

from dls_pmaccontrol.gatherchannel import (
    LONGWORD,
    WORD,
    PmacGatherChannel,
    motorBaseAddrs,
    pmacDataSources,
)
from dls_pmaccontrol.ui_formGather import Ui_formGather

# TODO - this needs the logic decoupled from the GUI and moved into pmaclib
#  work has started in pmaclib but currently duplicates code in this module

# TODO Find out why the gathering fails with an response "ERR003" from the
#   PMAC for PMAC2-VME (does work for Geo Brick)!
#   (ERR003 = Data error or unrecognized command - solution: correct command syntax)


class myThread(threading.Thread):
    def __init__(self, instance, waittime):
        threading.Thread.__init__(self)
        self.waittime = waittime
        self.instance = instance

    def run(self):
        PmacGatherform.triggerWait(self.instance, self.waittime)


class PmacGatherform(QDialog, Ui_formGather):
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
        for dataPoint in pmacDataSources:
            for cmBox in self.lstComboboxes:
                cmBox.addItem(dataPoint["desc"])

    def gatherConfig(self):
        # Create i5050 variable value to mask out what values to sample
        tmpIvar = 0
        for bit, checkbox in enumerate(self.lstCheckboxes):
            if checkbox.isChecked():
                tmpIvar |= 0x01 << bit
        if tmpIvar == 0:
            return False
        cmd = "i5051=0 i5050=$%x" % tmpIvar
        self.parent.pmac.sendCommand(cmd)

        # Clear the plot by setting empty plotitems
        for chIndex, ch in enumerate(self.lstChannels):
            ch.qwtCurve.setData([], [])

        # reset the data channels from class GatherChannel
        self.lstChannels = []

        # Left or right Y axis
        enableRight = False
        enableLeft = False

        # Create the i5001 - i5005 values to specify what data to sample
        for index, axisSpinBox in enumerate(self.lstSpinboxes):
            cmbBox = self.lstComboboxes[index]
            chkBox = self.lstCheckboxes[index]
            dataOffset = pmacDataSources[cmbBox.currentIndex()]["reg"]
            baseAddress = motorBaseAddrs[axisSpinBox.value() - 1]
            dataWidth = pmacDataSources[cmbBox.currentIndex()]["size"]
            ivar = "i50%02d" % (index + 1)
            addr = "$%X%05X" % (dataWidth, baseAddress + dataOffset)
            cmd = "%s=%s" % (ivar, addr)
            if chkBox.isChecked():
                self.parent.pmac.sendCommand(cmd)

                # create a new curve for the qwt plot and instanciate a
                # GatherChannel.

                # print "Set data: %s"%cmd
                curve = QwtPlotCurve("Ch%d" % index)
                curve.attach(self.qwtPlot)
                # curve = self.qwtPlot.insertCurve("Ch%d"%index)
                channel = PmacGatherChannel(self.parent.pmac, curve)
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
        # set the sampling time (in servo cycles)
        self.parent.pmac.sendCommand("i5049=%d" % int(str(self.lneSampleTime.text())))
        return True

    def gatherSetup(self, numberOfSamples=1):

        # Run through the bitmasks i5050 and i5051 to see which of the
        # 48 channels should be sampled.
        bitOffset = 1
        for ivarMask in range(5050, 5052):
            (retStr, status) = self.parent.pmac.sendCommand("i%d" % ivarMask)

            # For each channel to sample, get the ivariable with the
            # ivariable to sample from,
            # This value is read from the PMAC as a double check to avoid
            # differences between the
            # PMAC data settings and the data set in this application.
            chCount = 0
            for bit in range(WORD):
                if (int(retStr.strip("$")[:-1], 16) >> bit & 0x01) > 0:
                    chIndex = bit + bitOffset
                    ivar = "i50%02d" % chIndex
                    chCount += 1
                    if chCount > len(self.lstChannels):
                        print(
                            "gatherSetup: Error: not enough GatherChannels "
                            "instantiated."
                        )
                        break
                    self.lstChannels[chCount - 1].setDataGatherPointer(ivar)

            bitOffset += WORD

        self.numberOfChannels = len(self.lstChannels)
        # print "number of channels = %d"%self.numberOfChannels

        self.numberOfWords = 0
        noBits = 0

        # Run through all the channels to sample from
        self.oddNumberOfWords = False
        for chIndex, ch in enumerate(self.lstChannels):

            # Get the data info
            # print "channel: %d"%chIndex
            ch.getDataInfo()

            # Figure out the data width and odd/even number of data words
            noBits += ch.dataWidth
            if ch.dataWidth == WORD:
                self.oddNumberOfWords = not self.oddNumberOfWords
        self.numberOfWords = int(noBits / WORD)

        readWords = self.numberOfWords
        if self.oddNumberOfWords:
            readWords += 1
        gatherBufSize = 47 + ((readWords / 2) * numberOfSamples)
        # print "number of words: %d - number of samples: %d"%(
        # self.numberOfWords, numberOfSamples)
        self.parent.pmac.sendCommand("define gather %d" % gatherBufSize)
        return

    def triggerWait(self, waittime):
        time.sleep(waittime)
        self.btnCollect.setEnabled(True)

    def gatherTrigger(self):
        self.parent.pmac.sendCommand("gather")
        # print "sleeping for %f s"%(self.sampleTime * self.nGatherPoints /
        # 1000.0)
        t = myThread(self, self.sampleTime * self.nGatherPoints / 1000.0)
        t.start()
        # time.sleep(self.sampleTime * self.nGatherPoints / 1000.0)

    def collectData(self):
        (retStr, status) = self.parent.pmac.sendCommand("list gather")
        lstDataStrings = []
        if status:
            # lstDataStrings = retStr[:-1].split()
            for long_val in retStr[:-1].split():
                lstDataStrings.append(long_val.strip()[6:])
                lstDataStrings.append(long_val.strip()[:6])
        else:
            print(
                "Problem retrieving gather buffer, status: ",
                status,
                " returned data: ",
                retStr,
            )
            return False

        # print retStr[:-1].split()
        return lstDataStrings

    def parseData(self, lstDataStrings):
        lstDataArrays = []
        for _ in self.lstChannels:
            lstDataArrays.append([])

        channel = 0
        tmpLongVal = None

        for strVal in lstDataStrings:
            if channel >= self.numberOfChannels:
                channel = 0
                if self.oddNumberOfWords:
                    # Read a dummy word since an uneven number of words
                    # causes the pmac to send a random word at the end of a
                    # line...
                    continue

            if self.lstChannels[channel].dataWidth == WORD:
                lstDataArrays[channel].append(strVal)
                channel += 1
                continue
            if self.lstChannels[channel].dataWidth == LONGWORD:
                if not tmpLongVal:
                    tmpLongVal = strVal
                else:
                    lstDataArrays[channel].append(strVal + tmpLongVal)
                    tmpLongVal = None
                    channel += 1
                continue

        for chIndex, ch in enumerate(self.lstChannels):
            ch.setStrData(lstDataArrays[chIndex])
            ch.strToRaw()
            ch.rawToScaled()

    def plotData(self):

        # xAxisData = range(self.numberOfSamples)
        for chIndex, ch in enumerate(self.lstChannels):
            data = ch.scaledData
            # print "*** plotting data channel %d **************"%chIndex
            # print "datatype: %s"%str(ch.dataType)
            # print "length: %d"%len(data)
            # print "data: %s"%str(data)

            ch.qwtCurve.setData(arange(len(data)), data)

        self.qwtPlot.replot()
        # print "********** Done plotting **************"

    def calcSampleTime(self):
        cmd = "I10"
        (retStr, status) = self.parent.pmac.sendCommand(cmd)
        ivarI10 = int(retStr.strip("$")[:-1])
        self.servoCycleTime = ivarI10 / 8388608.0  # in ms

        # print "Length clock ticks: %.2fns #clock ticks per cycle: %d
        # servocycle time: %.3fms"%(lenClkTick, nClkTickServoCycle,
        # self.servoCycleTime)

        # calculate the actual sample time and frequency of the data
        # gathering function
        self.sampleTime = self.nServoCyclesGather * self.servoCycleTime
        realSampleFreq = 1.0 / self.sampleTime
        self.txtLblFreq.setText("%.3f kHz" % realSampleFreq)
        self.txtLblSignalLen.setText("%.2f ms" % (self.sampleTime * self.nGatherPoints))

    # ############## button clicked slots from here
    # #######################################

    def changedTab(self):
        # print "Changed tab"
        # Get the sample time (in servo cycles unit)
        cmd = "i5049"
        (retStr, status) = self.parent.pmac.sendCommand(cmd)
        newNGatherPoints = int(retStr.strip("$")[:-1])
        if not (newNGatherPoints == self.nServoCyclesGather):
            self.nServoCyclesGather = newNGatherPoints
            self.calcSampleTime()
        self.nServoCyclesGather = newNGatherPoints
        self.lneSampleTime.setText(str(self.nServoCyclesGather))

    def servoCyclesChanged(self):
        # Get the # of servo cycles per gather sampling
        self.nServoCyclesGather = int(str(self.lneSampleTime.text()))
        self.nGatherPoints = int(str(self.lneNumberSamples.text()))
        self.calcSampleTime()

    def changedNoSamples(self):
        # Get the # of data points to gather
        self.nGatherPoints = int(str(self.lneNumberSamples.text()))
        self.nServoCyclesGather = int(str(self.lneSampleTime.text()))
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
        # self.btnCollect.setEnabled(True)
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
        if len(self.lstChannels) < 1:
            QMessageBox.information(self, "Error", "No data has been collected yet.")
            return
        myDialog = QFileDialog(self)
        # myDialog.setShowHiddenFiles(False)
        fileName = myDialog.getSaveFileName(
            parent=self.parent,
            caption="Comma seperated data file (*.csv *.CSV)",
            directory=os.path.expanduser("~"),
            # options=None,
        )

        if not fileName:
            return
        try:
            fptr = open(str(fileName[0]), "w")
        except Exception:
            QMessageBox.information(
                self,
                "Error",
                "Could not open file for writing."
                # buttons=1,
                # p_str_1="OK",
            )
            print("could not open file '" + fileName[0] + "' for writing")
            return

        dataLists = []
        line = "point,"
        for i, channel in enumerate(self.lstChannels):
            line += "CH%d Axis%d %s," % (
                i,
                channel.axisNo,
                channel.dataSourceInfo["desc"],
            )
            dataLists.append(channel.scaledData)
        fptr.write(line + "\n")

        for lineNo, lineData in enumerate(zip(*dataLists)):
            line = "%d," % lineNo
            for data_point in lineData:
                line += "%f," % data_point
            fptr.write(line + "\n")
        fptr.close()
