#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import csv
import os
import threading
import time
import random
import datetime
from PyQt5 import QtGui, QtWidgets, QtCore

# please add the assets2 folder to the same directory like this python script
# otherwise the distraction mode doesn't work

# keys for CSV header
participant_key = "PARTICIPANT"
repetition_key = "REPETITIONS"
time_between_key = "TIME_BETWEEN_SIGNALS_MS"
order_key = "ORDER"
gender_key = "GENDER"
age_key = "AGE"
handedness_key = "HANDEDNESS"
reaction_time_key = "REACTION_TIME"
expected_button_key = "EXPECTED_BUTTON"
pressed_button_key = "PRESSED_KEY"
timestamp_key = "TIMESTAMP"
was_correct_button_key = "WAS_CORRECT_BUTTON"
signal_mode_key = "SIGNAL_MODE"
has_distraction_key = "HAS_DISTRACTION"
date_time_key = "DATE_TIME"


# reads a given file and its parameters
class FileReader():
    def readFile(self):
        parameters = {}
        if (len(sys.argv) == 2):
            file = open(sys.argv[1])
            for line in file:
                line = line.replace("\n", "")
                line = line.replace(" ", "")
                values = line.split(":")
                key = values[0]
                value = values[1]
                if (key == repetition_key or key == time_between_key or
                        key == age_key):
                    try:
                        value = int(value)
                    except ValueError:
                        print("Invalid value in " + key)
                        exit()
                parameters[key] = value
        self.checkDictionary(parameters)
        parameters[order_key] = self.splitOrderString(
            parameters[order_key])
        for key in parameters:
            print(key + ": " + str(parameters[key]))
        return parameters

    # checks if all required parameters exist in the given file
    def checkDictionary(self, dictionary):
        self.checkKey(dictionary, participant_key)
        self.checkKey(dictionary, repetition_key)
        self.checkKey(dictionary, time_between_key)
        self.checkKey(dictionary, order_key)
        self.checkKey(dictionary, gender_key)
        self.checkKey(dictionary, age_key)
        self.checkKey(dictionary, handedness_key)

    # checks if a specific parameter exists
    def checkKey(self, dictionary, key):
        if (key in dictionary.keys()):
            if (dictionary[key] is None or dictionary[key] == ""):
                print("no value for " + key + " variable")
                exit()
        else:
            print(key + " variable not found")
            exit()

    # splits up the parameter "order" into a list
    def splitOrderString(self, values):
        orderList = list(map(int, values.split(",")))
        if(len(orderList) != 4):
            print("Invalid order parameters")
            exit()
        return orderList


# creates and writes the obtained data to a CSV-file
class CSVWriter():
    def __init__(self, participantId, values):
        super(CSVWriter, self).__init__()
        self.createCSV(participantId, values)

    # creates a CSV file with header
    def createCSV(self, participantId, values):
        values = self.addMissingKeys(values)
        self.csvFileName = (os.path.dirname(__file__) + 'Test_Result' +
                            str(participantId) + '.csv')

        with open(self.csvFileName, 'a', newline='') as csvFile:
            fieldNames = list(sorted(values))
            csvWriter = csv.DictWriter(csvFile, fieldnames=fieldNames)
            csvWriter.writeheader()

    # writes data to the CSV-file
    def writeCSV(self, values):
        # convert order to string format:
        values.update(
            {order_key: str.replace(str(values[order_key]), ", ", "-")})
        with open(self.csvFileName, 'a', newline='') as csvFile:
            fieldNames = list(sorted(values))
            csvWriter = csv.DictWriter(csvFile, fieldnames=fieldNames)
            csvWriter.writerow(values)

    # adds all remaining headers
    def addMissingKeys(self, values):
        values.update({reaction_time_key: 0, pressed_button_key:
                       "", expected_button_key: "", timestamp_key: 0,
                       was_correct_button_key: False, signal_mode_key: "",
                       has_distraction_key: False, date_time_key: ""})
        return values


# creates the ui and handles ui-logic
class ClickRecorder(QtWidgets.QWidget):
    def __init__(self, values, writer):
        super(ClickRecorder, self).__init__()
        self.randInt = 0
        self.writer = writer
        self.values = values
        self.palette = QtGui.QPalette()
        self.position = (0, 0)
        self.showIntro = True
        self.maxCountdown = 4
        self.countdown = 0
        self.timeBetweenSignals = values[time_between_key] / 1000
        self.order = values[order_key]
        self.currentCondition = 0
        self.maxRepetitions = values[repetition_key]
        self.repetition = 0
        self.keys = (QtCore.Qt.Key_1, QtCore.Qt.Key_2)
        self.keyMapping = {self.keys[0]: "1", self.keys[1]: "2"}

        # 0 -> attentive; 1 -> pre-attentive
        self.mode = 0
        # 0 -> without distractions; 1 -> with distractions
        self.backgroundMode = 1

        self.uiBlocked = False
        self.showRect = True
        self.theThread = self.Distraction(self)
        self.theThread.start()
        self.timestampBuffer = 0
        self.correctKey = ""

        self.instructionsPreAttentive = """Everytime a SINGLE RECTANGLE appears press the "1"-KEY.
Everytime TWO RECTANGLES appear press the "2"-KEY.
Use the keys on the NUMPAD!
Try to press the corresponding key as fast as possible!
Use the index-finger of your right hand only."""

        self.instructionsAttentive = """Everytime an ODD NUMBER appears press the "1"-KEY.
Everytime an EVEN NUMBER appears press the "2"-KEY.
Use the keys on the NUMPAD!
Try to press the corresponding key as fast as possible!
Use the index-finger of your right hand only."""
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle('Paint')
        self.showIntroMessage()
        self.show()

    # shows the instructions for the current condition
    def showIntroMessage(self):
        if self.currentCondition > len(self.order) - 1:
            self.close()
            sys.exit(0)

        if self.currentCondition == 1:
            self.maxCountdown = int(self.maxCountdown / 2)

        # pre-attentive (squares) without distractions
        if self.order[self.currentCondition] == 1:
            self.mode = 1
            self.backgroundMode = 0
            self.instructions = self.instructionsPreAttentive
            self.values.update({signal_mode_key: "pre-attentive"})
            self.values.update({has_distraction_key: False})
        # pre-attentive (sqaures) with distractions
        elif self.order[self.currentCondition] == 2:
            self.mode = 1
            self.backgroundMode = 1
            self.instructions = self.instructionsPreAttentive
            self.values.update({signal_mode_key: "pre-attentive"})
            self.values.update({has_distraction_key: True})
        # attentive (numbers) without distrations
        elif self.order[self.currentCondition] == 3:
            self.mode = 0
            self.backgroundMode = 0
            self.instructions = self.instructionsAttentive
            self.values.update({signal_mode_key: "attentive"})
            self.values.update({has_distraction_key: False})
        # attentive (numbers) with distrations
        elif self.order[self.currentCondition] == 4:
            self.mode = 0
            self.backgroundMode = 1
            self.instructions = self.instructionsAttentive
            self.values.update({signal_mode_key: "attentive"})
            self.values.update({has_distraction_key: True})

        self.uiBlocked = True
        self.showIntro = True
        self.countdown = self.maxCountdown
        self.repetition = self.maxRepetitions
        t = threading.Timer(1.0, self.lowerCountdown)
        t.start()

    # clears out the background for the instructions screen
    def clearBackground(self):
        self.palette.setColor(QtGui.QPalette.Background, QtCore.Qt.white)
        self.setPalette(self.palette)

    def lowerCountdown(self):
        self.countdown -= 1
        if (self.countdown >= 0):
            t = threading.Timer(1.0, self.lowerCountdown)
            t.start()
            self.update()
        else:
            self.showIntro = False
            self.newSign()

    # selects a random image for the background
    def changeCatPic(self):
        self.palette.setBrush(
            QtGui.QPalette.Background, QtGui.QBrush(QtGui.QImage(
                "assets2/cat" + str(random.randint(1, 20)) + ".jpg")))
        self.setPalette(self.palette)

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.showIntro:
            self.drawIntro(qp)
        else:
            self.drawRectangle(qp)
        qp.end()

    # display a new sign/number on the screen
    def newSign(self):
        self.getNewRandomVars()
        self.uiBlocked = False
        self.showRect = True
        self.update()

    # get some random values to display
    def getNewRandomVars(self):
        self.position = (random.randint(0, 900), random.randint(0, 700))
        if self.mode == 0:
            self.randInt = random.randint(1, 8)
            if self.randInt % 2 == 0:
                self.correctKey = self.keys[1]
            else:
                self.correctKey = self.keys[0]
        else:
            self.randInt = random.randint(0, 1)
            if self.randInt == 0:
                self.correctKey = self.keys[1]
            else:
                self.correctKey = self.keys[0]

        self.values.update(
            {expected_button_key: self.keyMapping[self.correctKey]})

    # handle keypresses
    def keyPressEvent(self, ev):
        if self.uiBlocked:
            return

        try:
            pressedKey = chr(ev.key())
        except ValueError:
            pressedKey = "KeyCode: " + str(ev.key())

        reactionTime = time.time() - self.timestampBuffer
        self.values.update({pressed_button_key: pressedKey})

        if self.correctKey == ev.key():
            self.values.update({was_correct_button_key: True})
        else:
            self.values.update({was_correct_button_key: False})

        self.values.update({reaction_time_key: reactionTime})
        self.values.update({timestamp_key: time.time()})
        self.values.update({date_time_key: datetime.datetime.fromtimestamp(
            time.time()).strftime('%Y-%m-%d %H:%M:%S')})

        # write all the data for previous repetition to CSV
        self.writer.writeCSV(self.values)

        # block user-input until next sign/number is displayed
        self.uiBlocked = True
        self.repetition -= 1

        if self.repetition > 0:
            # create new signal after some delay
            self.t = threading.Timer(self.timeBetweenSignals, self.newSign)
            self.t.start()
        else:
            # return to instruction screen for next condition
            self.currentCondition += 1
            self.showIntroMessage()

        self.showRect = False
        self.update()

    # draws the rectangle which contains a sign/number
    def drawRectangle(self, qp):
        if self.showRect:
            qp.setBrush(QtGui.QColor(255, 255, 255))
            qp.drawRect(self.position[0], self.position[1], 100, 100)
            rect = QtCore.QRect(self.position[0], self.position[1], 100, 100)
            self.timestampBuffer = time.time()

            # attentive-mode -> display a number
            if self.mode == 0:
                qp.setFont(QtGui.QFont('Decorative', 32))
                qp.drawText(
                    rect, QtCore.Qt.AlignCenter, str(self.randInt))

            # pre-attentive-mode -> display squares
            else:
                qp.setBrush(QtGui.QColor(0, 0, 255))
                if self.randInt == 0:
                    qp.drawRect(
                        self.position[0] + 5, self.position[1] + 30, 40, 40)
                    qp.drawRect(
                        self.position[0] + 55, self.position[1] + 30, 40, 40)
                else:
                    qp.drawRect(
                        self.position[0] + 30, self.position[1] + 30, 40, 40)

    # draws instructions and countdown
    def drawIntro(self, qp):
        qp.setFont(QtGui.QFont('Decorative', 18))
        qp.drawText(
            QtCore.QRect(100, 100, 800, 300), QtCore.Qt.AlignCenter, self.instructions)
        qp.setFont(QtGui.QFont('Decorative', 32))
        qp.drawText(
            QtCore.QRect(100, 300, 800, 300), QtCore.Qt.AlignCenter, str(self.countdown))

    # thread which handles distractions without blocking main thread
    class Distraction(threading.Thread):
        def __init__(self, outer):
            threading.Thread.__init__(self)
            self.outer = outer

        def run(self):
            while True:
                if not self.outer.showIntro and self.outer.backgroundMode == 1:
                    self.outer.changeCatPic()
                    time.sleep(1)
                else:
                    self.outer.clearBackground()
                    time.sleep(1)


def main():
    reader = FileReader()
    values = reader.readFile()
    writer = CSVWriter(values[participant_key], values)
    app = QtWidgets.QApplication(sys.argv)
    recorder = ClickRecorder(values, writer)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
