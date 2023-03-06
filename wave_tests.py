#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 15:01:29 2023

@author: luca
"""

import pigpio
import time

pi = pigpio.pi()


freq_1 = 432
freq_2 = 6533
freq_3 = 65.54

bpm = 90

duty_1 = 0.5 #0 to 1
duty_2 = 0.5
duty_3 = 0.5

phase_1 = 0#-0.5 to +0.5
phase_2 = 0.5
phase_3 = -0.5

cycle_1 = int(1000000/freq_1)
cycle_2 = int(1000000/freq_2)
cycle_3 = int(1000000/freq_3)

overall_cycle = int(1000000*60/bpm)

init_1 = int(-phase_1+duty_1)
init_2 = int(-phase_2+duty_2)
inti_3 = int(-phase_3+duty_3)

first_on_1 = int(phase_1*cycle_1)+1
first_on_2 = int(phase_2*cycle_2)+1
first_on_3 = int(phase_3*cycle_3)+1

ons_1 = list(range(first_on_1, overall_cycle, cycle_1))
ons_2 = list(range(first_on_2, overall_cycle, cycle_2))
ons_3 = list(range(first_on_3, overall_cycle, cycle_3))

offs_1 = [on + int(cycle_1*duty_1) for on in ons_1]
offs_2 = [on + int(cycle_2*duty_2) for on in ons_2]
offs_3 = [on + int(cycle_3*duty_3) for on in ons_3]


pin_1 = 24
pin_2 = 12
pin_3 = 13
zero = 4

events_on_1 = {on: f"on_{pin_1}" for on in ons_1}
events_off_1 = {off: f"off_{pin_1}" for off in offs_1}

events = {**events_on_1, **events_off_1}

pi.set_mode(pin_1, pigpio.OUTPUT)
pi.set_mode(zero, pigpio.OUTPUT)

waveforms = []

if init_1:
    waveforms.append(pigpio.pulse(1<<pin_1, 1<<zero, 1))
else:
    waveforms.append(pigpio.pulse(1<<zero, 1<<pin_1, 1))

last_event = 0

for key, value in sorted(events.items()):
    pin = int(value.split("_")[1])
    event = value.split("_")[0]
    delay = key - last_event
    print(f"pin {pin} going {event} for {delay}")
    if event == "on":
        waveforms.append(pigpio.pulse(1<<pin, 1<<zero, delay))
    else:
        waveforms.append(pigpio.pulse(1<<zero, 1<<pin, delay))
    last_event = key

pi.wave_clear()
pi.wave_add_generic(waveforms)
waveforms_id = pi.wave_create()

pi.wave_send_repeat(waveforms_id)
print("starting wave")
time.sleep(5)

pi.wave_tx_stop()

pi.wave_clear()
