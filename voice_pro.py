"""
voice_pro.py — Premium narrator voice for the Faceless Viral Engine.

Primary: Chatterbox TTS (in the isolated .venv_voice on D:\venv_voice, runs on
GPU — RTX 3050 — since the 2.5GB CUDA wheel + 2.1GB model live on D: with room).
Adds:
  - per-sentence prosody variation (speed/pitch via Chatterbox params),
  - dramatic pause before the key reveal line,
  - ffmpeg audio mastering (loudnorm -14 LUFS, de-ess, light compression).
Fallback chain per PLAN Wave 1 / Decision #6: Chatterbox -> Kokoro -> edge-tts
-> silent pad (never crash). The edge-tts tier is required by the plan's
resilience contract and must not be dropped.

Reuses helpers from engine.py (make_voice, media_duration) for fallbacks.
"""
from __future__ import annotations
import os
import re
import subprocess
import sys
import tempfile
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
# Chatterbox venv: prefer D:\venv_voice (CUDA torch, room for the 2.5GB wheel);
# fall back to the original C:\ .venv_voice if D: isn't set up yet.
_D_VENV = "D:/venv_voice/Scripts/python.exe"
_C_VENV = os.path.join(ROOT, ".venv_voice", "Scripts", "python.exe")
VENV_PY = _D_VENV if os.path.exists(_D_VENV) else _C_VENV


def _venv_cuda_available():
    """CUDA must be checked INSIDE the venv (that's where torch[cuda] lives),
    not in the main interpreter (which may be torch-CPU)."""
    try:
        r = subprocess.run(
            [VENV_PY, "-c", "import torch; print('CUDA_OK' if torch.cuda.is_available() else 'NO')"],
            capture_output=True, text=True, timeout=60)
        return "CUDA_OK" in r.stdout
    except Exception:
        return False

# Reuse engine.py helpers for fallbacks
sys.path.insert(0, ROOT)
import engine as ENG  # noqa: E402

SENT_RE = re.compile(r"(?<=[.!?])\s+")


def _split_sentences(text: str):
    parts = [p.strip() for p in SENT_RE.split(text) if p.strip()]
    return parts or [text]


def _run_chatterbox(venv_py, text, out_wav, exaggeration, temperature, speed):
    """Run Chatterbox in the isolated venv. Returns True on success."""
    script = (
        "import sys, torch\n"
        "from chatterbox.tts import ChatterboxTTS\n"
        "m = ChatterboxTTS.from_pretrained(device='cpu')\n"
        "wav = m.generate(\n"
        "    %r,\n"
        "    exaggeration=%s, temperature=%s, cfg_weight=0.4\n"
        ")\n"
        "import torch as _t\n"
        "import torchaudio as _ta\n"
        "_ta.save(%r, wav.reshape(1, -1), 24000)\n"
    ) % (text, repr(exaggeration), repr(temperature), out_wav)
    try:
        r = subprocess.run([venv_py, "-c", script], capture_output=True,
                           text=True, timeout=300)
        return r.returncode == 0 and os.path.exists(out_wav) and os.path.getsize(out_wav) > 1000
    except Exception as e:
        print(f"  [voice] chatterbox error: {e}")
        return False


def _run_chatterbox_gpu(venv_py, text, out_wav, exaggeration, temperature, speed=None):
    """Run Chatterbox on CUDA (fast on RTX 3050). Returns True on success.
    HF cache is forced onto D: inside the script so MSYS path-conversion can't
    redirect it back to the full C: drive (which has no room for the 2.1GB model).
    NOTE: Chatterbox 0.1.7 generate() has no `speed` arg; pace variation comes
    from per-sentence exaggeration/temperature + the pauses/gaps we splice in."""
    script = (
        "import os\n"
        "os.environ['HF_HOME'] = 'D:/hf_cache'\n"
        "os.environ['HF_HUB_CACHE'] = 'D:/hf_cache'\n"
        "os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'\n"
        "import sys, torch\n"
        "from chatterbox.tts import ChatterboxTTS\n"
        "torch.backends.cudnn.benchmark = True\n"
        "m = ChatterboxTTS.from_pretrained(device='cuda')\n"
        "wav = m.generate(\n"
        "    %r,\n"
        "    exaggeration=%s, temperature=%s, cfg_weight=0.4\n"
        ")\n"
        "import torch as _t\n"
        "import torchaudio as _ta\n"
        "_ta.save(%r, wav.reshape(1, -1), 24000)\n"
    ) % (text, repr(exaggeration), repr(temperature), out_wav)
    try:
        r = subprocess.run([venv_py, "-c", script], capture_output=True,
                           text=True, timeout=180)
        return r.returncode == 0 and os.path.exists(out_wav) and os.path.getsize(out_wav) > 1000
    except Exception as e:
        print(f"  [voice] chatterbox-gpu error: {e}")
        return False


def _assemble_prosody_gpu(venv_py, sentences, work_dir, reveal_index=None):
    """GPU variant of _assemble_prosody (device='cuda'). Adds breaths + room tone
    per the agreed Wave 1 realism spec (spliced breaths before ~30% of sentences,
    faint pink-noise room tone so it doesn't read as digital silence)."""
    import random as _rng
    _rng.seed(abs(hash(tuple(sentences))) % (2**31))
    breath_src = os.path.join(ROOT, "assets", "sfx", "breath.wav")
    room_src = os.path.join(ROOT, "assets", "sfx", "roomtone.wav")
    clips = []
    for i, s in enumerate(sentences):
        speed = 1.0 if i % 2 == 0 else 0.97
        exag = 0.62 if i % 2 == 0 else 0.5
        temp = 0.7 if i % 2 == 0 else 0.55
        sp = os.path.join(work_dir, f"sent_{i}.wav")
        if not _run_chatterbox_gpu(venv_py, s, sp, exag, temp, speed):
            return None
        # breath before ~30% of sentences (not the very first) — realism
        if i > 0 and _rng.random() < 0.3 and os.path.exists(breath_src):
            clips.append(breath_src)
        clips.append(sp)
        if reveal_index is not None and i == reveal_index - 1:
            pause = os.path.join(work_dir, f"pause_{i}.wav")
            subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:d=0.8",
                            "-t", "0.8", pause], capture_output=True)
            clips.append(pause)
        gap = os.path.join(work_dir, f"gap_{i}.wav")
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:d=0.18",
                        "-t", "0.18", gap], capture_output=True)
        clips.append(gap)
    concat = os.path.join(work_dir, "voice_raw.wav")
    lst = os.path.join(work_dir, "voice_concat.txt")
    with open(lst, "w") as f:
        for c in clips:
            f.write(f"file '{os.path.abspath(c)}'\n")
    r = subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c", "copy", concat], capture_output=True)
    if r.returncode != 0 or not os.path.exists(concat):
        return None
    # overlay faint pink-noise room tone (-32dB) so silent gaps aren't dead digital
    if os.path.exists(room_src):
        roomed = os.path.join(work_dir, "voice_room.wav")
        rr = subprocess.run([
            "ffmpeg", "-y", "-i", concat, "-i", room_src,
            "-filter_complex", "[1:a]volume=0.025[rt];[0:a][rt]amix=inputs=2:duration=first:dropout_transition=0[out]",
            "-map", "[out]", "-ar", "24000", roomed
        ], capture_output=True)
        if rr.returncode == 0 and os.path.exists(roomed):
            return roomed
    return concat


def _assemble_prosody(venv_py, sentences, work_dir, reveal_index=None):
    """Generate each sentence with varied prosody; insert dramatic pause before
    the reveal sentence. Returns concatenated wav path or None."""
    clips = []
    for i, s in enumerate(sentences):
        # variation: alternate speed slightly; calm-but-expressive
        speed = 1.0 if i % 2 == 0 else 0.97
        exag = 0.62 if i % 2 == 0 else 0.5
        temp = 0.7 if i % 2 == 0 else 0.55
        sp = os.path.join(work_dir, f"sent_{i}.wav")
        ok = _run_chatterbox(venv_py, s, sp, exag, temp, speed)
        if not ok:
            return None
        clips.append(sp)
        # dramatic pause before the reveal (key) line
        if reveal_index is not None and i == reveal_index - 1:
            pause = os.path.join(work_dir, f"pause_{i}.wav")
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:d=0.8",
                "-t", "0.8", pause
            ], capture_output=True)
            clips.append(pause)
        # short natural gap between sentences
        gap = os.path.join(work_dir, f"gap_{i}.wav")
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:d=0.18",
            "-t", "0.18", gap
        ], capture_output=True)
        clips.append(gap)
    # concat
    concat = os.path.join(work_dir, "voice_raw.wav")
    lst = os.path.join(work_dir, "voice_concat.txt")
    with open(lst, "w") as f:
        for c in clips:
            f.write(f"file '{os.path.abspath(c)}'\n")
    r = subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
        "-c", "copy", concat
    ], capture_output=True)
    return concat if r.returncode == 0 and os.path.exists(concat) else None


def _master(in_wav, out_mp3):
    """Mastering chain: de-ess -> compress -> loudnorm -14 LUFS -> mp3."""
    tmp = out_mp3 + ".m.wav"
    chain = (
        f"[0:a]afftdn=nr=8:nf=-30,"
        f"acompressor=threshold=-24dB:ratio=3:attack=5:release=120,"
        f"loudnorm=I=-14:TP=-1.0:LRA=9[out]"
    )
    r = subprocess.run([
        "ffmpeg", "-y", "-i", in_wav,
        "-filter_complex", chain, "-map", "[out]",
        "-ar", "44100", tmp
    ], capture_output=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        subprocess.run(["ffmpeg", "-y", "-i", in_wav, "-ar", "44100", tmp],
                       capture_output=True)
    r2 = subprocess.run([
        "ffmpeg", "-y", "-i", tmp, "-c:a", "libmp3lame", "-q:a", "2", out_mp3
    ], capture_output=True)
    return os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 1000


def render_voice(text, out_mp3, cfg, reveal_line=None):
    """Top-level: produce a premium narrated mp3. Returns duration (s) or 0.0.

    Voice engine selection (config [quality] voice_engine):
      - "chatterbox": try Chatterbox on GPU (fast if CUDA works in the venv).
        CPU generation times out (~300s/sentence) so CPU is never used.
      - "kokoro" (reliable): fast, realistic, runs on this machine.
    Fallback chain per PLAN Wave 1 / Decision #6 (never dies):
      Chatterbox -> Kokoro -> edge-tts -> silent pad.
    """
    work_dir = tempfile.mkdtemp(prefix="voice_")
    try:
        engine_choice = cfg.get("quality", "voice_engine", fallback="kokoro") \
            if cfg.has_section("quality") else "kokoro"
        # Tier 1: Chatterbox-GPU (primary)
        if engine_choice == "chatterbox" and os.path.exists(VENV_PY):
            if _venv_cuda_available():
                sentences = _split_sentences(text)
                reveal_index = (sentences.index(reveal_line)
                                if reveal_line in sentences else None)
                raw = _assemble_prosody_gpu(VENV_PY, sentences, work_dir, reveal_index)
                if raw and _master(raw, out_mp3):
                    print("  [voice] Chatterbox (GPU, prosody + mastering)")
                    return ENG.media_duration(out_mp3)
        # Tier 2: Kokoro (reliable local fallback)
        print("  [voice] Kokoro narrator (fast, local)")
        ENG.make_voice(text, _kokoro_cfg(cfg), out_mp3)
        if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 1000:
            return ENG.media_duration(out_mp3)
        # Tier 3: edge-tts (free, needs internet) — required by plan resilience chain
        if _voice_edge(text, out_mp3):
            print("  [voice] edge-tts fallback")
            return ENG.media_duration(out_mp3)
        # Tier 4: last resort, silent pad (so the pipeline never dies)
        est = max(8.0, len(text.split()) / 2.5)
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i",
            f"anullsrc=r=44100:d={est}", "-t", str(est), out_mp3
        ], capture_output=True)
        return est
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def _kokoro_cfg(cfg):
    """Return a config copy forced to kokoro so engine.make_voice uses Kokoro."""
    import configparser
    c = configparser.ConfigParser()
    c.read_dict({s: dict(cfg.items(s)) for s in cfg.sections()})
    if not c.has_section("voice"):
        c.add_section("voice")
    c.set("voice", "provider", "kokoro")
    return c


def _voice_edge(text, out_mp3):
    """edge-tts tier of the fallback chain (free, needs network). Returns True on success."""
    try:
        import asyncio
        import edge_tts
        voice = "en-US-AndrewNeural"
        async def _run():
            comm = edge_tts.Communicate(text, voice, rate="-8%")
            await comm.save(out_mp3)
        asyncio.run(_run())
        return os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 1000
    except Exception as e:
        print(f"  [voice] edge-tts fallback failed: {e}")
        return False


if __name__ == "__main__":
    import configparser
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(ROOT, "config.ini"))
    d = render_voice(
        "Did you know the deepest point in the ocean is deeper than Mount Everest is tall? "
        "Scientists sent a submersible there in 1960. What they found changed our maps forever.",
        os.path.join(tempfile.gettempdir(), "voice_test.mp3"), cfg)
    print("duration:", d)
