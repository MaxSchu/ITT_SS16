from enum import Enum
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy import signal
from PyQt5.QtCore import pyqtSignal, QObject


class Oscillator(QObject):
    class UIElement(Enum):
        X_AXIS, Y_AXIS, Z_AXIS, SINE, SQUARE, SAW, TRI, NOISE, PLOT, DOWNSAMPLE, STRETCH, ENABLED = range(
            12)

    class Waveform(Enum):
        SINE, SQUARE, SAW, TRI, NOISE = range(5)

    class Axis(Enum):
        X, Y, Z = range(3)

    updatePlot = pyqtSignal(object)

    def __init__(self, index, synth):
        super(self.__class__, self).__init__()
        self.ui = synth.ui
        self.updatePlot[object].connect(self.setPlot)
        self.index = index
        self.plot = None
        self.stretchRate = 0
        self.synth = synth
        self.dsRate = 0
        self.currentWave = None
        self.rawData = {}
        self.processedData = {}
        self.currentAxis = None
        self.currentWaveform = None
        self.uiElements = None
        self.setupControls()

    def setupControls(self):
        ui = self.ui

        if self.index == 0:
            self.uiElements = {self.UIElement.X_AXIS: ui.x_radio_1, self.UIElement.Y_AXIS: ui.y_radio_1,
                               self.UIElement.Z_AXIS: ui.z_radio_1, self.UIElement.SINE: ui.sine_radio_1,
                               self.UIElement.TRI: ui.tri_radio_1, self.UIElement.SQUARE: ui.square_radio_1,
                               self.UIElement.SAW: ui.saw_radio_1, self.UIElement.NOISE: ui.noise_radio_1,
                               self.UIElement.PLOT: ui.osc_plot_1, self.UIElement.DOWNSAMPLE: ui.downsample_1,
                               self.UIElement.STRETCH: ui.stretch_1, self.UIElement.ENABLED: ui.osc_enabled_1}
        elif self.index == 1:
            self.uiElements = {self.UIElement.X_AXIS: ui.x_radio_2, self.UIElement.Y_AXIS: ui.y_radio_2,
                               self.UIElement.Z_AXIS: ui.z_radio_2, self.UIElement.SINE: ui.sine_radio_2,
                               self.UIElement.TRI: ui.tri_radio_2, self.UIElement.SQUARE: ui.square_radio_2,
                               self.UIElement.SAW: ui.saw_radio_2, self.UIElement.NOISE: ui.noise_radio_2,
                               self.UIElement.PLOT: ui.osc_plot_2, self.UIElement.DOWNSAMPLE: ui.downsample_2,
                               self.UIElement.STRETCH: ui.stretch_2, self.UIElement.ENABLED: ui.osc_enabled_2}
        elif self.index == 2:
            self.uiElements = {self.UIElement.X_AXIS: ui.x_radio_3, self.UIElement.Y_AXIS: ui.y_radio_3,
                               self.UIElement.Z_AXIS: ui.z_radio_3, self.UIElement.SINE: ui.sine_radio_3,
                               self.UIElement.TRI: ui.tri_radio_3, self.UIElement.SQUARE: ui.square_radio_3,
                               self.UIElement.SAW: ui.saw_radio_3, self.UIElement.NOISE: ui.noise_radio_3,
                               self.UIElement.PLOT: ui.osc_plot_3, self.UIElement.DOWNSAMPLE: ui.downsample_3,
                               self.UIElement.STRETCH: ui.stretch_3, self.UIElement.ENABLED: ui.osc_enabled_3}

        self.setDefaultValues()
        self.setPlot(np.zeros(100))
        self.setupButtonSignals()

    def setupButtonSignals(self):
        # set accelerator axis
        self.uiElements[self.UIElement.X_AXIS].clicked.connect(
            lambda ignore, x=self.Axis.X: self.setAxis(x))
        self.uiElements[self.UIElement.Y_AXIS].clicked.connect(
            lambda ignore, x=self.Axis.Y: self.setAxis(x))
        self.uiElements[self.UIElement.Z_AXIS].clicked.connect(
            lambda ignore, x=self.Axis.Z: self.setAxis(x))

        # set waveform
        self.uiElements[self.UIElement.SINE].clicked.connect(
            lambda ignore, x=self.Waveform.SINE: self.setWaveform(x))
        self.uiElements[self.UIElement.TRI].clicked.connect(
            lambda ignore, x=self.Waveform.TRI: self.setWaveform(x))
        self.uiElements[self.UIElement.SQUARE].clicked.connect(
            lambda ignore, x=self.Waveform.SQUARE: self.setWaveform(x))
        self.uiElements[self.UIElement.SAW].clicked.connect(
            lambda ignore, x=self.Waveform.SAW: self.setWaveform(x))
        self.uiElements[self.UIElement.NOISE].clicked.connect(
            lambda ignore, x=self.Waveform.NOISE: self.setWaveform(x))

        # set sliders
        self.uiElements[self.UIElement.DOWNSAMPLE].valueChanged[
            int].connect(self.downsample)
        self.uiElements[self.UIElement.STRETCH].valueChanged[
            int].connect(self.stretch)

        self.ui.smoothing.clicked.connect(self.createWaveform)

    def downsample(self, rate):
        self.dsRate = rate
        self.createWaveform()

    def stretch(self, rate):
        self.stretchRate = rate
        self.createWaveform()

    def setDefaultValues(self):
        if self.uiElements[self.UIElement.X_AXIS].isChecked():
            self.setAxis(self.Axis.X)
        elif self.uiElements[self.UIElement.Y_AXIS].isChecked():
            self.setAxis(self.Axis.Y)
        elif self.uiElements[self.UIElement.Z_AXIS].isChecked():
            self.setAxis(self.Axis.Z)

        if self.uiElements[self.UIElement.SINE].isChecked():
            self.setWaveform(self.Waveform.SINE)
        elif self.uiElements[self.UIElement.SQUARE].isChecked():
            self.setWaveform(self.Waveform.SQUARE)
        elif self.uiElements[self.UIElement.SAW].isChecked():
            self.setWaveform(self.Waveform.SAW)
        elif self.uiElements[self.UIElement.NOISE].isChecked():
            self.setWaveform(self.Waveform.NOISE)

    def setData(self, data):
        self.rawData = data
        self.createWaveform()

    def calculateMaxFFT(self, values):
        if len(self.rawData) == 0 or len(values) == 0:
            return

        data = np.absolute(np.fft.fft(values))
        data[0] = 0
        try:
            data = np.split(data, 2)[0]
        except ValueError:
            data = np.split(np.append(data, [0]), 2)[0]
        peakFrequency = np.where(data == np.amax(data))[0]
        return peakFrequency

    def createWaveform(self):
        if len(self.rawData) == 0:
            return

        if self.ui.smoothing.isChecked():
            window = self.synth.sampleRate / 5
            if window % 2 != 1:
                window = window + 1

            self.computedData = signal.savgol_filter(
                np.asarray(self.rawData), window, 2)
        else:
            self.computedData = self.rawData

        frequency = self.calculateMaxFFT(self.computedData)
        fs = self.synth.sampleRate
        duration = len(self.rawData) / self.synth.sampleRate
        f = frequency[0]

        if self.currentWaveform == self.Waveform.SINE:
            duration = duration * (self.stretchRate + 1)
            wave = (np.sin(2 * np.pi * np.arange(fs * duration) *
                           f / fs)).astype(np.float32)
            wave = self.downsampleWave(wave)

        elif self.currentWaveform == self.Waveform.SAW:
            duration = duration * (self.stretchRate + 1)
            wave = (signal.sawtooth(2 * np.pi * np.arange(fs * duration) *
                                    f / fs)).astype(np.float32)
            wave = self.downsampleWave(wave)

        elif self.currentWaveform == self.Waveform.SQUARE:
            duration = duration * (self.stretchRate + 1)
            wave = (signal.square(2 * np.pi * np.arange(fs * duration) *
                                  f / fs)).astype(np.float32)
            wave = self.downsampleWave(wave)

        elif self.currentWaveform == self.Waveform.TRI:
            duration = duration * (self.stretchRate + 1)
            wave = (signal.sawtooth(2 * np.pi * np.arange(fs * duration) *
                                    f / fs, 0.5)).astype(np.float32)
            wave = self.downsampleWave(wave)

        else:
            wave = self.downsampleWave(np.asarray(self.computedData))
            wave = self.stretchWave(wave)

        self.currentWave = wave
        self.updatePlot.emit(wave)

    def downsampleWave(self, wave):
        if self.dsRate > 0:
            return signal.decimate(wave, self.dsRate)
        else:
            return wave

    def stretchWave(self, wave):
        originalWave = wave
        for i in range(0, self.stretchRate):
            wave = np.append(wave, originalWave)
        return wave

    def isEnabled(self):
        return self.uiElements[self.UIElement.ENABLED].isChecked()

    def setPlot(self, data):
        figure = Figure()
        if self.plot is None:
            self.plot = figure.add_subplot(111)
            self.plot.set_ylim([-1, 1])
            self.canvas = FigureCanvas(figure)
            self.uiElements[self.UIElement.PLOT].addWidget(self.canvas)
        else:
            self.plot.clear()
        self.plot.plot(np.asarray(data))
        self.canvas.draw()

    def setAxis(self, axis):
        self.currentAxis = axis

    def setWaveform(self, waveform):
        self.currentWaveform = waveform
        self.createWaveform()

    def getAxis(self):
        if self.currentAxis == self.Axis.X:
            return 0
        elif self.currentAxis == self.Axis.Y:
            return 1
        elif self.currentAxis == self.Axis.Z:
            return 2
