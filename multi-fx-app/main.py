import argparse
import pyaudio
import numpy as np
import psutil, os
import platform
import signal
import sys
import wave

from effects import clean_effect, distortion_effect, DelayEffect, ChorusEffect

if platform.system() == "Windows":
    psutil.Process(os.getpid()).nice(psutil.HIGH_PRIORITY_CLASS)

# Constants
CHUNK = 1024
RATE = 44100
LEN = 50

# Recording setup: capture the dry (unprocessed) input and the wet
# (post-effect) output so they can be played back and compared.
RECORDINGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordings")
os.makedirs(RECORDINGS_DIR, exist_ok=True)

def open_wav(name):
    wav_file = wave.open(os.path.join(RECORDINGS_DIR, name), "wb")
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)  # 16-bit PCM
    wav_file.setframerate(RATE)
    return wav_file

dry_wav = open_wav("dry_latest.wav")
wet_wav = open_wav("wet_latest.wav")

parser = argparse.ArgumentParser()
# Distortion
parser.add_argument("--volume", type=int, default=0)
parser.add_argument("--gain", type=int, default=0)
parser.add_argument("--wetDry", type=int, default=0)
parser.add_argument("--enableDistortion", type=str, default="false")

# Chorus
parser.add_argument("--chorusLevel", type=int, default=0)
parser.add_argument("--chorusRate", type=int, default=0)
parser.add_argument("--chorusDepth", type=int, default=0)
parser.add_argument("--enableChorus", type=str, default="false")

# Delay
parser.add_argument("--delayLevel", type=int, default=0)
parser.add_argument("--feedback", type=int, default=0)
parser.add_argument("--delay", type=int, default=0)
parser.add_argument("--enableDelay", type=str, default="false")

args = parser.parse_args()

use_distortion = args.enableDistortion.lower() == "true"
use_chorus = args.enableChorus.lower() == "true"
use_delay = args.enableDelay.lower() == "true"

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open input and output streams
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
player = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, output=True, frames_per_buffer=CHUNK)

def cleanup(*_args):
    # Make sure the WAV recordings are finalized and audio streams are
    # released even when the backend stops us early with SIGTERM.
    for stream_obj in (stream, player):
        try:
            stream_obj.stop_stream()
            stream_obj.close()
        except Exception:
            pass
    try:
        p.terminate()
    except Exception:
        pass
    for wav_file in (dry_wav, wet_wav):
        try:
            wav_file.close()
        except Exception:
            pass
    sys.exit(0)

signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

# Determine which effect to run based on the flags passed in from the UI
if use_distortion:
    currentEffect = 'distortion'
elif use_chorus:
    currentEffect = 'chorus'
elif use_delay:
    currentEffect = 'delay'
else:
    currentEffect = 'clean'

delay_fx = DelayEffect(rate=RATE)
chorus_fx = ChorusEffect(rate=RATE)

# Main loop for audio processing
for i in range(int(LEN * RATE / CHUNK)):  # Go for LEN seconds
    # Read data from input stream
    raw_bytes = stream.read(CHUNK, exception_on_overflow=False)
    data = np.frombuffer(raw_bytes, dtype=np.int16)
    dry_wav.writeframes(raw_bytes)

    # Apply the selected effect
    if currentEffect == 'distortion':
        output_data = distortion_effect(data, args.volume, args.gain, args.wetDry)
    elif currentEffect == 'chorus':
        output_data = chorus_fx.process(data, args.chorusLevel, args.chorusRate, args.chorusDepth)
    elif currentEffect == 'delay':
        output_data = delay_fx.process(data, args.delayLevel, args.feedback, args.delay)
    else:
        output_data = clean_effect(data)

    # Write the processed audio data to the output stream and to the wet recording
    player.write(output_data.tobytes(), CHUNK)
    wet_wav.writeframes(output_data.tobytes())

# Clean up and close streams, finalizing both recordings
cleanup()
