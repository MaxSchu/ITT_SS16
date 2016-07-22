#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
import glob
import wiimote
import scipy
from PyQt5 import QtGui, QtCore, QtWidgets
from activity_recognition import GestureRecognizer


class Gallery(QtWidgets.QMainWindow):
    """
    This Class manages the ui including all animations.

    Recognition of swipe gestures are handled by
    the GestureRecognizer in activity_recognition.py
    """

    defaultWiiMac = "B8:AE:6E:1B:AD:A0"
    startPos = None
    signal = QtCore.pyqtSignal(int, bool)
    pixmapStack = []
    currentPixmapIndex = 0
    painted = False

    def __init__(self, width, height):
        super(self.__class__, self).__init__()

        self.initUI(width, height)
        self.initPen("red")
        self.drawingPixmap = None
        self.count = 0
        self.curAngle = 0
        self.currentIndex = 0
        self.signal.connect(self.animate)
        self.initWiimote(self.defaultWiiMac)
        gr = GestureRecognizer(self.gestureAction, self.wm)

        self.pixmapStack.append(QtGui.QPixmap(self.image.pixmap()))
        self.currentPixmapIndex = 0

    def initUI(self, width, height):
        self.initGeometryVars(width, height)
        self.initImageContainers()
        self.getImageFiles()
        self.setPixmaps()
        self.initCursor()
        self.initArrow()
        self.initAnimations()

    def initGeometryVars(self, width, height):
        self.width = width
        # fix for hidden lower bar
        self.height = height - 30
        self.setGeometry(0, 0, width, height)
        self.thumbnailHeight = height / 6
        self.thumbnailWidth = self.thumbnailHeight
        self.heightPadding = height / 12
        self.imageHeight = height / 6 * 5
        self.imageWidth = width / 10 * 9
        self.arrowWidth = 10
        self.arrowHeight = 20
        self.arrowY = self.imageHeight - ((self.heightPadding - self.arrowHeight) / 2)
        self.maxImageCount = width / self.thumbnailWidth
        self.thumbnailPadding = self.thumbnailWidth / self.maxImageCount

    def initImageContainers(self):
        self.imageOff = QtWidgets.QLabel(self)
        self.imageOff.setGeometry(0, 0, self.width, self.imageHeight)
        self.imageOff.setAlignment(QtCore.Qt.AlignCenter)
        self.image = QtWidgets.QLabel(self)
        self.image.setGeometry(0, 0, self.width, self.imageHeight)
        self.image.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnails = []

    def getImageFiles(self):
        # Gets all .png, .jpg, .jpeg and .bmp images from the /images folder
        # Limited to the maxImageCount which is determined by the screen width
        # the images are sorted alphabetically by their name
        self.filenames = []
        self.filenames.extend(glob.glob('images/*.png'))
        self.filenames.extend(glob.glob('images/*.jpg'))
        self.filenames.extend(glob.glob('images/*.jpeg'))
        self.filenames.extend(glob.glob('images/*.bmp'))
        self.filenames = sorted(self.filenames)[:int(self.maxImageCount)]
        print(self.filenames)

    def setPixmaps(self):
        self.imageCount = 0
        for filename in self.filenames:
            if self.imageCount == 0:
                # main image container
                pixmap = QtGui.QPixmap(filename)
                pixmap = pixmap.scaled(
                    self.imageWidth, self.imageHeight - self.heightPadding, QtCore.Qt.KeepAspectRatio)
                self.image.setPixmap(pixmap)
                self.pixmap = pixmap
                # thumbnails
            self.thumbnails.append(QtWidgets.QLabel(self))
            self.thumbnails[self.imageCount].setAlignment(QtCore.Qt.AlignCenter)
            self.thumbnails[self.imageCount].setGeometry(
                self.imageCount * self.thumbnailWidth, self.imageHeight, self.thumbnailWidth, self.thumbnailHeight)
            pixmap = QtGui.QPixmap(filename)
            pixmap = pixmap.scaled(
                self.thumbnailWidth - self.thumbnailPadding,
                self.thumbnailHeight - self.thumbnailPadding, QtCore.Qt.KeepAspectRatio)
            self.thumbnails[self.imageCount].setPixmap(pixmap)
            self.imageCount += 1

    def initAnimations(self):
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

    def gestureAction(self, direction):
        if self.animationsRunning == 0:
            if (int(direction) == -1):
                # swipe left
                if self.currentIndex < self.imageCount - 1:
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
                    self.signal.emit(-self.width, True)
                else:
                    print("Max index reached")
            elif(int(direction) == 1):
                # swipe right
                if self.currentIndex > 0:
                    self.savePixMap(self.drawingPixmap)
                    self.setThumbnailPixmap(self.thumbnails[self.currentIndex], self.drawingPixmap)
                    self.currentIndex -= 1
                    pixmap = QtGui.QPixmap(self.filenames[self.currentIndex])
                    pixmap = pixmap.scaled(
                        self.imageWidth, self.imageHeight - self.heightPadding, QtCore.Qt.KeepAspectRatio)
                    self.imageOff.setPixmap(self.image.pixmap())
                    self.imageOff.setGeometry(0, 0, self.width, self.imageHeight)
                    self.image.setGeometry(-self.width, 0,
                                           self.width, self.imageHeight)
                    self.image.setPixmap(pixmap)
                    self.pixmap = pixmap
                    self.signal.emit(self.width, False)
                else:
                    print("Minimum index reached")
            elif(int(direction) == 2):
                self.transformPicture(1)
            elif(int(direction) == -2):
                self.transformPicture(-1)

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
        addr = ""
        if len(sys.argv) == 1:
            addr = wiimoteAddress
        elif len(sys.argv) == 2:
            addr = sys.argv[1]
            name = None
        elif len(sys.argv) == 3:
            addr, name = sys.argv[1:3]
        print(("Connecting to %s (%s)" % (name, addr)))
        self.wm = wiimote.connect(addr, name)
        self.wm.ir.register_callback(self.moveCursor)
        self.wm.buttons.register_callback(self.buttonPressed)
        # self.wm.accelerometer.register_callback(self.transformPicture)

    def buttonPressed(self, changedButtons):
        # undo redo
        for button in changedButtons:
            if(button[0] == 'B' and not button[1]):
                # B button released
                if self.painted:
                    self.painted = False
                    # Overwrite Pixmap stack when a new action is done after a redo
                    if self.currentPixmapIndex < len(self.pixmapStack) - 1:
                        del self.pixmapStack[-self.currentPixmapIndex + 1:]
                    self.pixmapStack.append(QtGui.QPixmap(self.image.pixmap()))
                    self.currentPixmapIndex += 1
            if(button[0] == 'Minus' and button[1] and len(self.pixmapStack) > 0 and self.currentPixmapIndex > 0):
                # Minus button released and undo stack is not empty -> undo
                self.currentPixmapIndex -= 1
                self.image.setPixmap(self.pixmapStack[self.currentPixmapIndex])
            if(button[0] == 'Plus' and button[1] and len(
                    self.pixmapStack) > 0 and self.currentPixmapIndex < (len(self.pixmapStack) - 1)):
                # Plus button released and undo stack is not empty -> redo
                self.currentPixmapIndex += 1
                self.image.setPixmap(self.pixmapStack[self.currentPixmapIndex])
            if(button[0] == 'Down'):
                if(button[1]):
                    # DPAD down pressed
                    self.wm.accelerometer.register_callback(self.zoomPicture)
                else:
                    # DPAD down released
                    self.wm.accelerometer.unregister_callback(self.zoomPicture)

    def initCursor(self):
        self.cursor = QtWidgets.QLabel(self)
        self.cursor.setAlignment(QtCore.Qt.AlignCenter)
        self.cursor.setGeometry(100, 50, 10, 10)
        self.cursor.setPixmap(QtGui.QPixmap(("cursor.png")).scaledToHeight(10))

    def initArrow(self):
        self.arrow = QtWidgets.QLabel(self)
        self.arrow.setAlignment(QtCore.Qt.AlignCenter)
        self.arrow.setGeometry(self.thumbnailWidth / 2 - self.arrowWidth / 2,
                               self.arrowY, self.arrowWidth, self.arrowHeight)
        self.arrow.setPixmap(QtGui.QPixmap(("arrow.png")).scaledToHeight(20))

    def resetUndoRedoStack(self):
        print("resttin")
        self.pixmapStack = []
        self.pixmapStack.append(QtGui.QPixmap(self.image.pixmap()))
        self.currentPixmapIndex = 0

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
        # remove offset to match cursor with image coordinates
        x -= (self.width - self.drawingPixmap.width()) / 2
        y -= (self.image.height() - self.drawingPixmap.height()) / 2
        painter = QtGui.QPainter()
        painter.begin(self.drawingPixmap)
        painter.setBrush(QtGui.QColor("red"))
        painter.setPen(self.pen)
        painter.drawEllipse(x, y, 10, 10)
        painter.end()
        self.painted = True
        self.image.setPixmap(self.drawingPixmap)

    def initPen(self, color):
        # pen width and color for the painting
        self.pen = QtGui.QPen(QtGui.QColor(color))
        self.pen.setWidth(1)

    def animationFinished(self, newState, oldState):
        if newState == QtCore.QAbstractAnimation.Stopped and oldState == QtCore.QAbstractAnimation.Running:
            self.animationsRunning -= 1
            if self.animationsRunning == 0:
                # all animations for last swipe gesture finished -> reset undo stack
                self.pixmapStack = []
                self.pixmapStack.append(QtGui.QPixmap(self.image.pixmap()))
                self.currentPixmapIndex = 0

    def collectData(self, accelData):
        if self.count < 32:
            self.count += 1
            x, z = accelData[0], accelData[2]
            rot_angle = int(- (scipy.degrees(scipy.arctan2(z - 512, x - 512)) - 90))
            self.list.append(rot_angle)
        else:
            self.transformPicture(accelData)
            self.count = 0
            self.list = []

    def transformPicture(self, direction):
        # rotate
        angle = self.curAngle
        for i in range(45):
            angle += (direction * 2)
            self.image.setPixmap(self.pixmap.transformed(
                QtGui.QTransform().rotate(angle), QtCore.Qt.SmoothTransformation))
        self.curAngle = angle
        self.drawingPixmap = self.image.pixmap()
        self.resetUndoRedoStack()

    def zoomPicture(self, accelData):
        y, z = accelData[1], accelData[2]
        offset = 512
        centeredZ = z - offset
        centeredY = y - offset
        tilt_angle = scipy.degrees(scipy.arctan2(centeredZ, centeredY)) - 90
        if tilt_angle <= -90:
            tilt_angle = 360 + tilt_angle
        scale_val = (tilt_angle / 100) + 1
        if scale_val < 0:
            scale_val = - scale_val
        self.image.setPixmap(self.pixmap.transformed(
            QtGui.QTransform().scale(scale_val, scale_val), QtCore.Qt.SmoothTransformation))
        self.drawingPixmap = self.image.pixmap()
        self.resetUndoRedoStack()

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
