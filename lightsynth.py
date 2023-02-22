
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 11:08:15 2023

@author: luca
"""

import os
if os.uname()[4] == 'x86_64':
	pi = 0
else:
	pi = 1

import mido
from audiolazy import midi2freq
import numpy as np
import time

pins = [11,12,13]

if pi:
    import pigpio
    pi = pigpio.pi()
    
    print("setting up gpio")

    for pin in pins:
        pi.set_mode(pin, pigpio.OUTPUT)


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
            delreg = np.where(freqs == librosa.midi_to_hz(msg.note))[0][0]
            vels[delreg] = 0
            changes[writereg] = True
            
        print(msg)
        print(freqs)
        print(vels)
        print(starts)
        print(changes)
        
        for reg, pin in enumerate(pins):
            if changes[reg]:
                
                duty_cycle = 0.5
                frequency = freqs[reg]
                cycle_length = 1/frequency
                
                on_time = cycle_length*duty_cycle
                off_time = cycle_length*(1-duty_cycle)

                wavereg=[]
                
                #                              ON     OFF  DELAY
                wavereg.append(pigpio.pulse(1<<pin, 0, on_time*1000000))
                wavereg.append(pigpio.pulse(0, 1<<pin, off_time*1000000))
                
                
                
                changes[reg] = False
            
            else:
                
                wavereg.append(pigpio.pulse(1<<pin, 0, on_time*1000000))
                wavereg.append(pigpio.pulse(0, 1<<pin, off_time*1000000))
                
                
        pi.wave_clear() # clear any existing waveforms
        
        pi.wave_add_generic(wavereg)
        wave = pi.wave_create() # create and save id          

        pi.wave_send_repeat(wave)
        
        
        #pi.wave_tx_stop() # stop waveform
                
        #pi.wave_clear() # clear all waveforms
            
            
