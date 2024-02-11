import os
import threading
import time

from numpy import arange
from PyQt5.Qt import QPen
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from qwt import QwtPlotCurve

from dls_pmaccontrol.gatherchannel import PpmacGatherChannel, ppmacDataSources
from dls_pmaccontrol.ui_formGather import Ui_formGather

# TODO - this needs the logic decoupled from the GUI and moved into pmaclib
#  work has started in pmaclib but currently duplicates code in this module


class myThread(threading.Thread):
    def __init__(self, instance, waittime):
        threading.Thread.__init__(self)
        self.waittime = waittime
        self.instance = instance

    def run(self):
        PpmacGatherform.triggerWait(self.instance, self.waittime)


class PpmacGatherform(QDialog, Ui_formGather):
    def __init__(self, parent, currentMotor=1):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.parent = parent
        if not self.parent:
            raise ValueError(
                "It is now required to provide a parent form for this form"
            )

        # initialize the data lists that will contain
        # the gathered data
        self.numberOfSamples = 0
        # self.numberOfChannels = 0
        self.lstChannels = []

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
        for dataPoint in ppmacDataSources:
            for cmBox in self.lstComboboxes:
                cmBox.addItem(dataPoint["desc"])

    def gatherConfig(self):
        # Clear the plot by setting empty plotitems
        for chIndex, ch in enumerate(self.lstChannels):
            ch.qwtCurve.setData([], [])

        # Reset the data channels from class PpmacGatherChannel
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

            addr_str = ppmacDataSources[cmBox.currentIndex()]["addr"]
            gather_addr = "Gather.Addr[%d]" % items
            addr = "Motor[%d].%s" % (axisSpinBox.value(), addr_str)
            cmd = "%s=%s" % (gather_addr, addr)

            if chkBox.isChecked():
                items += 1
                self.parent.pmac.sendCommand(cmd)

                # create a new curve for the qwt plot and instanciate a
                # PpmacGatherChannel.
                curve = QwtPlotCurve("Ch%d" % index)
                curve.attach(self.qwtPlot)
                channel = PpmacGatherChannel(self.parent.pmac, curve)
                self.lstChannels.append(channel)

                channel.axisNo = axisSpinBox.value()
                channel.descNo = cmBox.currentIndex()

                # Set the colour of the graph
                colour = self.lstColours[self.lstColourBoxes[index].currentIndex()]
                channel.qwtCurve.setPen(QPen(colour))
                # set the left or right Y axis
                if self.lstCmbYaxis[index].currentIndex() == 0:
                    channel.qwtCurve.setYAxis(self.qwtPlot.yLeft)
                    enableLeft = True
                elif self.lstCmbYaxis[index].currentIndex() == 1:
                    enableRight = True
                    channel.qwtCurve.setYAxis(self.qwtPlot.yRight)

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
        self.parent.pmac.sendCommand(
            "Gather.Period=%d" % int(str(self.lneSampleTime.text()))
        )
        # set the number of samples
        self.parent.pmac.sendCommand(
            "Gather.MaxSamples=%d" % int(str(self.lneNumberSamples.text()))
        )
        return

    def triggerWait(self, waittime):
        time.sleep(waittime)
        self.btnCollect.setEnabled(True)

    def gatherTrigger(self):
        self.parent.pmac.sendCommand("Gather.enable=2")
        # gather time in secs
        gather_time = self.sampleTime * self.nGatherPoints / 1000.0
        t = myThread(self, gather_time)
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
        except Exception:
            QMessageBox.information(
                self, "Error", "Could not get gather file from power pmac."
            )
            return

    def parseData(self, lstDataStrings):
        pass  # need to write code here

    def plotData(self):
        gather_file = "./gather.txt"
        # if gather file does not exist
        if not os.path.isfile(gather_file):
            QMessageBox.information(self, "Error", "No data has been collected yet.")
            return
        # if gather file is empty
        if os.path.getsize(gather_file) == 0:
            QMessageBox.information(self, "Error", "No data has been collected yet.")
            return
        for chIndex, ch in enumerate(self.lstChannels):
            data = [line.split(" ")[chIndex] for line in open(gather_file).readlines()]
            data = [float(s.strip("/n")) for s in data]
            ch.qwtCurve.setData(arange(len(data)), data)
            ch.Data = data
        self.qwtPlot.replot()

    def calcSampleTime(self):
        cmd = "Sys.ServoPeriod"
        (retStr, status) = self.parent.pmac.sendCommand(cmd)
        self.servoCycleTime = float(retStr)
        # calculate the actual sample time and frequency of the data
        # gathering function
        self.sampleTime = self.nServoCyclesGather * self.servoCycleTime
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
        # Get the number of samples
        cmd = "Gather.MaxSamples"
        (retStr, status) = self.parent.pmac.sendCommand(cmd)
        newNSamples = int(retStr)
        if not (newNSamples == self.nGatherPoints):
            self.nGatherPoints = newNSamples
            self.calcSampleTime()
        self.nGatherPoints = newNSamples
        self.lneNumberSamples.setText(str(self.nGatherPoints))

    def servoCyclesChanged(self):
        # Get the # of servo cycles per gather sampling
        self.nServoCyclesGather = int(str(self.lneSampleTime.text()))
        # self.nGatherPoints = int(str(self.lneNumberSamples.text()))
        if self.nServoCyclesGather == 0:
            QMessageBox.information(self, "Error", "Sample time cannot be zero.")
            return
        if self.nGatherPoints == 0:
            QMessageBox.information(self, "Error", "# of samples cannot be zero.")
            return
        cmd = "Gather.Period=" + str(self.lneSampleTime.text())
        (retStr, success) = self.parent.pmac.sendCommand(cmd)
        if success:
            self.calcSampleTime()
        else:
            QMessageBox.information(self, "Error", "Could not set sample time.")

    def changedNoSamples(self):
        # Get the # of data points to gather
        self.nGatherPoints = int(str(self.lneNumberSamples.text()))
        # self.nServoCyclesGather = int(str(self.lneSampleTime.text()))
        if self.nGatherPoints == 0:
            QMessageBox.information(self, "Error", "# of samples cannot be zero.")
            return
        if self.nServoCyclesGather == 0:
            QMessageBox.information(self, "Error", "Sample time cannot be zero.")
            return
        cmd = "Gather.MaxSamples=" + str(self.lneNumberSamples.text())
        (retStr, success) = self.parent.pmac.sendCommand(cmd)
        if success:
            self.calcSampleTime()
        else:
            QMessageBox.information(self, "Error", "Could not # of samples.")

    def collectClicked(self):
        self.btnSetup.setEnabled(False)
        self.btnTrigger.setEnabled(False)
        self.btnCollect.setEnabled(False)
        self.btnSave.setEnabled(False)
        self.collectData()
        # self.parseData(self.collectData())
        self.plotData()

        self.btnSetup.setEnabled(True)
        self.btnTrigger.setEnabled(False)
        self.btnCollect.setEnabled(False)
        self.btnSave.setEnabled(True)

    def setupClicked(self):
        self.numberOfSamples = int(str(self.lneNumberSamples.text()))
        self.gatherSetup(self.numberOfSamples)
        self.btnSetup.setEnabled(True)
        self.btnTrigger.setEnabled(True)
        self.btnCollect.setEnabled(False)
        self.btnSave.setEnabled(False)

    def triggerClicked(self):
        self.btnTrigger.setEnabled(False)
        self.gatherTrigger()
        self.btnSetup.setEnabled(True)
        # self.btnCollect.setEnabled(True)
        self.btnSave.setEnabled(False)

    def applyConfigClicked(self):
        if self.nServoCyclesGather == 0:
            QMessageBox.information(self, "Error", "Sample time cannot be zero.")
            return
        if self.nGatherPoints == 0:
            QMessageBox.information(self, "Error", "# of samples cannot be zero.")
            return
        if not self.gatherConfig():
            return
        self.btnSetup.setEnabled(True)
        self.btnTrigger.setEnabled(False)
        self.btnCollect.setEnabled(False)
        self.btnSave.setEnabled(False)

    def saveClicked(self):
        myDialog = QFileDialog(self)
        fileName = myDialog.getSaveFileName(
            caption="Comma seperated data file (*.csv *.CSV)",
            directory=os.path.expanduser("~"),
            # options=None,
        )
        if not fileName:
            QMessageBox.information(self, "Error.", fileName[0] + " does not exist")
            return
        try:
            fptr = open(str(fileName[0]), "w")
        except Exception:
            QMessageBox.information(self, "Error.", "Could not open file for writing.")
            return

        dataLists = []
        line = "point,"
        for i, channel in enumerate(self.lstChannels):
            line += "CH%d, Axis %d, %s, " % (
                i,
                channel.axisNo,
                ppmacDataSources[channel.descNo]["desc"],
            )
            dataLists.append(channel.Data)
        fptr.write(line + "\n")

        for lineNo, lineData in enumerate(zip(*dataLists)):
            line = "%d," % lineNo
            for data_point in lineData:
                line += "%f," % data_point
            fptr.write(line + "\n")
        fptr.close()
