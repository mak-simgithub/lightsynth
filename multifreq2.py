#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 15:28:40 2023

@author: luca
"""

import pigpio
import numpy as np
import os
import atexit

if os.uname()[4] == 'x86_64':
    pi_here = 0
    print("not running on a raspberry pi, only demo mode")
else:
    pi_here = 1
    print("potentially running on a raspi, let's hope so")

if pi_here:
    pi = pigpio.pi()

@atexit.register
def say_goodbye():
    print("exiting now, goodbye")
    pi.wave_tx_stop()

    pi.wave_clear()

    pi.write(pins[0],0)
    pi.write(pins[1],0)
    pi.write(pins[2],0)
    

freqs = np.array([130.81, 64.81, 196])*2

bpm = 90

steps = 1000000


duty = 0.5


cycles = np.array([int(steps/freq) for freq in freqs])

overall_cycle = int(steps*60/bpm)

events = {}
for i, cycle in enumerate(cycles):
    for j in list(range(0, overall_cycle, cycle)):
        if j not in events:
            events[j] = [i+1]
        else:
            events[j].append(i+1)
        
        k = j + int(cycle*duty)  
        if k not in events:
            events[k] = [-(i+1)]
        else:
            events[k].append(-(i+1))
        
pins=[2,3,4]
zero = 5                

if pi_here:
    for pin in pins:
        pi.set_mode(pin, pigpio.OUTPUT)
    
    pi.set_mode(zero, pigpio.OUTPUT)

waveforms = []

last_event = 0

events_sorted = dict(sorted(events.items()))

for step, values in events_sorted.items():
    for val in values:
        pin = abs(value-1)
        event = value>0
        delay = step - last_event
        print(f"pin {pin} going {event} for {delay}")
        if event:
            waveforms.append(pigpio.pulse(1<<pin, 1<<zero, delay))
        else:
            waveforms.append(pigpio.pulse(1<<zero, 1<<pin, delay))
        last_event = step

pi.wave_clear()
pi.wave_add_generic(waveforms)
waveforms_id = pi.wave_create()

pi.wave_send_repeat(waveforms_id)
print("starting wave")

while True:
	pass
