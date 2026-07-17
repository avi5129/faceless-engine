"""Generate breath + room-tone assets locally (no downloads, no licensing risk).

Per the locked plan (Wave 1 voice spec):
  - breaths: short inhaled/exhaled noise bursts, ~ -18 dB, spliced before ~30% of sentences
  - room tone: faint pink noise (-45 to -50 dB) under the whole track so digital
    silence doesn't scream "TTS"

Outputs (into assets/):
  assets/breath.wav      ~0.35s breath (soft inhale+exhale shape)
  assets/room_tone.wav   ~2.0s loopable pink noise, very low level
"""
from __future__ import annotations
import os
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)

SR = 44100


def _pink_noise(n: int) -> np.ndarray:
    """Voss-McCartney-ish pink noise via filtered white noise."""
    white = np.random.randn(n)
    # simple 1-pole low-pass cascade approximation of pink spectrum
    b = np.zeros(n)
    last = 0.0
    for i in range(n):
        last = 0.98 * last + white[i] * 0.02
        b[i] = last
    # normalize
    b -= b.mean()
    peak = np.max(np.abs(b)) + 1e-9
    return b / peak


def _make_breath(path, dur=0.35, level=-18.0):
    n = int(SR * dur)
    t = np.linspace(0, 1, n, endpoint=False)
    # breath = filtered noise with a soft inhale->exhale envelope
    noise = np.random.randn(n)
    # low-pass-ish: smooth
    from numpy.fft import rfft, irfft, rfftfreq
    spec = rfft(noise)
    freq = rfftfreq(n, d=1.0 / SR)
    # attenuate highs (breath is mostly low/mid)
    atten = 1.0 / (1.0 + (freq / 1800.0) ** 2)
    spec *= atten
    sig = irfft(spec, n=n)
    env = np.sin(np.pi * t) ** 1.5  # 0->1->0 shape
    sig *= env
    sig -= sig.mean()
    peak = np.max(np.abs(sig)) + 1e-9
    sig = sig / peak * (10 ** (level / 20.0)) * 0.7
    sig = np.clip(sig, -1.0, 1.0)
    _write_wav(path, sig)


def _make_room_tone(path, dur=2.0, level=-48.0):
    n = int(SR * dur)
    pink = _pink_noise(n)
    # gentle amplitude wander so it's not a static hiss
    t = np.linspace(0, 1, n)
    wander = 0.6 + 0.4 * np.sin(2 * np.pi * 0.3 * t)
    sig = pink * wander
    sig -= sig.mean()
    peak = np.max(np.abs(sig)) + 1e-9
    sig = sig / peak * (10 ** (level / 20.0))
    sig = np.clip(sig, -1.0, 1.0)
    _write_wav(path, sig)


def _write_wav(path, sig):
    import wave
    sig_int = (sig * 32767.0).astype(np.int16)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(sig_int.tobytes())
    print(f"  wrote {path} ({len(sig)/SR:.2f}s)")


if __name__ == "__main__":
    _make_breath(os.path.join(ASSETS, "breath.wav"))
    _make_room_tone(os.path.join(ASSETS, "room_tone.wav"))
    print("breath + room-tone assets generated")
