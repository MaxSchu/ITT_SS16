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
    win.setWindowTitle('WiimoteNode demo')
    cw = QtGui.QWidget()
    win.setCentralWidget(cw)
    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    ## Create an empty flowchart with a single input and output
    fc = Flowchart(terminals={
    })
    w = fc.widget()

    layout.addWidget(fc.widget(), 0, 0, 2, 1)

    pw1 = pg.PlotWidget()
    layout.addWidget(pw1, 0, 1)
    pw1.setYRange(0,1024)
    pw1Node = fc.createNode('PlotWidget', pos=(-150, 300))
    pw1Node.setPlot(pw1)
    
    pw2 = pg.PlotWidget()
    layout.addWidget(pw2, 1, 1)
    pw2.setYRange(0,1024)
    pw2Node = fc.createNode('PlotWidget', pos=(0, 300))
    pw2Node.setPlot(pw2)
    
    pw3 = pg.PlotWidget()
    layout.addWidget(pw3, 2, 1)
    pw3.setYRange(0,1024)
    pw3Node = fc.createNode('PlotWidget', pos=(150, 300))
    pw3Node.setPlot(pw3)

    wiimoteNode = fc.createNode('Wiimote', pos=(0, 0), )
    bufferNodeX = fc.createNode('Buffer', pos=(-150, 150))
    bufferNodeY = fc.createNode('Buffer', pos=(0, 150))
    bufferNodeZ = fc.createNode('Buffer', pos=(150, 150))

    fc.connectTerminals(wiimoteNode['accelX'], bufferNodeX['dataIn'])
    fc.connectTerminals(wiimoteNode['accelY'], bufferNodeY['dataIn'])
    fc.connectTerminals(wiimoteNode['accelZ'], bufferNodeZ['dataIn'])
    fc.connectTerminals(bufferNodeX['dataOut'], pw1Node['In'])
    fc.connectTerminals(bufferNodeY['dataOut'], pw2Node['In'])
    fc.connectTerminals(bufferNodeZ['dataOut'], pw3Node['In'])

    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
