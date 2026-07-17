"""style.py — Per-video variation engine + anti-clone fingerprint (Wave 4).

Brand constants (FIXED across the library -> recognizability):
  - one Chatterbox narrator voice (handled in voice_pro)
  - one gold #F5C518 accent (handled in captions/DESIGN)
  - one caption system (handled in captions)
Everything else VARIES per video via a seeded VideoStyle, so no two videos
share >=3 of 5 varying axes (passes YouTube reused-content / uniqueness).

State persisted in assets/style_state.json (no-repeat + anti-clone history).
"""
from __future__ import annotations

import json
import os
import random

ROOT = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(ROOT, "assets", "style_state.json")

# Varying axes (the things that rotate per video)
LUTS = ["teal_orange.cube", "warm_film.cube", "moody.cube",
        "clean_bright.cube", "desaturated_doc.cube", "vivid_gold.cube"]
MUSIC_MOODS = ["none", "lofi", "cinematic"]          # matched to assets/music if present
HOOK_FORMATS = ["curiosity-gap", "number-first", "myth-bust", "science-says",
                "what-if", "then-vs-now", "cause-effect"]
CAPTION_ANIMS = ["pop", "slide", "fade-up", "typewriter"]
TRANSITION_PROFILES = ["hard-wipe", "hard-only", "hard-crossfade", "gold-wipe"]
PACING_CURVES = ["steady", "front-loaded", "back-loaded", "wave"]

# The 5 axes checked by anti-clone
AXES = ["lut", "music", "hook", "caption_anim", "transition"]


def _load_state():
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return {"history": []}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def _fingerprint(style):
    return {ax: style[ax] for ax in AXES}


def _too_similar(fp, history, threshold=3):
    """True if fp shares >= threshold axes with any recent video."""
    for past in history[-8:]:
        shared = sum(1 for ax in AXES if fp.get(ax) == past.get(ax))
        if shared >= threshold:
            return True
    return False


def make_style(seed=None, force_new=True):
    """Produce a VideoStyle dict, ensuring anti-clone uniqueness.

    seed: optional int for reproducible styles (testing).
    force_new: if True, retry until the fingerprint differs from recent history
               on >=3 of 5 axes. If False, just return a random style (testing).
    """
    rng = random.Random(seed) if seed is not None else random
    state = _load_state()
    history = state.get("history", [])

    attempts = 0
    while True:
        style = {
            "lut": rng.choice(LUTS),
            "music": rng.choice(MUSIC_MOODS),
            "hook": rng.choice(HOOK_FORMATS),
            "caption_anim": rng.choice(CAPTION_ANIMS),
            "transition": rng.choice(TRANSITION_PROFILES),
            "pacing": rng.choice(PACING_CURVES),
            "grain": rng.randint(4, 8),
            "shake": rng.choice([0, 3, 4, 5]),
        }
        fp = _fingerprint(style)
        if (not force_new) or (not history) or (not _too_similar(fp, history)):
            # push to history
            history.append(fp)
            state["history"] = history[-12:]
            _save_state(state)
            return style
        attempts += 1
        if attempts > 40:
            # give up trying to differ; just return (rare)
            history.append(fp)
            state["history"] = history[-12:]
            _save_state(state)
            return style


def reset_history():
    _save_state({"history": []})


if __name__ == "__main__":
    s = make_style(seed=42)
    print("style seed=42:", json.dumps(s, indent=2))
    s2 = make_style()
    print("random style:", json.dumps(s2, indent=2))
    # verify anti-clone differences on >=3 axes
    fp1, fp2 = _fingerprint(s), _fingerprint(s2)
    shared = sum(1 for ax in AXES if fp1[ax] == fp2[ax])
    print("axes shared between two consecutive:", shared, "(want <3 after forced new)")
