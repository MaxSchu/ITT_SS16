#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtGui, QtWidgets, QtCore


class ClickRecorder():

    participant_key = "PARTICIPANT"
    repetition_key = "REPETITIONS"
    time_between_key = "TIME_BETWEEN_SIGNALS_MS"
    order_key = "ORDER"

    def __init__(self):
        print("in init" + sys.argv[1])
        print(self)
        self.readFile()
        #self.counter = 0
        #self.initUI()

    def readFile(self):
        parameters = {}
        if (len(sys.argv) == 2):
            file = open(sys.argv[1])
            for line in file:
                line = line.replace("\n", "")
                values = line.split(": ")
                key = values[0]
                value = values[1]
                if (key == self.repetition_key or key == self.time_between_key):
                    try:
                        value = int(value)
                    except ValueError:
                        print("Invalid value in " + key)
                        exit()
                parameters[key] = value
        self.checkDictionary(parameters)
        parameters[self.order_key] = self.splitOrderString(parameters[self.order_key])
        for key in parameters:
            print(key + ": " + str(parameters[key]))
        return parameters

    def checkDictionary(self, dictionary):
        self.checkKey(dictionary, self.participant_key)
        self.checkKey(dictionary, self.repetition_key)
        self.checkKey(dictionary, self.time_between_key)
        self.checkKey(dictionary, self.order_key)

    def checkKey(self, dictionary, key):
        if (key in dictionary.keys()):
            if (dictionary[key] is None or dictionary[key] == ""):
                print("no value for " + key)
                exit()
        else:
            print(key + " not found")
            exit()

    def splitOrderString(self, values):
        orderList = list(map(int, values.split(" ")))
        if(len(orderList) != 4):
            print("Invalid order parameters")
            exit()
        return orderList

    def initUI(self):
        # set the text property of the widget we are inheriting
        self.text = "Please press 'space' repeatedly."
        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('ClickRecorder')
        # widget should accept focus by click and tab key
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.show()

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Space:
            self.counter += 1
            self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        self.drawRect(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 32))
        if self.counter > 0:
            self.text = str(self.counter)
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)

    def drawRect(self, event, qp):
        if (self.counter % 2) == 0:
            rect = QtCore.QRect(10, 10, 80, 80)
            qp.setBrush(QtGui.QColor(34, 34, 200))
        else:
            rect = QtCore.QRect(100, 10, 80, 80)
            qp.setBrush(QtGui.QColor(200, 34, 34))
        qp.drawRoundedRect(rect, 10.0, 10.0)


def main():
    ClickRecorder()
if __name__ == '__main__':
    main()
