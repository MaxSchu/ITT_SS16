from PyQt5 import uic, QtWidgets
from enum import Enum
import sys


class Calculator(QtWidgets.QMainWindow):

    class Operations(Enum):
        ADD, SUB, MUL, DIV, REMOVE, CLEAR, EQUALS = range(7)

    def __init__(self):
        super(self.__class__, self).__init__()
        self.ui = uic.loadUi('calculator.ui', self)
        self.currentValue = 0
        self.setupButtons()

    def addNumber(self, text):
        self.ui.textBrowser.insertPlainText(text)
        print(float(self.ui.textBrowser.toPlainText()))

    def performOperation(self, op):
        print(op)

    def setupButtons(self):
        NUMBERS = {0: self.ui.number_0, 1: self.ui.number_1, 2: self.ui.number_2, 3: self.ui.number_3,
                   4: self.ui.number_4, 5: self.ui.number_5, 6: self.ui.number_6, 7: self.ui.number_7,
                   8: self.ui.number_8, 9: self.ui.number_9, ".0": self.ui.funcDec}

        OPERATORS = {self.Operations.ADD: self.ui.opAdd, self.Operations.SUB: self.ui.opSub,
                     self.Operations.MUL: self.ui.opMul, self.Operations.DIV: self.ui.opDiv}

        for number in NUMBERS.keys():
            NUMBERS[number].clicked.connect(lambda ignore, x=number: self.addNumber(str(x)))

        for operator in OPERATORS.keys():
            OPERATORS[operator].clicked.connect(lambda ignore, x=operator: self.performOperation(x))


def main():
    app = QtWidgets.QApplication(sys.argv)
    calculator = Calculator()
    calculator.show()
    app.exec_()


if __name__ == '__main__':
    main()
