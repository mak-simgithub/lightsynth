
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
starts  = np.zeros(n_freq)

bpm = 90

duty_1 = 0.5 #0 to 1
duty_2 = 0.5
duty_3 = 0.5

phase_1 = 0#-0.5 to +0.5
phase_2 = 0.5
phase_3 = -0.5

print("listening")

with mido.open_input() as inport:
    for msg in inport:
        if msg.type == 'note_on':
            #note is being hit
            
            #look for empty register
            hit_empty = np.where(freqs == 0)
            if hit_empty:
                #look for empty register
                writereg = hit_empty[0][0]
            else:
                #look for oldest register
                writereg = np.argmin(starts)
            
            freqs[writereg] = midi2freq(msg.note)
            starts[writereg] = time.time()
            print(f"writing reg{writereg} to freq {msg.note}")
            
        else:
            #check if note still here
            hit_note = np.where(freqs == midi2freq(msg.note))
            if len(hit_note):
                delreg = hit_note[0][0]
                freqs[delreg] = 0
                print(f"taking freq {msg.note} from reg {delreg}")
                
                
        #writing new freqs
        
        freq_1 = 130.81*2
        freq_2 = 164.81*2
        freq_3 = 196*2


        cycle_1 = int(1000000/freq_1)
        cycle_2 = int(1000000/freq_2)
        cycle_3 = int(1000000/freq_3)

        overall_cycle = int(1000000*60/bpm)

        init_1 = int(-phase_1+duty_1)
        init_2 = int(-phase_2+duty_2)
        init_3 = int(-phase_3+duty_3)

        first_on_1 = int(phase_1*cycle_1)+1
        first_on_2 = int(phase_2*cycle_2)+1
        first_on_3 = int(phase_3*cycle_3)+1

        ons_1 = list(range(first_on_1, overall_cycle, cycle_1))
        ons_2 = list(range(first_on_2, overall_cycle, cycle_2))
        ons_3 = list(range(first_on_3, overall_cycle, cycle_3))

        offs_1 = [on + int(cycle_1*duty_1) for on in ons_1]
        offs_2 = [on + int(cycle_2*duty_2) for on in ons_2]
        offs_3 = [on + int(cycle_3*duty_3) for on in ons_3]


        pins=[2,3,4]
        zero = 5

        events_on_1 = {on: f"on_{pins[0]}" for on in ons_1}
        events_off_1 = {off: f"off_{pins[0]}" for off in offs_1}

        events_on_2 = {on: f"on_{pins[1]}" for on in ons_2}
        events_off_2 = {off: f"off_{pins[1]}" for off in offs_2}

        events_on_3 = {on: f"on_{pins[2]}" for on in ons_3}
        events_off_3 = {off: f"off_{pins[2]}" for off in offs_3}

        events = {**events_on_1, **events_off_1, **events_on_2, **events_off_2, **events_on_3, **events_off_3}

        if pi_here:
            pi.set_mode(pins[0], pigpio.OUTPUT)
            pi.set_mode(pins[1], pigpio.OUTPUT)
            pi.set_mode(pins[2], pigpio.OUTPUT)
            pi.set_mode(zero, pigpio.OUTPUT)

        waveforms = []

        if init_1:
            waveforms.append(pigpio.pulse(1<<pins[0], 1<<zero, 0))
        else:
            waveforms.append(pigpio.pulse(1<<zero, 1<<pins[0], 0))

        if init_2:
            waveforms.append(pigpio.pulse(1<<pins[1], 1<<zero, 0))
        else:
            waveforms.append(pigpio.pulse(1<<zero, 1<<pins[1], 0))

        if init_3:
            waveforms.append(pigpio.pulse(1<<pins[2], 1<<zero, 0))
        else:
            waveforms.append(pigpio.pulse(1<<zero, 1<<pins[2], 0))

        last_event = 0

        for key, value in sorted(events.items()):
            if key > 0:
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
            
        

       
            
