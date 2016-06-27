#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
from PyQt5 import Qt, QtGui, QtCore, QtWidgets
from math import sin, cos, pi, sqrt
from numpy import matrix

# the recorded gestures are stored in this list
# as a tuple of a name and a list of points
gestures = []


# this is the main widget
# the user can try the recorded gestures here
# feedback is provided via the bottom label
# via the record button new gestures can be trained
class QGestureWidget(QtWidgets.QWidget):

    def __init__(self, width=800, height=950):
        super().__init__()
        self.resize(width, height)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)  # only get events when button is pressed
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Gesture Magic')
        layout = QtWidgets.QVBoxLayout(self)
        self.dw = QDrawWidget(self, False)
        layout.addWidget(self.dw)
        self.button = QtWidgets.QPushButton("Record Gesture", self)
        self.button.setMaximumHeight(25)
        self.button.clicked.connect(self.openRecordWidget)
        layout.addWidget(self.button)
        self.label = QtWidgets.QLabel("Press the button to record gestures", self)
        self.label.setMaximumHeight(25)
        layout.addWidget(self.label)
        self.show()

    # start the RecordWidget to record a new gesture
    def openRecordWidget(self):
        self.label.setText("Try a recorded gesture or record a new one")
        self.dw.points = []
        self.dw.update()
        self.popup = QRecordWidget()

    # compares given points to all recorded gesture templates
    def compareToTemplates(self, points):
        if(len(gestures) > 0):
            # gestures with more distance than maxDistance are ignored
            maxDistance = 1000
            # index of the currently closest gesture
            # -1 means no gesture was closer than maxDistance yet
            currentIndex = -1
            i = 0
            for gesture in gestures:
                gestureDistance = self.compare(gesture[1], points)
                if (gestureDistance < maxDistance):
                    maxDistance = gestureDistance
                    currentIndex = i
                i += 1
            if currentIndex > -1:
                self.label.setText("Recognized gesture: " + str(gestures[currentIndex][0]))
            else:
                self.label.setText("Could not recognize gesture. Try again!")
        else:
            self.label.setText("No gestures recorded yet. Press the button to record gestures")

    # compare two gestures and return the overall distance of their points
    def compare(self, pointsA, pointsB):
        overallDistance = 0
        if(len(pointsA) == 64 and len(pointsB) == 64):
            for i in range(64):
                overallDistance += distance(pointsA[i], pointsB[i])
            return overallDistance
        else:
            return 9999


# this widget allows the user to record a new gesture
# to press the save button a gesture has to be drawn
# and a name has to be entered in the edit text
class QRecordWidget(QtWidgets.QWidget):
    def __init__(self, width=800, height=950):
        super().__init__()
        self.resize(width, height)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)  # only get events when button is pressed
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Record Gesture')
        layout = QtWidgets.QVBoxLayout(self)
        self.drawWidget = QDrawWidget(self, True)
        layout.addWidget(self.drawWidget)
        self.textEdit = QtWidgets.QPlainTextEdit(self)
        self.textEdit.setMaximumHeight(25)
        layout.addWidget(self.textEdit)
        self.button = QtWidgets.QPushButton("Save Gesture", self)
        self.button.setMaximumHeight(25)
        self.button.clicked.connect(self.saveGesture)
        layout.addWidget(self.button)
        self.show()

    # try to save the gesture, close the RecordWidget when successful
    def saveGesture(self):
        gestureName = str(self.textEdit.toPlainText())
        if self.drawWidget.saveGesture(gestureName):
            self.close()


# This widget is used by the GestureWidget and the RecordWidget
# it enables the user to draw gestures
# which then will be resampled, transformed and resized
class QDrawWidget(QtWidgets.QWidget):

    def __init__(self, parent, recordMode, width=800, height=800):
        super().__init__(parent)
        self.resize(width, height)
        self.drawing = False
        self.recordMode = recordMode
        self.points = []
        self.templatePoints = []
        self.setMouseTracking(True)  # only get events when button is pressed

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            # user is drawing a gesture
            self.drawing = True
            self.points = []
            self.update()

    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            # user finished drawing a gesture
            self.drawing = False
            if (len(self.points) > 0):
                self.templatePoints = self.resample(self.points)
                self.templatePoints = self.transform(self.templatePoints)
                self.templatePoints = self.bounding_box(self.templatePoints)
            if (not self.recordMode and len(self.templatePoints) > 0):
                self.parent().compareToTemplates(self.templatePoints)
            self.update()

    def mouseMoveEvent(self, ev):
        if self.drawing:
            # draw
            self.points.append((ev.x(), ev.y()))
            self.update()

    def poly(self, pts):
        return QtGui.QPolygonF(map(lambda p: QtCore.QPointF(*p), pts))

    def paintEvent(self, ev):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(ev.rect())
        qp.setBrush(QtGui.QColor(20, 255, 190))
        qp.setPen(QtGui.QColor(0, 155, 0))
        qp.drawPolyline(self.poly(self.points))
        for point in self.points:
            qp.drawEllipse(point[0]-1, point[1] - 1, 2, 2)
        qp.end()

    # only save gesture if a gesture was recorded
    # and a name was entered
    def saveGesture(self, gestureName):
        if (len(self.templatePoints) > 0 and len(gestureName) > 0):
            gestures.append((gestureName, self.templatePoints))
            return True
        else:
            return False

    def total_length(self, point_list):
        p1 = point_list[0]
        length = 0.0
        for i in range(1, len(point_list)):
            length += distance(p1, point_list[i])
            p1 = point_list[i]
        return length

    def resample(self, point_list, step_count=64):
        newpoints = []
        length = self.total_length(point_list)
        stepsize = length/step_count
        curpos = 0
        newpoints.append(point_list[0])
        i = 1
        while i < len(point_list):
            p1 = point_list[i-1]
            d = distance(p1, point_list[i])
            if curpos+d >= stepsize:
                nx = p1[0] + ((stepsize-curpos)/d)*(point_list[i][0]-p1[0])
                ny = p1[1] + ((stepsize-curpos)/d)*(point_list[i][1]-p1[1])
                newpoints.append([nx, ny])
                point_list.insert(i, [nx, ny])
                curpos = 0
            else:
                curpos += d
            i += 1
        # we only want 64 points!
        newpoints = newpoints[:64]
        return newpoints

    def transform(self, points):
        center = (400, 400)
        new_points = []
        r = 5 * (pi / 180)  # degrees multmat
        rot_matrix = matrix([[cos(r), -sin(r), 0],  # clockwise
                             [sin(r),  cos(r), 0],
                             [0, 0, 1]])
        t1 = matrix([[1, 0, -center[0]], [0, 1, -center[1]], [0, 0, 1]])
        t2 = matrix([[1, 0, center[0]], [0, 1, center[1]], [0, 0, 1]])

        for point in points:
            hom_point = matrix([[point[0]], [point[1]], [1]])
            transform = t2  @ rot_matrix @ t1
            rotated_point = transform @ hom_point
            new_points.append((int(rotated_point[0]), int(rotated_point[1])))
        return new_points

    # returns a scaled representation of the given points
    # which fits into a 100x100 bounding box
    def bounding_box(self, points):
        # we assume there are no negative points
        # because we executed transform() before
        right, up = 0, 0
        for point in points:
            if(point[0] > right):
                right = point[0]
            if(point[1] > up):
                up = point[1]
            if(right > up):
                factor = 100.0 / right
            else:
                factor = 100.0 / up
        new_points = []
        for point in points:
            new_points.append((int(point[0]*factor), int(point[1]*factor)))
        return new_points


# this function is needed by multiple widgets and thus global
def distance(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return sqrt(dx*dx+dy*dy)


def main():
    app = QtWidgets.QApplication(sys.argv)
    dw = QGestureWidget()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
