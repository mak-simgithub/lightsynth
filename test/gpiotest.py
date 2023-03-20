#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 14:17:42 2023

@author: luca
"""

import pigpio
import time

pi = pigpio.pi()

pins = [2,3,4]

for pin in pins:
    pi.set_mode(pin, pigpio.OUTPUT)
    pi.set_pull_up_down(pin, pigpio.PUD_DOWN)
  
while True:
    for pin in pins:
        pi.write(pin,1)
        time.sleep(1)
        pi.write(pin,0)