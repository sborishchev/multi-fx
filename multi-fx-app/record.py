import os
import signal
import sys
import wave

import pyaudio

# Constants
CHUNK = 1024
RATE = 44100
MAX_SECONDS = 120  # Safety net so a forgotten recording doesn't run forever

RECORDINGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordings")
os.makedirs(RECORDINGS_DIR, exist_ok=True)

dry_wav = wave.open(os.path.join(RECORDINGS_DIR, "dry_latest.wav"), "wb")
dry_wav.setnchannels(1)
dry_wav.setsampwidth(2)  # 16-bit PCM
dry_wav.setframerate(RATE)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)


def cleanup(*_args):
    try:
        stream.stop_stream()
        stream.close()
    except Exception:
        pass
    try:
        p.terminate()
    except Exception:
        pass
    try:
        dry_wav.close()
    except Exception:
        pass
    sys.exit(0)


signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

# Record raw mic input only (no effect, no playback) until stopped
for _ in range(int(MAX_SECONDS * RATE / CHUNK)):
    raw_bytes = stream.read(CHUNK, exception_on_overflow=False)
    dry_wav.writeframes(raw_bytes)

cleanup()
