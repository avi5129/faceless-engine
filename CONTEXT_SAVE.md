# CONTEXT SAVE — Faceless Viral Engine
Saved: 2026-07-16 (session switch). Resume by reading this file + engine.py.

## What this is
A single-file, fully-automated FACELESS video pipeline (Python). It turns a niche
topic into a finished, publish-ready 9:16 YouTube Short (AI voice + real visuals +
retention-tuned edit + drafted title/description) and drops it into `publish/`.
You press publish. Niche locked: curiosity/discovery facts.

## Verified working (end-to-end, this session)
- `engine.py` runs start to finish on Python 3.12, produces a real .mp4 in publish/.
- Voice: Kokoro-82M (local, free, realistic) — verified, runs on GPU (torch CUDA).
- Visuals: Wikimedia Commons photos (no API key) + Ken Burns; Pexels video coded
  but key-gated; animated gradient last resort.
- Edit: ffmpeg, 1080x1920, per-beat cuts, crossfade, kinetic ASS captions, NVENC GPU encode.
- Script: `template` default (zero cost); `ollama` (local gemma4) also works now.
- Health: ruff lint 10/10 clean, 6 pytest tests pass, compiles clean.

## Key environment facts (Windows, RTX 3050 6GB)
- Engine MUST run via:
  C:\Users\Avishkar\AppData\Local\Programs\Python\Python312\python.exe engine.py
  (Hermes venv 3.11 lacks kokoro/pip; plain `python` may point there.)
- GPU crash FIXED: Ollama gemma4 hits a broken CUDA init (Ollama 0.32.0 + driver
  610.62) -> exit 0xc0000409. Fix: call ollama with env CUDA_VISIBLE_DEVICES=-1
  (forces CPU mode). GPU itself is fine (torch CUDA, NVENC, Kokoro all use it).
- NVENC: ffmpeg has h264_nvenc; engine auto-detects + uses it for the final mux.
- Wikimedia API needs a User-Agent header on BOTH the API call and the
  upload.wikimedia.org download, or you get HTTP 403.

## Files
- engine.py        — full pipeline (topic, script, voice, visuals, edit, metadata, queue)
- config.ini       — all settings (niche, script/voice/visuals providers, music, output)
- topics.txt       — static niche seed topics
- SPEC.md          — product spec (from gstack office-hours/spec)
- README.md        — run docs, GPU notes, health/CLI section
- tests.py         — 6 pytest tests (config parse, script template, ASS build, duration)
- publish/         — finished videos + .txt metadata (the review/publish queue)
- work/            — temp render files (per-run dirs cleaned after success)

## Latest produced video
publish/vid_1784207901.mp4 (template run) — real photo, Kokoro voice, ~21s,
9:16, NVENC. (vid_1784206750.mp4 was the Ollama+GPU-fix verification run.)

## CEO REVIEW (plan-ceo-review) — outcome
Business-model fork gate: user did NOT explicitly answer. Agent judgment call =
FORK A (monetize own content; matches SPEC + user's "minimal time" preference).
B = sell the engine, C = agency service. If user wants B/C, re-scope materially.

ACCEPTED next-phase scope (user had NOT said "go" yet — pending confirmation):
  P0 (blocking for earning):
    - Copyright/license filter on Wikimedia visuals (skip non-commercial CC-NC;
      capture CC-BY + auto-embed attribution in video/description).
    - Failure resilience: voice fallback (Kokoro->edge-tts), NVENC->libx264
      auto-retry, per-run status log + failure alert (no silent queue death).
  P1:
    - Windows Task Scheduler setup (true hands-off daily runs).
    - Measurement loop: pull per-video YT stats -> promote winners / drop losers
      back into topics.txt.
    - Per-video visual-source manifest (observability: which clips were real).

DEFERRED (not building now):
  - Variation engine (voice/visual/hook rotation) to dodge YT reuse suppression.
  - Multi-niche / multi-channel portfolio (Approach B in the review).
  - Fork B/C productization (only if user chooses to be a software vendor).

OPEN CONCERNS raised in review:
  1. Fork A vs B vs C not user-confirmed.
  2. Copyright/license gap = real monetization risk before wide publishing.
  3. No measurement loop yet -> "earn money reliably" still unproven.

## Run commands
  cd C:\Users\Avishkar\faceless-engine
  C:\Users\Avishkar\AppData\Local\Programs\Python\Python312\python.exe engine.py --count 1
  C:\Users\Avishkar\AppData\Local\Programs\Python\Python312\python.exe -m pytest tests.py -q
  C:\Users\Avishkar\AppData\Local\Programs\Python\Python312\python.exe -m ruff check engine.py

## To resume this topic
Read CONTEXT_SAVE.md + engine.py. The next logical build step is the P0 scope above
(copyright filter + failure resilience). Confirm Fork A with the user first.
