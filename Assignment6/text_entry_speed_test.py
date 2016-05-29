#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore, QtWidgets, QtGui
import csv as csv
import time as clock


class SuperText(QtWidgets.QTextEdit):

    currentText = ""
    currentWord = ""
    currentSentence = ""
    sentenceCount = 0

    def __init__(self, sentences, logger):
        super(SuperText, self).__init__()
        self.setPlainText(sentences[0])
        self.initUI()
        self.logger = logger
        self.sentences = sentences
        self.textChanged.connect(self.textChangedCallback)

    def initUI(self):
        self.setGeometry(200, 200, 400, 400)
        self.setWindowTitle('Text Entry Speed Test')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)
        self.show()
        self.cursor = self.textCursor()
        self.cursor.movePosition(QtGui.QTextCursor.End,
                                 QtGui.QTextCursor.MoveAnchor)
        self.setTextCursor(self.cursor)

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
        additions = self.getAdditions()
        self.addChar(additions)
        self.checkWordEnd(additions)
        self.checkSentenceEnd(additions)

    def getAdditions(self):
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
        time = 0
        if char == "\n" and self.currentSentence != "":
            time = clock.time() - self.sentenceTime
            self.logger.logData({"event_type": "sentence finished", "value": self.currentSentence,
                                 "start_time": self.sentenceTime, "time_needed": time})
            #print("sentence: " + self.currentSentence + " time: " + str(time))
            self.currentSentence = ""
            self.setupNextSentence()

    def checkWordEnd(self, char):
        time = 0
        if char == " " or not char.isalpha() and char != "'":
            if self.currentWord != "":
                time = clock.time() - self.wordTime
                self.logger.logData({"event_type": "word finished", "value": self.currentWord,
                                     "start_time": self.wordTime, "time_needed": time})
                #print("word: " + self.currentWord + " time: " + str(time))
                self.currentWord = ""

    def startWordTimer(self):
        self.wordTime = clock.time()

    def startSentenceTimer(self):
        self.sentenceTime = clock.time()

    def setupNextSentence(self):
        self.sentenceCount += 1
        if self.sentenceCount == len(self.sentences):
            exit()
        self.setPlainText(self.sentences[self.sentenceCount])
        self.setTextCursor(self.cursor)


class CSVLogger:

    keys = ["event_type", "value", "start_time", "time_needed"]

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
    sentences = ["Das ist ein Satz.\n",
                 "Ich schreibe ein paar Wörter.\n",
                 "Dieses Programm ist wirklich beeindruckend.\n"
                 ]
    super_text = SuperText(sentences, logger)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
