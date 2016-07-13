import pyaudio
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import wiimote
import sys
import time

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

print("connected")

data = []
repeatedData = []
currentPos = 0

while not wm.buttons["A"]:
    currentPos = currentPos + wm.accelerometer[0] - 512
    data.append(currentPos)
    time.sleep(0.005)
    pass

p = pyaudio.PyAudio()


def downsample(s, n, phase=0):
    """Decrease sampling rate by integer factor n with included offset phase.
    """
    return s[phase::n]

volume = 0.5     # range [0.0, 1.0]
fs = 44100       # sampling rate, Hz, must be integer
duration = 3.0   # in seconds, may be float
f1 = 1.0        # sine frequency, Hz, may be float
f2 = 440.0        # sine frequency, Hz, may be float

# generate samples, note conversion to float32 array
samples = (np.sin(2 * np.pi * np.arange(fs * duration) * f1 / fs)
           ).astype(np.float32)

samples2 = (signal.square(2 * np.pi * np.arange(fs * duration) * f2 / fs)
            ).astype(np.float32)

normalized = []

highestSample = max(abs(min(data)), abs(max(data)))

print("normalizing")

# Normalize
for x in range(0, len(data)):
    normalized.append((data[x] / highestSample))

plt.plot(normalized)

filtered = signal.savgol_filter(np.asarray(normalized), 51, 5)

print("repeating")

for i in range(0, 1500):
    repeatedData.extend(normalized)

print("downsampling")

data = downsample(repeatedData, 2)
data_array = np.asarray(data)

# for paFloat32 sample values must be in range [-1.0, 1.0]
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=fs,
                output=True)

print("playing")

# play. May repeat with different volume values (if done interactively)
stream.write(data_array)
# stream.write(volume * samples2)

print("done")

stream.stop_stream()
stream.close()

p.terminate()
