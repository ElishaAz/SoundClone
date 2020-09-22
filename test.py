import soundcard as sc
import numpy as np
import time

# get a list of all speakers:
speakers = sc.all_speakers()
# get the current default speaker on your system:
# default_speaker = sc.default_speaker()
# get a list of all microphones:
mics = sc.all_microphones()
# get the current default microphone on your system:
# default_mic = sc.default_microphone()

default_mic = sc.get_microphone("Steam Streaming Speakers", include_loopback=True)
default_speaker = sc.get_speaker("Realtek Audio")

# record and play back one second of audio:
# data = default_mic.record(samplerate=48000, numframes=48000 * 10)
# default_speaker.play(data/np.max(data), samplerate=48000)
# time.sleep(10)
# default_speaker.play(data/np.max(data) / 10, samplerate=48000)

# alternatively, get a `Recorder` and `Player` object
# and play or record continuously:
with default_mic.recorder(samplerate=48000, blocksize=1) as mic, \
        default_speaker.player(samplerate=48000, blocksize=1) as sp:
    for _ in range(1000):
        data = mic.record(numframes=1024)
        sp.play(data)
