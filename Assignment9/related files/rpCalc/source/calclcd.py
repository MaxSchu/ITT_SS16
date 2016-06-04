#!/usr/bin/env python3

#****************************************************************************
# calclcd.py, provides an LCD display
#
# rpCalc, an RPN calculator
# Copyright (C) 2014, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

from PyQt5 import QtCore, QtGui, QtWidgets


class Lcd(QtWidgets.QLCDNumber):
    """Main LCD Display.
    """
    def __init__(self, sizeFactor=1, numDigits=8, parent=None):
        QtWidgets.QLCDNumber.__init__(self, numDigits, parent)
        self.sizeFactor = sizeFactor
        self.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.setMinimumSize(10, 23)
        self.setFrameStyle(QtWidgets.QFrame.NoFrame)

    def setDisplay(self, text, numDigits):
        """Update display value.
        """
        text = text.replace('e', ' E', 1)  # add space before exp
        if len(text) > numDigits:  # mark if digits hidden
            text = 'c{0}'.format(text[1-numDigits:])
        self.setNumDigits(numDigits)
        self.display(text)

    def sizeHint(self):
        """Set prefered size.
        """
        # default in Qt is 23 height & about 10 * numDigits
        size = QtWidgets.QLCDNumber.sizeHint(self)
        return QtCore.QSize(int(size.width() * self.sizeFactor),
                            int(size.height() * self.sizeFactor))


class LcdBox(QtWidgets.QFrame):
    """Frame for LCD display.
    """
    def __init__(self, parent=None):
        QtWidgets.QFrame.__init__(self, parent)
        self.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)
        self.setLineWidth(3)
 
    def mouseReleaseEvent(self, event):
        """Mouse release event for popup menus.
        """
        if event.button() == QtCore.Qt.RightButton:
            popup = self.parentWidget().popupMenu
            popup.exec_(self.mapToGlobal(event.pos()))
            popup.clearFocus()
        QtWidgets.QFrame.mouseReleaseEvent(self, event)
