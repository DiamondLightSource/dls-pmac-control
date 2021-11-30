import unittest

from mock import Mock, patch
from PyQt5.QtWidgets import QCheckBox, QMainWindow

from dls_pmaccontrol.energise import Energiseform


class DummyTestWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.pmac = Mock()
        self.commsThread = Mock()
        self.chkShowAll = QCheckBox(self)
        attrs = {"sendCommand.return_value": ("0\r5", True)}
        self.pmac.configure_mock(**attrs)


class EnergiseTest(unittest.TestCase):
    @patch("dls_pmaccontrol.energise.Energiseform.updateScreen")
    @patch("dls_pmaccontrol.energise.Energiseform.readM750x")
    @patch("dls_pmaccontrol.energise.Energiseform.createCheckBoxes")
    def setUp(self, mock_boxes, mock_read, mock_update):
        mock_read.return_value = (0, 0)
        self.test_widget = DummyTestWidget()
        self.obj = Energiseform(self.test_widget.pmac, self.test_widget)

    def test_initial_form(self):
        assert self.obj.pmac == self.test_widget.pmac
        assert self.obj.parent == self.test_widget
        assert self.obj.lstCheckBoxes is None

    def test_readM750x(self):
        (val1, val2) = self.obj.readM750x()
        self.obj.parent.pmac.sendCommand.assert_called_with("m7501 m7503")
        assert val1 == 0
        assert val2 == 5

    def test_update_screen(self):
        self.obj.createCheckBoxes()
        self.obj.val7501 = 1
        self.obj.val7503 = 3
        self.obj.updateScreen()
        for i in [0, 16, 17]:
            assert self.obj.lstCheckBoxes[i].isChecked() is True
        for j in range(1, 16):
            assert self.obj.lstCheckBoxes[j].isChecked() is False
        for k in range(18, 32):
            assert self.obj.lstCheckBoxes[k].isChecked() is False

    @patch("dls_pmaccontrol.energise.Energiseform.readM750x")
    def test_isScreenUpToDate(self, mock_read):
        mock_read.return_value = (0x00FFFF, 0x00FFFF)
        self.obj.val7501 = 0x00FFFF
        self.obj.val7503 = 0x00FFFF
        assert self.obj.isScreenUpToDate() is True

    @patch("dls_pmaccontrol.energise.Energiseform.updateScreen")
    @patch("dls_pmaccontrol.energise.Energiseform.readM750x")
    @patch("PyQt5.QtWidgets.QMessageBox.information")
    @patch("dls_pmaccontrol.energise.Energiseform.isScreenUpToDate")
    def test_sendCommand_outofdate(self, mock_screen, mock_box, mock_read, mock_update):
        mock_screen.return_value = False
        mock_read.return_value = (None, None)
        assert self.obj.sendCommand() is None
        assert mock_screen.called
        mock_box.assert_called_with(
            self.obj,
            "Error",
            "The screen is out of date, even if "
            "ignoring your changes!\n" + "This may be e.g. due to PLCs running in "
            "the background which de/energised some "
            "motors.\n"
            "To avoid inconsistency, the screen will "
            "reload now. Re-do your changes and submit "
            "again.",
        )
        assert mock_read.called
        assert mock_screen.called

    @patch("dls_pmaccontrol.energise.Energiseform.isScreenUpToDate")
    def test_sendCommand_uptodate(self, mock_screen):
        mock_screen.return_value = True
        self.obj.val7501 = 0xFF0000
        self.obj.val7503 = 0xFF0000
        self.obj.createCheckBoxes()
        assert self.obj.sendCommand() is None
        assert mock_screen.called
        cmd = "m7501=$ff0000 m7503=$ff0000"
        self.obj.parent.pmac.sendCommand.assert_called_with(cmd)

    def tearDown(self):
        self.obj.close()
