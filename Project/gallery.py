#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import os
import sys
import glob
import _thread
import time
import wiimote
from PyQt5 import QtGui, QtCore, QtWidgets
from activity_recognition import GestureRecognizer


class Gallery(QtWidgets.QMainWindow):
    defaultWiiMac = "B8:AE:6E:50:05:32"
    startPos = None
    signal = QtCore.pyqtSignal(int)

    def __init__(self, width, height):
        super(self.__class__, self).__init__()
        # fix for hidden lower bar
        height -= 30
        self.width = width
        self.height = height
        self.setGeometry(0, 0, width, height)
        self.thumbnailHeight = height / 6
        self.thumbnailWidth = self.thumbnailHeight
        self.heightPadding = height / 6
        self.imageHeight = height / 6 * 5
        self.imageWidth = width / 10 * 9
        self.currentIndex = 0
        self.imageOff = QtWidgets.QLabel(self)
        self.imageOff.setGeometry(0, 0, width, self.imageHeight)
        self.imageOff.setAlignment(QtCore.Qt.AlignCenter)
        self.image = QtWidgets.QLabel(self)
        self.image.setGeometry(0, 0, width, self.imageHeight)
        self.image.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnails = []
        self.maxCount = width / self.thumbnailWidth
        self.filenames = glob.glob('*.png')[:int(self.maxCount)]
        print(width, height, self.thumbnailWidth, self.thumbnailHeight,
              self.imageHeight, int(self.maxCount))
        self.count = 0
        for filename in self.filenames:
            if self.count == 0:
                pixmap = QtGui.QPixmap(filename)
                pixmap = pixmap.scaled(
                    self.imageWidth, self.imageHeight - self.heightPadding, QtCore.Qt.KeepAspectRatio)
                self.image.setPixmap(pixmap)
            self.thumbnails.append(QtWidgets.QLabel(self))
            self.thumbnails[self.count].setAlignment(QtCore.Qt.AlignCenter)
            self.thumbnails[self.count].setGeometry(
                self.count * self.thumbnailWidth, self.imageHeight, self.thumbnailWidth, self.thumbnailHeight)
            # use full ABSOLUTE path to the image, not relative
            pixmap = QtGui.QPixmap(filename)
            pixmap = pixmap.scaled(
                self.thumbnailWidth, self.thumbnailHeight, QtCore.Qt.KeepAspectRatio)
            self.thumbnails[self.count].setPixmap(pixmap)
            self.count += 1

        self.initCursor()
        self.signal.connect(self.animate)
        self.initWiimote(self.defaultWiiMac)
        gr = GestureRecognizer(self.gestureAction, self.wm)

    def gestureAction(self, action):
        print(str(action))
        if (str(action) == "right"):
            if self.currentIndex < self.count - 1:
                self.currentIndex += 1
                pixmap = QtGui.QPixmap(self.filenames[self.currentIndex])
                pixmap = pixmap.scaled(
                    self.imageWidth, self.imageHeight - self.heightPadding, QtCore.Qt.KeepAspectRatio)
                self.imageOff.setPixmap(self.image.pixmap())
                self.imageOff.setGeometry(0, 0, self.width, self.imageHeight)
                self.image.setGeometry(
                    self.width, 0, self.width, self.imageHeight)
                self.image.setPixmap(pixmap)
                self.signal.emit(-self.width)
            else:
                print("Max index reached")
        elif(str(action) == "left"):
            if self.currentIndex > 0:
                self.currentIndex -= 1
                pixmap = QtGui.QPixmap(self.filenames[self.currentIndex])
                pixmap = pixmap.scaled(
                    self.imageWidth, self.imageHeight - self.heightPadding, QtCore.Qt.KeepAspectRatio)
                self.imageOff.setPixmap(self.image.pixmap())
                self.imageOff.setGeometry(0, 0, self.width, self.imageHeight)
                self.image.setGeometry(-self.width, 0,
                                       self.width, self.imageHeight)
                self.image.setPixmap(pixmap)
                self.signal.emit(self.width)
            else:
                print("Minimum index reached")

    def animate(self, targetPos):
        self.animateOut = QtCore.QPropertyAnimation(
            self.imageOff, str("geometry").encode("utf-8"), self)
        self.animateOut.setDuration(1000)
        self.animateOut.setEndValue(QtCore.QRect(
            targetPos, 0, self.width, self.imageHeight))
        self.animateIn = QtCore.QPropertyAnimation(
            self.image, str("geometry").encode("utf-8"), self)
        self.animateIn.setDuration(1000)
        self.animateIn.setEndValue(QtCore.QRect(
            0, 0, self.width, self.imageHeight))
        self.animateOut.start()
        self.animateIn.start()

    def initWiimote(self, wiimoteAddress):
        name = None
        print(("Connecting to %s (%s)" % (name, wiimoteAddress)))
        self.wm = wiimote.connect(wiimoteAddress, name)
        self.wm.ir.register_callback(self.moveCursor)

    def initCursor(self):
        self.cursor = QtWidgets.QLabel(self)
        self.cursor.setAlignment(QtCore.Qt.AlignCenter)
        self.cursor.setGeometry(100, 50, 10, 10)
        self.cursor.setPixmap(QtGui.QPixmap(("cursor.png")).scaledToHeight(10))

    def moveCursor(self, irData):
        if len(irData) == 0:
            self.startPos = None
        if self.startPos is None and len(irData) != 0:
            self.startPos = [irData[0]["x"], irData[0]["y"]]
        else:
            if(self.startPos is not None):
                difx = self.startPos[0] - irData[0]["x"]
                dify = self.startPos[1] - irData[0]["y"]
                coordx = self.cursor.x() + difx
                coordy = self.cursor.y() - dify
                if coordx < self.width and coordy < self.height and coordx > 0 and coordy > 0:
                    self.cursor.move(coordx, coordy)
                    if self.wm.buttons["B"]:
                        self.paint(coordx, coordy)
                self.startPos = [irData[0]["x"], irData[0]["y"]]
                difx = 0
                dify = 0

    def paint(self, x, y):
        pixmap = self.image.pixmap()
        x -= pixmap.width()
        y -= pixmap.height()
        print("paint, x: " + str(x) + " , y: " + str(y))
        pen = QtGui.QPen(QtGui.QColor("red"))
        pen.setWidth(1)
        painter = QtGui.QPainter()
        painter.begin(pixmap)
        painter.setBrush(QtGui.QColor("red"))
        painter.setPen(pen)
        painter.drawEllipse(x, y, 10, 10)
        painter.end()
        self.image.setPixmap(pixmap)


def main():
    app = QtWidgets.QApplication(sys.argv)
    screen = QtWidgets.QDesktopWidget().availableGeometry()
    gallery = Gallery(screen.width(), screen.height())
    gallery.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
