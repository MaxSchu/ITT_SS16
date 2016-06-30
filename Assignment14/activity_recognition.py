from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import *
import sys
import wiimote
import os
import wii_gesture_classifier as c


class GestureTool(QtWidgets.QMainWindow):
    """
    This Class manages the UI and the WiiMote
    It records the accelerometer values from the Wiimote
    and stores them into a WiiGesture

    It is able to even retain the data after restart.
    For this feature all recorded values are stored into CSV.
    """

    gestureList = []
    currentGestureData = []
    currentGestureName = ""
    trainingMode = True
    recording = False
    defaultWiiMac = "B8:AE:6E:50:05:32"
    gestureListFileName = "gesture_list.txt"

    def __init__(self):
        super(self.__class__, self).__init__()
        self.ui = uic.loadUi('gesture.ui', self)
        self.setupUI()

    def setupUI(self):
        self.setupButtons()
        self.setupRadios()
        self.ui.wiiMacEdit.setText(self.defaultWiiMac)
        self.loadGestureList()

    def setupButtons(self):
        self.ui.addButton.clicked.connect(self.onAddClick)
        self.ui.deleteButton.clicked.connect(self.onDeleteClick)
        self.ui.connectButton.clicked.connect(self.onConnectClick)
        self.ui.gestureListWidget.currentItemChanged.connect(self.onListItemChanged)

    def setupRadios(self):
        self.ui.trainingRadio.setChecked(True)
        self.ui.trainingRadio.clicked.connect(self.onRadioClick)
        self.ui.classifyRadio.clicked.connect(self.onRadioClick)

    def updateListView(self):
        self.ui.gestureListWidget.clear()
        for gesture in self.gestureList:
            self.ui.gestureListWidget.addItem(gesture.name)
        self.ui.gestureListWidget.setCurrentRow(len(self.gestureList) - 1)

    def loadGestureList(self):
        lines = [line.rstrip("\n") for line in open(self.gestureListFileName)]
        for line in lines:
            if(line != ""):
                gesture = WiiGesture(line)
                self.loadCSVData(gesture)
                self.gestureList.append(gesture)
        self.updateListView()
        self.reloadClassifier()

    def loadCSVData(self, gesture):
        fileCount = 0
        #the csv in the training samples folder should not be altered by user
        path = "training_samples/" + gesture.name + "_" + str(0) + ".csv"
        data = []
        while os.path.isfile(path):
            lines = [line.rstrip("\n") for line in open(path)]
            for line in lines:
                values = line.split(",")
                print(values[3])
                data.append([int(values[1]), int(values[2]), int(values[3])])
            gesture.addTrainingsData(data)
            data = []
            fileCount += 1
            path = "training_samples/" + gesture.name + "_" + str(fileCount) + ".csv"

    def onAddClick(self):
        gestureName = self.ui.gestureNameEdit.text()
        if(gestureName == ""):
            self.output("Please input a name for gesture")
            return
        for gesture in self.gestureList:
            if(gestureName == gesture.name):
                self.output("Please dont use the same name twice")
                return
        self.gestureList.append(WiiGesture(gestureName))
        self.updateListView()
        self.save()
        self.output("Gesture %s added to list!" % gestureName)

    def onDeleteClick(self):
        fileCount = 0
        path = "training_samples/" + self.currentGestureName + "_" + str(0) + ".csv"
        while os.path.isfile(path):
            os.remove(path)
            fileCount += 1
            path = "training_samples/" + self.currentGestureName + "_" + str(fileCount) + ".csv"
        currentGesture = self.getGestureByName(self.currentGestureName)
        if currentGesture in self.gestureList:
            self.gestureList.remove(currentGesture)
        self.save()
        self.updateListView()
        self.reloadClassifier()

    def onConnectClick(self):
        wiimoteAddress = self.ui.wiiMacEdit.text()
        self.initWiimote(wiimoteAddress)

    def save(self):
        #saves the gesturelist into a textfile
        gestureListTxt = open(self.gestureListFileName, "w")
        for gesture in self.gestureList:
            gestureListTxt.write(gesture.name + "\n")
        gestureListTxt.close()

    def onRadioClick(self):
        #toggle between the two modes
        if self.trainingMode:
            self.ui.trainingRadio.setChecked(False)
            self.ui.classifyRadio.setChecked(True)
            self.trainingMode = False
        else:
            self.ui.trainingRadio.setChecked(True)
            self.ui.classifyRadio.setChecked(False)
            self.trainingMode = True

    def onListItemChanged(self, current, previous):
        if(current is not None):
            self.currentGestureName = current.text()

    def output(self, text):
        #method for displaying results in the UI
        self.ui.outputLabel.setText("Output: " + str(text))

    def wiimoteButtonPressed(self, btns):
        if len(btns) == 0:
            return
        for btn in btns:
            if btn[1]:
                if btn[0] == "A" and not self.recording:
                    self.startRecording()
                    self.recording = True
                elif btn[0] == "A" and self.recording:
                    self.stopRecording()
                    self.recording = False

    def initWiimote(self, wiimoteAddress):
        name = None
        self.output(("Connecting to %s (%s)" % (name, wiimoteAddress)))
        self.wm = wiimote.connect(wiimoteAddress, name)
        self.wm.buttons.register_callback(self.wiimoteButtonPressed)

    def stopRecording(self):
        self.wm.accelerometer.unregister_callback(self.recordAccel)
        #in here the recorded gesture is stored into the gesture list
        if self.trainingMode:
            gesture = self.getGestureByName(self.currentGestureName)
            gesture.addTrainingsData(self.currentGestureData)
            gesture.dataToCSV(self.currentGestureData)
            self.currentGestureData = []
            #update the classifier with the new list
            self.classifier = c.WiiGestureClassifier()
            callback = self.classifier.train(self.gestureList)
            self.output("%s training samples for %s recorded" % (len(gesture.trainingsData), gesture.name) + str(callback)) 
        else:
            #this case is the classifying mode
            gesture = WiiGesture(self.currentGestureName)
            gesture.addTrainingsData(self.currentGestureData)
            self.currentGestureData = []
            if self.classifier is not None:
                self.output(self.gestureList[self.classifier.classify(gesture)].name)
            else:
                self.output("Before classifying you need to train some gestures first!")

    def startRecording(self):
        self.wm.accelerometer.register_callback(self.recordAccel)
        self.output("started recording") 

    def recordAccel(self, values):
        self.currentGestureData.append(values)

    def gestureListToString(self, gestureList):
        #for debugging porposes, gets a string representation of gestureList
        string = ""
        for gesture in gestureList:
            string += gesture.toString() + "\n"
        return string

    def reloadClassifier(self):
        self.classifier = c.WiiGestureClassifier()
        self.classifier.train(self.gestureList)

    def getGestureByName(self, name):
        for gesture in self.gestureList:
            if gesture.name == name:
                return gesture
        return None


class WiiGesture():
    """
    This class is used to store all training samples
    for a certain gesture
    """
    path = "training_samples/"

    def __init__(self, name):
        self.name = name
        self.trainingsData = []
        self.frequencies = []

    def toString(self):
        string = self.name + "\n"
        for dataSet in self.trainingsData:
            for xyz in dataSet:
                string += "["
                for value in xyz:
                    string += str(value) + " "
                string += "], "
            string += "\n"
        return string

    def addTrainingsData(self, data):
        self.trainingsData.append(data)

    def dataToCSV(self, data):
        #method to store training data into csv
        csv = open("training_samples/" + self.name + "_" + str(len(self.trainingsData) - 1) + ".csv", "w")
        for values in data:
            csv.write(self.name + "," + str(values[0]) + "," + str(values[1]) + "," + str(values[2]) + "\n")
        csv.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    gestureTool = GestureTool()
    gestureTool.show()
    app.exec_()


if __name__ == '__main__':
    main()
