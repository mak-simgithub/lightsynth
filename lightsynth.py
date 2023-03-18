
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


if os.uname()[4] == 'x86_64':
    pi = 0
    print("not running on a raspberry pi, only demo mode")
else:
    pi = 1
    print("potentially running on a raspi, let's hope so")


pins = [2,3,4]

if pi:
    print("setting up gpio")
    import pigpio
    
    pi = pigpio.pi()
    
    for pin in pins:
        pi.set_mode(pin, pigpio.OUTPUT)
        pi.set_pull_up_down(pin, pigpio.PUD_DOWN)
        print(f"setting pin {pin} to input with pulldown")

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
vels    = np.zeros(n_freq)
starts  = np.zeros(n_freq)
changes = np.zeros(n_freq)

print("listening")

with mido.open_input() as inport:
    for msg in inport:

        if msg.type == 'note_on':
            #note is being hit

            if np.size(np.where(vels == 0)):
                #look for empty register
                writereg = np.where(vels == 0)[0][0]
            else:
                #look for oldest register
                writereg = np.argmin(starts)
            
            print(f"writereg: {writereg}")
            freqs[writereg] = midi2freq(msg.note)
            vels[writereg] = msg.velocity
            starts[writereg] = time.time()
            changes[writereg] = True
        else:
            delreg = np.where(freqs == midi2freq(msg.note))[0][0]
            vels[delreg] = 0
            changes[writereg] = True
            
        print(msg)
        print(freqs)
        print(vels)
        print(starts)
        print(changes)
        
       
            
