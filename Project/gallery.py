#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import os
import sys
import glob
import _thread
import time
import wiimote
import scipy
from PyQt5 import QtGui, QtCore, QtWidgets
from activity_recognition import GestureRecognizer


class Gallery(QtWidgets.QMainWindow):
    defaultWiiMac = "B8:AE:6E:1B:AD:A0"
    startPos = None
    signal = QtCore.pyqtSignal(int, bool)
    pixmapStack = []
    currentPixmapIndex = 0
    painted = False

    def __init__(self, width, height):
        super(self.__class__, self).__init__()
        self.drawingPixmap = None
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
        self.arrowWidth = 10
        self.arrowHeight = 20
        self.arrowY = self.imageHeight - ((self.heightPadding - self.arrowHeight)/2)
        self.currentIndex = 0
        self.imageOff = QtWidgets.QLabel(self)
        self.imageOff.setGeometry(0, 0, width, self.imageHeight)
        self.imageOff.setAlignment(QtCore.Qt.AlignCenter)
        self.image = QtWidgets.QLabel(self)
        self.image.setGeometry(0, 0, width, self.imageHeight)
        self.image.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnails = []
        self.maxCount = width / self.thumbnailWidth
        self.filenames = glob.glob('images/*.png')[:int(self.maxCount)]
        print(width, height, self.thumbnailWidth, self.thumbnailHeight,
              self.imageHeight, int(self.maxCount))
        self.count = 0
        for filename in self.filenames:
            if self.count == 0:
                pixmap = QtGui.QPixmap(filename)
                pixmap = pixmap.scaled(
                    self.imageWidth, self.imageHeight - self.heightPadding, QtCore.Qt.KeepAspectRatio)
                self.image.setPixmap(pixmap)
                self.pixmap = pixmap
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
        self.initArrow()
        self.signal.connect(self.animate)
        self.initWiimote(self.defaultWiiMac)
        gr = GestureRecognizer(self.gestureAction, self.wm)
        self.animateOut = QtCore.QPropertyAnimation(
            self.imageOff, str("geometry").encode("utf-8"), self)
        self.animateIn = QtCore.QPropertyAnimation(
            self.image, str("geometry").encode("utf-8"), self)
        self.animateArrow = QtCore.QPropertyAnimation(
            self.arrow, str("geometry").encode("utf-8"), self)
        self.animateOut.stateChanged.connect(self.animationFinished)
        self.animateIn.stateChanged.connect(self.animationFinished)
        self.animateArrow.stateChanged.connect(self.animationFinished)
        self.animationsRunning = 0
        self.pixmapStack.append(QtGui.QPixmap(self.image.pixmap()))
        self.currentPixmapIndex = 0

    def gestureAction(self, action):
        print(str(action))
        if self.animationsRunning == 0:
            if (str(action) == "right"):
                if self.currentIndex < self.count - 1:
                    self.savePixMap(self.drawingPixmap)
                    self.setThumbnailPixmap(self.thumbnails[self.currentIndex], self.drawingPixmap)
                    self.currentIndex += 1
                    pixmap = QtGui.QPixmap(self.filenames[self.currentIndex])
                    pixmap = pixmap.scaled(
                        self.imageWidth, self.imageHeight - self.heightPadding, QtCore.Qt.KeepAspectRatio)
                    self.imageOff.setPixmap(self.image.pixmap())
                    self.imageOff.setGeometry(0, 0, self.width, self.imageHeight)
                    self.image.setGeometry(
                        self.width, 0, self.width, self.imageHeight)
                    self.image.setPixmap(pixmap)
                    self.pixmap = pixmap
                    print('set pixmap')
                    self.signal.emit(-self.width, True)
                else:
                    print("Max index reached")
            elif(str(action) == "left"):
                if self.currentIndex > 0:
                    self.currentIndex -= 1
                    self.savePixMap(self.drawingPixmap)
                    self.setThumbnailPixmap(self.thumbnails[self.currentIndex], self.drawingPixmap)
                    pixmap = QtGui.QPixmap(self.filenames[self.currentIndex])
                    pixmap = pixmap.scaled(
                        self.imageWidth, self.imageHeight - self.heightPadding, QtCore.Qt.KeepAspectRatio)
                    self.imageOff.setPixmap(self.image.pixmap())
                    self.imageOff.setGeometry(0, 0, self.width, self.imageHeight)
                    self.image.setGeometry(-self.width, 0,
                                           self.width, self.imageHeight)
                    self.image.setPixmap(pixmap)
                    self.pixmap = pixmap
                    print('set pixmap')
                    self.signal.emit(self.width, False)
                else:
                    print("Minimum index reached")

    def animate(self, targetPos, directionRight):
        self.animationsRunning = 3
        self.animateOut.setDuration(1000)
        self.animateOut.setEndValue(QtCore.QRect(
            targetPos, 0, self.width, self.imageHeight))
        self.animateIn.setDuration(1000)
        self.animateIn.setEndValue(QtCore.QRect(
            0, 0, self.width, self.imageHeight))
        if directionRight:
            arrowPos = self.arrow.geometry().topLeft().x() + self.thumbnailWidth
        else:
            arrowPos = self.arrow.geometry().topLeft().x() - self.thumbnailWidth
        self.animateArrow.setEndValue(QtCore.QRect(
            arrowPos, self.arrowY, self.arrowWidth, self.arrowHeight))
        self.animateArrow.setDuration(1000)
        self.animateOut.start()
        self.animateIn.start()
        self.animateArrow.start()

    def initWiimote(self, wiimoteAddress):
        name = None
        print(("Connecting to %s (%s)" % (name, wiimoteAddress)))
        self.wm = wiimote.connect(wiimoteAddress, name)
        self.wm.ir.register_callback(self.moveCursor)
        self.wm.buttons.register_callback(self.buttonPressed)
        self.wm.accelerometer.register_callback(self.transformPicture)

    def buttonPressed(self, changedButtons):
        for button in changedButtons:
            if(button[0] == 'B'):
                if(button[1]):
                    print("B pressed")
                else:
                    print("B released")
                    if self.painted:
                        self.painted = False
                        self.pixmapStack.append(QtGui.QPixmap(self.image.pixmap()))
                        self.currentPixmapIndex += 1
            if(button[0] == 'Minus' and button[1] and len(self.pixmapStack) > 0 and self.currentPixmapIndex > 0):
                self.currentPixmapIndex -= 1
                print(self.currentPixmapIndex, self.pixmapStack)
                self.image.setPixmap(self.pixmapStack[self.currentPixmapIndex])
            if(button[0] == 'Plus' and button[1] and len(self.pixmapStack) > 0 and self.currentPixmapIndex < (len(self.pixmapStack)-1)):
                self.currentPixmapIndex += 1
                print(self.currentPixmapIndex, self.pixmapStack)
                self.image.setPixmap(self.pixmapStack[self.currentPixmapIndex])

    def initCursor(self):
        self.cursor = QtWidgets.QLabel(self)
        self.cursor.setAlignment(QtCore.Qt.AlignCenter)
        self.cursor.setGeometry(100, 50, 10, 10)
        self.cursor.setPixmap(QtGui.QPixmap(("cursor.png")).scaledToHeight(10))

    def initArrow(self):
        self.arrow = QtWidgets.QLabel(self)
        self.arrow.setAlignment(QtCore.Qt.AlignCenter)
        self.arrow.setGeometry(self.thumbnailWidth / 2 - self.arrowWidth / 2, self.arrowY, self.arrowWidth, self.arrowHeight)
        self.arrow.setPixmap(QtGui.QPixmap(("arrow.png")).scaledToHeight(20))

    def moveCursor(self, irData):
        if self.wm.buttons["A"]:
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
        self.drawingPixmap = self.image.pixmap()
        x -= (self.width - self.drawingPixmap.width())/2
        y -= (self.image.height() - self.drawingPixmap.height())/2
        pen = QtGui.QPen(QtGui.QColor("red"))
        pen.setWidth(1)
        painter = QtGui.QPainter()
        painter.begin(self.drawingPixmap)
        painter.setBrush(QtGui.QColor("red"))
        painter.setPen(pen)
        painter.drawEllipse(x, y, 10, 10)
        painter.end()
        self.image.setPixmap(self.drawingPixmap)

    def animationFinished(self, newState, oldState):
        if newState == QtCore.QAbstractAnimation.Stopped and oldState == QtCore.QAbstractAnimation.Running:
            self.animationsRunning -= 1
            if self.animationsRunning == 0:
                self.pixmapStack = []
                self.pixmapStack.append(QtGui.QPixmap(self.image.pixmap()))
                self.currentPixmapIndex = 0

    def transformPicture(self, accelData):
        # rotate
        if self.wm.buttons['Two']:
            x, y, z = accelData[0], accelData[1], accelData[2]
            offset = 512    
            centeredZ = z - offset
            centeredX = x - offset
            rot_angle = int(-(scipy.degrees(scipy.arctan2(centeredZ, centeredX)) - 90))
            if rot_angle < 0:
               rot_angle = 360 + rot_angle
            self.image.setPixmap(self.pixmap.transformed(QtGui.QTransform().rotate(rot_angle), 1))
        elif self.wm.buttons['Down']:
            self.zoomPicture(accelData)
    
    def zoomPicture(self, accelData):
        x, y, z = accelData[0], accelData[1], accelData[2]
        offset = 512  
        centeredZ = z - offset
        centeredY = y - offset

        tilt_angle = scipy.degrees(scipy.arctan2(centeredZ, centeredY)) - 90
        print('tilt_angle: '+str(tilt_angle))
        if tilt_angle <= -90:
            tilt_angle = 360 + tilt_angle 
        scale_val = (tilt_angle / 100) + 1
        if scale_val < 0:
            scale_val = - scale_val 
        print('tilt_angle: '+str(tilt_angle)+ ' scale_val: '+str(scale_val))
        self.image.setPixmap(self.pixmap.transformed(QtGui.QTransform().scale(scale_val, scale_val),1))   

    def get_sector(self, rot_angle):
        base = 45
        return int(base * round(float(rot_angle)/base))

    def setThumbnailPixmap(self, thumb, pixmap):
        if pixmap is not None:
            pixmap = pixmap.scaled(
                    self.thumbnailWidth, self.thumbnailHeight, QtCore.Qt.KeepAspectRatio)
            thumb.setPixmap(pixmap)
            self.drawingPixmap = None

    def savePixMap(self, pixmap):
        if pixmap is not None:
            pixmap.save(self.filenames[self.currentIndex], "png")
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    screen = QtWidgets.QDesktopWidget().availableGeometry()
    gallery = Gallery(screen.width(), screen.height())
    palette = gallery.palette()
    palette.setColor(gallery.backgroundRole(), QtCore.Qt.black)
    gallery.setPalette(palette)
    gallery.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
