import matplotlib.pyplot as plt
import numpy as np

fs = 44100
t = np.arange(-0.002, .002, 1.0 / fs)
f0 = 1000
phi = np.pi / 2
A = .8
x = A * np.sin(2 * np.pi * f0 * t + phi)
plt.plot(t, x)
plt.axis([-0.002, .002, -.8, .8])
plt.xlabel('time')
plt.ylabel('amplitude')
plt.show()