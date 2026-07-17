"""Word-by-word Hormozi-style karaoke captions (2026 premium revision).

Turns a (word, start, end) token stream into a SubStation Alpha (.ass) file
that ffmpeg/libass can burn in. Design per DESIGN.md:
  - Display font: Anton (heavy condensed). Body line stays mixed-case.
  - ONE keyword per page highlighted GOLD (#F5C518) — not cliche yellow.
  - The CURRENT word pops (scale 0.85->1.2->1.0) with a bounce; prior words on
    the page sit just above, dimmed; ALL-CAPS only on the keyword, body mixed.
  - 2-3 words per visible page, lower-middle (66% down) of a 9:16 frame.
  - Brand constants never vary (one caption system = recognizable identity).
"""
from __future__ import annotations

import os
import random
import tempfile
from datetime import timedelta

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
# Anton is the single display face (valid + installed) for keywords/numbers.
DISPLAY_FONT = "Anton"
# Body line stays mixed-case per DESIGN.md; Roboto Bold if present, else Anton for
# cohesion (DESIGN.md prefers Roboto/Lato Bold over Arial/Inter — never bare Anton body).
import os as _os
if _os.path.exists(os.path.join(FONT_DIR, "Roboto-Bold.ttf")):
    BODY_FONT = "Roboto Bold"
elif _os.path.exists(os.path.join(FONT_DIR, "Lato-Bold.ttf")):
    BODY_FONT = "Lato Bold"
else:
    BODY_FONT = "Anton"

WHITE = "&H00FFFFFF"
BLACK = "&H00000000"
GOLD = "&H0018C5F5"      # &H is BGR -> 0xF5C518 (warm gold)
GREY = "&H00808080"


def _fmt(sec: float) -> str:
    if sec < 0:
        sec = 0.0
    td = timedelta(seconds=sec)
    h = int(td.total_seconds() // 3600)
    m = int((td.total_seconds() % 3600) // 60)
    s = td.total_seconds() % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def _cap(text: str) -> str:
    # Body stays as spoken (mixed case). Only keywords go ALL-CAPS.
    return text


def _pick_keyword(words_chunk):
    """Emphasis word in a page: longest alphabetic word, else first."""
    cands = [w for w in words_chunk if w[0].strip().isalpha()]
    if not cands:
        return words_chunk[0] if words_chunk else None
    return max(cands, key=lambda w: len(w[0]))


def build_ass(words, out_path, w=1080, h=1920, per_page=2, seed=None):
    """words: list of (text, start, end). Writes karaoke .ass to out_path.

    Layout:
      - each spoken word = its own Dialogue line, centered, pops in.
      - a 'page' of up to `per_page` words is visible together; within a page the
        keyword is GOLD + ALL-CAPS + larger, the rest white + mixed-case.
      - the previous page's keyword lingers dimmed above (ghost) for rhythm.
    """
    rng = random.Random(seed)
    cx = w // 2
    cy = int(h * 0.66)        # 66% down -> lower-middle safe area

    pages = []
    i = 0
    while i < len(words):
        chunk = words[i:i + per_page]
        kw = _pick_keyword(chunk)
        pages.append((chunk, kw))
        i += per_page

    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {w}",
        f"PlayResY: {h}",
        "WrapStyle: 2",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding",
        # Active keyword: gold, big, ALL-CAPS, pops
        f"Style: Active, {DISPLAY_FONT}, 120, {GOLD}, {BLACK}, {BLACK}, "
        f"&H00000000, 1, 0, 0, 0, 100, 100, 3, 0, 1, 7, 1, 2, 0, 0, 0, 1",
        # Spoken (other words on the page): white, mixed-case, slightly smaller
        f"Style: Spoken, {BODY_FONT}, 104, {WHITE}, {BLACK}, {BLACK}, "
        f"&H00000000, 1, 0, 0, 0, 100, 100, 2, 0, 1, 6, 1, 2, 0, 0, 0, 1",
        # Ghost (previous page keyword, dimmed, above): grey
        f"Style: Ghost, {DISPLAY_FONT}, 76, {GREY}, {BLACK}, {BLACK}, "
        f"&H00000000, 1, 0, 0, 0, 100, 100, 2, 0, 1, 4, 1, 2, 0, 0, 0, 1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, "
        "Effect, Text",
    ]

    for pi, (chunk, kw) in enumerate(pages):
        page_start = chunk[0][1]
        page_end = chunk[-1][2]
        for wi, (text, s, e) in enumerate(chunk):
            is_kw = (text == kw)
            style = "Active" if is_kw else "Spoken"
            disp = text.upper() if is_kw else _cap(text)
            dur = max(0.08, e - s)
            pop_ms = int(dur * 1000 * 0.45)
            settle_ms = 70
            esc = disp.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
            t = (f"{{\\pos({cx},{cy})\\an2\\fscx100\\fscy100"
                 f"\\t(0,{pop_ms},\\fscx120\\fscy120)"
                 f"\\t({pop_ms},{pop_ms + settle_ms},\\fscx100\\fscy100)}}")
            lines.append(
                f"Dialogue: 0,{_fmt(s)},{_fmt(e)},{style},,{cx},{cx},0,,{t}{esc}"
            )
        # ghost: last word of this page lingers dimmed just above, until next page starts
        if pi + 1 < len(pages):
            next_chunk = pages[pi + 1][0]
            ghost_text = chunk[-1][0]
            gesc = ghost_text.upper().replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
            lines.append(
                f"Dialogue: 0,{_fmt(page_end)},{_fmt(next_chunk[0][1])},Ghost,,"
                f"{cx},{cx},0,,{{\\pos({cx},{cy - 150})\\an2}}{gesc}"
            )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return out_path

def align_words_stable_ts(voice_path, venv_python, model="base.en"):
    """Use stable-ts (in the isolated voice venv) for word timings from rendered
    TTS audio. Returns list of (word, start, end). Retries once on transient
    failure (the model is cached after first run, so retries are fast).

    NOTE: we write the runner to a temp .py file and pass the voice path as a
    sys.argv argument (NOT interpolated into a string literal) — Windows paths
    contain backslashes that break Python string-literal escaping ('\\U...').
    """
    import subprocess
    import json
    import tempfile
    out_json = os.path.join(tempfile.gettempdir(), "align_words.json")
    runner = os.path.join(tempfile.gettempdir(), "stable_ts_runner.py")
    with open(runner, "w") as f:
        f.write(
            "import sys, json\n"
            "import stable_whisper\n"
            "vp, out_json, model = sys.argv[1], sys.argv[2], sys.argv[3]\n"
            "m = stable_whisper.load_model(model)\n"
            "r = m.transcribe(vp, word_timestamps=True, regroup=True, fp16=False)\n"
            "words = []\n"
            "for seg in r.segments:\n"
            "    for w in seg.words:\n"
            "        words.append({'w': w.word.strip(), 's': float(w.start), 'e': float(w.end)})\n"
            "json.dump(words, open(out_json, 'w'))\n"
        )
    last_err = None
    for _ in range(2):
        try:
            r = subprocess.run(
                [venv_python, runner, voice_path, out_json, model],
                capture_output=True, text=True, timeout=240)
            if r.returncode == 0 and os.path.exists(out_json):
                with open(out_json) as f:
                    data = json.load(f)
                return [(d["w"], d["s"], d["e"]) for d in data]
            last_err = r.stderr[-400:]
        except Exception as e:
            last_err = str(e)
    raise RuntimeError(f"stable-ts failed after retry: {last_err}")


if __name__ == "__main__":
    sample = [("The", 0.0, 0.3), ("deep", 0.3, 0.6), ("ocean", 0.6, 0.9),
              ("hides", 0.9, 1.2), ("a", 1.2, 1.4), ("secret", 1.4, 1.9)]
    p = build_ass(sample, os.path.join(tempfile.gettempdir(), "caps_test.ass"))
    print("wrote", p)
