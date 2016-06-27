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
import sys


class NormalVectorNode(Node):
    nodeName = "NormalVector"

    def __init__(self, name):
        terminals = {
            'Znormal': dict(io='in'),
            'Xnormal': dict(io='in'),
            'VectorX': dict(io='out'),
            'VectorY': dict(io='out'),
        }
        self._stuff = np.array([])
        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        #reduce sensor default values to 0 and calculate angle
        angle = np.arctan2(kwds['Znormal'] - 512, kwds['Xnormal'] - 512)
        return {'VectorX': np.array([0, np.cos(angle)]), 'VectorY': np.array([0, np.sin(angle)])}
fclib.registerNodeType(NormalVectorNode, [('NormalVector',)])


def setupFlowChart(layout, fc, wiimoteNode):
    pw1 = pg.PlotWidget()
    layout.addWidget(pw1, 0, 1)
    pw1.setYRange(0, 1024)
    pw1Node = fc.createNode('PlotWidget', pos=(-150, 300))
    pw1Node.setPlot(pw1)

    pw2 = pg.PlotWidget()
    layout.addWidget(pw2, 1, 1)
    pw2.setYRange(0, 1024)
    pw2Node = fc.createNode('PlotWidget', pos=(0, 300))
    pw2Node.setPlot(pw2)

    pw3 = pg.PlotWidget()
    layout.addWidget(pw3, 2, 1)
    pw3.setYRange(0, 1024)
    pw3Node = fc.createNode('PlotWidget', pos=(300, 300))
    pw3Node.setPlot(pw3)

    filterNode = fc.createNode('MedianFilter', pos=(150, 300))
    bufferNodeX = fc.createNode('Buffer', pos=(-150, 150))
    bufferNodeY = fc.createNode('Buffer', pos=(0, 150))
    bufferNodeZ = fc.createNode('Buffer', pos=(150, 150))

    fc.connectTerminals(wiimoteNode['accelX'], bufferNodeX['dataIn'])
    fc.connectTerminals(wiimoteNode['accelY'], bufferNodeY['dataIn'])
    fc.connectTerminals(wiimoteNode['accelZ'], bufferNodeZ['dataIn'])
    fc.connectTerminals(bufferNodeX['dataOut'], pw1Node['In'])
    fc.connectTerminals(bufferNodeY['dataOut'], pw2Node['In'])
    fc.connectTerminals(bufferNodeZ['dataOut'], filterNode['In'])
    fc.connectTerminals(filterNode['Out'], pw3Node['In'])


def initWiiMote(wiimoteNode):
    if len(sys.argv) > 1:
        wiimoteNode.btaddr = sys.argv[1]
    else:
        wiimoteNode.btaddr = "b8:ae:6e:50:05:32"


def setupRotationPlot(layout, fc, wiimoteNode):
    normalNode = fc.createNode('NormalVector', pos=(0, 450))
    plotCurve = fc.createNode('PlotCurve', pos=(150, 450))

    pw1 = pg.PlotWidget()
    pw1.setYRange(-1, 1)
    pw1.setXRange(-1, 1)
    layout.addWidget(pw1, 0, 4)
    pw1Node = fc.createNode('PlotWidget', pos=(300, 450))
    pw1Node.setPlot(pw1)

    fc.connectTerminals(wiimoteNode['accelX'], normalNode['Xnormal'])
    fc.connectTerminals(wiimoteNode['accelZ'], normalNode['Znormal'])
    fc.connectTerminals(normalNode['VectorX'], plotCurve['x'])
    fc.connectTerminals(normalNode['VectorY'], plotCurve['y'])
    fc.connectTerminals(plotCurve['plot'], pw1Node['In'])


if __name__ == '__main__':
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.setWindowTitle('WiiMote Sensor Analyzer')
    cw = QtGui.QWidget()
    win.setCentralWidget(cw)
    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    # Create an empty flowchart with a single input and output
    fc = Flowchart(terminals={
    })
    w = fc.widget()
    layout.addWidget(fc.widget(), 0, 0, 2, 1)
    wiimoteNode = fc.createNode('Wiimote', pos=(0, 0), )
    initWiiMote(wiimoteNode)
    setupFlowChart(layout, fc, wiimoteNode)
    setupRotationPlot(layout, fc, wiimoteNode)

    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
