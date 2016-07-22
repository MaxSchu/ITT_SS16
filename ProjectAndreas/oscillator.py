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
    # Mapping for all UI elements
    class UIElement(Enum):
        (X_AXIS, Y_AXIS, Z_AXIS, SINE, SQUARE, SAW, TRI, NOISE, PLOT, DOWNSAMPLE, STRETCH,
         ENABLED, VOLUME, STRETCH_VAL, VOLUME_VAL, SAMPLE_VAL, COPY, PASTE, OVERWRITE) = range(19)

    # Supported Waveforms - NOISE is for raw sensor data
    class Waveform(Enum):
        SINE, SQUARE, SAW, TRI, NOISE = range(5)

    # Different accelerometer axis
    class Axis(Enum):
        X, Y, Z = range(3)

    # Custom signal to update the plots from another thread
    updatePlot = pyqtSignal(object)

    def __init__(self, index, synth):
        super(self.__class__, self).__init__()
        self.ui = synth.ui
        self.updatePlot[object].connect(self.setPlot)
        self.index = index
        self.plot = None
        self.stretchRate = 0
        self.volume = 50
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
        """Setup all UI elements for the specific oscillator"""
        ui = self.ui

        # Dictionary is filled with the corresponding UI elements
        if self.index == 0:
            self.uiElements = {self.UIElement.X_AXIS: ui.x_radio_1, self.UIElement.Y_AXIS: ui.y_radio_1,
                               self.UIElement.Z_AXIS: ui.z_radio_1, self.UIElement.SINE: ui.sine_radio_1,
                               self.UIElement.TRI: ui.tri_radio_1, self.UIElement.SQUARE: ui.square_radio_1,
                               self.UIElement.SAW: ui.saw_radio_1, self.UIElement.NOISE: ui.noise_radio_1,
                               self.UIElement.PLOT: ui.osc_plot_1, self.UIElement.DOWNSAMPLE: ui.downsample_1,
                               self.UIElement.STRETCH: ui.stretch_1, self.UIElement.ENABLED: ui.osc_enabled_1,
                               self.UIElement.VOLUME: ui.vol_1, self.UIElement.VOLUME_VAL: ui.vol_val_1,
                               self.UIElement.STRETCH_VAL: ui.stretch_val_1, self.UIElement.COPY: ui.copy_1,
                               self.UIElement.SAMPLE_VAL: ui.sample_val_1, self.UIElement.PASTE: ui.paste_1,
                               self.UIElement.OVERWRITE: ui.overwrite_1}
        elif self.index == 1:
            self.uiElements = {self.UIElement.X_AXIS: ui.x_radio_2, self.UIElement.Y_AXIS: ui.y_radio_2,
                               self.UIElement.Z_AXIS: ui.z_radio_2, self.UIElement.SINE: ui.sine_radio_2,
                               self.UIElement.TRI: ui.tri_radio_2, self.UIElement.SQUARE: ui.square_radio_2,
                               self.UIElement.SAW: ui.saw_radio_2, self.UIElement.NOISE: ui.noise_radio_2,
                               self.UIElement.PLOT: ui.osc_plot_2, self.UIElement.DOWNSAMPLE: ui.downsample_2,
                               self.UIElement.STRETCH: ui.stretch_2, self.UIElement.ENABLED: ui.osc_enabled_2,
                               self.UIElement.VOLUME: ui.vol_2, self.UIElement.VOLUME_VAL: ui.vol_val_2,
                               self.UIElement.STRETCH_VAL: ui.stretch_val_2, self.UIElement.COPY: ui.copy_2,
                               self.UIElement.SAMPLE_VAL: ui.sample_val_2, self.UIElement.PASTE: ui.paste_2,
                               self.UIElement.OVERWRITE: ui.overwrite_2}
        elif self.index == 2:
            self.uiElements = {self.UIElement.X_AXIS: ui.x_radio_3, self.UIElement.Y_AXIS: ui.y_radio_3,
                               self.UIElement.Z_AXIS: ui.z_radio_3, self.UIElement.SINE: ui.sine_radio_3,
                               self.UIElement.TRI: ui.tri_radio_3, self.UIElement.SQUARE: ui.square_radio_3,
                               self.UIElement.SAW: ui.saw_radio_3, self.UIElement.NOISE: ui.noise_radio_3,
                               self.UIElement.PLOT: ui.osc_plot_3, self.UIElement.DOWNSAMPLE: ui.downsample_3,
                               self.UIElement.STRETCH: ui.stretch_3, self.UIElement.ENABLED: ui.osc_enabled_3,
                               self.UIElement.VOLUME: ui.vol_3, self.UIElement.VOLUME_VAL: ui.vol_val_3,
                               self.UIElement.STRETCH_VAL: ui.stretch_val_3, self.UIElement.COPY: ui.copy_3,
                               self.UIElement.SAMPLE_VAL: ui.sample_val_3, self.UIElement.PASTE: ui.paste_3,
                               self.UIElement.OVERWRITE: ui.overwrite_3}

        self.setDefaultValues()
        self.setPlot(np.zeros(100))
        self.setupButtonSignals()

    def shouldOverWrite(self):
        """Check if oscillator data should be overwritten"""
        return self.uiElements[self.UIElement.OVERWRITE].isChecked()

    def setupButtonSignals(self):
        # Set accelerator axis
        self.uiElements[self.UIElement.X_AXIS].clicked.connect(
            lambda ignore, x=self.Axis.X: self.setAxis(x))
        self.uiElements[self.UIElement.Y_AXIS].clicked.connect(
            lambda ignore, x=self.Axis.Y: self.setAxis(x))
        self.uiElements[self.UIElement.Z_AXIS].clicked.connect(
            lambda ignore, x=self.Axis.Z: self.setAxis(x))

        # Set waveform
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

        # Set sliders
        self.uiElements[self.UIElement.DOWNSAMPLE].valueChanged[
            int].connect(self.downsample)
        self.uiElements[self.UIElement.STRETCH].valueChanged[
            int].connect(self.stretch)
        self.uiElements[self.UIElement.VOLUME].valueChanged[
            int].connect(self.changeVolume)

        # Copy/paste
        self.uiElements[self.UIElement.COPY].clicked.connect(self.copyOsc)
        self.uiElements[self.UIElement.PASTE].clicked.connect(self.pasteOsc)

        self.ui.smoothing.clicked.connect(self.createWaveform)

    def copyOsc(self):
        """Create copy of oscillator object"""
        self.synth.copiedOsc = self

    def pasteOsc(self):
        """Set values of copied oscillator to current object"""
        if self.synth.copiedOsc is None:
            return
        osc = self.synth.copiedOsc
        self.downsample(osc.dsRate)
        self.stretch(osc.stretchRate)

    def downsample(self, rate):
        """Down/Up-sampling of current data"""
        self.dsRate = rate
        sliderPos = self.uiElements[self.UIElement.DOWNSAMPLE].sliderPosition
        if sliderPos != rate:
            self.uiElements[self.UIElement.DOWNSAMPLE].setSliderPosition(rate)
        # Update UI
        self.uiElements[self.UIElement.SAMPLE_VAL].setText(str(rate))
        self.createWaveform()

    def stretch(self, rate):
        """Stretch current data"""
        self.stretchRate = rate
        sliderPos = self.uiElements[self.UIElement.STRETCH].sliderPosition
        if sliderPos != rate:
            self.uiElements[self.UIElement.STRETCH].setSliderPosition(rate)
        # Update UI
        self.uiElements[self.UIElement.STRETCH_VAL].setText(str(rate))
        self.createWaveform()

    def changeVolume(self, rate):
        """Change volume of current oscillator signal"""
        self.volume = rate
        self.uiElements[self.UIElement.VOLUME_VAL].setText(str(rate))

    def setDefaultValues(self):
        """Set default values from UI"""

        # Set default axis
        if self.uiElements[self.UIElement.X_AXIS].isChecked():
            self.setAxis(self.Axis.X)
        elif self.uiElements[self.UIElement.Y_AXIS].isChecked():
            self.setAxis(self.Axis.Y)
        elif self.uiElements[self.UIElement.Z_AXIS].isChecked():
            self.setAxis(self.Axis.Z)

        # Set default waveform
        if self.uiElements[self.UIElement.SINE].isChecked():
            self.setWaveform(self.Waveform.SINE)
        elif self.uiElements[self.UIElement.SQUARE].isChecked():
            self.setWaveform(self.Waveform.SQUARE)
        elif self.uiElements[self.UIElement.SAW].isChecked():
            self.setWaveform(self.Waveform.SAW)
        elif self.uiElements[self.UIElement.NOISE].isChecked():
            self.setWaveform(self.Waveform.NOISE)

    def setData(self, data):
        """Set raw data from recording and update plot"""
        self.rawData = data
        self.createWaveform()

    def calculateMaxFFT(self, values):
        """Returns the maximum occuring frequency from a set of
        samples"""
        if len(self.rawData) == 0 or len(values) == 0:
            return

        # Calculate FFT
        data = np.absolute(np.fft.fft(values))
        data[0] = 0

        # Only look at first half of the FFT (because it is mirrored)
        try:
            data = np.split(data, 2)[0]
        except ValueError:
            # Add another sample if number of samples is uneven
            data = np.split(np.append(data, [0]), 2)[0]
        # Retrieve and return the peak frequency
        peakFrequency = np.where(data == np.amax(data))[0]
        return peakFrequency

    def getCurrentWave(self):
        """Returns current data multiplied by selected volume"""
        if len(self.rawData) == 0:
            return [0]
        return (self.volume / 100) * self.currentWave

    def createWaveform(self):
        """Create the selected waveform out of oscillator's raw data"""
        if len(self.rawData) == 0:
            return

        # Check if smoothing is enabled
        if self.ui.smoothing.isChecked():
            # Calculate appropriate data for filter
            window = self.synth.sampleRate / 5
            if window % 2 != 1:
                window = window + 1
            # Apply filter
            self.computedData = signal.savgol_filter(
                np.asarray(self.rawData), window, 2)
        else:
            # Continue with raw data if disabled
            self.computedData = self.rawData

        # Get frequency to use for waveforms
        frequency = self.calculateMaxFFT(self.computedData)
        # Get current sample rate
        fs = self.synth.sampleRate
        # Calculate duration
        duration = len(self.rawData) / self.synth.sampleRate
        f = frequency[0]

        # Create selected waveform and apply streching and down-/upsampling:
        # Create sine wave
        if self.currentWaveform == self.Waveform.SINE:
            duration = duration * (self.stretchRate + 1)
            wave = (np.sin(2 * np.pi * np.arange(fs * duration) *
                           f / fs)).astype(np.float32)
            wave = self.downsampleWave(wave)

        # Create sawtooth wave
        elif self.currentWaveform == self.Waveform.SAW:
            duration = duration * (self.stretchRate + 1)
            wave = (signal.sawtooth(2 * np.pi * np.arange(fs * duration) *
                                    f / fs)).astype(np.float32)
            wave = self.downsampleWave(wave)

        # Create square wave
        elif self.currentWaveform == self.Waveform.SQUARE:
            duration = duration * (self.stretchRate + 1)
            wave = (signal.square(2 * np.pi * np.arange(fs * duration) *
                                  f / fs)).astype(np.float32)
            wave = self.downsampleWave(wave)

        # Create triangular wave
        elif self.currentWaveform == self.Waveform.TRI:
            duration = duration * (self.stretchRate + 1)
            wave = (signal.sawtooth(2 * np.pi * np.arange(fs * duration) *
                                    f / fs, 0.5)).astype(np.float32)
            wave = self.downsampleWave(wave)

        # Apply stretching and down-/upsampling to raw values (noise)
        else:
            wave = self.downsampleWave(np.asarray(self.computedData))
            wave = self.stretchWave(wave)

        self.currentWave = wave
        # Update the plot in the UI
        self.updatePlot.emit(wave)

    def downsampleWave(self, wave):
        """Applies down-/upsampling to wave"""
        if self.dsRate == 0:
            return wave
        if self.dsRate > 0:
            # Downsampling -> remove samples
            return signal.decimate(wave, self.dsRate + 1)
        if self.dsRate < 0:
            # Upsampling -> add samples
            return wave.repeat(abs(self.dsRate) + 1)

    def stretchWave(self, wave):
        """Applies streching to wave"""
        originalWave = wave
        for i in range(0, self.stretchRate):
            wave = np.append(wave, originalWave)
        return wave

    def isEnabled(self):
        """Check if current oscillator is enabled"""
        return self.uiElements[self.UIElement.ENABLED].isChecked()

    def setPlot(self, data):
        """Update the plot for the current oscillator in the UI"""
        figure = Figure()
        if self.plot is None:
            # Add a subplot with appropriate default values to placeholder
            # UI element if it is initiated for the first time
            self.plot = figure.add_subplot(111)
            self.plot.set_ylim([-1, 1])
            self.canvas = FigureCanvas(figure)
            self.uiElements[self.UIElement.PLOT].addWidget(self.canvas)
        else:
            # Clear the plot if it already exists
            self.plot.clear()

        # Draw the plot
        self.plot.plot(np.asarray(data))
        self.canvas.draw()

    def setAxis(self, axis):
        """Sets the current axis"""
        self.currentAxis = axis

    def setWaveform(self, waveform):
        """Sets the current waveform"""
        self.currentWaveform = waveform
        self.createWaveform()

    def getAxis(self):
        """Returns ID for selected axis"""
        if self.currentAxis == self.Axis.X:
            return 0
        elif self.currentAxis == self.Axis.Y:
            return 1
        elif self.currentAxis == self.Axis.Z:
            return 2
