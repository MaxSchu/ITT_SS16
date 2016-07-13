#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import numpy as np
from scipy import fft
import math
from sklearn import svm
from gesture import WiiGesture


class WiiGestureClassifier():
    """
    This class uses the FFT on the average of all three sensor values
    to provide the training data for the SVM

    Three good distinguishable gestures are:
        Fast circle movement
        Still, doing nothing
        Fast swing movement from behind the shoulder (like a whip)
    """
    def __init__(self):
        super(self.__class__, self).__init__()

    def train(self, gestureList):
        self.gestureList = gestureList
        self.parsedGestureList = []
        self.parseArrays(self.gestureList)
        if self.checkListForEmpty():
            return "\na gesture has no trained samples"
        self.minlen = self.calcMinLength()
        self.cutGestureList()
        self.getFrequencies()
        self.buildClassifier()

    def parseArrays(self, data):
        parsedData = []
        for gesture in data:
            parsedGesture = WiiGesture(gesture.name)
            parsedData = [self.parseDataset(dataSet)
                          for dataSet in gesture.trainingsData]
            parsedGesture.trainingsData = parsedData
            self.parsedGestureList.append(parsedGesture)

    def parseDataset(self, dataSet):
        x = []
        y = []
        z = []
        avg = []
        # Use the difference from default sensor value
        for values in dataSet:
            x.append(values[0] - 512)
            y.append(values[1] - 512)
            z.append(values[2] - 512)
            avg.append((values[0] - 512 + values[1] - 512 + values[2] - 512) / 3)
        return avg

    def calcMinLength(self):
        all = []
        for gesture in self.parsedGestureList:
            all += gesture.trainingsData
        minlen = min([len(x) for x in all])
        return minlen

    def cutGestureList(self):
        for gesture in self.parsedGestureList:
            gesture.trainingsData = [l[:self.minlen] for l in gesture.trainingsData]

    def getFrequencies(self):
        for gesture in self.parsedGestureList:
            gesture.frequencies = [
                np.abs(fft(l) / len(l))[1:len(l) / 2] for l in gesture.trainingsData]

    def buildClassifier(self):
        self.c = svm.SVC()
        count = 0
        categories = []
        trainingData = []
        for gesture in self.parsedGestureList:
            categories += [count] * len(gesture.frequencies)
            trainingData += gesture.frequencies
            count += 1
        try:
            self.c.fit(trainingData, categories)
        except ValueError:
            return 'More traininsdata for some gestures required'

    def classify(self, gesture):
        parsedData = []
        parsedGesture = WiiGesture(gesture.name)
        parsedData = [self.parseDataset(dataSet) for dataSet in gesture.trainingsData]
        parsedGesture.trainingsData = parsedData
        if len(parsedGesture.trainingsData[0]) < self.minlen:
            missingValues = self.minlen - len(parsedGesture.trainingsData[0])
            for x in range(missingValues):
                parsedGesture.trainingsData[0].append(0)
        parsedGesture.trainingsData = [l[:self.minlen] for l in parsedGesture.trainingsData]
        parsedGesture.frequencies = [np.abs(fft(l) / len(l))[1:len(l) / 2] for l in parsedGesture.trainingsData]
        return self.c.predict(parsedGesture.frequencies[0])

    def checkListForEmpty(self):
        # checks for empty gestures and exits code
        if len(self.parsedGestureList) <= 0:
            return True
        for gesture in self.parsedGestureList:
            if len(gesture.trainingsData) <= 0:
                return True
            else:
                return False
