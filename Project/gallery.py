#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import os, sys, glob
from PyQt5 import QtGui, QtCore, QtWidgets

app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()
window.setGeometry(0, 0, 600, 600)
i = 0
filenames = glob.glob('*.png')
for filename in filenames[:6]:
    if i == 0:
        image = QtWidgets.QLabel(window)
        image.setAlignment(QtCore.Qt.AlignCenter)
        image.setGeometry(100, 50, 400, 400)
        image.setPixmap(QtGui.QPixmap((filename)).scaledToHeight(400))
    thumbnail = QtWidgets.QLabel(window)
    thumbnail.setAlignment(QtCore.Qt.AlignCenter)
    thumbnail.setGeometry(i*100, 500, 100, 100)
    #use full ABSOLUTE path to the image, not relative
    thumbnail.setPixmap(QtGui.QPixmap((filename)).scaledToHeight(100))
    i += 1

window.show()
sys.exit(app.exec_())