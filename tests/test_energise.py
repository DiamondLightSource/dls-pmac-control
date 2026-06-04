import unittest
from unittest.mock import Mock, patch

from PyQt6.QtWidgets import QCheckBox, QMainWindow

from dls_pmac_control.energise import Energiseform


class DummyTestWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.pmac = Mock()
        self.commsThread = Mock()
        self.chkShowAll = QCheckBox(self)
        attrs = {"send_command.return_value": ("0\r5", True)}
        self.pmac.configure_mock(**attrs)


class EnergiseTest(unittest.TestCase):
    @patch("dls_pmac_control.energise.Energiseform.update_screen")
    @patch("dls_pmac_control.energise.Energiseform.read_m750x")
    @patch("dls_pmac_control.energise.Energiseform.create_check_boxes")
    def setUp(self, mock_boxes, mock_read, mock_update):
        mock_read.return_value = (0, 0)
        self.test_widget = DummyTestWidget()
        self.obj = Energiseform(self.test_widget.pmac, self.test_widget)

    def test_initial_form(self):
        assert self.obj.pmac == self.test_widget.pmac
        assert self.obj.parent == self.test_widget
        assert self.obj.lstCheckBoxes is None

    def test_read_m750x(self):
        (val1, val2) = self.obj.read_m750x()
        self.obj.parent.pmac.send_command.assert_called_with("m7501 m7503")
        assert val1 == 0
        assert val2 == 5

    def test_update_screen(self):
        self.obj.create_check_boxes()
        self.obj.val7501 = 1
        self.obj.val7503 = 3
        self.obj.update_screen()
        for i in [0, 16, 17]:
            assert self.obj.lstCheckBoxes[i].isChecked() is True
        for j in range(1, 16):
            assert self.obj.lstCheckBoxes[j].isChecked() is False
        for k in range(18, 32):
            assert self.obj.lstCheckBoxes[k].isChecked() is False

    @patch("dls_pmac_control.energise.Energiseform.read_m750x")
    def test_is_screen_up_to_date(self, mock_read):
        mock_read.return_value = (0x00FFFF, 0x00FFFF)
        self.obj.val7501 = 0x00FFFF
        self.obj.val7503 = 0x00FFFF
        assert self.obj.is_screen_up_to_date() is True

    @patch("dls_pmac_control.energise.Energiseform.update_screen")
    @patch("dls_pmac_control.energise.Energiseform.read_m750x")
    @patch("PyQt6.QtWidgets.QMessageBox.information")
    @patch("dls_pmac_control.energise.Energiseform.is_screen_up_to_date")
    def test_send_command_outofdate(
        self, mock_screen, mock_box, mock_read, mock_update
    ):
        mock_screen.return_value = False
        mock_read.return_value = (None, None)
        assert self.obj.send_command() is None
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

    @patch("dls_pmac_control.energise.Energiseform.is_screen_up_to_date")
    def test_send_command_uptodate(self, mock_screen):
        mock_screen.return_value = True
        self.obj.val7501 = 0xFF0000
        self.obj.val7503 = 0xFF0000
        self.obj.create_check_boxes()
        assert self.obj.send_command() is None
        assert mock_screen.called
        cmd = "m7501=$ff0000 m7503=$ff0000"
        self.obj.parent.pmac.send_command.assert_called_with(cmd)

    def tearDown(self):
        self.obj.close()
