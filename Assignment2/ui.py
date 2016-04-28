import sys
from PyQt5 import QtGui, QtWidgets, QtCore
from threading import Timer
import random


class Example(QtWidgets.QWidget):

    def __init__(self):
        super(Example, self).__init__()
        self.position = (0, 0)
        self.sign = ("X", "O")
        self.timerBlocked = False
        self.showRect = True
        self.counter = 0
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle('Paint')
        self.show()
        self.newSign()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawRectangle(qp)
        qp.end()

    def newSign(self):
        self.timerBlocked = False
        self.position = (random.randint(0, 900), random.randint(0, 700))
        self.showRect = True
        self.update()

    def keyPressEvent(self, ev):
        if self.timerBlocked:
            return

        if ev.key() == QtCore.Qt.Key_Space:
            self.timerBlocked = True
            t = Timer(1.0, self.newSign)
            t.start()
            self.counter += 1
            self.showRect = False
            self.update()

    def drawRectangle(self, qp):
        if not self.showRect:
            return

        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.drawRect(self.position[0], self.position[1], 100, 100)
        rect = QtCore.QRect(self.position[0], self.position[1], 100, 100)
        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 32))
        qp.drawText(
            rect, QtCore.Qt.AlignCenter, self.sign[random.randint(0, 1)])

    def buttn(self):
        self.draw = True
        self.update()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
