import sys
import time
import pyaudio
import wiimote
import bluetooth
import numpy as np
import matplotlib.pyplot as plt
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
        self.sampleRate = 0
        self.copiedOsc = None
        self.setupUI()
        self.initOscillators()

    def setupUI(self):
        """Setup all UI elements and connect signals"""
        self.ui.bt_connect.clicked.connect(self.connectToWiimote)
        self.ui.record.clicked.connect(self.openRecordingPopup)
        self.ui.play.clicked.connect(self.playSound)
        self.ui.preview.clicked.connect(self.showPreview)
        self.sampleRate = int(self.ui.sample_rate.text())

    def connectToWiimote(self):
        """Connect to WiiMote via Bluetooth"""
        try:
            self.wm = wiimote.connect(self.ui.bt_address.text())
        except(bluetooth.BluetoothError):
            # Show info when connection fails
            self.ui.connection_label.setText("Connection failed")
            self.ui.connection_label.setStyleSheet("color: red")
            self.enableUI(False)
            return

        self.ui.connection_label.setText("Connected")
        self.ui.connection_label.setStyleSheet("color: green")
        self.enableUI(True)

    def enableUI(self, enabled):
        """Enabled or disabled UI elements in the main window"""
        self.ui.osc_tabs.setEnabled(enabled)
        self.ui.record.setEnabled(enabled)
        self.ui.play.setEnabled(enabled)
        self.ui.preview.setEnabled(enabled)
        self.ui.stretch_3.setEnabled(enabled)

    def openRecordingPopup(self):
        """Open the popup which enables recording"""
        self.ui.setEnabled(False)
        self.sampleRate = int(self.ui.sample_rate.text())
        popup = RecordingPopup(self, self.sampleRate)
        popup.show()

    def initOscillators(self):
        for i in range(0, 3):
            self.oscillators.append(osc.Oscillator(i, self))

    def playSound(self):
        """Play the current soundwave"""
        p = pyaudio.PyAudio()
        wave = self.createWaveform()
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=44100,
                        output=True)

        # keep playing the sound until A button on wiiMote is pressed
        while not self.wm.buttons["A"]:
            stream.write(wave)

        stream.stop_stream()
        stream.close()

        p.terminate()

    def showPreview(self):
        """Draw current wave"""
        wave = self.createWaveform()
        plt.plot(wave)
        plt.show()

    def createWaveform(self):
        """Create the final waveform out of all oscillator data"""
        waves = []

        # check if oscillators are enabled
        if self.oscillators[0].isEnabled():
            waves.append(self.oscillators[0].getCurrentWave())
        else:
            waves.append([0])
        if self.oscillators[1].isEnabled():
            waves.append(self.oscillators[1].getCurrentWave())
        else:
            waves.append([0])
        if self.oscillators[2].isEnabled():
            waves.append(self.oscillators[2].getCurrentWave())
        else:
            # avoid nullpointer if all oscillators are disabled
            waves.append([0])

        # get longest signal and fill all other signals with zeros to match
        # its length
        maxLength = max([len(waves[0]), len(waves[1]), len(waves[2])])
        if len(waves[0]) < maxLength:
            waves[0] = np.append(waves[0], np.zeros(maxLength - len(waves[0])))
        if len(waves[1]) < maxLength:
            waves[1] = np.append(waves[1], np.zeros(maxLength - len(waves[1])))
        if len(waves[2]) < maxLength:
            waves[2] = np.append(waves[2], np.zeros(maxLength - len(waves[2])))

        # add up all enabled oscillator waves
        addedWave = np.zeros(maxLength)
        if self.oscillators[0].isEnabled():
            addedWave = addedWave + waves[0]
        if self.oscillators[1].isEnabled():
            addedWave = addedWave + waves[1]
        if self.oscillators[2].isEnabled():
            addedWave = addedWave + waves[2]

        return addedWave


class RecordingPopup(QtWidgets.QMainWindow):
    """Ui-popup which allows to record and name gestures"""

    def __init__(self, parent, sampleRate):
        super(self.__class__, self).__init__()
        self.parent = parent
        self.wm = parent.wm
        self.dataSets = []
        self.delay = 1 / sampleRate
        self.ui = uic.loadUi('recordingpopup.ui', self)
        start_new_thread(self.recordGestures, ())

    def closeEvent(self, event):
        # enable ui of parent when popup is closed
        self.parent.setEnabled(True)

    def resetData(self):
        self.dataSets = []

    def saveData(self, data):
        """Set data for each oscillator according to their selected axis"""
        for oscillator in self.parent.oscillators:
            if oscillator.shouldOverWrite():
                oscillator.setData(data[oscillator.getAxis()])
        # close the popup window
        self.close()

    def recordGestures(self):
        """Executed in a thread. Records data while the "A" button on the WiiMote
        is pressed"""
        isRecording = False
        currentRecordX = []
        currentRecordY = []
        currentRecordZ = []

        while self.isVisible():
            if self.wm.buttons["A"]:
                # check if recording is already running
                if not isRecording:
                    self.ui.status_label.setText("Recording...")
                    isRecording = True
                else:
                    # center the accelerometer values to zero
                    centeredX = self.wm.accelerometer[0] - 512
                    centeredY = self.wm.accelerometer[1] - 512
                    centeredZ = self.wm.accelerometer[2] - 512
                    centered = [centeredX, centeredY, centeredZ]
                    # normalize vector of all accelerometer axis
                    normalized = normalize(centered).ravel()
                    currentRecordX.append(normalized[0])
                    currentRecordZ.append(normalized[1])
                    currentRecordY.append(normalized[2])
                time.sleep(self.delay)
            elif isRecording:
                # save data after recording
                self.saveData([currentRecordX, currentRecordY, currentRecordZ])


def main():
    app = QtWidgets.QApplication(sys.argv)
    synth = Synthesizer()
    synth.show()
    app.exec_()


if __name__ == '__main__':
    main()
