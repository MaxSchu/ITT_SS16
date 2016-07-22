#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import wiimote
import numpy as np
import scipy as sp


class GestureRecognizer():
    """
    This Class manages the swipe recognition.
    It records the accelerometer values from the Wiimote
    and stores them into a WiiGesture

    It calculates the derivative of the x axis values of
    the accelerometer to get the direction of the swipe gesture
    """

    recording = False

    def __init__(self, callback, wm):
        self.callback = callback
        self.wm = wm
        self.wm.buttons.register_callback(self.wiimoteButtonPressed)
        self.rotList = []

    def wiimoteButtonPressed(self, btns):
        if len(btns) == 0:
            return
        for btn in btns:
            if btn[1]:
                if btn[0] == "One" and not self.recording:
                    self.startRecording()
                    self.recording = True
                elif btn[0] == "One" and self.recording:
                    self.stopRecording()
                    self.recording = False
                elif btn[0] == "Two" and not self.recording:
                    print('pressed two')
                    self.startRecording()
                    self.recording = True
                elif btn[0] == "Two" and self.recording:
                    self.stopRecordingRot()
                    self.recording = False

    def stopRecordingRot(self):
        self.wm.accelerometer.unregister_callback(self.recordAccel)
        for value in self.currentGestureData:
            x, y, z = value[0], value[1], value[2]
            rot_angle = int(-(sp.degrees(sp.arctan2(z-512, x-512)) - 90))
            self.rotList.append(rot_angle)
        print(self.rotList)
        self.currentGestureData = []
        direction = self.getDirection()
        if direction == 1:
            self.callback(2)
        else:
            self.callback(-2)

    def stopRecording(self):
        self.wm.accelerometer.unregister_callback(self.recordAccel)
        # classify
        gesture = WiiGesture()
        gesture.addTrainingsData(self.currentGestureData)
        self.currentGestureData = []
        gradientSum = self.classify(gesture)
        if gradientSum > 0:
            self.callback(1)
        elif gradientSum < 0:
            self.callback(-1)
        else:
            # gradientSum = 0 -> do nothing, not likely to happen
            return

    def startRecording(self):
        self.currentGestureData = []
        self.wm.accelerometer.register_callback(self.recordAccel)

    def getDirection(self):
        left = 0
        right = 0
        left = self.rotList[0]
        right = self.rotList[-1]
        # counter-clockwise
        if left > right:
            return -1
        # clockwise
        elif right > left: 
            return 1
        else:
            return 0

    def recordAccel(self, values):
        self.currentGestureData.append(values)

    def classify(self, gesture):
        parsedData = [self.parseDataset(dataSet) for dataSet in gesture.trainingsData]
        gradient = np.gradient(parsedData[0])
        return sum(gradient)

    def parseDataset(self, dataSet):
        x = []
        # Use the difference from default sensor value
        for values in dataSet:
            x.append(values[0]-512)
            x.append(values[0] - 512)
        return x


class WiiGesture():
    """
    This class is used to store all training samples
    for a certain gesture
    """
    path = "training_samples/"

    def __init__(self, name=""):
        self.name = name
        self.trainingsData = []
        self.frequencies = []

    def toString(self):
        # for Logging purposes
        string = self.name + "\n"
        for dataSet in self.trainingsData:
            for xyz in dataSet:
                string += "["
                for value in xyz:
                    string += str(value) + " "
                string += "], "
            string += "\n"
        return string

    def addTrainingsData(self, data):
        self.trainingsData.append(data)

    def dataToCSV(self, data):
        # method to store training data into csv
        csv = open("training_samples/" + self.name + "_" + str(len(self.trainingsData) - 1) + ".csv", "w")
        for values in data:
            csv.wri