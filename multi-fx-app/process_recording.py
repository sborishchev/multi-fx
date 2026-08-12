import argparse
import os
import sys
import wave

import numpy as np

from effects import clean_effect, distortion_effect, DelayEffect, ChorusEffect

RECORDINGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordings")

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

dry_path = os.path.join(RECORDINGS_DIR, "dry_latest.wav")
if not os.path.exists(dry_path):
    print("No dry recording found. Record something first.", file=sys.stderr)
    sys.exit(1)

with wave.open(dry_path, "rb") as dry_file:
    rate = dry_file.getframerate()
    raw_bytes = dry_file.readframes(dry_file.getnframes())

data = np.frombuffer(raw_bytes, dtype=np.int16)

# Chain every chosen effect together (in a typical pedalboard order: drive
# first, then modulation, then time-based effects last), so Process
# Recording applies all effects that were chosen, not just one.
output_data = data
if use_distortion:
    output_data = distortion_effect(output_data, args.volume, args.gain, args.wetDry)
if use_chorus:
    output_data = ChorusEffect(rate=rate).process(output_data, args.chorusLevel, args.chorusRate, args.chorusDepth)
if use_delay:
    output_data = DelayEffect(rate=rate).process(output_data, args.delayLevel, args.feedback, args.delay)
if not (use_distortion or use_chorus or use_delay):
    output_data = clean_effect(output_data)

wet_path = os.path.join(RECORDINGS_DIR, "wet_latest.wav")
with wave.open(wet_path, "wb") as wet_file:
    wet_file.setnchannels(1)
    wet_file.setsampwidth(2)
    wet_file.setframerate(rate)
    wet_file.writeframes(output_data.tobytes())

print("Processed recording written to", wet_path)
