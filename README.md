# Faceless Viral Engine — Run Notes (upgraded / engine_pro)

Top-notch, premium faceless Shorts pipeline. Built to the locked standard from
`PLAN_quality_upgrade.md`: Chatterbox voice (prosody + breaths + room tone +
-14 LUFS mastering), word-level Hormozi karaoke captions, 2.5–4s restrained
edits, licensed/attributed Wikimedia visuals, seeded per-video variation +
anti-clone fingerprint. `engine.py` is untouched (safe fallback).

## 1. One-time setup

### Python + base deps (already present)
- Main interpreter: `C:\Users\Avishkar\AppData\Local\Programs\Python\Python312\python.exe`
  (runs Kokoro + the orchestrator). ffmpeg with NVENC must be on PATH.

### Chatterbox (primary voice) — isolated venv on D:
C: is full, so the Chatterbox/CUDA venv lives on **D:\venv_voice** (isolated,
per plan Decision #6). The 2.1 GB model caches to **D:/hf_cache**.

```
D:\venv_voice\Scripts\python.exe -m pip install "torch==2.6.0+cu124" --index-url https://download.pytorch.org/whl/cu124
D:\venv_voice\Scripts\python.exe -m pip install chatterbox-tts
```
The code forces `HF_HOME=D:/hf_cache` inside the Chatterbox subprocess, so the
model never lands on the full C: drive. No action needed at runtime.

### Assets (all generated locally — no downloads, no licensing risk)
Run once:
```
python assets/generate_assets.py        # 6 .cube LUTs + 3 SFX (whoosh/riser/tick)
python assets/make_breath_roomtone.py   # breath.wav + roomtone.wav
python assets/make_music_bed.py         # original royalty-free music bed
```
Fonts: `fonts/Anton-Regular.ttf` (valid). Copy it to your Windows Fonts folder
once so ffmpeg/libass resolves "Anton" by name, OR it falls back to a default
bold (still works).

## 2. Run

Same CLI as the old engine (plan Decision #9):
```
python engine_pro.py --count 1                 # one video, random topic
python engine_pro.py --topic "your topic"       # specific topic
python engine_pro.py --count 3 --seed 7         # reproducible batch
```
Output: `publish/vid_<ts>.mp4` + `publish/vid_<ts>_attrib.txt` (CC credits).
`run_status.log` records every run (OK/FAIL + style axes).

Voice engine is chosen in `config.ini [quality] voice_engine`:
`chatterbox` (primary, GPU) or `kokoro` (fast fallback). The resilience chain is
Chatterbox-GPU → Kokoro → edge-tts → silent, so a run never dies.

## 3. Hands-off daily runs (plan: "schedule N/day")
You publish from `publish/` (human stays in the loop — never auto-post).
```
setup_scheduler.bat     # registers a Windows Task Scheduler job (run as admin once)
run_daily.bat           # produces N videos via engine_pro.py --count N
```
Edit `COUNT` in `run_daily.bat` to set videos/day.

## 4. Config quick reference (`config.ini`)
- `[quality]` voice_engine, cut_rate, captions on/off, variation_seed
- `[music]` bg_music — original bed is set; leave empty for no music
- `[visuals]` pexels_api_key — optional; without it, licensed Wikimedia stills are used
- `[output]` width/height/fps (1080x1920 / 30)

## 5. TTHW (time-to-first-video) < 5 min after the one-time setup above.

## 6. Verifying the standard
`python -m pytest tests.py -q`  → 11 tests (license filter, anti-clone,
captions, config). To eyeball a video: open the latest `publish/vid_*.mp4`.
Check: Chatterbox voice (not flat), word-by-word gold captions, restrained
cuts, different licensed image per beat, music ducked under voice, seamless loop.
