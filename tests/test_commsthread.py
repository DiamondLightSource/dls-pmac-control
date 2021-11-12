import PyQt5
import unittest
from mock import patch, Mock, call
import time
import sys
sys.path.append('/home/dlscontrols/bem-osl/dls-pmac-control/dls_pmaccontrol')
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem
from commsThread import CommsThread

app = QApplication(sys.argv)

class TestWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.pmac = Mock()
        self.progressEventType = Mock()
        self.downloadDoneEventType = Mock()
        self.updatesReadyEventType = Mock()
        self.verboseMode = False
        iter_ret = [(True,0,"command","response"),(True,0,"command","response")]
        attrs = {
        "sendCommand.return_value" : ("0\r1\r2\r3",True),
        "getNumberOfAxes.return_value" : 8,
        "sendSeries.return_value" : iter(iter_ret)}
        self.pmac.configure_mock(**attrs)

class CommsthreadTest(unittest.TestCase):

    @patch("threading.Lock")
    @patch("threading.Thread")
    @patch("queue.Queue")
    def setUp(self, mock_queue, mock_thread, mock_lock):
        self.test_widget = TestWidget()
        self.obj = CommsThread(self.test_widget)

    def test_init(self):
        assert self.obj.parent == self.test_widget
        assert self.obj.CSNum == 1
        assert self.obj.gen == None
        assert self.obj.updateReadyEvent == None
        assert self.obj.disablePollingStatus == False
        assert self.obj.max_pollrate == None
        assert self.obj.lineNumber == 0
        assert self.obj._watch_window == {}

    def test_add_watch(self):        
        self.obj.add_watch("test")
        assert self.obj._watch_window["test"] == None

    def test_remove_watch(self):        
        self.obj.add_watch("test")
        self.obj.remove_watch("test")
        assert self.obj._watch_window == {}

    def test_clear_watch(self):        
        self.obj.add_watch("test")
        self.obj.clear_watch()
        assert self.obj._watch_window == {}

    def test_read_watch(self):        
        self.obj.add_watch("test")
        assert self.obj.read_watch("test") == None

    @patch("PyQt5.QtCore.QCoreApplication.postEvent")
    @patch("commsThread.CustomEvent")
    def test_send_tick(self, mock_custom, mock_event):        
        self.obj.sendTick(0,"err")
        assert mock_custom.called
        assert mock_event.called

    @patch("PyQt5.QtCore.QCoreApplication.postEvent")
    @patch("commsThread.CustomEvent")
    def test_send_complete(self, mock_custom, mock_event):        
        self.obj.sendComplete("msg")
        assert self.obj.gen == None
        assert mock_custom.called
        assert mock_event.called

    @patch("commsThread.CommsThread.updateFunc")
    def test_update_thread(self, mock_updatefunc):
        mock_updatefunc.return_value = True
        self.obj.updateThread()
        assert mock_updatefunc.called

class UpdatefuncTest(unittest.TestCase):

    @patch("threading.Lock")
    @patch("threading.Thread")
    @patch("queue.Queue")
    def setUp(self, mock_queue, mock_thread, mock_lock):
        self.test_widget = TestWidget()
        self.obj = CommsThread(self.test_widget)

    @patch("queue.Queue.get")
    def test_update_func_die(self, mock_get):
        mock_get.return_value = ("die", "data")
        assert self.obj.updateFunc() == True

    @patch("PyQt5.QtCore.QCoreApplication.postEvent")
    @patch("commsThread.CustomEvent")
    @patch("queue.Queue.put")
    @patch("queue.Queue.get")
    def test_update_func_sendseries(self, mock_get, mock_put, mock_custom, mock_event):
        mock_get.return_value = ("sendSeries", "data")
        self.obj.parent.pmac.isConnectionOpen = True
        self.obj.disablePollingStatus = None
        assert self.obj.updateFunc() == None

    @patch("queue.Queue.get")
    def test_update_func_disable(self, mock_get):
        mock_get.return_value = ("disablePollingStatus", True)
        self.obj.gen = False
        self.obj.parent.pmac.isConnectionOpen = True
        ret = self.obj.updateFunc()
        assert self.obj.disablePollingStatus == True
        assert ret == None

    @patch("PyQt5.QtCore.QCoreApplication.postEvent")
    @patch("commsThread.CustomEvent")
    @patch("queue.Queue.put")
    @patch("queue.Queue.get")
    def test_update_func_cancel(self, mock_get, mock_put, mock_custom, mock_event):
        mock_get.return_value = ("cancelSendSeries", "data")
        self.obj.parent.pmac.isConnectionOpen = True
        self.obj.disablePollingStatus = False
        self.obj.gen = False
        ret = self.obj.updateFunc()
        assert ret == None
        assert mock_put.call_count == 5
        assert mock_custom.called
        assert mock_event.called
