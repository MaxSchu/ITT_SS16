from PyQt5 import uic, QtWidgets, QtGui
from _thread import start_new_thread
import sys
import time
import wiimote
import bluetooth
import pylab
from scipy import fft
from sklearn import svm
import numpy as np

# ammount of samples that should be recorded for each dataset
EXPECTED_SAMPLES = 50

DEFAULT_PROGRESS_BAR = """
QProgressBar{
    border: 2px solid grey;
    border-radius: 5px;
    text-align: center
}

QProgressBar::chunk {
    background-color: lightgreen;
    width: 10px;
    margin: 1px;
}
"""

UNCOMPLETE_PROGRESS_STYLE = """
QProgressBar{
    border: 2px solid grey;
    border-radius: 5px;
    text-align: center
}

QProgressBar::chunk {
    background-color: red;
    width: 10px;
    margin: 1px;
}
"""


class DataSet():
    """Contains raw recorded accelerometer for one executed gesture data and
    extracts features like stddev, fft and mean values."""

    def __init__(self, rawData):
        super(self.__class__, self).__init__()
        self.rawData = rawData
        self.xFreq = self.calculateFFT(0)
        self.yFreq = self.calculateFFT(1)
        self.zFreq = self.calculateFFT(2)
        self.xDev = self.calculateSTD(0)
        self.yDev = self.calculateSTD(1)
        self.zDev = self.calculateSTD(2)
        self.xMean = self.calculateMean(0)
        self.yMean = self.calculateMean(1)
        self.zMean = self.calculateMean(2)

    def calculateFFT(self, index):
        """Calculate the FFT from the raw recorded accelerometer data.
        Index indicates the axis. """

        values = []
        for n in self.rawData:
            values.extend([n[index]])

        return [np.abs(fft(values) / len(values))[1:len(values) / 2]]

    def calculateSTD(self, index):
        """Calculate the standard deviation from the raw recorded accelerometer data.
        Index indicates the axis. """

        values = []
        for n in self.rawData:
            values.extend([n[index]])

        return np.std(values)

    def calculateMean(self, index):
        """Calculate the mean from the raw recorded accelerometer data.
        Index indicates the axis. """

        values = []
        for n in self.rawData:
            values.extend([n[index]])

        return np.std(values)

    def returnDataSet(self):
        return self.xFreq + self.yFreq + self.zFreq
        + self.xDev + self.yDev + self.zDev
        + self.xMean + self.yMean + self.zMean


class Gesture():
    """Contains all recorded datasets for a defined gesture"""

    def __init__(self, gestureId, dataSets):
        super(self.__class__, self).__init__()
        self.gestureId = gestureId
        self.dataSets = dataSets

    def getID(self):
        return self.gestureId

    def getData(self):
        data = []
        for n in self.dataSets:
            data.append(n.returnDataSet())

        return data


class RecordingPopup(QtWidgets.QMainWindow):
    """Ui-popup which allows to record and name gestures"""

    def __init__(self, parent):
        super(self.__class__, self).__init__()
        self.parent = parent
        self.wm = parent.wm
        self.dataSets = []
        self.ui = uic.loadUi('popup.ui', self)
        self.setupButtons()
        start_new_thread(self.recordGestures, ())

    def setupButtons(self):
        self.ui.saveButton.clicked.connect(self.saveData)
        self.ui.resetButton.clicked.connect(self.resetData)

    def closeEvent(self, event):
        # enable ui of parent when popup is closed
        self.parent.setEnabled(True)

    def resetData(self):
        self.dataSets = []
        self.ui.exampleCounter.setText(
            "Recorded examples: " +
            str(len(self.recordedPattern)))

    def saveData(self):
        if len(self.dataSets) > 0:
            self.parent.addListEntry(self.ui.gestureName.text())
            test = Gesture(len(self.parent.gestures), self.dataSets)
            self.parent.addGesture(test)
        else:
            print("no data recorded")
        self.close()

    def recordGestures(self):
        """Executed in a thread. Records gestures while the a button on the WiiMote
        is pressed"""

        isRecording = False
        currentRecord = []

        while self.isVisible():
            if self.wm.buttons["A"]:
                if not isRecording:
                    self.ui.progressBar.setStyleSheet(DEFAULT_PROGRESS_BAR)
                    self.ui.recordingStatus.setText("Recording...")
                    isRecording = True

                if len(currentRecord) < EXPECTED_SAMPLES:
                    currentRecord.append(self.wm.accelerometer._state)
                    self.ui.progressBar.setValue(
                        (len(currentRecord) / EXPECTED_SAMPLES) * 100)
            else:
                if isRecording:
                    if len(currentRecord) < EXPECTED_SAMPLES:
                        # need more samples
                        self.ui.recordingStatus.setText("Not enough data!")
                        self.ui.progressBar.setStyleSheet(
                            UNCOMPLETE_PROGRESS_STYLE)
                    else:
                        self.ui.recordingStatus.setText(
                            "Recording successfull!")
                        self.dataSets.append(DataSet(currentRecord))
                        self.ui.exampleCounter.setText(
                            "Recorded examples: " +
                            str(len(self.dataSets)))
                    currentRecord = []
                    isRecording = False

            time.sleep(0.04)


class DetectionPopup(QtWidgets.QMainWindow):
    """Ui-popup which allows to detect gestures"""

    def __init__(self, parent, classifier):
        super(self.__class__, self).__init__()
        self.parent = parent
        self.wm = parent.wm
        self.classifier = classifier
        self.ui = uic.loadUi('popupDetection.ui', self)
        start_new_thread(self.recordGestures, ())

    def closeEvent(self, event):
        # enable ui of parent when popup is closed
        self.parent.setEnabled(True)

    def recordGestures(self):
        """Executed in a thread. Records gestures while the a button on the WiiMote
        is pressed"""

        isRecording = False
        currentRecord = []

        while self.isVisible():
            if self.wm.buttons["A"]:
                if not isRecording:
                    self.ui.progressBar.setStyleSheet(DEFAULT_PROGRESS_BAR)
                    self.ui.recordingStatus.setText("Recording...")
                    isRecording = True

                if len(currentRecord) < EXPECTED_SAMPLES:
                    currentRecord.append(self.wm.accelerometer._state)
                    self.ui.progressBar.setValue(
                        (len(currentRecord) / EXPECTED_SAMPLES) * 100)
            else:
                if isRecording:
                    if len(currentRecord) < EXPECTED_SAMPLES:
                        # need more samples
                        self.ui.recordingStatus.setText("Not enough data!")
                        self.ui.progressBar.setStyleSheet(
                            UNCOMPLETE_PROGRESS_STYLE)
                    else:
                        dataSet = DataSet(currentRecord)
                        self.predict(dataSet)
                    currentRecord = []
                    isRecording = False

            time.sleep(0.04)

    def predict(self, dataSet):
        """Predicts the recorded dataSet with trained classifier"""

        # map data to 2-dimensional array
        nparray = np.array([dataSet.returnDataSet()])
        nsamples, nx, ny = nparray.shape
        data = nparray.reshape((nsamples, nx * ny))

        category = self.classifier.predict(data)
        self.ui.recordingStatus.setText(
            "DETECTED GESTURE: " +
            self.parent.listModel.item(category).text())


class MainApp(QtWidgets.QMainWindow):
    """Main application window"""

    def __init__(self):
        super(self.__class__, self).__init__()
        self.wm = None
        self.gestures = []
        self.classifier = svm.SVC()
        self.ui = uic.loadUi('mainwindow.ui', self)
        self.listView = self.ui.listView
        self.listModel = QtGui.QStandardItemModel(self.listView)
        self.interactionButtons = self.getInteractionButtons()
        self.listView.setModel(self.listModel)
        self.setupButtons()

    def closeEvent(self, event):
        # When main window is closed: quit the whole program
        sys.exit(0)

    def getInteractionButtons(self):
        ui = self.ui
        return [ui.addButton, ui.deleteButton, ui.detectButton,
                ui.editButton, ui.listView]

    def setupButtons(self):
        # connect clicked signals to methods
        self.ui.addButton.clicked.connect(self.openGestureEditor)
        self.ui.deleteButton.clicked.connect(self.removeGesture)
        self.ui.editButton.clicked.connect(self.editGesture)
        self.ui.detectButton.clicked.connect(self.detectGesture)
        self.ui.connectionButton.clicked.connect(self.connectWiiMote)

    def addGesture(self, gesture):
        self.gestures.append(gesture)
        if (len(self.gestures)) > 1:
            self.trainSVM()

    def trainSVM(self):
        """Train the SVM classifier with all recorded gestures"""

        trainingData = []
        gestureID = []
        for gesture in self.gestures:
            trainingData += gesture.getData()
            gestureID += [gesture.getID()] * len(gesture.getData())

        # map data to 2-dimensional array
        nparray = np.array(trainingData)
        nsamples, nx, ny = nparray.shape
        trainingData2 = nparray.reshape((nsamples, nx * ny))

        self.classifier = svm.SVC()
        self.classifier.fit(trainingData2, gestureID)

    def openGestureEditor(self):
        self.ui.setEnabled(False)
        popup = RecordingPopup(self)
        popup.show()

    def addListEntry(self, name):
        newItem = QtGui.QStandardItem(name)
        self.listModel.appendRow(newItem)

    def removeGesture(self):
        if len(self.listView.selectedIndexes()) < 1:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Select at least one gesture to remove.")
            return
        else:
            for i in self.listView.selectedIndexes():
                item = self.listModel.item(i)
                self.gestures.pop(item.row)
                self.listModel.removeRow(item.row())
            # TODO: remove gesture

    def detectGesture(self):
        self.ui.setEnabled(False)
        popup = DetectionPopup(self, self.classifier)
        popup.show()

    def editGesture(self):
        if len(self.listView.selectedIndexes()) != 1:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Select exactly one gesture to edit.")
        else:
            pass
            # TODO: edit gestures

    def connectWiiMote(self):
        """Connect to WiiMote via Bluetooth"""

        try:
            self.wm = wiimote.connect(self.ui.btAddressInput.text())
        except(bluetooth.BluetoothError):
            self.ui.connectionLabel.setText("Connection failed")
            self.ui.connectionLabel.setStyleSheet("color: red")
            self.enableInteractionButtons(False)
            return

        self.ui.connectionLabel.setText("Connected")
        self.ui.connectionLabel.setStyleSheet("color: green")
        self.enableInteractionButtons(True)

    def enableInteractionButtons(self, enabled):
        for button in self.interactionButtons:
            button.setEnabled(enabled)


def main():
    app = QtWidgets.QApplication(sys.argv)
    mainApp = MainApp()
    mainApp.show()
    app.exec_()


if __name__ == '__main__':
    main()
