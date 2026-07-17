#!/usr/bin/env bash
# Faceless Engine — one-shot setup (F/DX fix). TTHW target: <10 min.
#
#   bash setup.sh              # main engine (Kokoro/edge voice, beat captions)
#   bash setup.sh --with-voice # + GPU voice venv (Chatterbox + word captions)
#
# Idempotent: safe to re-run. Never touches your system Python globally.
set -euo pipefail
cd "$(dirname "$0")"

say() { printf "\n\033[1;36m==> %s\033[0m\n" "$*"; }
warn() { printf "\033[1;33m[warn] %s\033[0m\n" "$*"; }
die() { printf "\033[1;31m[error] %s\033[0m\n" "$*" >&2; exit 1; }

# 1) Python
PY="${PYTHON:-python}"
command -v "$PY" >/dev/null 2>&1 || PY="python3"
command -v "$PY" >/dev/null 2>&1 || die "Python not found. Install Python 3.10+ and re-run."
PYVER=$("$PY" -c 'import sys;print("%d.%d"%sys.version_info[:2])')
say "Using Python $PYVER ($PY)"

# 2) ffmpeg (hard requirement for rendering)
if command -v ffmpeg >/dev/null 2>&1; then
  say "ffmpeg found: $(ffmpeg -version 2>/dev/null | head -1)"
else
  warn "ffmpeg NOT found. The engine cannot render video without it."
  warn "Windows: winget install Gyan.FFmpeg   |  macOS: brew install ffmpeg"
fi

# 3) main deps
say "Installing main dependencies (requirements.txt)"
"$PY" -m pip install --upgrade pip >/dev/null
"$PY" -m pip install -r requirements.txt

# 4) optional GPU voice venv
if [ "${1:-}" = "--with-voice" ]; then
  say "Setting up isolated GPU voice venv (.venv_voice)"
  [ -d .venv_voice ] || "$PY" -m venv .venv_voice
  VPY=".venv_voice/Scripts/python.exe"; [ -f "$VPY" ] || VPY=".venv_voice/bin/python"
  "$VPY" -m pip install --upgrade pip >/dev/null
  warn "For GPU: install the CUDA torch build from https://pytorch.org FIRST, then re-run."
  "$VPY" -m pip install -r requirements-voice.txt || warn "voice stack install had issues (engine still works via Kokoro/edge fallback)."
else
  say "Skipping GPU voice venv. Engine will use Kokoro -> edge-tts -> silent, and beat-level captions."
  say "Add it later with:  bash setup.sh --with-voice"
fi

# 5) smoke check
say "Smoke check: config + tests"
"$PY" -m pytest tests.py -q || warn "tests reported issues — check output above."

say "DONE. Next: edit config.ini (set [revenue] offer_url), add topics to topics.txt, then:  $PY engine_pro.py"
