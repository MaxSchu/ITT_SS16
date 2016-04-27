#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys


class FileReader():
    participant_key = "PARTICIPANT"
    repetition_key = "REPETITIONS"
    time_between_key = "TIME_BETWEEN_SIGNALS_MS"
    order_key = "ORDER"

    def __init__(self):
        self.readFile()

    def readFile(self):
        parameters = {}
        if (len(sys.argv) == 2):
            file = open(sys.argv[1])
            for line in file:
                line = line.replace("\n", "")
                values = line.split(": ")
                key = values[0]
                value = values[1]
                if (key == self.repetition_key or key == self.time_between_key):
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

    def checkKey(self, dictionary, key):
        if (key in dictionary.keys()):
            if (dictionary[key] is None or dictionary[key] == ""):
                print("no value for " + key)
                exit()
        else:
            print(key + " not found")
            exit()

    def splitOrderString(self, values):
        orderList = list(map(int, values.split(" ")))
        if(len(orderList) != 4):
            print("Invalid order parameters")
            exit()
        return orderList


def main():
    FileReader()

if __name__ == '__main__':
    main()
