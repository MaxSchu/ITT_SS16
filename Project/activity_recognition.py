#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
import wiimote
import os
import wii_gesture_classifier as c
from gesture import WiiGesture


class GestureRecognizer():
    """
    This Class manages the UI and the WiiMote
    It records the accelerometer values from the Wiimote
    and stores them into a WiiGesture

    It is able to even retain the data after restart.
    For this feature all recorded values are stored into CSV.
    """

    gestureList = []
    currentGestureData = []
    recording = False
    gestureListFileName = "gesture_list.txt"
    
    def __init__(self, callback, wm):
        self.callback = callback
        self.wm = wm
        self.wm.buttons.register_callback(self.wiimoteButtonPressed)
        self.loadGestureList()

    def loadGestureList(self):
        lines = [line.rstrip("\n") for line in open(self.gestureListFileName)]
        for line in lines:
            if(line != ""):
                gesture = WiiGesture(line)
                self.loadCSVData(gesture)
                self.gestureList.append(gesture)
        self.reloadClassifier()

    def loadCSVData(self, gesture):
        fileCount = 0
        #the csv in the training samples folder should not be altered by user
        path = "training_samples/" + gesture.name + "_" + str(0) + ".csv"
        data = []
        while os.path.isfile(path):
            lines = [line.rstrip("\n") for line in open(path)]
            for line in lines:
                values = line.split(",")
                data.append([int(values[1]), int(values[2]), int(values[3])])
            gesture.addTrainingsData(data)
            data = []
            fileCount += 1
            path = "training_samples/" + gesture.name + "_" + str(fileCount) + ".csv"


    def wiimoteButtonPressed(self, btns):
        if len(btns) == 0:
            return
        for btn in btns:
            if btn[1]:
                if btn[0] == "A" and not self.recording:
                    self.startRecording()
                    self.recording = True
                elif btn[0] == "A" and self.recording:
                    self.stopRecording()
                    self.recording = False

    def stopRecording(self):
        self.wm.accelerometer.unregister_callback(self.recordAccel)
        # classify
        gesture = WiiGesture()
        gesture.addTrainingsData(self.currentGestureData)
        self.currentGestureData = []
        if self.classifier is not None:
            self.callback(self.gestureList[self.classifier.classify(gesture)].name)
        else:
            self.callback("Before classifying you need to train some gestures first!")

    def startRecording(self):
        self.wm.accelerometer.register_callback(self.recordAccel)
        self.callback("started recording") 

    def recordAccel(self, values):
        self.currentGestureData.append(values)

    def gestureListToString(self, gestureList):
        #for debugging porposes, gets a string representation of gestureList
        string = ""
        for gesture in gestureList:
            string += gesture.toString() + "\n"
        return string

    def reloadClassifier(self):
        self.classifier = c.WiiGestureClassifier()
        self.classifier.train(self.gestureList)
