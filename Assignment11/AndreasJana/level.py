#!/usr/bin/env python3

import wiimote
import time
import sys

if len(sys.argv) == 2:
    input("Press the 'sync' button on the back of your Wiimote Plus.\n" +
          "Press <return> once the Wiimote's LEDs start blinking.")
    addr = sys.argv[1]
    name = None
    print(("Connecting to %s (%s)" % (name, addr)))
    wm = wiimote.connect(addr, name)
else:
    sys.exit("Please enter your Wiimote's MAC-adress as first parameter.")
    
    

patterns = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1],[0,0,1,0],[0,1,0,0],[1,0,0,0]]
for i in range(5):
    for p in patterns:
        wm.leds = p
        time.sleep(0.05)

level = 0
axis = "X"

def print_acc(acc_data):
    global level
    x = wm.accelerometer[0]
    y = wm.accelerometer[1]
    cur_axis = 0
    neutral_pos = 512
    level_patterns = [[1,0,0,0],[1,1,0,0],[1,1,1,0],[1,1,1,1],[0,1,1,1],[0,0,1,1],[0,0,0,1]]
    if axis == "X":
        cur_axis = x
    elif axis == "Y":
        cur_axis = y
    if cur_axis == neutral_pos:
        wm.leds = level_patterns[3]
        if level == 0:
            level = 1
            print((wm.accelerometer))
            wm.rumble(0.1)
            time.sleep(1)
    elif cur_axis <= 482:
        level = 0
        wm.leds = level_patterns[0]
    elif 482< cur_axis <= 492:
        level = 0
        wm.leds = level_patterns[1]
    elif 492 < cur_axis <= 502:
        level = 0
        wm.leds = level_patterns[2]
    elif 524 <= cur_axis < 534:
        level = 0
        wm.leds = level_patterns[4]
    elif 534 <= cur_axis < 544:
        level = 0
        wm.leds = level_patterns[5]
    elif cur_axis >= 544:
        level = 0
        wm.leds = level_patterns[6]

wm.accelerometer.register_callback(print_acc)

while True:
    if wm.buttons["Left"]:
        level = 0
        axis = "X"
    elif wm.buttons["Up"]:
        level = 0
        axis = "Y"
    else:
        pass
    time.sleep(0.05)

