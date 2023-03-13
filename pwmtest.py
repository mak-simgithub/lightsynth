import pigpio
import time
from audiolazy import midi2freq

pi = pigpio.pi()

duty = 0.75

for i in range(1,88):
    freq = int(midi2freq(i))
    print(f"playing {freq}")
    pi.hardware_PWM(18, freq, int(duty*1000000)) # 2000Hz 75% dutycycle
    time.sleep(1)
