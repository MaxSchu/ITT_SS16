import sys
import time
import wiimote
import bluetooth
import numpy as np
from sklearn.preprocessing import normalize
from _thread import start_new_thread
import oscillator as osc
from PyQt5 import QtWidgets, uic


class Synthesizer(QtWidgets.QMainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.ui = uic.loadUi('mainwindow.ui', self)
        self.wm = None
        self.oscillators = []
        self.setupUI()
        self.initOscillators()

    def setupUI(self):
        self.ui.bt_connect.clicked.connect(self.connectToWiimote)
        self.ui.record.clicked.connect(self.openRecordingPopup)

    def connectToWiimote(self):
        """Connect to WiiMote via Bluetooth"""
        try:
            self.wm = wiimote.connect(self.ui.bt_address.text())
        except(bluetooth.BluetoothError):
            self.ui.connection_label.setText("Connection failed")
            self.ui.connection_label.setStyleSheet("color: red")
            self.enableUI(False)
            return

        self.ui.connection_label.setText("Connected")
        self.ui.connection_label.setStyleSheet("color: green")
        self.enableUI(True)

    def enableUI(self, enabled):
        self.ui.osc_tabs.setEnabled(enabled)
        self.ui.record.setEnabled(enabled)

    def openRecordingPopup(self):
        self.ui.setEnabled(False)
        popup = RecordingPopup(self)
        popup.show()

    def initOscillators(self):
        for i in range(0, 3):
            self.oscillators.append(osc.Oscillator(i, self.ui))


class RecordingPopup(QtWidgets.QMainWindow):
    """Ui-popup which allows to record and name gestures"""

    def __init__(self, parent):
        super(self.__class__, self).__init__()
        self.parent = parent
        self.wm = parent.wm
        self.dataSets = []
        self.ui = uic.loadUi('recordingpopup.ui', self)
        start_new_thread(self.recordGestures, ())

    def closeEvent(self, event):
        # enable ui of parent when popup is closed
        self.parent.setEnabled(True)

    def resetData(self):
        self.dataSets = []

    def saveData(self, data):
        for oscillator in self.parent.oscillators:
            oscillator.setData(data[oscillator.getAxis()])

        self.close()

    def recordGestures(self):
        """Executed in a thread. Records data while the a button on the WiiMote
        is pressed"""
        isRecording = False
        currentRecordX = []
        currentRecordY = []
        currentRecordZ = []

        while self.isVisible():
            if self.wm.buttons["A"]:
                if not isRecording:
                    self.ui.status_label.setText("Recording...")
                    isRecording = True
                else:
                    centeredX = self.wm.accelerometer[0] - 512
                    centeredY = self.wm.accelerometer[1] - 512
                    centeredZ = self.wm.accelerometer[2] - 512
                    centered = [centeredX, centeredY, centeredZ]
                    normalized = normalize(centered).ravel()
                    currentRecordX.append(normalized[0])
                    currentRecordZ.append(normalized[1])
                    currentRecordY.append(normalized[2])
                time.sleep(0.05)
            elif isRecording:
                self.saveData([currentRecordX, currentRecordY, currentRecordZ])


def main():
    app = QtWidgets.QApplication(sys.argv)
    synth = Synthesizer()
    synth.show()
    app.exec_()


if __name__ == '__main__':
    main()
