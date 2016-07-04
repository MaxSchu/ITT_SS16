#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import glob
from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import wiimote
import scipy
import time


class Gestures(QtWidgets.QMainWindow):
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
                self.pixmap = QtGui.QPixmap((filename))
                self.image = QtWidgets.QLabel(self)
                self.image.setAlignment(QtCore.Qt.AlignCenter)
                self.image.setGeometry(100, 50, 400, 400)
                self.image.setPixmap(self.pixmap.scaledToHeight(400))
                #self.image.setPixmap(QtGui.QPixmap((filename)).transformed(QtGui.QTransform().rotate(90)))
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
        #self.wm.ir.register_callback(self.moveCursor)
        self.wm.accelerometer.register_callback(self.rotatePicture)
        
    def curImg(self):
        i = 0
        image = ""
        filenames = glob.glob('*.png')
        for filename in filenames[:6]:
            if i == 0:
                image = filename
                i += 1
        return image
    
    def rotatePicture(self, accelData):
        if self.wm.buttons["A"]:
            x, y, z = accelData[0], accelData[1], accelData[2]
            angle = ((x - 482) * 2.9)-90
            print('x: '+str(x)+' angle: '+str(angle))
            self.image.setPixmap(self.pixmap.transformed(QtGui.QTransform().rotate(angle)).scaledToHeight(400))
            time.sleep(0.5)

    def toArray(self, source):
        return []

    '''while True:
        if self.wm.buttons["A"]:
            self.wm.leds[1] = True
            self.wm.rumble(0.1)
        else:
            self.wm.leds[1] = False
            pass
        time.sleep(0.05)'''


def main():
    app = QtWidgets.QApplication(sys.argv)
    gestures = Gestures()
    gestures.show()
    app.exec_()


if __name__ == '__main__':
    main()
