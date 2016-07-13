#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-


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
            csv.write(self.name + "," + str(values[0]) + "," + str(values[1]) + "," + str(values[2]) + "\n")
        csv.close()
