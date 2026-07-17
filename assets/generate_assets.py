"""
Generate local, royalty-free assets for the Faceless Viral Engine:
  - 6 .cube LUTs (teal-orange cinematic, warm film, moody, clean-bright, desaturated-doc, vivid-gold)
  - 3 SFX wavs (reveal whoosh, number tick, soft riser)
No network needed. Run with the MAIN python (Py3.12, has numpy).

These are always-safe (no licensing risk) and live under assets/. The engine
references them; if a file is missing it degrades gracefully (graceful skip).
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LUT_DIR = os.path.join(HERE, "luts")
SFX_DIR = os.path.join(HERE, "sfx")
os.makedirs(LUT_DIR, exist_ok=True)
os.makedirs(SFX_DIR, exist_ok=True)

SIZE = 33  # 33x33x33 lattice cube (smooth, ffmpeg lut3d friendly)

# ---------- LUT generation ----------
def identity_lattice():
    # returns (33,33,33,3) float grid in [0,1]
    g = np.linspace(0.0, 1.0, SIZE)
    R, G, B = np.meshgrid(g, g, g, indexing="ij")
    return np.stack([R, G, B], axis=-1).astype(np.float64)

def write_cube(path, lattice, title):
    # lattice: (33,33,33,3) in [0,1]
    with open(path, "w") as f:
        f.write(f"TITLE \"{title}\"\n")
        f.write("LUT_3D_SIZE {}\n".format(SIZE))
        f.write("DOMAIN_MIN 0.0 0.0 0.0\n")
        f.write("DOMAIN_MAX 1.0 1.0 1.0\n")
        flat = lattice.reshape(-1, 3)
        for r, g, b in flat:
            f.write("{:.6f} {:.6f} {:.6f}\n".format(r, g, b))

def clamp(x): return np.clip(x, 0.0, 1.0)

def apply_slope(lattice, shadows, mids, highs):
    """Multiply by a per-channel piecewise curve around midtone."""
    out = lattice.copy()
    for c in range(3):
        ch = out[..., c]
        # weight: more lift in shadows, more in highs
        w_shadow = (1.0 - ch) ** 2
        w_high = ch ** 2
        w_mid = 1.0 - w_shadow - w_high
        factor = (shadows * w_shadow + mids * w_mid + highs * w_high)
        out[..., c] = clamp(ch * factor)
    return out

def teal_orange(lattice):
    # cool shadows (lift blue, lower red), warm highlights (lift red, lower blue)
    out = lattice.copy()
    r, g, b = out[..., 0], out[..., 1], out[..., 2]
    shadow = (1.0 - (r + g + b) / 3.0)  # 1 in shadows, 0 in highlights
    highlight = 1.0 - shadow
    r = r + 0.06 * highlight - 0.04 * shadow
    b = b + 0.06 * shadow - 0.04 * highlight
    g = g + 0.01 * (highlight - shadow)
    out[..., 0] = clamp(r); out[..., 1] = clamp(g); out[..., 2] = clamp(b)
    out = apply_slope(out, shadows=1.02, mids=1.0, highs=1.02)
    return out

def warm_film(lattice):
    out = lattice.copy()
    out[..., 0] = clamp(out[..., 0] * 1.06 + 0.01)
    out[..., 1] = clamp(out[..., 1] * 1.01)
    out[..., 2] = clamp(out[..., 2] * 0.94 - 0.005)
    # soft contrast
    out = apply_slope(out, shadows=0.96, mids=1.0, highs=1.06)
    return out

def moody(lattice):
    # crushed shadows, slightly desaturated, cool
    out = lattice.copy()
    lum = 0.299 * out[..., 0] + 0.587 * out[..., 1] + 0.114 * out[..., 2]
    for c in range(3):
        out[..., c] = clamp(out[..., c] + (lum - out[..., c]) * 0.18)  # desaturate
    out[..., 2] = clamp(out[..., 2] * 1.04)
    out = apply_slope(out, shadows=0.82, mids=1.0, highs=1.05)
    return out

def clean_bright(lattice):
    out = lattice.copy()
    out = apply_slope(out, shadows=1.06, mids=1.0, highs=1.02)
    out = clamp(out * 1.02 + 0.005)
    return out

def desaturated_doc(lattice):
    out = lattice.copy()
    lum = 0.299 * out[..., 0] + 0.587 * out[..., 1] + 0.114 * out[..., 2]
    for c in range(3):
        out[..., c] = clamp(out[..., c] + (lum - out[..., c]) * 0.32)
    return out

def vivid_gold(lattice):
    # warm, slightly saturated, gold-biased highlights (brand-tinted)
    out = lattice.copy()
    lum = 0.299 * out[..., 0] + 0.587 * out[..., 1] + 0.114 * out[..., 2]
    for c in range(3):
        out[..., c] = clamp(out[..., c] + (out[..., c] - lum) * 0.18)
    out = warm_film(out)
    return out

LUTS = [
    ("teal_orange.cube", teal_orange, "Cinematic teal-orange"),
    ("warm_film.cube", warm_film, "Warm film"),
    ("moody.cube", moody, "Moody desaturated"),
    ("clean_bright.cube", clean_bright, "Clean bright"),
    ("desaturated_doc.cube", desaturated_doc, "Desaturated documentary"),
    ("vivid_gold.cube", vivid_gold, "Vivid gold-warm"),
]

base = identity_lattice()
for fname, fn, title in LUTS:
    out = fn(base)
    write_cube(os.path.join(LUT_DIR, fname), out, title)
    print("wrote", os.path.join(LUT_DIR, fname))

# ---------- SFX generation ----------
SR = 44100

def write_wav(path, samples):
    samples = np.clip(samples, -1.0, 1.0)
    # 16-bit PCM wav
    import struct
    n = len(samples)
    data = b"".join(struct.pack("<h", int(s * 32767)) for s in samples)
    header = b"RIFF"
    header += struct.pack("<I", 36 + len(data))
    header += b"WAVEfmt "
    header += struct.pack("<IHHIIHH", 16, 1, 1, SR, SR * 2, 2, 16)
    header += b"data"
    header += struct.pack("<I", len(data))
    with open(path, "wb") as f:
        f.write(header + data)
    print("wrote", path)

def whoosh(dur=0.5):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    # downward filtered noise sweep (whoosh)
    noise = np.random.randn(len(t)) * 0.5
    # frequency sweep on a bandpass-ish via simple modulation
    env = np.sin(np.pi * t / dur) ** 2  # soft in/out
    sweep = np.sin(2 * np.pi * (600 + 1400 * (1 - t / dur)) * t)
    s = (0.6 * noise * np.sin(2 * np.pi * 200 * t) + 0.4 * sweep) * env
    # gentle lowpass via moving average
    kernel = np.ones(8) / 8
    s = np.convolve(s, kernel, mode="same")
    return s * 0.5

def tick(dur=0.08):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    env = np.exp(-t * 90)
    s = np.sin(2 * np.pi * 1500 * t) * env
    return s * 0.6

def riser(dur=0.6):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    env = t / dur  # swell up
    freq = 200 + 1200 * (t / dur) ** 2
    s = np.sin(2 * np.pi * freq * t) * env
    s += np.random.randn(len(t)) * 0.05 * env
    kernel = np.ones(16) / 16
    s = np.convolve(s, kernel, mode="same")
    return s * 0.35

write_wav(os.path.join(SFX_DIR, "reveal_whoosh.wav"), whoosh())
write_wav(os.path.join(SFX_DIR, "number_tick.wav"), tick())
write_wav(os.path.join(SFX_DIR, "soft_riser.wav"), riser())

print("\nDONE. LUTs:", len(LUTS), "SFX: 3")
