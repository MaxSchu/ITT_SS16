from PyQt5 import uic, QtWidgets, QtCore
from functools import partial
import sys


class Calculator(QtWidgets.QMainWindow):

    BUTTONS = {}

    def __init__(self):
        super(self.__class__, self).__init__()
        self.ui = uic.loadUi('calculator.ui', self)
        self.setupButtons()

    def addNumber(self, text):
        self.ui.textBrowser.append(text)

    def setupButtons(self):
        BUTTONS = {0: self.ui.number_0, 1: self.ui.number_1, 2: self.ui.number_2, 3: self.ui.number_3,
                   4: self.ui.number_4, 5: self.ui.number_5, 6: self.ui.number_6, 7: self.ui.number_7,
                   8: self.ui.number_8, 9: self.ui.number_9}

        for button in BUTTONS.keys():
            print (button)
            BUTTONS[button].clicked.connect(partial(self.addNumber, str(button)))


def main():
    app = QtWidgets.QApplication(sys.argv)
    calculator = Calculator()
    calculator.show()
    app.exec_()


if __name__ == '__main__':
    main()
