#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import glob
from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import wiimote


class Painter(QtWidgets.QMainWindow):
    defaultWiiMac = "B8:AE:6E:1B:AD:A0"
    startPos = None

    def __init__(self):
        super(self.__class__, self).__init__()
        self.initUI()
        self.initWiimote(self.defaultWiiMac)

    def initUI(self):
        self.setGeometry(0, 0, 600, 600)
        i = 0
        filenames = glob.glob('*.png')
        for filename in filenames[:6]:
            if i == 0:
                image = QtWidgets.QLabel(self)
                image.setAlignment(QtCore.Qt.AlignCenter)
                image.setGeometry(100, 50, 400, 400)
                image.setPixmap(QtGui.QPixmap((filename)).scaledToHeight(400))
            thumbnail = QtWidgets.QLabel(self)
            thumbnail.setAlignment(QtCore.Qt.AlignCenter)
            thumbnail.setGeometry(i * 100, 500, 100, 100)
            # use full ABSOLUTE path to the image, not relative
            thumbnail.setPixmap(QtGui.QPixmap((filename)).scaledToHeight(100))
            i += 1
        self.cursor = QtWidgets.QLabel(self)
        self.cursor.setAlignment(QtCore.Qt.AlignCenter)
        self.cursor.setGeometry(100, 50, 10, 10)
        self.cursor.setPixmap(QtGui.QPixmap(("cursor.png")).scaledToHeight(10))

    def initWiimote(self, wiimoteAddress):
        name = None
        print(("Connecting to %s (%s)" % (name, wiimoteAddress)))
        self.wm = wiimote.connect(wiimoteAddress, name)
        self.wm.ir.register_callback(self.moveCursor)

    def moveCursor(self, irData):
        if len(irData) == 0:
            self.startPos = None
        if self.startPos is None and len(irData) != 0:
            print("Lol")
            self.startPos = [irData[0]["x"], irData[0]["y"]]
        else:
            if(self.startPos is not None):
                difx = self.startPos[0] - irData[0]["x"]
                dify = self.startPos[1] - irData[0]["y"]
                coordx = self.cursor.x() + difx
                coordy = self.cursor.y() - dify
                if coordx < 600 and coordy < 600 and coordx > 0 and coordy > 0:
                    self.cursor.move(coordx, coordy)
                self.startPos = [irData[0]["x"], irData[0]["y"]]
                print("difx: " + str(difx) + ", difY: " + str(dify))
                difx = 0
                dify = 0


def main():
    app = QtWidgets.QApplication(sys.argv)
    painter = Painter()
    painter.show()
    app.exec_()


if __name__ == '__main__':
    main()
