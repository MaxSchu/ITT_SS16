#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import csv as csv
import time as clock
from PyQt5 import Qt, QtGui, QtCore, QtWidgets
import re


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
        if char == "":
            return
        if char[len(char) - 1] == " " or not char.isalpha():
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
        return {"pid": 1, "chords": True, "event_type": eventType, "value": value,
                "start_time": startTime, "time_passed": timeNeeded,
                "words_per_minute": wpm}

    def calcWordsPerMinute(self):
        typedCharactersCount = len(self.typedText)
        return (float(typedCharactersCount) / (float(clock.time()) - float(self.startTime)) * float(60)) / float(5)


class CSVLogger:

     keys = ["pid", "chords", "event_type", "value", "start_time",
            "time_passed", "words_per_minute"]

    def __init__(self):
        self.csvWriter = csv.DictWriter(sys.stdout, self.keys)

    def logData(self, data):
        self.csvWriter.writerow(data)
        sys.stdout.flush


class ChordInputMethod(QtCore.QObject):
    VALID_LETTERS = "[a-zäöüß ]"

    def __init__(self, superText):
        super(ChordInputMethod, self).__init__()
        self.superText = superText
        self.keys = []
        self.chordCode = []
        self.chordSwitcher = False
        self.counter = 0
        self.chords = self.readChords()

    def readChords(self):
        # read the possible chords from a file
        defaultFile = "chords_default.txt"
        chords = {}
        frozenchord = {}
        chord = ""
        words = ""

        if (len(sys.argv) == 2):
            # load chord file - use either default or custom file
            try:
                file = open(sys.argv[1], "r")
            except (IOError, OSError):
                print("Could not find file with chords. Using default file.")

                try:
                    file = open(defaultFile, "r")
                except (IOError, OSError):
                    print("Could not load chord file.")
                    sys.exit()
        else:
            try:
                file = open(defaultFile, "r")
            except (IOError, OSError):
                print("Could not load chord file.")
                sys.exit()

        temp = file.read().splitlines()

        for line in temp:
            try:
                # read chord combination
                chord = (line.split(":"))[0]
                # create frozenset to use as key in dictionary
                frozenchord = frozenset(list(chord))

                if len(chord) == 1:
                    print(
                        "Hint - Chord should be at least two characters long: " + chord)

                # read possible translations for chord
                words = ((line.split(":"))[1]).split(",")

                if frozenchord in chords:
                    print("Warning - Duplicate Chord: " + chord)
                    # add possible translations if chord is a duplicate
                    words.extend(chords[frozenchord])

                chords.update({frozenchord: words})
            except IndexError:
                print("Could not read chord " + line + "!")

        file.close()
        return chords

    def resetChordCounter(self):
        self.keys = []
        self.chordCode = []
        self.chordSwitcher = False
        self.counter = 0

    def getWord(self):
        titleCase = False
        compareSet = []

        try:
            for s in self.keys:
                if s.isupper():
                    # check if any character in chord is uppercase
                    # -> make word titlecase if true
                    titleCase = True
                # set has to be lowercase when compared to possible chords
                compareSet.append(s.lower())

            if " " in compareSet:
                # remove 'space' when comparing set to chards
                compareSet.remove(" ")
            if len(self.chords[frozenset(compareSet)]) <= self.counter:
                # avoud out of bounds exception
                self.counter = 0

            if (titleCase):
                return ((self.chords[frozenset(compareSet)]))[self.counter].title()
            else:
                return ((self.chords[frozenset(compareSet)]))[self.counter]
        except KeyError:
            self.counter = 0
            self.chordSwitcher = False
            return "".join(self.keys)

    def removePastLetter(self, watched_textedit, count):
        # remove characters from widget
        for x in range(0, count):
            Qt.qApp.postEvent(watched_textedit, QtGui.QKeyEvent(
                Qt.QKeyEvent.KeyPress, QtCore.Qt.Key_Backspace, QtCore.Qt.NoModifier))

    def eventFilter(self, watched_textedit, ev):
        if not ev.spontaneous():
            # ignore events that we injected ourselves
            return False
        if not ev.type() in [Qt.QKeyEvent.KeyPress, Qt.QKeyEvent.KeyRelease]:
            # ignore everything else
            return False
        if re.match(ChordInputMethod.VALID_LETTERS, ev.text().lower()) is None:
            # only check this _after_ we are sure that we have a QKeyEvent!
            return False
        if ev.isAutoRepeat():
            # completely eliminate these, as they might interfere with chords!
            return True
        # finally, we only have interesting key presses/releases left
        if ev.type() == Qt.QKeyEvent.KeyPress:  # collect keys
            self.keys.append(ev.text())

            if self.chordSwitcher:
                if ev.text() == " " and self.keys == self.chordCode:
                    # replace the old word...
                    self.removePastLetter(
                        watched_textedit, len(self.getWord()))
                    # ...and switch through alternatives
                    self.counter += 1
                    Qt.qApp.postEvent(watched_textedit, QtGui.QKeyEvent(
                        Qt.QKeyEvent.KeyPress, 0, QtCore.Qt.NoModifier, text=self.getWord()))
                    return True
            else:
                self.chordCode = []
                self.chordSwitcher = False

            # always filter press events
            if (ev.text() == " "):
                return True
            else:
                return False
        elif ev.type() == Qt.QKeyEvent.KeyRelease:  # release chord once one of the keys is released
            if " " not in self.keys:
                # space has to be used to build a chord
                self.resetChordCounter()
                return False

            # chords have to be at least one character + space
            if len(self.keys) > 1 and not self.chordSwitcher:
                # if chord is used, remove the past characters first
                self.removePastLetter(
                    watched_textedit, len(self.keys) - 1)
                result = self.getWord()
                Qt.qApp.postEvent(watched_textedit, QtGui.QKeyEvent(
                    Qt.QKeyEvent.KeyPress, 0, QtCore.Qt.NoModifier, text=result))

                if (ev.text() != " "):
                    self.resetChordCounter()
                else:
                    # if only space is released, the user wants to switch to
                    # aternative maybe
                    self.chordCode = self.keys
                    self.keys.remove(" ")
                    self.chordSwitcher = True
                    return False
            if ev.text() in self.keys:
                # remove released buttons from set
                self.keys.remove(ev.text())
            if ev.text() == " " and not self.chordSwitcher:
                Qt.qApp.postEvent(watched_textedit, QtGui.QKeyEvent(
                    Qt.QKeyEvent.KeyPress, 0, QtCore.Qt.NoModifier, text=" "))
            return False
        else:
            print("Should'nt arrive here: " + str(ev))
            return False


def main():
    app = QtWidgets.QApplication(sys.argv)

    sentences = ["Ein Smartphone ist ein Mobiltelefon, das erheblich umfangreichere Funktionalitäten als ein herkömmliches Mobiltelefon zur Verfügung stellt.\n",
                 "Erste Smartphones vereinigten die Funktionen eines Personal Digital Assistant mit der Funktionalität eines Mobiltelefons.\n",
                 "Später wurde dem Smartphone die Funktion eines transportablen Medienabspielgerätes und einer Digitalkamera hinzugefügt.\n",
                 "Ein zentrales Merkmal moderner Smartphones sind berührungsempfindliche Bildschirme.\n",
                 "Heute sind die meisten verkauften Mobiltelefone Smartphones.\n"
                 ]
    logger = CSVLogger()
    super_text = SuperText(sentences, logger)
    chord_input = ChordInputMethod(super_text)
    super_text.installEventFilter(chord_input)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
