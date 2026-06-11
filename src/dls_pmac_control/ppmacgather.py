import os
import time

from numpy import arange
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox
from qwt import QwtPlotCurve

from dls_pmac_control.gatherchannel import PpmacGatherChannel, ppmac_data_sources
from dls_pmac_control.ui_form_gather import UiFormGather

# TODO - this needs the logic decoupled from the GUI and moved into pmaclib
#  work has started in pmaclib but currently duplicates code in this module


class MyThread(QThread):
    def __init__(self, instance, waittime):
        self.waittime = waittime
        self.instance = instance

    def run(self):
        PpmacGatherform.trigger_wait(self.instance, self.waittime)


class PpmacGatherform(QDialog, UiFormGather):
    def __init__(self, parent, current_motor=1):
        QDialog.__init__(self, parent)
        self.setup_ui(self)

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
        for data_point in ppmac_data_sources:
            for cm_box in self.lstComboboxes:
                cm_box.addItem(data_point["desc"])

    def gather_config(self):
        # Clear the plot by setting empty plotitems
        for _ch_index, ch in enumerate(self.lstChannels):
            ch.qwtCurve.setData([], [])

        # Reset the data channels from class PpmacGatherChannel
        self.lstChannels = []

        # Left or right Y axis
        enable_right = False
        enable_left = False

        # use counter to find number of items to gather
        items = 0

        # Specify data to sample
        for index, axis_spin_box in enumerate(self.lstSpinboxes):
            cm_box = self.lstComboboxes[index]
            chk_box = self.lstCheckboxes[index]

            addr_str = ppmac_data_sources[cm_box.currentIndex()]["addr"]
            gather_addr = f"Gather.Addr[{items}]"
            addr = f"Motor[{axis_spin_box.value()}].{addr_str}"
            cmd = f"{gather_addr}={addr}"

            if chk_box.isChecked():
                items += 1
                self.parent.pmac.sendCommand(cmd)

                # create a new curve for the qwt plot and instanciate a
                # PpmacGatherChannel.
                curve = QwtPlotCurve(f"Ch{index}")
                curve.attach(self.qwtPlot)
                channel = PpmacGatherChannel(self.parent.pmac, curve)
                self.lstChannels.append(channel)

                channel.axisNo = axis_spin_box.value()
                channel.descNo = cm_box.currentIndex()

                # Set the colour of the graph
                colour = self.lstColours[self.lstColourBoxes[index].currentIndex()]
                channel.qwtCurve.setPen(QPen(colour))
                # set the left or right Y axis
                if self.lstCmbYaxis[index].currentIndex() == 0:
                    channel.qwtCurve.setYAxis(self.qwtPlot.yLeft)
                    enable_left = True
                elif self.lstCmbYaxis[index].currentIndex() == 1:
                    enable_right = True
                    channel.qwtCurve.setYAxis(self.qwtPlot.yRight)

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

        # set the number of items to gather
        self.parent.pmac.sendCommand(f"Gather.items={items}")
        return True

    def gather_setup(self, number_of_samples=1):
        # set the sampling time (in servo cycles)
        self.parent.pmac.sendCommand(
            f"Gather.Period={int(str(self.lneSampleTime.text()))}"
        )
        # set the number of samples
        self.parent.pmac.sendCommand(
            f"Gather.MaxSamples={int(str(self.lneNumberSamples.text()))}"
        )
        return

    def trigger_wait(self, waittime):
        time.sleep(waittime)
        self.btnCollect.setEnabled(True)

    def gather_trigger(self):
        self.parent.pmac.sendCommand("Gather.enable=2")
        # gather time in secs
        gather_time = self.sampleTime * self.nGatherPoints / 1000.0
        t = MyThread(self, gather_time)
        t.start()

    def collect_data(self):
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

    def parse_data(self, lst_data_strings):
        pass  # need to write code here

    def plot_data(self):
        gather_file = "./gather.txt"
        # if gather file does not exist
        if not os.path.isfile(gather_file):
            QMessageBox.information(self, "Error", "No data has been collected yet.")
            return
        # if gather file is empty
        if os.path.getsize(gather_file) == 0:
            QMessageBox.information(self, "Error", "No data has been collected yet.")
            return
        for ch_index, ch in enumerate(self.lstChannels):
            data = [line.split(" ")[ch_index] for line in open(gather_file).readlines()]
            data = [float(s.strip("/n")) for s in data]
            ch.qwtCurve.setData(arange(len(data)), data)
            ch.Data = data
        self.qwtPlot.replot()

    def calc_sample_time(self):
        cmd = "Sys.ServoPeriod"
        (ret_str, status) = self.parent.pmac.sendCommand(cmd)
        self.servoCycleTime = float(ret_str)
        # calculate the actual sample time and frequency of the data
        # gathering function
        self.sampleTime = self.nServoCyclesGather * self.servoCycleTime
        real_sample_freq = 1.0 / self.sampleTime
        self.txtLblFreq.setText(f"{real_sample_freq:.3f} kHz")
        self.txtLblSignalLen.setText("%.2f ms" % (self.sampleTime * self.nGatherPoints))

    # ############## button clicked slots from here
    # #######################################

    def changed_tab(self):
        # Get the sample time (in servo cycles unit)
        cmd = "Gather.Period"
        (ret_str, status) = self.parent.pmac.sendCommand(cmd)
        new_n_gather_points = int(ret_str)
        if not (new_n_gather_points == self.nServoCyclesGather):
            self.nServoCyclesGather = new_n_gather_points
            self.calc_sample_time()
        self.nServoCyclesGather = new_n_gather_points
        self.lneSampleTime.setText(str(self.nServoCyclesGather))
        # Get the number of samples
        cmd = "Gather.MaxSamples"
        (ret_str, status) = self.parent.pmac.sendCommand(cmd)
        new_n_samples = int(ret_str)
        if not (new_n_samples == self.nGatherPoints):
            self.nGatherPoints = new_n_samples
            self.calc_sample_time()
        self.nGatherPoints = new_n_samples
        self.lneNumberSamples.setText(str(self.nGatherPoints))

    def servo_cycles_changed(self):
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
        (ret_str, success) = self.parent.pmac.sendCommand(cmd)
        if success:
            self.calc_sample_time()
        else:
            QMessageBox.information(self, "Error", "Could not set sample time.")

    def changed_no_samples(self):
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
        (ret_str, success) = self.parent.pmac.sendCommand(cmd)
        if success:
            self.calc_sample_time()
        else:
            QMessageBox.information(self, "Error", "Could not # of samples.")

    def collect_clicked(self):
        self.btnSetup.setEnabled(False)
        self.btnTrigger.setEnabled(False)
        self.btnCollect.setEnabled(False)
        self.btnSave.setEnabled(False)
        self.collect_data()
        # self.parseData(self.collectData())
        self.plot_data()

        self.btnSetup.setEnabled(True)
        self.btnTrigger.setEnabled(False)
        self.btnCollect.setEnabled(False)
        self.btnSave.setEnabled(True)

    def setup_clicked(self):
        self.numberOfSamples = int(str(self.lneNumberSamples.text()))
        self.gather_setup(self.numberOfSamples)
        self.btnSetup.setEnabled(True)
        self.btnTrigger.setEnabled(True)
        self.btnCollect.setEnabled(False)
        self.btnSave.setEnabled(False)

    def trigger_clicked(self):
        self.btnTrigger.setEnabled(False)
        self.gather_trigger()
        self.btnSetup.setEnabled(True)
        # self.btnCollect.setEnabled(True)
        self.btnSave.setEnabled(False)

    def apply_config_clicked(self):
        if self.nServoCyclesGather == 0:
            QMessageBox.information(self, "Error", "Sample time cannot be zero.")
            return
        if self.nGatherPoints == 0:
            QMessageBox.information(self, "Error", "# of samples cannot be zero.")
            return
        if not self.gather_config():
            return
        self.btnSetup.setEnabled(True)
        self.btnTrigger.setEnabled(False)
        self.btnCollect.setEnabled(False)
        self.btnSave.setEnabled(False)

    def save_clicked(self):
        my_dialog = QFileDialog(self)
        file_name = my_dialog.getSaveFileName(
            caption="Comma seperated data file (*.csv *.CSV)",
            directory=os.path.expanduser("~"),
            # options=None,
        )
        if not file_name:
            QMessageBox.information(self, "Error.", file_name[0] + " does not exist")
            return
        try:
            fptr = open(str(file_name[0]), "w")
        except Exception:
            QMessageBox.information(self, "Error.", "Could not open file for writing.")
            return

        data_lists = []
        line = "point,"
        for i, channel in enumerate(self.lstChannels):
            line += f"CH{i}, Axis {channel.axisNo}, {ppmac_data_sources[channel.descNo]['desc']}, "
            data_lists.append(channel.Data)
        fptr.write(line + "\n")

        for line_no, line_data in enumerate(zip(*data_lists, strict=False)):
            line = f"{line_no},"
            for data_point in line_data:
                line += f"{data_point:f},"
            fptr.write(line + "\n")
        fptr.close()
