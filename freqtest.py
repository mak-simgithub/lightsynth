#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 14:43:43 2023

@author: luca
"""


import pigpio
import time

pi = pigpio.pi()

pins = [2,3,4]

zero = 5
pi.set_mode(zero, pigpio.OUTPUT)
pi.set_pull_up_down(zero, pigpio.PUD_DOWN)

for pin in pins:
    pi.set_mode(pin, pigpio.OUTPUT)
    pi.set_pull_up_down(pin, pigpio.PUD_DOWN)


freq = 2
duty = 0.2

steps = 1000000
period = int(steps/freq)

ontime = int(period*duty)
offtime = period-ontime


flash_500=[] # flash every 500 ms
flash_100=[] # flash every 100 ms
freq_wave=[]
weird=[]

#                             ON         OFF          DELAY

flash_500.append(pigpio.pulse(1<<pins[0], 1<<pins[1], 500000))
flash_500.append(pigpio.pulse(1<<pins[1], 1<<pins[0], 500000))

flash_100.append(pigpio.pulse(1<<pins[0], 1<<pins[1], 100000))
flash_100.append(pigpio.pulse(1<<pins[1], 1<<pins[0], 100000))

freq_wave.append(pigpio.pulse(1<<pins[0], 1<<zero, ontime))
freq_wave.append(pigpio.pulse(1<<zero, 1<<pins[0], offtime))

weird.append(pigpio.pulse(1<<pins[0], 1<<zero, 500000))
weird.append(pigpio.pulse(1<<pins[1], 1<<zero, 500000))
weird.append(pigpio.pulse(1<<pins[2], 1<<zero, 500000))
weird.append(pigpio.pulse(1<<pins[2], 1<<pins[0], 50000))
weird.append(pigpio.pulse(1<<pins[0], 1<<zero, 50000))
weird.append(pigpio.pulse(1<<pins[2], 1<<pins[0], 50000))
weird.append(pigpio.pulse(1<<pins[0], 1<<zero, 50000))
weird.append(pigpio.pulse(1<<pins[2], 1<<pins[0], 50000))
weird.append(pigpio.pulse(1<<pins[0], 1<<zero, 50000))
weird.append(pigpio.pulse(1<<pins[2], 1<<pins[0], 50000))
weird.append(pigpio.pulse(1<<pins[0], 1<<zero, 50000))
weird.append(pigpio.pulse(1<<pins[1], 1<<zero,0))

pi.wave_clear() # clear any existing waveforms

pi.wave_add_generic(flash_500) # 500 ms flashes
f500 = pi.wave_create() # create and save id

pi.wave_add_generic(flash_100) # 100 ms flashes
f100 = pi.wave_create() # create and save id

pi.wave_add_generic(freq_wave) # 100 ms flashes
freq_wave_id = pi.wave_create() # create and save id

pi.wave_add_generic(weird) # 100 ms flashes
weird_id = pi.wave_create() # create and save id

print("starting 500ms pulse")
pi.wave_send_repeat(f500)
time.sleep(4)
print("starting 100ms pulse")
pi.wave_send_repeat(f100)
time.sleep(4)
print(f"starting {freq}Hz, {duty}duty wave")
pi.wave_send_repeat(freq_wave_id)
time.sleep(4)
print(f"starting weird")
pi.wave_send_repeat(weird_id)
time.sleep(4)
print("ending pulses")

pi.wave_tx_stop() # stop waveform

pi.wave_clear() # clear all waveforms
