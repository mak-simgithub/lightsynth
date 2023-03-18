
import pigpio
import time

pi = pigpio.pi()

pins = [2,3,4]

for pin in pins:
    pi.set_mode(pin, pigpio.OUTPUT)
    pi.set_pull_up_down(pin, pigpio.PUD_DOWN)

flash_500=[] # flash every 500 ms
flash_100=[] # flash every 100 ms

#                              ON     OFF  DELAY

flash_500.append(pigpio.pulse(1<<pins[0], 1<<pins[1], 500000))
flash_500.append(pigpio.pulse(1<<pins[1], 1<<pins[0], 1))

flash_100.append(pigpio.pulse(1<<pins[0], 1<<pins[1], 100000))
flash_100.append(pigpio.pulse(1<<pins[1], 1<<pins[0], 100000))

for i in range(100,1000,100):
    flash_500.append(pigpio.pulse(1<<pins[0], 1<<pins[1], i))


pi.wave_clear() # clear any existing waveforms

pi.wave_add_generic(flash_500) # 500 ms flashes
f500 = pi.wave_create() # create and save id

pi.wave_add_generic(flash_100) # 100 ms flashes
f100 = pi.wave_create() # create and save id

pi.wave_send_repeat(f500)
print("starting wave")
time.sleep(4)
print("ending wave")


pi.wave_tx_stop() # stop waveform

pi.wave_clear() # clear all waveforms
