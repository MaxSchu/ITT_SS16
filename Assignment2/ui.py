import sys
from PyQt5 import QtGui, QtWidgets, QtCore
from threading import Timer
import time
import random


class Example(QtWidgets.QWidget):

    def __init__(self):
        super(Example, self).__init__()
        self.position = (0, 0)
        self.showIntro = False
        self.maxCountdown = 3
        self.countdown = 0
        self.maxRepetitions = 10
        self.repetitions = 0
        self.keys = (QtCore.Qt.Key_V, QtCore.Qt.Key_B)
        self.keyMapping = {self.keys[0]: "V", self.keys[1]: "B"}
        self.mode = 0
        self.backgroundMode = 0
        self.uiBlocked = False
        self.showRect = True
        self.counter = 0
        self.timestampBuffer = 0
        self.correctKey = ""
        self.initUI()
        self.instructions = "Anleitung"

    def initUI(self):
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle('Paint')
        palette = QtGui.QPalette()
        palette.setBrush(
            QtGui.QPalette.Background, QtGui.QBrush(QtGui.QPixmap("test.jpg")))
        self.setPalette(palette)
        self.show()
        self.showIntroMessage()

    def showIntroMessage(self):
        self.uiBlocked = True
        self.countdown = self.maxCountdown
        self.repetitions = self.maxRepetitions
        t = Timer(1.0, self.lowerCountdown)
        t.start()
        self.showIntro = True

    def lowerCountdown(self):
        self.countdown -= 1
        if (self.countdown >= 0):
            t = Timer(1.0, self.lowerCountdown)
            t.start()
        else:
            self.showIntro = False
            self.newSign()
        self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 32))
        if self.showIntro:
            self.drawIntro(qp)
        else:
            self.drawRectangle(qp)
        qp.end()

    def newSign(self):
        self.uiBlocked = False
        self.position = (random.randint(0, 900), random.randint(0, 700))
        self.showRect = True
        self.update()

    def keyPressEvent(self, ev):
        if self.uiBlocked:
            return

        try:
            pressedKey = chr(ev.key())
        except ValueError:
            pressedKey = "KeyCode: " + str(ev.key())

        print("Key pressed: " + pressedKey)

        # TODO: save current Timestamp
        # TODO: save reactionTime
        reactionTime = time.time() - self.timestampBuffer
        print ("reactionTime: " + str(reactionTime))

        if self.correctKey == ev.key():
            # TODO: set correctKeyPressed to true
            print("Correct!")
        else:
            # TODO: set correctKeyPressed to false
            print("Wrong!")

        self.uiBlocked = True
        self.repetitions -= 1

        if self.repetitions > 0:
            t = Timer(1.0, self.newSign)
            t.start()
        else:
            self.showIntroMessage()
        self.showRect = False
        self.update()

    def drawRectangle(self, qp):
        if self.showRect:
            qp.setBrush(QtGui.QColor(255, 255, 255))
            qp.drawRect(self.position[0], self.position[1], 100, 100)
            rect = QtCore.QRect(self.position[0], self.position[1], 100, 100)
            self.timestampBuffer = time.time()

            if self.mode == 0:
                randomInt = random.randint(1, 8)
                qp.drawText(
                    rect, QtCore.Qt.AlignCenter, str(randomInt))
                self.correctKey = list((self.keyMapping).keys())[randomInt % 2]

                # TODO: set requiredKeyPressed to
                # self.keyMapping[self.correctKey]
                print(self.keyMapping[self.correctKey])
            else:
                qp.setBrush(QtGui.QColor(0, 0, 255))
                if random.randint(0, 1) == 0:
                    qp.drawRect(
                        self.position[0] + 5, self.position[1] + 30, 40, 40)
                    qp.drawRect(
                        self.position[0] + 55, self.position[1] + 30, 40, 40)
                else:
                    qp.drawRect(
                        self.position[0] + 30, self.position[1] + 30, 40, 40)

    def drawIntro(self, qp):
        qp.drawText(
            QtCore.QRect(100, 100, 800, 300), QtCore.Qt.AlignCenter, self.instructions)
        qp.drawText(
            QtCore.QRect(100, 200, 800, 300), QtCore.Qt.AlignCenter, str(self.countdown))


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
