# lightsynth

lightsynth is a project that creates sounds from a solar cell that is illuminated by a RGB LED stripe. At the heart of the lightsynth sits a Raspberry Pi Zero that reads a MIDI signal from an arbitrary source. An algorithm then converts the MID notes into the corresponding frequencies. At this step the operator can influence the still digital part of sound generation with various parameters such as PWM duty-cycle and wave cycle length. These can be locked to the BPM on the MIDI signal. As there are three light channels this synthesizer offers 3-voice polyphony, meaning that at most three notes can be played at the same time. The generated waveforms are then used to drive current through the LED. The LED will alter between the on and off state at high frequencies, mostly undetectable by the human eye. By adding resistors, capacitors or inductances to the signal path, this conversion from the digital to the analog domain can be influenced and filtered. Finally, a solar cell picks up the resulting light from the LED and surrounding and converts it to an electric signal that can be used as an audio source. Depending on how well the solar cell is isolated from the venue, the sound this instrument creates is influenced by the already existing light and therefore sounds different everywhere.


To run on a Raspberry Pi Zero project, clone repo and install dependencies:

    `sudo apt install python-dev`
    `sudo apt install libatlas-base-dev`
    `sudo apt-get install libopenblas-dev`
    `sudo apt install jackd2`
    `sudo apt install python-gpio python3-pigpio`
    `sudo apt-get install libopenjp2-7`


then set up virtaulenv with:

    `python3 -m venv virtualenv`
    `source virtualenv/bin/activate`
    `pip3 install -r requirements.txt`

then

    'python3 lightsynth.py'