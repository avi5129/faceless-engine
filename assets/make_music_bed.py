"""Generate a royalty-free, original ambient music bed for the engine.

Synthesized (NOT sampled from any copyrighted track) so it is 100% safe for
monetization. A slow lo-fi pad loop in A minor, ~30s, designed to sit under
narration and be sidechain-ducked by edit_pro.py.

No external downloads -> no licensing risk.
"""
import os
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
MUSIC = os.path.join(ASSETS, "music")
os.makedirs(MUSIC, exist_ok=True)

OUT = os.path.join(MUSIC, "bed_ambient.wav")

# A minor pad: root A2 (110Hz) + fifth E3 (164.81) + octave A3 (220) + minor third C4 (261.63)
# via triangle/sine, gently enveloped per bar, low overall level.
# Build with aevalsrc for a soft evolving chord, then lowpass for warmth.
chord = (
    "0.18*sin(2*PI*110*t) + 0.14*sin(2*PI*164.81*t) + "
    "0.12*sin(2*PI*220*t) + 0.08*sin(2*PI*261.63*t)"
)
r = subprocess.run([
    "ffmpeg", "-y", "-f", "lavfi",
    "-i", f"aevalsrc='{chord}':s=44100:d=30",
    "-filter_complex",
    "[0:a]lowpass=f=900,highpass=f=60,"
    "alimiter=limit=0.8,volume=0.5[out]",
    "-map", "[out]", "-ar", "44100", OUT,
], capture_output=True)
print("music bed:", os.path.getsize(OUT) if os.path.exists(OUT) else "FAIL",
      "| rc", r.returncode)
