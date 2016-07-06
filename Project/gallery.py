#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import os, sys, glob
from PyQt5 import QtGui, QtCore, QtWidgets
from activity_recognition import GestureRecognizer


class Gallery(QtWidgets.QMainWindow):
    
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setGeometry(0, 0, 600, 600)
        filenames = glob.glob('*.png')
        self.currentIndex = 0
        self.image = QtWidgets.QLabel(self)
        self.image.setAlignment(QtCore.Qt.AlignCenter)
        self.image.setGeometry(100, 50, 400, 400)
        self.thumbnails = []
        self.count = 0
        for filename in filenames[:6]:
            if self.count == 0:
                self.image.setPixmap(QtGui.QPixmap((filename)).scaledToHeight(400))
            self.thumbnails.append(QtWidgets.QLabel(self))
            self.thumbnails[self.count].setAlignment(QtCore.Qt.AlignCenter)
            self.thumbnails[self.count].setGeometry(self.count*100, 500, 100, 100)
            #use full ABSOLUTE path to the image, not relative
            self.thumbnails[self.count].setPixmap(QtGui.QPixmap((filename)).scaledToHeight(100))
            self.count += 1
        

        defaultWiiMac = "B8:AE:6E:1B:AD:A0"
        gr = GestureRecognizer(self.gestureAction)
        gr.initWiimote(defaultWiiMac)

    def gestureAction(self, action):
        if (str(action) == "swipeleft"):
            if self.currentIndex < self.count - 1:
                self.currentIndex += 1
                self.image.setPixmap(self.thumbnails[self.currentIndex].pixmap().scaledToHeight(400))
            else:
                print("Max index reached")
        elif(str(action) == "swiperight"):
            if self.currentIndex > 0:
                self.currentIndex -= 1
                self.image.setPixmap(self.thumbnails[self.currentIndex].pixmap().scaledToHeight(400))
            else:
                print("Minimum index reached")

app = QtWidgets.QApplication(sys.argv)
gallery = Gallery()
gallery.show()
sys.exit(app.exec_())
