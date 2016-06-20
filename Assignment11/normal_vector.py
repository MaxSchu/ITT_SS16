#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from pyqtgraph.flowchart import Flowchart, Node
from pyqtgraph.flowchart.library.common import CtrlNode
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np

import wiimote
import wiimote_node

    
if __name__ == '__main__':
    import sys
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.setWindowTitle('NormalVector Demo')
    cw = QtGui.QWidget()
    win.setCentralWidget(cw)
    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    ## Create an empty flowchart with a single input and output
    fc = Flowchart(terminals={
    })
    w = fc.widget()

    layout.addWidget(fc.widget(), 0, 0, 2, 1)

    wiimoteNode = fc.createNode('Wiimote', pos=(-150, 150))
    normalNode = fc.createNode('NormalVector', pos=( 0, 150))
    plotCurve = fc.createNode('PlotCurve', pos=(150, 150))

    pw1 = pg.PlotWidget()
    pw1.setYRange(-1, 1)
    pw1.setXRange(-1, 1)
    layout.addWidget(pw1, 0, 1)
    pw1Node = fc.createNode('PlotWidget', pos=(300, 150))
    pw1Node.setPlot(pw1)
    
    fc.connectTerminals(wiimoteNode['accelX'], normalNode['Xnormal'])
    fc.connectTerminals(wiimoteNode['accelZ'], normalNode['Znormal'])
    fc.connectTerminals(normalNode['VectorX'], plotCurve['x'])
    fc.connectTerminals(normalNode['VectorY'], plotCurve['y'])
    fc.connectTerminals(plotCurve['plot'], pw1Node['In'])

    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
