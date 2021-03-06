from PyQt5 import uic, QtWidgets, QtCore
from enum import Enum
import sys
import time


class Logger():
    def __init__(self):
        super(self.__class__, self).__init__()
        self.taskId = "5"
        self.repetition = "4"
        self.wasKeyboard = False
        self.lastTimestamp = 0
        self.printHeader()

    def getWasKeyboard(self):
        return self.wasKeyboard

    def getTimePassed(self):
        time_passed = time.time() - self.lastTimestamp
        self.lastTimestamp = time.time()
        return time_passed

    def logSomething(self, event, wasKeyboard, operator):
        if self.lastTimestamp == 0:
            self.lastTimestamp = time.time()

        # switched hand
        if self.wasKeyboard != wasKeyboard and wasKeyboard:
            self.logSwitching("switched to keyboard", wasKeyboard)

        self.wasKeyboard = wasKeyboard

        print(str(time.time()) + ";" + str(self.getTimePassed()) + ";" + str(wasKeyboard) + ";" + str(event) +
              ";" + str(operator) + ";" + self.taskId + ";" + self.repetition)
        sys.stdout.flush

    def logSwitching(self, event, wasKeyboard):
        print(str(time.time()) + ";" + str(self.getTimePassed()) + ";" + str(wasKeyboard) + ";" + str(event) +
              ";" + "H" + ";" + self.taskId + ";" + self.repetition)
        sys.stdout.flush
        self.wasKeyboard = wasKeyboard

    def printHeader(self):
        print("timestamp; time_passed; from_keyboard; event; operator; task_id, repetition")
        sys.stdout.flush


class Calculator(QtWidgets.QMainWindow):

    class Operations(Enum):
        ADD, SUB, MUL, DIV, REMOVE, CLEAR, EQUALS, DEC = range(8)

    def __init__(self, logger):
        super(self.__class__, self).__init__()
        self.ui = uic.loadUi('calculator.ui', self)
        self.currentValue = 0
        self.previousValue = 0
        self.suppressLog = False
        self.logger = logger
        self.resetClaculator()
        self.previouslyClicked = None
        self.setupButtons()
        self.currentOperation = None

        # mapping keys to ui buttons
        self.KEY_MAPPING = {QtCore.Qt.Key_1: self.ui.number_1, QtCore.Qt.Key_2: self.ui.number_2,
                            QtCore.Qt.Key_3: self.ui.number_3, QtCore.Qt.Key_4: self.ui.number_4,
                            QtCore.Qt.Key_5: self.ui.number_5, QtCore.Qt.Key_6: self.ui.number_6,
                            QtCore.Qt.Key_7: self.ui.number_7, QtCore.Qt.Key_8: self.ui.number_8,
                            QtCore.Qt.Key_9: self.ui.number_9, QtCore.Qt.Key_Comma: self.ui.funcDec,
                            QtCore.Qt.Key_Enter: self.ui.funcCalc, QtCore.Qt.Key_Return: self.ui.funcCalc,
                            QtCore.Qt.Key_Delete: self.ui.funcClear, QtCore.Qt.Key_Plus: self.ui.opAdd,
                            QtCore.Qt.Key_Minus: self.ui.opSub, QtCore.Qt.Key_Slash: self.ui.opDiv,
                            QtCore.Qt.Key_Asterisk: self.ui.opMul, QtCore.Qt.Key_Backspace: self.ui.funcBack}

        self.OPERATION_SIGNS = {self.Operations.ADD: "+", self.Operations.DIV: "/",
                                self.Operations.SUB: "-", self.Operations.MUL: "*"}

        self.setMouseTracking(True)

    def setMouseTracking(self, flag):
        def recursive_set(parent):
            for child in parent.findChildren(QtCore.QObject):
                try:
                    child.setMouseTracking(flag)
                except:
                    pass
                recursive_set(child)
        QtWidgets.QMainWindow.setMouseTracking(self, flag)
        recursive_set(self)

    def mouseMoveEvent(self, event):
        if self.logger.getWasKeyboard():
            self.logger.logSwitching("switched to mouse", False)

    def keyReleaseEvent(self, e):
        if e.key() in self.KEY_MAPPING:
            self.logger.logSomething("KeyReleased: " + str(e.key()), True, "K")

    def keyPressEvent(self, e):
        self.suppressLog = True
        # emit corresponding signals
        try:
            self.KEY_MAPPING[e.key()].clicked.emit()
        except KeyError:
            # Key not mapped - do nothing
            self.suppressLog = False
            return

    def resetClaculator(self):
        # calculator always starts with 0
        self.currentValue = 0
        self.ui.textBrowser.setPlainText("0")

    def addNumber(self, text):
        if not self.suppressLog:
            if text != self.previouslyClicked:
                self.logger.logSomething("Mouse Moved", False, "P")
                self.previouslyClicked = text
            else:
                self.logger.logSomething(text, False, "B")
        else:
            self.logger.logSomething(text, True, "K")
            self.suppressLog = False

        if self.ui.textBrowser.toPlainText() == "0":
            if text == "0":
                # value 0 stays 0
                return
            if text == ".":
                # handle decimal point
                self.ui.textBrowser.setPlainText("")
                self.ui.textBrowser.insertPlainText("0.")
                return
            else:
                # remove 0
                self.ui.textBrowser.setPlainText("")

        self.ui.textBrowser.insertPlainText(text)
        self.setCurrentValueToOutput()

    def setCurrentValueToOutput(self):
        try:
            self.currentValue = float(self.ui.textBrowser.toPlainText())
        except ValueError:
            # last sign has to be decimal point
            self.currentValue = float(self.ui.textBrowser.toPlainText()[:-1])

    def performOperation(self, op):
        if not self.suppressLog:
            if op != self.previouslyClicked:
                self.logger.logSomething("Mouse Moved", False, "P")
                self.previouslyClicked = op
            else:
                self.logger.logSomething(op, False, "B")
        else:
            self.logger.logSomething(op, True, "K")
            self.suppressLog = False

        if op == self.Operations.DEC:
            # avoid multiple decimal points
            if "." not in self.ui.textBrowser.toPlainText():
                self.addNumber(".")
            return
        elif op == self.Operations.CLEAR:
            self.textBrowser_prev.setPlainText("")
            self.previousValue = 0
            self.currentOperation = 0
            self.resetClaculator()
        elif op == self.Operations.REMOVE:
            self.ui.textBrowser.setPlainText(self.ui.textBrowser.toPlainText()[:-1])
            if self.ui.textBrowser.toPlainText() == "":
                self.ui.textBrowser.setPlainText("0")
            self.setCurrentValueToOutput()
        elif op == self.Operations.EQUALS:
            self.previousValue = self.solvePreviousOperation()
            if self.previousValue is None:
                # an error occured
                return
            self.ui.textBrowser_prev.setPlainText(str(self.previousValue))
            self.currentOperation = None
            self.previousValue = 0
            self.resetClaculator()
        else:
            self.previousValue = self.solvePreviousOperation()
            if self.previousValue is None:
                # an error occured
                return
            self.ui.textBrowser_prev.setPlainText(str(self.previousValue) + " " + self.OPERATION_SIGNS[op])
            self.currentOperation = op
            self.resetClaculator()

    def solvePreviousOperation(self):
        if self.currentOperation == self.Operations.ADD:
            return self.previousValue + self.currentValue
        if self.currentOperation == self.Operations.SUB:
            return self.previousValue - self.currentValue
        if self.currentOperation == self.Operations.MUL:
            return self.previousValue * self.currentValue
        if self.currentOperation == self.Operations.DIV:
            try:
                return self.previousValue / self.currentValue
            except ZeroDivisionError:
                # division by zero not allowed
                self.handleError()
                return None
        else:
            return self.currentValue

    def handleError(self):
        self.ui.textBrowser_prev.setPlainText("ERROR")
        self.resetClaculator()
        self.previousValue = 0
        self.currentOperation = None

    def setupButtons(self):
        NUMBERS = {0: self.ui.number_0, 1: self.ui.number_1, 2: self.ui.number_2, 3: self.ui.number_3,
                   4: self.ui.number_4, 5: self.ui.number_5, 6: self.ui.number_6, 7: self.ui.number_7,
                   8: self.ui.number_8, 9: self.ui.number_9}

        OPERATORS = {self.Operations.ADD: self.ui.opAdd, self.Operations.SUB: self.ui.opSub,
                     self.Operations.MUL: self.ui.opMul, self.Operations.DIV: self.ui.opDiv,
                     self.Operations.DEC: self.ui.funcDec, self.Operations.REMOVE: self.ui.funcBack,
                     self.Operations.CLEAR: self.ui.funcClear, self.Operations.EQUALS: self.ui.funcCalc}

        for number in NUMBERS.keys():
            NUMBERS[number].clicked.connect(lambda ignore, x=number: self.addNumber(str(x)))

        for operator in OPERATORS.keys():
            OPERATORS[operator].clicked.connect(lambda ignore, x=operator: self.performOperation(x))


def main():
    app = QtWidgets.QApplication(sys.argv)
    logger = Logger()
    calculator = Calculator(logger)
    calculator.show()
    app.exec_()


if __name__ == '__main__':
    main()
