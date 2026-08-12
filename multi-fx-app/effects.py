import numpy as np

RATE = 44100
GAIN = 8.0  # Max additional gain multiplier applied by the distortion slider
SATURATION_CEILING = 26000  # Soft-clip headroom, well under int16 full scale
MAX_DELAY_SECONDS = 2  # Size of the delay ring buffer
MAX_CHORUS_MS = 50  # Size of the chorus ring buffer


def clean_effect(data):
    return data


def distortion_effect(data, volume=0, gain=0, wet_dry=0):
    # Map the 0-10 sliders onto usable ranges. Volume defaults to a sensible
    # mid-level instead of silence, and the drive amount scales from clean
    # (gain=0) up to heavily saturated (gain=10).
    gain_factor = 1.0 + (gain / 10.0) * GAIN
    wet = wet_dry / 10.0
    volume_factor = 0.3 + (volume / 10.0) * 0.7

    dry = data.astype(np.float32)
    # Soft-clip (tanh) saturation instead of a hard clip. A hard clip at a
    # low, fixed threshold made *any* signal turn into a harsh square wave
    # (perceived as static) regardless of the gain setting. tanh saturates
    # smoothly, so low gain stays mostly clean and only high gain drives
    # the signal hard into saturation.
    distorted = np.tanh(dry * gain_factor / SATURATION_CEILING) * SATURATION_CEILING
    mixed = dry * (1 - wet) + distorted * wet
    output = np.clip(mixed * volume_factor, -32768, 32767)
    return output.astype(np.int16)


class DelayEffect:
    """Feedback delay with its own ring buffer, so each instance (live run
    or offline batch run) keeps independent state."""

    def __init__(self, rate=RATE):
        self.rate = rate
        self.buffer = np.zeros(rate * MAX_DELAY_SECONDS, dtype=np.float32)
        self.write_idx = 0

    def process(self, data, level=0, feedback_amt=0, delay_amt=0):
        buf_len = len(self.buffer)
        delay_ms = 20 + delay_amt * 48  # 0-10 -> 20ms .. 500ms
        delay_samples = max(1, int(self.rate * delay_ms / 1000))
        feedback = min(0.95, feedback_amt / 10.0)
        wet = level / 10.0

        output = np.empty(len(data), dtype=np.float32)
        for i, sample in enumerate(data):
            read_idx = (self.write_idx - delay_samples) % buf_len
            delayed_sample = self.buffer[read_idx]
            in_sample = float(sample)
            output[i] = in_sample + delayed_sample * wet
            self.buffer[self.write_idx] = in_sample + delayed_sample * feedback
            self.write_idx = (self.write_idx + 1) % buf_len

        return np.clip(output, -32768, 32767).astype(np.int16)


class ChorusEffect:
    """LFO-modulated delay with its own ring buffer + phase, so each
    instance (live run or offline batch run) keeps independent state."""

    def __init__(self, rate=RATE):
        self.rate = rate
        self.buffer = np.zeros(int(rate * MAX_CHORUS_MS / 1000), dtype=np.float32)
        self.write_idx = 0
        self.phase = 0.0

    def process(self, data, level=0, rate_amt=0, depth_amt=0):
        buf_len = len(self.buffer)
        lfo_rate = 0.5 + rate_amt * 0.5  # 0-10 -> 0.5Hz .. 5.5Hz
        # Depth was previously scaled in *samples* (1-21, i.e. ~0.02-0.5ms),
        # far too small to produce an audible chorus wobble. Real chorus
        # needs a few milliseconds of modulation depth on top of a short
        # base delay, so scale both in ms and convert to samples.
        base_delay_ms = 8.0  # 0-10 -> base_delay stays fixed at 8ms
        depth_ms = depth_amt * 1.4  # 0-10 -> 0ms .. 14ms of modulation depth
        base_delay = base_delay_ms * self.rate / 1000.0
        depth_samples = depth_ms * self.rate / 1000.0
        wet = level / 10.0
        phase_inc = 2 * np.pi * lfo_rate / self.rate

        output = np.empty(len(data), dtype=np.float32)
        for i, sample in enumerate(data):
            in_sample = float(sample)
            self.buffer[self.write_idx] = in_sample

            mod = base_delay + depth_samples * (0.5 * (1 + np.sin(self.phase)))
            read_pos = (self.write_idx - mod) % buf_len
            idx0 = int(read_pos)
            frac = read_pos - idx0
            idx1 = (idx0 + 1) % buf_len
            delayed_sample = self.buffer[idx0] * (1 - frac) + self.buffer[idx1] * frac

            output[i] = in_sample * (1 - wet) + delayed_sample * wet
            self.write_idx = (self.write_idx + 1) % buf_len
            self.phase += phase_inc

        return np.clip(output, -32768, 32767).astype(np.int16)
