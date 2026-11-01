"""Microphone capture on the shared session clock, plus WAV replay at the pipeline rate."""
import math

import numpy as np

from cuecom.perception.audio.events import SR, SampleCapture


class SharedAudioCapture(SampleCapture):
    def __init__(self, clock, max_blocks=128):
        super().__init__(max_blocks)
        self.clock = clock
        self.anchor_s = None
        self.timestamp_basis = 'uninitialized'

    def callback(self, data, frames, time_info, status):
        if self.anchor_s is None:
            now = self.clock.now()
            try:
                adc = float(time_info.inputBufferAdcTime)
                current = float(time_info.currentTime)
                if not math.isfinite(adc + current) or adc <= 0 or current < adc or current - adc > 5:
                    raise ValueError('device clock unavailable')
                self.anchor_s = now - (current - adc)
                self.timestamp_basis = 'portaudio_adc_offset_to_session_monotonic'
            except (AttributeError, TypeError, ValueError):
                self.anchor_s = now - frames / SR
                self.timestamp_basis = 'host_callback_estimate; sensor latency uncertain'
        super().callback(data, frames, time_info, status)

    def at(self, sample_index):
        return self.anchor_s + sample_index / SR if self.clock_valid and self.anchor_s is not None else None


def read_audio(path):
    import soundfile as sf
    from scipy.signal import resample_poly
    wave, sr = sf.read(str(path), dtype='float32', always_2d=True)
    wave = wave.mean(axis=1)
    if sr != SR:
        divisor = math.gcd(sr, SR)
        wave = resample_poly(wave, SR // divisor, sr // divisor).astype(np.float32)
    if not len(wave) or not np.isfinite(wave).all():
        raise ValueError('WAV has no finite audio samples')
    return wave


def input_stream(capture, device):
    import sounddevice as sd
    return sd.InputStream(samplerate=SR, channels=1, blocksize=320, dtype='float32',
                          device=device, callback=capture.callback)
