#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from pyqtgraph.flowchart import Flowchart, Node
from pyqtgraph.flowchart.library.common import CtrlNode
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph import Vector
import pyqtgraph as pg
import numpy as np
import math as math

import wiimote

btaddr = None


class NormalVectorNode(CtrlNode):
    """
    Calculates the rotation around one axis from the accelerometer values of the
    other two axes and outputs a vector (i.e., two 2D points) that can be plotted 
    by a PlotWidget to indicate the rotation
    """

    nodeName = "NormalVector"
    uiTemplate = [
        ('size', 'spin', {'value': 32.0, 'step': 1.0, 'range': [0.0, 128.0]}),
    ]

    def __init__(self, name):
        terminals = {
            'xIn': dict(io='in'),
            'zIn': dict(io='in'),
            'xOut': dict(io='out'),
            'yOut': dict(io='out'),
        }
        self._normalVector = np.array([])
        self._offset = 512
        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        """
        Calculation here; returns a vector as output
        """
        centeredZ = kwds['zIn'] - self._offset
        centeredX = kwds['xIn'] - self._offset

        angle = math.atan2(centeredZ, centeredX)
        xValues = np.array([1, math.cos(angle) + 1])
        yValues = np.array([0, math.sin(angle)])
        return {'xOut': xValues, 'yOut': yValues}

fclib.registerNodeType(NormalVectorNode, [('Data',)])


class BufferNode(CtrlNode):
    """
    Buffers the last n samples provided on input and provides them as a list of
    length n on output.
    A spinbox widget allows for setting the size of the buffer.
    Default size is 32 samples.
    """
    nodeName = "Buffer"
    uiTemplate = [
        ('size', 'spin', {'value': 32.0, 'step': 1.0, 'range': [0.0, 128.0]}),
    ]

    def __init__(self, name):
        terminals = {
            'dataIn': dict(io='in'),
            'dataOut': dict(io='out'),
        }
        self._buffer = np.array([])
        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        size = int(self.ctrls['size'].value())
        self._buffer = np.append(self._buffer, kwds['dataIn'])
        self._buffer = self._buffer[-size:]
        output = self._buffer
        return {'dataOut': output}

fclib.registerNodeType(BufferNode, [('Data',)])


class WiimoteNode(Node):
    """
    Outputs sensor data from a Wiimote.

    Supported sensors: accelerometer (3 axis)
    Text input box allows for setting a Bluetooth MAC address.
    Pressing the "connect" button tries connecting to the Wiimote.
    Update rate can be changed via a spinbox widget. Setting it to "0"
    activates callbacks every time a new sensor value arrives (which is
    quite often -> performance hit)
    """
    nodeName = "Wiimote"

    def __init__(self, name):
        terminals = {
            'accelX': dict(io='out'),
            'accelY': dict(io='out'),
            'accelZ': dict(io='out'),
        }
        self.wiimote = None
        self._acc_vals = []

        # Configuration UI
        self.ui = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()

        label = QtGui.QLabel("Bluetooth MAC address:")
        self.layout.addWidget(label)
        self.text = QtGui.QLineEdit()
        self.layout.addWidget(self.text)

        label2 = QtGui.QLabel("Update rate (Hz)")
        self.layout.addWidget(label2)

        self.update_rate_input = QtGui.QSpinBox()
        self.update_rate_input.setMinimum(0)
        self.update_rate_input.setMaximum(60)
        self.update_rate_input.setValue(20)
        self.update_rate_input.valueChanged.connect(self.set_update_rate)
        self.layout.addWidget(self.update_rate_input)

        self.connect_button = QtGui.QPushButton("connect")
        self.connect_button.clicked.connect(self.connect_wiimote)
        self.layout.addWidget(self.connect_button)
        self.ui.setLayout(self.layout)

        # update timer
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_all_sensors)

        # super()
        Node.__init__(self, name, terminals=terminals)

        try:
            self.btaddr = sys.argv[1]  # set given value
            self.text.setText(self.btaddr)
            self.connect_wiimote()
        except IndexError:
            self.btaddr = "B8:AE:6E:EF:D2:D0"  # set some example
            self.text.setText(self.btaddr)

    def update_all_sensors(self):
        if self.wiimote is None:
            return
        self._acc_vals = self.wiimote.accelerometer
        # todo: other sensors...
        self.update()

    def update_accel(self, acc_vals):
        self._acc_vals = acc_vals
        self.update()

    def ctrlWidget(self):
        return self.ui

    def connect_wiimote(self):
        self.btaddr = str(self.text.text()).strip()
        if self.wiimote is not None:
            self.wiimote.disconnect()
            self.wiimote = None
            self.connect_button.setText("connect")
            return
        if len(self.btaddr) == 17:
            self.connect_button.setText("connecting...")
            self.wiimote = wiimote.connect(self.btaddr)
            if self.wiimote is None:
                self.connect_button.setText("try again")
            else:
                self.connect_button.setText("disconnect")
                self.set_update_rate(self.update_rate_input.value())

    def set_update_rate(self, rate):
        if rate == 0:  # use callbacks for max. update rate
            self.update_timer.stop()
            self.wiimote.accelerometer.register_callback(self.update_accel)
        else:
            self.wiimote.accelerometer.unregister_callback(self.update_accel)
            self.update_timer.start(1000.0 / rate)

    def process(self, **kwdargs):
        x, y, z = self._acc_vals
        return {'accelX': np.array([x]), 'accelY': np.array([y]), 'accelZ': np.array([z])}

fclib.registerNodeType(WiimoteNode, [('Sensor',)])

if __name__ == '__main__':
    import sys

    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.setWindowTitle('WiimoteNode demo')
    cw = QtGui.QWidget()
    win.setCentralWidget(cw)
    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    # Create an empty flowchart with a single input and output
    fc = Flowchart(terminals={
    })
    w = fc.widget()

    layout.addWidget(fc.widget(), 0, 0, 2, 1)

    pw1 = pg.PlotWidget()
    layout.addWidget(pw1, 0, 1)
    pw1.setYRange(0, 1024)
    pw2 = pg.PlotWidget()
    layout.addWidget(pw2, 1, 1)
    pw2.setYRange(0, 1024)
    pw3 = pg.PlotWidget()
    layout.addWidget(pw3, 2, 1)
    pw3.setYRange(0, 1024)
    pw4 = pg.PlotWidget()
    layout.addWidget(pw4, 3, 1)
    pw4.setYRange(0, 1024)
    pw5 = pg.PlotWidget()
    layout.addWidget(pw5, 4, 1)
    pw5.setYRange(-1, 1)
    pw5.setXRange(0, 2)

    pw1Node = fc.createNode('PlotWidget', pos=(0, -150))
    pw1Node.setPlot(pw1)
    pw2Node = fc.createNode('PlotWidget', pos=(0, -300))
    pw2Node.setPlot(pw2)
    pw3Node = fc.createNode('PlotWidget', pos=(0, -450))
    pw3Node.setPlot(pw3)
    pw4Node = fc.createNode('PlotWidget', pos=(0, -600))
    pw4Node.setPlot(pw4)
    pw5Node = fc.createNode('PlotWidget', pos=(0, -750))
    pw5Node.setPlot(pw5)

    wiimoteNode = fc.createNode('Wiimote', pos=(0, 0))
    bufferNodeX = fc.createNode('Buffer', pos=(150, 0))
    bufferNodeY = fc.createNode('Buffer', pos=(150, -150))
    bufferNodeZ = fc.createNode('Buffer', pos=(150, -300))
    filterNode = fc.createNode('MeanFilter', pos=(150, -450))
    normalVectorNode = fc.createNode('NormalVector', pos=(150, -300))
    curveNode = fc.createNode('PlotCurve', pos=(300, -300))

    fc.connectTerminals(wiimoteNode['accelX'], bufferNodeX['dataIn'])
    fc.connectTerminals(wiimoteNode['accelY'], bufferNodeY['dataIn'])
    fc.connectTerminals(wiimoteNode['accelZ'], bufferNodeZ['dataIn'])
    fc.connectTerminals(wiimoteNode['accelX'], normalVectorNode['xIn'])
    fc.connectTerminals(wiimoteNode['accelZ'], normalVectorNode['zIn'])
    fc.connectTerminals(normalVectorNode['xOut'], curveNode['x'])
    fc.connectTerminals(normalVectorNode['yOut'], curveNode['y'])
    fc.connectTerminals(bufferNodeX['dataOut'], filterNode['In'])
    fc.connectTerminals(bufferNodeX['dataOut'], pw1Node['In'])
    fc.connectTerminals(bufferNodeY['dataOut'], pw2Node['In'])
    fc.connectTerminals(bufferNodeZ['dataOut'], pw3Node['In'])
    fc.connectTerminals(filterNode['Out'], pw4Node['In'])
    fc.connectTerminals(curveNode['plot'], pw5Node['In'])

    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
