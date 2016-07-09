#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import os, sys, glob, _thread, time
from PyQt5 import QtGui, QtCore, QtWidgets
from activity_recognition import GestureRecognizer


class Gallery(QtWidgets.QMainWindow):
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
        print(width, height, self.thumbnailWidth, self.thumbnailHeight, self.imageHeight, int(self.maxCount))
        self.count = 0
        for filename in self.filenames:
            if self.count == 0:
                pixmap = QtGui.QPixmap(filename)
                pixmap = pixmap.scaled(self.imageWidth, self.imageHeight-self.heightPadding, QtCore.Qt.KeepAspectRatio)
                self.image.setPixmap(pixmap)
            self.thumbnails.append(QtWidgets.QLabel(self))
            self.thumbnails[self.count].setAlignment(QtCore.Qt.AlignCenter)
            self.thumbnails[self.count].setGeometry(self.count*self.thumbnailWidth, self.imageHeight, self.thumbnailWidth, self.thumbnailHeight)
            #use full ABSOLUTE path to the image, not relative
            pixmap = QtGui.QPixmap(filename)
            pixmap = pixmap.scaled(self.thumbnailWidth, self.thumbnailHeight, QtCore.Qt.KeepAspectRatio)
            self.thumbnails[self.count].setPixmap(pixmap)
            self.count += 1
        

        defaultWiiMac = "B8:AE:6E:18:3A:ED"
        self.signal.connect(self.animate)
        gr = GestureRecognizer(self.gestureAction)
        gr.initWiimote(defaultWiiMac)

    def gestureAction(self, action):
        print(str(action))
        if (str(action) == "right"):
            if self.currentIndex < self.count - 1:
                self.currentIndex += 1
                pixmap = QtGui.QPixmap(self.filenames[self.currentIndex])
                pixmap = pixmap.scaled(self.imageWidth, self.imageHeight-self.heightPadding, QtCore.Qt.KeepAspectRatio)
                self.imageOff.setPixmap(self.image.pixmap())
                self.imageOff.setGeometry(0, 0, self.width, self.imageHeight)
                self.image.setGeometry(self.width, 0, self.width, self.imageHeight)
                self.image.setPixmap(pixmap)
                self.signal.emit(-self.width)
            else:
                print("Max index reached")
        elif(str(action) == "left"):
            if self.currentIndex > 0:
                self.currentIndex -= 1
                pixmap = QtGui.QPixmap(self.filenames[self.currentIndex])
                pixmap = pixmap.scaled(self.imageWidth, self.imageHeight-self.heightPadding, QtCore.Qt.KeepAspectRatio)
                self.imageOff.setPixmap(self.image.pixmap())
                self.imageOff.setGeometry(0, 0, self.width, self.imageHeight)
                self.image.setGeometry(-self.width, 0, self.width, self.imageHeight)
                self.image.setPixmap(pixmap)
                self.signal.emit(self.width)
            else:
                print("Minimum index reached")

    def animate(self, targetPos):
        self.animateOut = QtCore.QPropertyAnimation(self.imageOff, str("geometry").encode("utf-8"), self)
        self.animateOut.setDuration(1000)
        self.animateOut.setEndValue(QtCore.QRect(targetPos, 0, self.width, self.imageHeight))
        self.animateIn = QtCore.QPropertyAnimation(self.image, str("geometry").encode("utf-8"), self)
        self.animateIn.setDuration(1000)
        self.animateIn.setEndValue(QtCore.QRect(0, 0, self.width, self.imageHeight))
        self.animateOut.start()
        self.animateIn.start()

app = QtWidgets.QApplication(sys.argv)
screen = QtWidgets.QDesktopWidget().availableGeometry()
gallery = Gallery(screen.width(), screen.height())
gallery.show()
sys.exit(app.exec_())
