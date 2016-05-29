#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5 import Qt, QtGui, QtCore, QtWidgets
import re


class TextLogger(QtWidgets.QTextEdit):
    def __init__(self):
        super(TextLogger, self).__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 400, 400)
        self.setWindowTitle('TextLogger')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.show()

    def keyPressEvent(self, ev):
        super(TextLogger, self).keyPressEvent(ev)
        # print("Pressed: " + ev.text())

    def keyReleaseEvent(self, ev):
        super(TextLogger, self).keyReleaseEvent(ev)
        # print("Released: " + ev.text())


class ChordInputMethod(QtCore.QObject):
    VALID_LETTERS = "[a-zäöüß ]"

    def __init__(self):
        super(ChordInputMethod, self).__init__()
        self.keys = []
        self.chordCode = []
        self.chordSwitcher = False
        self.counter = 0
        self.chords = self.readChords()

    def readChords(self):
        # read the possible chords from a file
        chords = {}
        frozenchord = {}
        chord = ""
        words = ""

        file = open("chords.txt", "r")
        temp = file.read().splitlines()

        for line in temp:
            try:
                # read chord combination
                chord = (line.split(":"))[0]
                # create frozenset to use as key in dictionary
                frozenchord = frozenset(list(chord))

                if len(chord) == 1:
                    print("Hint - Chord should be at least two characters long: " + chord)

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
                    watched_textedit, len(self.keys))
                result = self.getWord()
                Qt.qApp.postEvent(watched_textedit, QtGui.QKeyEvent(
                    Qt.QKeyEvent.KeyPress, 0, QtCore.Qt.NoModifier, text=result))

                if (ev.text() != " "):
                    self.resetChordCounter()
                else:
                    # if only space is released, the user wants to switch to aternative maybe
                    self.chordCode = self.keys
                    self.keys.remove(" ")
                    self.chordSwitcher = True
                    return False
            if ev.text() in self.keys:
                # remove released buttons from set
                self.keys.remove(ev.text())
            return True
        else:
            print("Should'nt arrive here: " + str(ev))
            return False


def main():
    app = QtWidgets.QApplication(sys.argv)
    text_logger = TextLogger()
    chord_input = ChordInputMethod()
    text_logger.installEventFilter(chord_input)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
