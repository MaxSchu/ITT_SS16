from PyQt5 import uic, QtWidgets
import sys


class Calculator(QtWidgets.QMainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        uic.loadUi('calculator.ui', self)


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = Calculator()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
