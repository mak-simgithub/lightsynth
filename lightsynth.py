

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

import time


start = time.time()

if os.uname()[4] == 'x86_64':
    pi_here = 0
    print("not running on a raspberry pi, only demo mode")
else:
    pi_here = 1
    print("potentially running on a raspi, let's hope so")

end = time.time()
print(f"pi check: {end - start}s")
start = time.time()

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
divider = 8
steps = 1000000

overall_cycle = int(steps*60/bpm/divider)

duty = 0.5

print("listening")

with mido.open_input() as inport:
    for msg in inport:
        pi.wave_tx_stop()
        #pi.wave_clear()
        if msg.type == 'note_on':
            #note is being hit
            
            #look for empty register
            hit_empty = np.where(freqs == 0)
            print(f"hit empty: {hit_empty}")
            if len(hit_empty):
                #look for empty register
                writereg = hit_empty[0][0]
            else:
                #look for oldest register
                writereg = np.argmin(starts)
            
            freqs[writereg] = midi2freq(msg.note)
            starts[writereg] = time.time()
            #print(f"writing {freqs[writereg]}Hz to pin {writereg}")
            
        elif msg.type == 'note_off':
            #check if note still here
            hit_note = np.where(freqs == midi2freq(msg.note))
            if len(hit_note):
                delreg = hit_note[0][0]
                freqs[delreg] = 0
                #print(f"taking wave from pin {delreg}")
                
        #writing pulses        
        def save_div(a,b):
            if b == 0:
                return 0
            else:
                return int(a/b)

        cycles = np.array([save_div(steps,freq) for freq in freqs])


        if sum(cycles):
            
            start = time.time()
            
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
            
            end = time.time()
            print(f"constructing events: {end - start}s")
            start = time.time()
            
            waveforms = []
    
            last_event = 0
    
            events_sorted = dict(sorted(events.items()))
    
            for step, values in events_sorted.items():
                for value in values:
                    pin = abs(value)-1
                    event = value>0
                    delay = step - last_event
                    #print(f"pin {pins[pin]} going {event} for {delay} micro")
                    if event:
                        waveforms.append(pigpio.pulse(1<<pins[pin], 1<<zero, delay))
                    else:
                        waveforms.append(pigpio.pulse(1<<zero, 1<<pins[pin], delay))
                    last_event = step
                    
            end = time.time()
            print(f"waveforms: {end - start}s")
            start = time.time()
            
            if pi_here:
                pi.wave_clear()
                pi.wave_add_generic(waveforms)
                waveforms_id = pi.wave_create()
                
                end = time.time()
                print(f"wavefroms2: {end - start}s")
                start = time.time()
                
                pi.wave_send_repeat(waveforms_id)
                
                end = time.time()
                print(f"send wave: {end - start}s")
                start = time.time()
            
            else:
                pi.wave_tx_stop()
                print("no note playing")
                pi.wave_clear()
            
                pi.write(pins[0],0)
                pi.write(pins[1],0)
                pi.write(pins[2],0)
            
        

@atexit.register
def say_goodbye():
    print("exiting now, goodbye")
    if pi_here:
        pi.wave_tx_stop()
    
        pi.wave_clear()
         
        pi.write(pins[0],0)
        pi.write(pins[1],0)
        pi.write(pins[2],0)  
            
