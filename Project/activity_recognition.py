#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import wiimote
import numpy as np
from gesture import WiiGesture


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

    def recordAccel(self, values):
        self.currentGestureData.append(values)

    def classify(self, gesture):
        parsedData = [self.parseDataset(dataSet) for dataSet in gesture.trainingsData]
        gradient = np.gradient(parsedData[0])
        return sum(gradient)

    def parseDataset(self, dataSet):
        x = []
        #Use the difference from default sensor value
        for values in dataSet:
            x.append(values[0]-512)
        return x