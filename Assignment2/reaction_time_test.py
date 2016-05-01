#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import csv
import os


class FileReader():
    participant_key = "PARTICIPANT"
    repetition_key = "REPETITIONS"
    time_between_key = "TIME_BETWEEN_SIGNALS_MS"
    order_key = "ORDER"
    gender_key = "GENDER"
    age_key = "AGE"
    handedness_key = "HANDEDNESS"

    def readFile(self):
        parameters = {}
        if (len(sys.argv) == 2):
            file = open(sys.argv[1])
            for line in file:
                line = line.replace("\n", "")
                line = line.replace(" ", "")
                values = line.split(":")
                key = values[0]
                value = values[1]
                if (key == self.repetition_key or key == self.time_between_key
                        or key == self.age_key):
                    try:
                        value = int(value)
                    except ValueError:
                        print("Invalid value in " + key)
                        exit()
                parameters[key] = value
        self.checkDictionary(parameters)
        parameters[self.order_key] = self.splitOrderString(
            parameters[self.order_key])
        for key in parameters:
            print(key + ": " + str(parameters[key]))
        return parameters

    def checkDictionary(self, dictionary):
        self.checkKey(dictionary, self.participant_key)
        self.checkKey(dictionary, self.repetition_key)
        self.checkKey(dictionary, self.time_between_key)
        self.checkKey(dictionary, self.order_key)
        self.checkKey(dictionary, self.gender_key)
        self.checkKey(dictionary, self.age_key)
        self.checkKey(dictionary, self.handedness_key)

    def checkKey(self, dictionary, key):
        if (key in dictionary.keys()):
            if (dictionary[key] is None or dictionary[key] == ""):
                print("no value for " + key + " variable")
                exit()
        else:
            print(key + " variable not found")
            exit()

    def splitOrderString(self, values):
        orderList = list(map(int, values.split(",")))
        if(len(orderList) != 4):
            print("Invalid order parameters")
            exit()
        return orderList


class CSVWriter():
    """docstring for CSVWriter"""

    def __init__(self, participantId, values):
        super(CSVWriter, self).__init__()
        self.createCSV(participantId, values)

    def createCSV(self, participantId, values):
        self.csvFileName = (os.path.dirname(__file__) + '/Test_Result'
                            + str(participantId) + '.csv')

        with open(self.csvFileName, 'a', newline='') as csvFile:
            fieldNames = list(values.keys())
            csvWriter = csv.DictWriter(csvFile, fieldnames=fieldNames)
            csvWriter.writeheader()

    def writeCSV(self, values):
        with open(self.csvFileName, 'a', newline='') as csvFile:
            fieldNames = list(values.keys())
            csvWriter = csv.DictWriter(csvFile, fieldnames=fieldNames)
            csvWriter.writerow(values)


def main():
    reader = FileReader()
    values = reader.readFile()
    writer = CSVWriter(1, values)
    writer.writeCSV(values)
    writer.writeCSV(values)

if __name__ == '__main__':
    main()
