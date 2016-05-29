#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5 import Qt, QtGui, QtCore, QtWidgets
import re


class TextLogger(QtWidgets.QTextEdit):

    def __init__(self, example_text=""):
        super(TextLogger, self).__init__()
        self.setText(example_text)
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 400, 400)
        self.setWindowTitle('TextLogger')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        # self.setMouseTracking(True)
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
        chords = {}
        chord = ""
        words = ""

        file = open("chords.txt", "r")
        temp = file.read().splitlines()

        for line in temp:
            chord = (line.split(":"))[0]
            words = ((line.split(":"))[1]).split(",")
            chords.update({frozenset(list(chord)): words})

        file.close()
        return chords

    def getWord(self):
        uppercase = False
        compareSet = []

        try:
            for s in self.keys:
                if s.isupper():
                    uppercase = True
                compareSet.append(s.lower())

            if " " in compareSet:
                compareSet.remove(" ")
            if len(self.chords[frozenset(compareSet)]) <= self.counter:
                self.counter = 0

            if (uppercase):
                return ((self.chords[frozenset(compareSet)]))[self.counter].title()
            else:
                return ((self.chords[frozenset(compareSet)]))[self.counter]
        except KeyError:
            self.counter = 0
            self.chordSwitcher = False
            return "".join(self.keys)

    def removePastLetter(self, watched_textedit, count):
        for x in range(0, count):
            Qt.qApp.postEvent(watched_textedit, QtGui.QKeyEvent(
                Qt.QKeyEvent.KeyPress, QtCore.Qt.Key_Backspace, QtCore.Qt.NoModifier))

    def eventFilter(self, watched_textedit, ev):
        if not ev.spontaneous():
            return False  # ignore events that we injected ourselves
        if not ev.type() in [Qt.QKeyEvent.KeyPress, Qt.QKeyEvent.KeyRelease]:
            return False  # ignore everything else
        if re.match(ChordInputMethod.VALID_LETTERS, ev.text().lower()) is None:
            return False  # only check this _after_ we are sure that we have a QKeyEvent!
        # TODO: allow autorepeat when only a single key is pressed at the
        # moment
        if ev.isAutoRepeat():  # completely eliminate these, as they might interfere with chords!
            return True
        # finally, we only have interesting key presses/releases left
        if ev.type() == Qt.QKeyEvent.KeyPress:  # collect keys
            self.keys.append(ev.text())

            if self.chordSwitcher:
                print(self.chordCode)
                if ev.text() == " " and self.keys == self.chordCode:
                    print(len(self.getWord()))
                    self.removePastLetter(
                        watched_textedit, len(self.getWord()))
                    self.counter += 1
                    Qt.qApp.postEvent(watched_textedit, QtGui.QKeyEvent(
                        Qt.QKeyEvent.KeyPress, 0, QtCore.Qt.NoModifier, text=self.getWord()))
                    return True
            else:
                self.chordCode = []
                self.chordSwitcher = False

            return False  # always filter press events
        elif ev.type() == Qt.QKeyEvent.KeyRelease:  # release chord once one of the keys is released
            if " " not in self.keys:
                self.keys = []
                self.chordCode = []
                self.chordSwitcher = False
                self.counter = 0
                return False
            if len(self.keys) > 2 and not self.chordSwitcher:
                self.removePastLetter(
                    watched_textedit, len(self.keys))
                result = self.getWord()
                Qt.qApp.postEvent(watched_textedit, QtGui.QKeyEvent(
                    Qt.QKeyEvent.KeyPress, 0, QtCore.Qt.NoModifier, text=result))

                if (ev.text() != " "):
                    self.counter = 0
                    self.chordCode = []
                    self.chordSwitcher = False
                    self.keys = []
                else:
                    self.chordCode = self.keys
                    self.keys.remove(" ")
                    self.chordSwitcher = True
                    return False
            if ev.text() in self.keys:
                self.keys.remove(ev.text())
            return True  # also when non-printables are released (sensible?)
        else:
            print("Should'nt arrive here: " + str(ev))
            return False


def main():
    app = QtWidgets.QApplication(sys.argv)
    text_logger = TextLogger("Es war einmal ein Mann.")
    chord_input = ChordInputMethod()
    text_logger.installEventFilter(chord_input)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
