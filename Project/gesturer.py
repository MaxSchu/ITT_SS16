#!/usr/bin/env python3
# coding: utf-8

import sys
import glob
from PyQt5 import QtGui, QtCore, QtWidgets
import wiimote
import scipy


class Gestures(QtWidgets.QMainWindow):
    defaultWiiMac = "B8:AE:6E:1B:AD:A0"
    startPos = None

    def __init__(self):
        super(self.__class__, self).__init__()
        self.c = 0
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
        self.wm.accelerometer.register_callback(self.transformPicture)
        self.wm.ir.register_callback(self.moveCursor)

    def moveCursor(self, irData):
        if self.wm.buttons["B"]:
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

    def transformPicture(self, accelData):
        x, y, z = accelData[0], accelData[1], accelData[2]
        offset = 512
        # rotate
        if self.wm.buttons["A"]:
            self.c += 1
            print(self.c)
            if self.c % 2 == 0:
                centeredZ = z - offset
                centeredX = x - offset
                rot_angle = int(-(scipy.degrees(scipy.arctan2(centeredZ, centeredX)) - 90))
                if rot_angle < 0:
                    rot_angle = 360 + rot_angle
                self.image.setPixmap(self.pixmap.transformed(
                    QtGui.QTransform().rotate(rot_angle), 1).scaledToHeight(400))

        # zoom
        if self.wm.buttons["Down"]:
            centeredZ = z - offset
            centeredY = y - offset

            tilt_angle = scipy.degrees(scipy.arctan2(centeredZ, centeredY)) - 90
            scale_val = abs(tilt_angle / 100)
            self.image.setPixmap(self.pixmap.transformed(QtGui.QTransform().scale(scale_val, scale_val)))

    def get_sector(self, rot_angle):
        if rot_angle >= 0 and rot_angle < 45:
            return 0
        elif rot_angle >= 45 and rot_angle < 90:
            return 45
        elif rot_angle >= 90 and rot_angle < 135:
            return 90
        elif rot_angle >= 135 and rot_angle < 180:
            return 135
        elif rot_angle >= 180 and rot_angle < 225:
            return 180
        elif rot_angle >= 225 and rot_angle < 270:
            return 225
        elif rot_angle >= 270 and rot_angle < 315:
            return 270
        elif rot_angle >= 315 and rot_angle < 360:
            return 315
        else:
            return -1


def main():
    app = QtWidgets.QApplication(sys.argv)
    gestures = Gestures()
    gestures.show()
    app.exec_()


if __name__ == '__main__':
    main()
