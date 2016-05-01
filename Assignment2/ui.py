import sys
from PyQt5 import QtGui, QtWidgets, QtCore
import threading
import time
import random


class Example(QtWidgets.QWidget):
    def __init__(self, maxRepetitions, timeBetweenSignals, order):
        super(Example, self).__init__()
        self.randInt = 0
        self.palette = QtGui.QPalette()
        self.position = (0, 0)
        self.showIntro = True
        self.maxCountdown = 2
        self.countdown = 0
        self.timeBetweenSignals = timeBetweenSignals
        self.order = order
        self.currentCondition = 0
        self.maxRepetitions = maxRepetitions
        self.repetition = 0
        self.keys = (QtCore.Qt.Key_B, QtCore.Qt.Key_V)
        self.keyMapping = {self.keys[0]: "B", self.keys[1]: "V"}

        # 0 -> attentive; 1 -> pre-attentive
        self.mode = 0

        # 0 -> without distractions; 1 -> with distractions
        self.backgroundMode = 1

        self.uiBlocked = False
        self.showRect = True
        self.counter = 0
        self.theThread = self.Distraction(self)
        self.theThread.start()
        self.timestampBuffer = 0
        self.correctKey = ""
        self.blockDrawCalls = False

        self.instructionsPreAttentive = """Everytime a SINGLE RECTANGLE appears press the V key.
Everytime TWO RECTANGLES appear press the B key.
Try to press the corresponding key as fast as possible!
Use the index-finger of your right hand only."""

        self.instructionsAttentive = """Everytime an EVEN NUMBER appears press the V key.
Everytime an ODD NUMBER appears press the B key.
Try to press the corresponding key as fast as possible!
Use the index-finger of your right hand only."""
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle('Paint')
        self.showIntroMessage()
        self.show()

    def showIntroMessage(self):
        if self.currentCondition > len(self.order) - 1:
            self.close()
            sys.exit(0)

        # pre-attentive (squares) without distractions
        if self.order[self.currentCondition] == 1:
            self.mode = 1
            self.backgroundMode = 0
            self.instructions = self.instructionsPreAttentive
        # pre-attentive (sqaures) with distractions
        elif self.order[self.currentCondition] == 2:
            self.mode = 1
            self.backgroundMode = 1
            self.instructions = self.instructionsPreAttentive
        # attentive (numbers) without distrations
        elif self.order[self.currentCondition] == 3:
            self.mode = 0
            self.backgroundMode = 0
            self.instructions = self.instructionsAttentive
        # attentive (numbers) with distrations
        elif self.order[self.currentCondition] == 4:
            self.mode = 0
            self.backgroundMode = 1
            self.instructions = self.instructionsAttentive

        self.uiBlocked = True
        self.showIntro = True
        self.countdown = self.maxCountdown
        self.repetition = self.maxRepetitions
        t = threading.Timer(1.0, self.lowerCountdown)
        t.start()

    def clearBackground(self):
        self.palette.setColor(QtGui.QPalette.Background, QtCore.Qt.white)
        self.setPalette(self.palette)

    def lowerCountdown(self):
        self.countdown -= 1
        if (self.countdown >= 0):
            # TODO: set time to given number
            t = threading.Timer(1.0, self.lowerCountdown)
            t.start()
            self.update()
        else:
            self.showIntro = False
            self.newSign()

    def changeCatPic(self):
        self.palette.setBrush(
            QtGui.QPalette.Background, QtGui.QBrush(QtGui.QImage("assets2/cat" + str(random.randint(1, 20)) + ".jpg")))
        self.setPalette(self.palette)

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.showIntro:
            self.drawIntro(qp)
        else:
            self.drawRectangle(qp)
        qp.end()

    def newSign(self):
        self.getNewRandomVars()
        self.uiBlocked = False
        self.showRect = True
        self.update()

    def getNewRandomVars(self):
        self.position = (random.randint(0, 900), random.randint(0, 700))
        if self.mode == 0:
            self.randInt = random.randint(1, 8)
            self.correctKey = list(
                (self.keyMapping).keys())[self.randInt % 2]
        else:
            self.randInt = random.randint(0, 1)
            if self.randInt == 0:
                self.correctKey = QtCore.Qt.Key_V
            else:
                self.correctKey = QtCore.Qt.Key_B

        # TODO: set requiredKeyPressed to
        # self.keyMapping[self.correctKey]
        print(self.keyMapping[self.correctKey])

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
        self.repetition -= 1

        if self.repetition > 0:
            self.t = threading.Timer(self.timeBetweenSignals, self.newSign)
            self.t.start()
        else:
            self.currentCondition += 1
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
                qp.setFont(QtGui.QFont('Decorative', 32))
                qp.drawText(
                    rect, QtCore.Qt.AlignCenter, str(self.randInt))
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

    def drawIntro(self, qp):
        qp.setFont(QtGui.QFont('Decorative', 18))
        qp.drawText(
            QtCore.QRect(100, 100, 800, 300), QtCore.Qt.AlignCenter, self.instructions)
        qp.setFont(QtGui.QFont('Decorative', 32))
        qp.drawText(
            QtCore.QRect(100, 300, 800, 300), QtCore.Qt.AlignCenter, str(self.countdown))

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
    app = QtWidgets.QApplication(sys.argv)
    ex = Example(10, 1, (1, 2, 3, 4))
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
