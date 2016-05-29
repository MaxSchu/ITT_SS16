#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore, QtWidgets, QtGui
import csv as csv
import time as time


class SuperText(QtWidgets.QTextEdit):

    currentText = ""
    currentWord = ""
    currentSentence = ""

    def __init__(self, example_text, logger):
        super(SuperText, self).__init__()
        self.setPlainText(example_text)
        self.initUI()
        self.logger = logger
        self.textChanged.connect(self.textChangedCallback)

    def initUI(self):
        self.setGeometry(200, 200, 400, 400)
        self.setWindowTitle('Text Entry Speed Test')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)
        self.show()
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)
        self.setTextCursor(cursor)

    def keyPressEvent(self, event):
        if self.currentWord == "":
            self.startWordTimer()
        if self.currentSentence == "":
            self.startSentenceTimer()
        QtWidgets.QTextEdit.keyPressEvent(self, event)

    def textChangedCallback(self):
        if len(self.currentText) > len(self.toPlainText()):
            self.deleteLastChar()
            return
        lastCharacter = self.getLastChar()
        self.addChar(lastCharacter)
        self.checkSentenceEnd(lastCharacter)
        self.checkWordEnd(lastCharacter)

    def getLastChar(self):
        if len(self.currentText) < len(self.toPlainText()):
            self.currentText = self.toPlainText()
            return self.currentText[len(self.currentText) - 1]
        return ""

    def deleteLastChar(self):
        self.currentText = self.toPlainText()
        if len(self.currentWord) >= 1:
            self.currentWord = self.currentWord[:-1]
        if len(self.currentSentence) >= 1:
            self.currentSentence = self.currentSentence[:-1]

    def addChar(self, char):
        if char != "\n":
            self.currentSentence = self.currentSentence + char
        if char.isalpha() or char == "'":
            self.currentWord = self.currentWord + char

    def checkSentenceEnd(self, char):
        if char == "\n" and self.currentSentence != "":
            print("sentence: " + self.currentSentence)
            self.currentSentence = ""

    def checkWordEnd(self, char):
        if char == " " or not char.isalpha() and char != "'":
            if self.currentWord != "":
                print("word: " + self.currentWord)
                self.currentWord = ""

    def startWordTimer(self):

    def startSentenceTimer(self):


class CSVLogger:

    keys = ["event_type", "value"]

    def __init__(self):
        print("logger instantiated")
        self.csvWriter = csv.DictWriter(sys.stdout, self.keys)

    def logData(self, data):
        row = {}
        for key in data:
            row[key] = data[key]
        self.csvWriter.writerow(row)
        sys.stdout.flush


def main():
    app = QtWidgets.QApplication(sys.argv)
    logger = CSVLogger()
    super_text = SuperText("An 123 Tagen kamen 1342 Personen.", logger)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
