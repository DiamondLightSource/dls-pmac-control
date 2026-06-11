import os
import time

from numpy import arange
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox
from qwt import QwtPlotCurve

from dls_pmac_control.gatherchannel import (
    LONGWORD,
    WORD,
    PmacGatherChannel,
    motor_base_addrs,
    pmac_data_sources,
)
from dls_pmac_control.ui_form_gather import UiFormGather

# TODO - this needs the logic decoupled from the GUI and moved into pmaclib
#  work has started in pmaclib but currently duplicates code in this module

# TODO Find out why the gathering fails with an response "ERR003" from the
#   PMAC for PMAC2-VME (does work for Geo Brick)!
#   (ERR003 = Data error or unrecognized command - solution: correct command syntax)


class MyThread(QThread):
    def __init__(self, instance, waittime):
        self.waittime = waittime
        self.instance = instance

    def run(self):
        PmacGatherform.trigger_wait(self.instance, self.waittime)


class PmacGatherform(QDialog, UiFormGather):
    def __init__(self, parent, current_motor=1):
        QDialog.__init__(self, parent)
        self.setup_ui(self)

        self.parent = parent
        if not self.parent:
            raise ValueError(
                "It is now required to provide a parent form for this form"
            )

        self.currentMotor = current_motor

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

        self.lstColours = [
            Qt.GlobalColor.red,
            Qt.GlobalColor.blue,
            Qt.GlobalColor.magenta,
            Qt.GlobalColor.green,
            Qt.GlobalColor.cyan,
        ]

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
        for cm_box in self.lstComboboxes:
            cm_box.clear()
        for data_point in pmac_data_sources:
            for cm_box in self.lstComboboxes:
                cm_box.addItem(data_point["desc"])

    def gather_config(self):
        # Create i5050 variable value to mask out what values to sample
        tmp_ivar = 0
        for bit, checkbox in enumerate(self.lstCheckboxes):
            if checkbox.isChecked():
                tmp_ivar |= 0x01 << bit
        if tmp_ivar == 0:
            return False
        cmd = f"i5051=0 i5050=${tmp_ivar:x}"
        self.parent.pmac.sendCommand(cmd)

        # Clear the plot by setting empty plotitems
        for _ch_index, ch in enumerate(self.lstChannels):
            ch.qwtCurve.setData([], [])

        # reset the data channels from class GatherChannel
        self.lstChannels = []

        # Left or right Y axis
        enable_right = False
        enable_left = False

        # Create the i5001 - i5005 values to specify what data to sample
        for index, axis_spin_box in enumerate(self.lstSpinboxes):
            cmb_box = self.lstComboboxes[index]
            chk_box = self.lstCheckboxes[index]
            data_offset = pmac_data_sources[cmb_box.currentIndex()]["reg"]
            base_address = motor_base_addrs[axis_spin_box.value() - 1]
            data_width = pmac_data_sources[cmb_box.currentIndex()]["size"]
            ivar = f"i50{index + 1:02d}"
            addr = f"${data_width:X}{base_address + data_offset:05X}"
            cmd = f"{ivar}={addr}"
            if chk_box.isChecked():
                self.parent.pmac.sendCommand(cmd)

                # create a new curve for the qwt plot and instanciate a
                # GatherChannel.

                # print "Set data: %s"%cmd
                curve = QwtPlotCurve(f"Ch{index}")
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
                    enable_left = True
                    # self.qwtPlot.setCurveYAxis(channel.qwtCurve,
                    # self.qwtPlot.yLeft)
                elif self.lstCmbYaxis[index].currentIndex() == 1:
                    enable_right = True
                    channel.qwtCurve.setYAxis(self.qwtPlot.yRight)
                    # self.qwtPlot.setCurveYAxis(channel.qwtCurve,
                    # self.qwtPlot.yRight)

        if enable_left and enable_right:
            self.qwtPlot.enableAxis(self.qwtPlot.yLeft, True)
            self.qwtPlot.enableAxis(self.qwtPlot.yRight, True)
        elif enable_left:
            self.qwtPlot.enableAxis(self.qwtPlot.yLeft, True)
            self.qwtPlot.enableAxis(self.qwtPlot.yRight, False)
        elif enable_right:
            self.qwtPlot.enableAxis(self.qwtPlot.yLeft, False)
            self.qwtPlot.enableAxis(self.qwtPlot.yRight, True)
        else:
            self.qwtPlot.enableAxis(self.qwtPlot.yLeft, False)
            self.qwtPlot.enableAxis(self.qwtPlot.yRight, False)
        # set the sampling time (in servo cycles)
        self.parent.pmac.sendCommand(f"i5049={int(str(self.lneSampleTime.text()))}")
        return True

    def gather_setup(self, number_of_samples=1):
        # Run through the bitmasks i5050 and i5051 to see which of the
        # 48 channels should be sampled.
        bit_offset = 1
        for ivar_mask in range(5050, 5052):
            (ret_str, status) = self.parent.pmac.sendCommand(f"i{ivar_mask}")

            # For each channel to sample, get the ivariable with the
            # ivariable to sample from,
            # This value is read from the PMAC as a double check to avoid
            # differences between the
            # PMAC data settings and the data set in this application.
            ch_count = 0
            for bit in range(WORD):
                if (int(ret_str.strip("$")[:-1], 16) >> bit & 0x01) > 0:
                    ch_index = bit + bit_offset
                    ivar = f"i50{ch_index:02d}"
                    ch_count += 1
                    if ch_count > len(self.lstChannels):
                        print(
                            "gatherSetup: Error: not enough GatherChannels "
                            "instantiated."
                        )
                        break
                    self.lstChannels[ch_count - 1].set_data_gather_pointer(ivar)

            bit_offset += WORD

        self.numberOfChannels = len(self.lstChannels)
        # print "number of channels = %d"%self.numberOfChannels

        self.numberOfWords = 0
        no_bits = 0

        # Run through all the channels to sample from
        self.oddNumberOfWords = False
        for _, ch in enumerate(self.lstChannels):
            # Get the data info
            ch.get_data_info()

            # Figure out the data width and odd/even number of data words
            no_bits += ch.dataWidth
            if ch.dataWidth == WORD:
                self.oddNumberOfWords = not self.oddNumberOfWords
        self.numberOfWords = int(no_bits / WORD)

        read_words = self.numberOfWords
        if self.oddNumberOfWords:
            read_words += 1
        gather_buf_size = 47 + ((read_words / 2) * number_of_samples)
        # print "number of words: %d - number of samples: %d"%(
        # self.numberOfWords, numberOfSamples)
        self.parent.pmac.sendCommand(f"define gather {gather_buf_size}")
        return

    def trigger_wait(self, waittime):
        time.sleep(waittime)
        self.btnCollect.setEnabled(True)

    def gather_trigger(self):
        self.parent.pmac.sendCommand("gather")
        # print "sleeping for %f s"%(self.sampleTime * self.nGatherPoints /
        # 1000.0)
        t = MyThread(self, self.sampleTime * self.nGatherPoints / 1000.0)
        t.start()
        # time.sleep(self.sampleTime * self.nGatherPoints / 1000.0)

    def collect_data(self):
        (ret_str, status) = self.parent.pmac.sendCommand("list gather")
        lst_data_strings = []
        if status:
            # lstDataStrings = retStr[:-1].split()
            for long_val in ret_str[:-1].split():
                lst_data_strings.append(long_val.strip()[6:])
                lst_data_strings.append(long_val.strip()[:6])
        else:
            print(
                "Problem retrieving gather buffer, status: ",
                status,
                " returned data: ",
                ret_str,
            )
            return False

        # print retStr[:-1].split()
        return lst_data_strings

    def parse_data(self, lst_data_strings):
        lst_data_arrays = []
        for _ in self.lstChannels:
            lst_data_arrays.append([])

        channel = 0
        tmp_long_val = None

        for str_val in lst_data_strings:
            if channel >= self.numberOfChannels:
                channel = 0
                if self.oddNumberOfWords:
                    # Read a dummy word since an uneven number of words
                    # causes the pmac to send a random word at the end of a
                    # line...
                    continue

            if self.lstChannels[channel].dataWidth == WORD:
                lst_data_arrays[channel].append(str_val)
                channel += 1
                continue
            if self.lstChannels[channel].dataWidth == LONGWORD:
                if not tmp_long_val:
                    tmp_long_val = str_val
                else:
                    lst_data_arrays[channel].append(str_val + tmp_long_val)
                    tmp_long_val = None
                    channel += 1
                continue

        for ch_index, ch in enumerate(self.lstChannels):
            ch.set_str_data(lst_data_arrays[ch_index])
            ch.str_to_raw()
            ch.raw_to_scaled()

    def plot_data(self):
        # xAxisData = range(self.numberOfSamples)
        for _ch_index, ch in enumerate(self.lstChannels):
            data = ch.scaledData
            # print "*** plotting data channel %d **************"%chIndex
            # print "datatype: %s"%str(ch.dataType)
            # print "length: %d"%len(data)
            # print "data: %s"%str(data)

            ch.qwtCurve.setData(arange(len(data)), data)

        self.qwtPlot.replot()
        # print "********** Done plotting **************"

    def calc_sample_time(self):
        cmd = "I10"
        (ret_str, status) = self.parent.pmac.sendCommand(cmd)
        ivar_i10 = int(ret_str.strip("$")[:-1])
        self.servoCycleTime = ivar_i10 / 8388608.0  # in ms

        # print "Length clock ticks: %.2fns #clock ticks per cycle: %d
        # servocycle time: %.3fms"%(lenClkTick, nClkTickServoCycle,
        # self.servoCycleTime)

        # calculate the actual sample time and frequency of the data
        # gathering function
        self.sampleTime = self.nServoCyclesGather * self.servoCycleTime
        real_sample_freq = 1.0 / self.sampleTime
        self.txtLblFreq.setText(f"{real_sample_freq:.3f} kHz")
        self.txtLblSignalLen.setText("%.2f ms" % (self.sampleTime * self.nGatherPoints))

    # ############## button clicked slots from here
    # #######################################

    def changed_tab(self):
        # print "Changed tab"
        # Get the sample time (in servo cycles unit)
        cmd = "i5049"
        (ret_str, status) = self.parent.pmac.sendCommand(cmd)
        new_n_gather_points = int(ret_str.strip("$")[:-1])
        if not (new_n_gather_points == self.nServoCyclesGather):
            self.nServoCyclesGather = new_n_gather_points
            self.calc_sample_time()
        self.nServoCyclesGather = new_n_gather_points
        self.lneSampleTime.setText(str(self.nServoCyclesGather))

    def servo_cycles_changed(self):
        # Get the # of servo cycles per gather sampling
        self.nServoCyclesGather = int(str(self.lneSampleTime.text()))
        self.nGatherPoints = int(str(self.lneNumberSamples.text()))
        self.calc_sample_time()

    def changed_no_samples(self):
        # Get the # of data points to gather
        self.nGatherPoints = int(str(self.lneNumberSamples.text()))
        self.nServoCyclesGather = int(str(self.lneSampleTime.text()))
        self.calc_sample_time()

    def collect_clicked(self):
        self.btnSetup.setEnabled(False)
        self.btnTrigger.setEnabled(False)
        self.btnCollect.setEnabled(False)
        self.btnSave.setEnabled(False)
        self.parse_data(self.collect_data())
        self.plot_data()

        self.btnSetup.setEnabled(True)
        self.btnTrigger.setEnabled(False)
        self.btnCollect.setEnabled(False)
        self.btnSave.setEnabled(True)

    def setup_clicked(self):
        # print "formGather.setupClicked(): Not implemented yet"
        self.numberOfSamples = int(str(self.lneNumberSamples.text()))
        self.gather_setup(self.numberOfSamples)
        self.btnSetup.setEnabled(True)
        self.btnTrigger.setEnabled(True)
        self.btnCollect.setEnabled(False)
        self.btnSave.setEnabled(False)

    def trigger_clicked(self):
        # print "formGather.triggerClicked(): Not implemented yet"
        self.btnTrigger.setEnabled(False)
        self.gather_trigger()
        self.btnSetup.setEnabled(True)
        # self.btnCollect.setEnabled(True)
        self.btnSave.setEnabled(False)

    def apply_config_clicked(self):
        # print "formGather.applyConfigClicked(): Not implemented yet"
        if not self.gather_config():
            return
        self.btnSetup.setEnabled(True)
        self.btnTrigger.setEnabled(False)
        self.btnCollect.setEnabled(False)
        self.btnSave.setEnabled(False)

    def save_clicked(self):
        if len(self.lstChannels) < 1:
            QMessageBox.information(self, "Error", "No data has been collected yet.")
            return
        my_dialog = QFileDialog(self)
        # myDialog.setShowHiddenFiles(False)
        file_name = my_dialog.getSaveFileName(
            parent=self.parent,
            caption="Comma seperated data file (*.csv *.CSV)",
            directory=os.path.expanduser("~"),
            # options=None,
        )

        if not file_name:
            return
        try:
            fptr = open(str(file_name[0]), "w")
        except Exception:
            QMessageBox.information(
                self,
                "Error",
                "Could not open file for writing.",
                # buttons=1,
                # p_str_1="OK",
            )
            print("could not open file '" + file_name[0] + "' for writing")
            return

        data_lists = []
        line = "point,"
        for i, channel in enumerate(self.lstChannels):
            line += f"CH{i} Axis{channel.axisNo} {channel.dataSourceInfo['desc']},"
            data_lists.append(channel.scaledData)
        fptr.write(line + "\n")

        for line_no, line_data in enumerate(zip(*data_lists, strict=False)):
            line = f"{line_no},"
            for data_point in line_data:
                line += f"{data_point:f},"
            fptr.write(line + "\n")
        fptr.close()
