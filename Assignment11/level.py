#!/usr/bin/env python3

import wiimote
import time
import sys


class Level(object):
    def __init__(self, wiimote):
        self._wiimote = wiimote
        self._x_axis_used = True
        self._y_axis_used = False
        self._last_rumble = time.time()
        # register callbacks
        wiimote.accelerometer.register_callback(self.acc_changed)
        wiimote.buttons.register_callback(self.button_pressed)

    # callback for accelerometer
    def acc_changed(self, acc_data):
        if len(acc_data) == 0:
            return
        # don't look at acceerometer values during rumble
        if ((time.time() - self._last_rumble) < 1.2):
            return
        if self._x_axis_used:
            axis_data = acc_data[0]
        elif self._y_axis_used:
            axis_data = acc_data[1]
        delta = 512 - int(axis_data)
        if delta >= 25:
            self._wiimote.leds = [0, 0, 0, 1]
        elif delta >= 10:
            self._wiimote.leds = [0, 0, 1, 1]
        elif delta > 0:
            self._wiimote.leds = [0, 1, 1, 1]
        elif delta <= -25:
            self._wiimote.leds = [1, 0, 0, 0]
        elif delta <= -10:
            self._wiimote.leds = [1, 1, 0, 0]
        elif delta < 0:
            self._wiimote.leds = [1, 1, 1, 0]
        else:
            # delta == 0
            self._wiimote.leds = [1, 1, 1, 1]
            self._wiimote.rumble(1)
            self._last_rumble = time.time()

    # callback for button presses
    def button_pressed(self, btns):
        if len(btns) == 0:
            return
        for btn in btns:
            if btn[1]:
                if btn[0] == "Up" or btn[0] == "Down":
                    self._x_axis_used = False
                    self._y_axis_used = True
                    print("Axis changed to Y")
                elif btn[0] == "Left" or btn[0] == "Right":
                    self._x_axis_used = True
                    self._y_axis_used = False
                    print("Axis changed to X")


if __name__ == '__main__':
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
    level = Level(wm)

    # this loop prevents the script from finishing
    # is there a better option?
    while True:
        pass
