#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import os, sys, glob
from PyQt5 import QtGui, QtCore, QtWidgets
from activity_recognition import GestureRecognizer


class Gallery(QtWidgets.QMainWindow):
    
    def __init__(self, width, height):
        super(self.__class__, self).__init__()
        # fix for hidden lower bar
        height -= 30
        self.setGeometry(0, 0, width, height)
        self.thumbnailHeight = height / 6
        self.thumbnailWidth = self.thumbnailHeight
        self.heightPadding = height / 6
        self.imageHeight = height / 6 * 5
        self.imageWidth = width / 10 * 9
        self.currentIndex = 0
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
        

        defaultWiiMac = "B8:AE:6E:1B:AD:A0"
        gr = GestureRecognizer(self.gestureAction)
        gr.initWiimote(defaultWiiMac)

    def gestureAction(self, action):
        if (str(action) == "swipeleft"):
            if self.currentIndex < self.count - 1:
                self.currentIndex += 1
                pixmap = QtGui.QPixmap(self.filenames[self.currentIndex])
                pixmap = pixmap.scaled(self.imageWidth, self.imageHeight-self.heightPadding, QtCore.Qt.KeepAspectRatio)
                self.image.setPixmap(pixmap)
            else:
                print("Max index reached")
        elif(str(action) == "swiperight"):
            if self.currentIndex > 0:
                self.currentIndex -= 1
                pixmap = QtGui.QPixmap(self.filenames[self.currentIndex])
                pixmap = pixmap.scaled(self.imageWidth, self.imageHeight-self.heightPadding, QtCore.Qt.KeepAspectRatio)
                self.image.setPixmap(pixmap)
            else:
                print("Minimum index reached")

app = QtWidgets.QApplication(sys.argv)
screen = QtWidgets.QDesktopWidget().availableGeometry()
gallery = Gallery(screen.width(), screen.height())
gallery.show()
sys.exit(app.exec_())
