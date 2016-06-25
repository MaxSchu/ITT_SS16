from PyQt5 import uic, QtWidgets, QtCore
import sys
import wiimote


class GestureTool(QtWidgets.QMainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.ui = uic.loadUi('gesture.ui', self)
        self.setupButtons()
        self.wm = initWiimote()

    def setupButtons(self):
        self.ui.executeButton.clicked.connect(lambda ignore, x=self.ui.executeButton: self.logLol("execuuute"))
        self.ui.recordButton.clicked.connect(lambda ignore, x=self.ui.recordButton: self.logLol("recoooord"))

    def initWiimote(self):
        input("Press the 'sync' button on the back of your Wiimote Plus " +
              "or buttons (1) and (2) on your classic Wiimote.\n" +
              "Press <return> once the Wiimote's LEDs start blinking.")
        if len(sys.argv) == 1:
            addr, name = wiimote.find()[0]
        elif len(sys.argv) == 2:
            addr = sys.argv[1]
            name = None
        elif len(sys.argv) == 3:
            addr, name = sys.argv[1:3]
        print(("Connecting to %s (%s)" % (name, addr)))
        wm = wiimote.connect(addr, name)
        return wm

        def logLol(self, txt):
            print("Lol: " + txt)


def main():
    app = QtWidgets.QApplication(sys.argv)
    gestureTool = GestureTool()
    gestureTool.show()
    app.exec_()


if __name__ == '__main__':
    main()
