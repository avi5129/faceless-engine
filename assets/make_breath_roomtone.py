"""Generate breath + room-tone assets locally (no downloads, no licensing risk).

- breath.wav : a soft inhaling/exhaling noise burst (~0.4s) shaped like a breath,
  attenuated to ~-18dB feel. Used spliced before ~30% of sentences.
- roomtone.wav : 30s of faint pink-noise room tone, loopable, low level.
  Overlaid under voice so silent gaps aren't dead digital silence.
"""
import os
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "sfx")
os.makedirs(OUT, exist_ok=True)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print("FAIL", " ".join(cmd[:6]), r.stderr.decode(errors="ignore")[-300:])
    return r.returncode == 0


# breath: band-passed noise with a slow amplitude envelope (sigh-like)
breath = os.path.join(OUT, "breath.wav")
run([
    "ffmpeg", "-y", "-f", "lavfi",
    "-i", "anoisesrc=r=24000:d=0.45:color=brown:amplitude=0.9",
    "-filter_complex",
    "[0:a]highpass=f=300,lowpass=f=1800,"
    "afade=t=in:d=0.08,afade=t=out:d=0.18,volume=0.5[out]",
    "-map", "[out]", "-ar", "24000", breath,
])

# room tone: pink noise, low level, 30s, loopable
room = os.path.join(OUT, "roomtone.wav")
run([
    "ffmpeg", "-y", "-f", "lavfi",
    "-i", "anoisesrc=r=24000:d=30:color=pink:amplitude=0.5",
    "-filter_complex",
    "[0:a]lowpass=f=1200,highpass=f=80,volume=0.18[out]",
    "-map", "[out]", "-ar", "24000", room,
])

print("breath:", os.path.getsize(breath), "bytes")
print("roomtone:", os.path.getsize(room), "bytes")
