#!/usr/bin/python3
# -*- coding: utf-8 -*-
import csv
import os.path
import sys
import time
import datetime

from time import gmtime, strftime
from PyQt5 import QtGui, QtWidgets, QtCore
from random import randint


class Parameters():

    # constructor
    def __init__(self, args):
        if len(args) == 2 and "reaction_time_test.py" in args[0]:

            # check if the parameter is a file
            if os.path.isfile(args[1]):
                self.parameters = self.readFile(args[1])
                self.areParametersValid(self.parameters)
            else:
                print('Unfortunately the given parameter is ' +
                      'not a file! Sorry!')
        elif len(args) < 2:
            print('No argument given! ' +
                  'Please add a filename for the test description! Thank you!')
            sys.exit(0)
        else:
            print('Sorry, you gave us too much arguments!')
            sys.exit(0)

    # Function to test if the given token is a integer or not
    def is_integer(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def readFile(self, filename):
        with open(filename) as f:
            content = f.readlines()
        result = {}
        # parse content in associative array
        for line in content:
            line = line.replace("\n", "")
            splitted = line.split(": ")
            key = splitted[0].strip()
            if(self.is_integer(splitted[1].strip())):
                value = int(splitted[1].strip())
            else:
                value = splitted[1].strip()
            result[key] = value
        return result

    def areParametersValid(self, arguments):
        if not (
                arguments['USER'] >= 1 and
                (arguments['HANDEDNESS'] == 'L'
                 or self.arguments['HANDEDNESS'] == 'R') and
                arguments['REPETITIONS'] > 0 and
                arguments['TIME_BETWEEN_SIGNALS_MS'] > 0 and
                len(arguments['HAND_TO_USE_ORDER']) -
                len(arguments['HAND_TO_USE_ORDER'].replace('L', '')) == 2 and
                len(arguments['HAND_TO_USE_ORDER']) -
                len(arguments['HAND_TO_USE_ORDER'].replace('R', '')) == 2):
            print('One or more definition values are invalid! Sorry!')
            sys.exit(0)

    def getParameters(self):
        return self.parameters


class ClickRecorder(QtWidgets.QMainWindow):
    user = 0
    handedness = ''
    repetitions = 0
    time_between_signals_ms = 0
    csvFileName = ''
    timers = []
    timespan = 0
    actualTest = 0
    keypairs = []
    keypair_for_test = []
    shown_key = ''
    pressed_key = ''

    # Only one measure for one signal
    keyPressed = False

    def __init__(self, dirname, user, handedness, repetitions,
                 time_between_signals_ms, handUsedOrder, orderTests, keypairs):
        super(ClickRecorder, self).__init__()
        self.user = user
        self.handedness = handedness
        self.repetitions = repetitions
        self.time_between_signals_ms = time_between_signals_ms
        self.counter = 0
        self.testActive = False
        self.csvFileName = (dirname + '\ClickResults_User_'
                            + str(self.user) + '_'
                            + str(strftime("%Y-%m-%d_%H_%M_%S",
                                           time.localtime()))
                            + '.csv')
        self.writeCSVHeader()
        self.handUsedOrder = handUsedOrder
        self.orderTests = orderTests
        self.actualTest = 0
        self.keypairs = keypairs
        self.text = self.setTestDescription()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 750, 600)
        self.setWindowTitle('ClickRecorder')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.show()

    def keyPressEvent(self, ev):
        timediff = int(round(time.time() * 1000)) - self.timespan

        try:
            self.pressed_key = chr(ev.key())
        except ValueError:
            print('Please press a valid key!')

        if (self.shown_key and self.pressed_key
                and self.testActive and self.counter <= self.repetitions
                and not self.keyPressed):
            print('Timespan ' + str(timediff))
            self.writeToCSV(self.user,
                            self.handedness,
                            self.repetitions,
                            self.time_between_signals_ms,
                            timediff, self.counter,
                            self.shown_key,
                            self.pressed_key,
                            self.orderTests[self.actualTest],
                            self.handUsedOrder[self.actualTest])
            self.keyPressed = True

        elif ev.key() == QtCore.Qt.Key_Return:
            print('Enter')
            if not self.testActive and len(self.orderTests) > self.actualTest:
                self.text = self.setTestDescription
                self.keypair_for_test = list(self.keypairs[self.actualTest])
                self.testActive = True
                self.startTest()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        if len(self.orderTests) > self.actualTest:
            if self.orderTests[self.actualTest] == 'Pre' and self.testActive:
                self.drawRandomRect(event, qp)
            elif (self.orderTests[self.actualTest] == 'Post' and
                  self.testActive):
                self.drawRandomText(event, qp)
            elif not self.testActive:
                self.drawText(event, qp)
        qp.end()

    def drawRandomText(self, event, qp):
        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 32))

        x = randint(20, 470)
        y = randint(20, 370)
        xend = x + 20
        yend = y + 20

        self.shown_key = self.keypair_for_test[
            randint(0, len(self.keypair_for_test) - 1)]

        qp.drawText(x, y, xend, yend, QtCore.Qt.AlignCenter, self.shown_key)

    def drawText(self, event, qp):
        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 24))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)
        self.timespan = int(round(time.time() * 1000))

    # the one signal
    def drawRandomRect(self, event, qp):
        rect = QtCore.QRect(randint(0, 670), randint(0, 520), 80, 80)
        qp.setBrush(QtGui.QColor(150, 150, 200))
        qp.drawRoundedRect(rect, 5.0, 5.0)
        self.shown_key = self.keypair_for_test[0]
        self.timespan = int(round(time.time() * 1000))

    # function to write in the csv
    def writeToCSV(self,
                   user,
                   handedness,
                   repetitions,
                   time_between_signals_ms,
                   timediff,
                   counter,
                   shown_key,
                   pressed_key,
                   test,
                   handUsed):
        with open(self.csvFileName, 'a', newline='') as csvFile:
            csvWriter = csv.writer(csvFile, delimiter=';',
                                   quoting=csv.QUOTE_MINIMAL)
            csvWriter.writerow(['{:%Y-%m-%d %H:%M:%S}'
                                .format(datetime.datetime.now()),
                                user,
                                handedness,
                                repetitions,
                                time_between_signals_ms,
                                timediff,
                                counter,
                                shown_key,
                                pressed_key,
                                test,
                                handUsed])

    def writeCSVHeader(self):
        with open(self.csvFileName, 'a', newline='') as csvFile:
            csvWriter = csv.writer(csvFile, delimiter=';',
                                   quoting=csv.QUOTE_MINIMAL)
            csvWriter.writerow(["Timestamp",
                                "User",
                                "Handedness",
                                "Repetitions",
                                "Time_between_signals_ms",
                                "Reation_Time", "Trial",
                                "Shown_Key",
                                "Pressed_Key",
                                "Mental_complexity",
                                "Hand_Used"])

    def preTest(self):
        if self.counter < self.repetitions and self.testActive:
            if self.keyPressed is False and self.counter != 0:
                self.writeToCSV(self.user,
                                self.handedness,
                                self.repetitions,
                                self.time_between_signals_ms,
                                self.time_between_signals_ms,
                                self.counter,
                                self.shown_key,
                                '',
                                self.orderTests[self.actualTest],
                                self.handUsedOrder[self.actualTest])
            self.update()
            self.keyPressed = False
            self.counter += 1
            self.text = ""
        else:
            if len(self.orderTests) > self.actualTest:
                self.actualTest += 1
                self.text = self.setTestDescription()
                self.testActive = False
                self.counter = 0
                self.update()
                self.timers[0].stop()
            else:
                self.counter = 0
                self.timers[0].stop()
                self.testActive = False
                self.update()

    def setTestDescription(self):
        if len(self.orderTests) > self.actualTest:
            hand_to_use = self.handUsedOrder[self.actualTest]
            if hand_to_use == 'L':
                hand_to_use = 'left'
            elif hand_to_use == 'R':
                hand_to_use = 'right'
            if self.orderTests[self.actualTest] == 'Pre':
                return ('Please press key '''
                        + self.keypairs[self.actualTest]
                        + ' with \n the index '
                        + 'finger of your '''
                        + hand_to_use
                        + ' hand \n every time a rectangle is shown!'
                        + '\n Press ''Enter'' to start the test!')
            elif self.orderTests[self.actualTest] == 'Post':
                return ('Please press the key presented on the screen'
                        + ' with \n the index '
                        + 'finger of your '''
                        + hand_to_use
                        + ' hand \n every time the character is shown!'
                        + '\n Press ''Enter'' to start the test!')
        else:
            return 'Thank you!'

    def startTest(self):
        self.timers = []
        timer = QtCore.QTimer()
        timer.timeout.connect(self.preTest)
        timer.start(self.time_between_signals_ms)
        self.timers.append(timer)


def main():
    parameterReader = Parameters(sys.argv)
    parameters = parameterReader.getParameters()
    orderTests = parameters['ORDER_TESTS'].split(' ')
    handUsedOrder = parameters['HAND_TO_USE_ORDER'].split(' ')
    keypair = parameters['KEY_PAIR'].split(' ')

    if len(orderTests) != len(handUsedOrder):
        print('Count of defined tests and count of hand to use ' +
              'order are not the same! Sorry!')
        sys.exit(0)

    app = QtWidgets.QApplication(sys.argv)
    click = ClickRecorder(os.path.dirname(__file__),
                          parameters['USER'],
                          parameters['HANDEDNESS'],
                          parameters['REPETITIONS'],
                          parameters['TIME_BETWEEN_SIGNALS_MS'],
                          handUsedOrder,
                          orderTests,
                          keypair)
    sys.exit(app.exec_())

# starting the main method
if __name__ == '__main__':
    main()
