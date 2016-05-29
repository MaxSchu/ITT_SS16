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
    typedText = ""
    sentenceCount = 0
    testStarted = False
    loadingNextSentence = False

    def __init__(self, sentences, logger):
        super(SuperText, self).__init__()
        self.setPlainText(sentences[0])
        self.currentText = sentences[0]
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
        if not self.testStarted:
            self.startTime = clock.time()
            self.testStarted = True
        self.logger.logData(self.buildLogData(
            "key_pressed", event.key(), clock.time(),
            0, self.calcWordsPerMinute()))
        if self.currentWord == "":
            self.startWordTimer()
        if self.currentSentence == "":
            self.startSentenceTimer()

        QtWidgets.QTextEdit.keyPressEvent(self, event)

    def textChangedCallback(self):
        if not self.loadingNextSentence:
            if len(self.currentText) > len(self.toPlainText()):
                self.deleteLastChar()
                return
            additions = self.getAdditions()
            self.addChar(additions)
            self.checkWordEnd(additions)
            self.checkSentenceEnd(additions)

    def getAdditions(self):
        if len(self.currentText) < len(self.toPlainText()):
            lengthDifference = len(self.toPlainText()) - len(self.currentText)
            self.currentText = self.toPlainText()
            self.typedText += self.currentText[-lengthDifference:]
            return self.currentText[-lengthDifference:]
        return ""

    def deleteLastChar(self):
        self.currentText = self.toPlainText()
        if len(self.currentWord) >= 1:
            self.currentWord = self.currentWord[:-1]
        if len(self.currentSentence) >= 1:
            self.currentSentence = self.currentSentence[:-1]
        if len(self.typedText) >= 1:
            self.typedText = self.typedText[:-1]

    def addChar(self, char):
        if char != "\n":
            self.currentSentence = self.currentSentence + char
        if char.isalpha() or char == "'":
            self.currentWord = self.currentWord + char

    def checkSentenceEnd(self, char):
        time = 0
        if char == "\n" and self.currentSentence != "":
            time = clock.time() - self.sentenceTime
            self.logger.logData(self.buildLogData(
                "sentence_finished", self.currentSentence, self.sentenceTime,
                time, self.calcWordsPerMinute()))
            self.currentSentence = ""
            self.setupNextSentence()

    def checkWordEnd(self, char):
        time = 0
        if char == " " or not char.isalpha() and char != "'":
            if self.currentWord != "":
                time = clock.time() - self.wordTime
                self.logger.logData(self.buildLogData(
                    "word finished", self.currentWord, self.wordTime,
                    time, self.calcWordsPerMinute()))
                self.currentWord = ""

    def startWordTimer(self):
        self.wordTime = clock.time()

    def startSentenceTimer(self):
        self.sentenceTime = clock.time()

    def setupNextSentence(self):
        self.loadingNextSentence = True
        self.sentenceCount += 1
        if self.sentenceCount == len(self.sentences):
            self.logger.logData(self.buildLogData("test finished", self.typedText,
                                                  self.startTime, (clock.time(
                                                  ) - self.startTime),
                                                  self.calcWordsPerMinute()))
            exit()
        self.setPlainText(self.sentences[self.sentenceCount])
        self.currentText = self.sentences[self.sentenceCount]
        self.setTextCursor(self.cursor)
        self.loadingNextSentence = False

    def buildLogData(self, eventType, value, startTime, timeNeeded, wpm):
        return {"event_type": eventType, "value": value,
                "start_time": startTime, "time_passed": timeNeeded,
                "words_per_minute": wpm}

    def calcWordsPerMinute(self):
        typedCharactersCount = len(self.typedText)
        return (float(typedCharactersCount) / (float(clock.time()) - float(self.startTime)) * float(60)) / float(5)


class CSVLogger:

    keys = ["event_type", "value", "start_time",
            "time_passed", "words_per_minute"]

    def __init__(self):
        self.csvWriter = csv.DictWriter(sys.stdout, self.keys)

    def logData(self, data):
        self.csvWriter.writerow(data)
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
