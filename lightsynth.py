

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 11:08:15 2023

@author: luca
"""

import os
import sys
import mido
from audiolazy import midi2freq
import numpy as np
import time

import atexit
import math

if os.uname()[4] == 'x86_64':
    pi_here = 0
    print("not running on a raspberry pi, only demo mode")
else:
    pi_here = 1
    print("potentially running on a raspi, let's hope so")


pins = [2,3,4]
zero = 5

if pi_here:
    print("setting up gpio")
    import pigpio

    pi = pigpio.pi()

    for pin in pins:
        pi.set_mode(pin, pigpio.OUTPUT)
        pi.set_pull_up_down(pin, pigpio.PUD_DOWN)
        print(f"setting pin {pin} to input with pulldown")
        
        
    pi.set_mode(zero, pigpio.OUTPUT)

def setting_pins_low(*args):
    print("exiting now, goodbye")
    if pi_here:
        pi.wave_tx_stop()

        pi.wave_clear()

        pi.write(pins[0],0)
        pi.write(pins[1],0)
        pi.write(pins[2],0)
        
atexit.register(setting_pins_low)


stream = os.popen('aconnect -l')
output = stream.read()

splits = output.split("client ")[1:]

midi_devices = {}
midi_through_id = -1

for split in splits:
    midi_id = int(split.split(":")[0])
    name = split.split(": ")[1].split(" [")[0][1:-1]
    if not (midi_id == 0 or midi_id == 128 or name == "Midi Through"):
        midi_devices[midi_id] = name
    elif name == "Midi Through":
        midi_through_id = midi_id

if len(midi_devices):
    if len(midi_devices) > 1:
        device_id = input(f"{midi_devices}\nEnter id of device you want to connet to lightsynth: ")
    else:
        print(f"{list(midi_devices.values())[0]} is only present MIDI device, connecting to it")
        device_id = list(midi_devices.keys())[0]
else:
    print("no MIDI device connected")
    sys.exit()

stream = os.popen(f"aconnect {device_id} {midi_through_id}")
output = stream.read()

n_freq = len(pins)

freqs   = np.zeros(n_freq)
starts  = np.zeros(n_freq)

bpm = 90

steps = 1000000
factor_max = 4
factor_min = 1/32

midi_knob_top = 124
midi_knob_update = 5

bpm_top = 200
bpm_low = 40

bpms = [int(40+i*(bpm_top-bpm_low)/127) for i in range(128)]

a = steps*60/bpm*factor_max
b = 1/midi_knob_top*math.log2(factor_max/factor_min)

cycles = [int(a/2**int(i*b)) for i in range(128)]
factors = [factor_max/2**int(i/midi_knob_top*math.log2(factor_max/factor_min)) for i in range(128)]

duties = [0.5+i/127*0.49 for i in range(128)]

start_midi_lfo = 12
overall_cycle = cycles[start_midi_lfo]

start_midi_duty = 64
duty = duties[start_midi_duty]

def updating_pulses():
    #writing pulses
    print("updating pulses")

    def save_div(a,b):
        if b == 0:
            return 0
        else:
            return int(a/b)

    cycles = np.array([save_div(steps,freq) for freq in freqs])

    if sum(cycles):
        events = {}
        for i, cycle in enumerate(cycles):
            if cycle:
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

        waveforms = []

        last_event = 0

        events_sorted = dict(sorted(events.items()))

        for step, values in events_sorted.items():
            for value in values:
                pin = abs(value)-1
                event = value>0
                delay = step - last_event

                if event:
                    waveforms.append(pigpio.pulse(1<<pins[pin], 1<<zero, delay))
                else:
                    waveforms.append(pigpio.pulse(1<<zero, 1<<pins[pin], delay))
                last_event = step

        if pi_here:
            pi.wave_clear()
            pi.wave_add_generic(waveforms)
            waveforms_id = pi.wave_create()

            pi.wave_send_repeat(waveforms_id)


    else:
        pi.wave_tx_stop()
        print("no note playing")
        pi.wave_clear()

        pi.write(pins[0],0)
        pi.write(pins[1],0)
        pi.write(pins[2],0)
            
if pi:
    pi.write(pins[0],1)
    pi.write(pins[1],0)
    pi.write(pins[2],1)


print("listening")

with mido.open_input() as inport:
    for msg in inport:
        pi.wave_tx_stop()
        if msg.type == 'note_on':

            #look for empty register
            hit_empty = np.where(freqs == 0)[0]

            if hit_empty.size:
                #look for empty register
                writereg = hit_empty[0]
            else:
                #look for oldest register
                writereg = np.argmin(starts)
                
            starts_modified = starts+freqs*time.time()
            writereg = np.argmin(starts_modified)
            
            
            freqs[writereg] = midi2freq(msg.note)
            starts[writereg] = time.time()
            print(f"writing {freqs[writereg]}Hz to pin {writereg}")
            
            updating_pulses()

        elif msg.type == 'note_off':

            #check if note still here
            hit_note = np.where(freqs == midi2freq(msg.note))[0]
            if hit_note.size:
                delreg = hit_note[0]
                freqs[delreg] = 0
                print(f"taking freq {midi2freq(msg.note)}Hz from pin {delreg}")
                
            updating_pulses()
            
        elif msg.type == "control_change":
            if msg.control == 1:
                if msg.value%midi_knob_update == 0:
                    duty = duties[msg.value]
                    print(f"setting duty to {duty}")
                
                    updating_pulses()
                
            elif msg.control == 2:
                if msg.value%midi_knob_update == 0:
                    overall_cycle = cycles[msg.value]
                    factor = factors[msg.value]
                    
                    if factor < 1:
                        print(f"lfo: 1/{int(1/factor)}")
                    else:
                        print(f"lfo: {int(factor)}")
                        
                    updating_pulses()
            
            elif msg.control == 3:
                bpm = bpms[msg.value]
                print(f"bpm: {bpm}")
                updating_pulses()
