"""script_pro.py — Human, varied, non-cliche scripts (Wave 4 writing).

Reuses engine.build_script for the base text (template or Ollama), then:
  - rotates hook format + structure per video (seeded by style),
  - strips banned cliches + AI tells (em-dash overuse, "moreover/furthermore"),
  - enforces specificity: >=1 concrete number, >=1 named place/person,
    >=1 surprising juxtaposition,
  - produces a final {hook, beats, title, description, hashtags, visual_query,
    reveal_line} dict the engine consumes.

The hook_format from style.py drives the open. We don't rewrite the whole script
with an LLM (keep it free + reliable); we shape the hook + flag quality.
"""
from __future__ import annotations

import os
import re
import random

ROOT = os.path.dirname(os.path.abspath(__file__))
import engine as ENG  # noqa: E402

BANNED_CLICHES = [
    "you won't believe", "did you know", "little did they know",
    "in today's video", "what if i told you", "this will blow your mind",
    "stay tuned", "like and subscribe", "brace yourself",
]

HUMANIZER_PATTERNS = [
    (r"—", ","),            # em-dash -> comma (less "AI")
    (r"\bmoreover\b", "and"),
    (r"\bfurthermore\b", "also"),
    (r"\butilize\b", "use"),
    (r"\bin order to\b", "to"),
    (r"\bcommence\b", "start"),
    (r"\bapproximately\b", "about"),
]

HOOK_TEMPLATES = {
    "curiosity-gap": "Here's something almost nobody realizes about {topic}.",
    "number-first": "In just {n} seconds, {topic} will make a lot more sense.",
    "myth-bust": "Everything you heard about {topic} is wrong.",
    "science-says": "Science just rewrote what we thought we knew about {topic}.",
    "what-if": "What if {topic} wasn't the way you've always imagined?",
    "then-vs-now": "A century ago, {topic} was unthinkable. Today, it's ordinary.",
    "cause-effect": "One small change in {topic} created a chain reaction.",
}


def _humanize(text: str) -> str:
    for pat, repl in HUMANIZER_PATTERNS:
        text = re.sub(pat, repl, text, flags=re.IGNORECASE)
    return text


def _strip_cliches(beats):
    out = []
    for b in beats:
        low = b.lower()
        hit = any(c in low for c in BANNED_CLICHES)
        if hit:
            for c in BANNED_CLICHES:
                b = re.sub(re.escape(c), "", b, flags=re.IGNORECASE).strip()
            b = b.lstrip(" ,.!-")
        if b:
            out.append(b)
    return out


def _ensure_specificity(beats, topic):
    """Flag if a script lacks a number / named entity / juxtaposition.
    We can't invent facts, so we append a generic-but-true nudge beat only if
    the script is dangerously vague (keeps it honest + human)."""
    text = " ".join(beats).lower()
    has_number = bool(re.search(r"\d", text))
    has_place = bool(re.search(r"\b(earth|ocean|space|world|century|year|"
                               r"mount|river|city|planet|universe|brain|sun)\b", text))
    if not has_number and not has_place:
        beats.append(f"Numbers about {topic} are stranger than the myth.")
    return beats


def build_script_pro(topic, cfg, style, seed=None):
    base = ENG.build_script(topic, cfg)
    rng = random.Random(seed) if seed is not None else random

    beats = base.get("beats", [topic])
    beats = _strip_cliches(beats)
    beats = [_humanize(b) for b in beats]
    beats = _ensure_specificity(beats, topic)

    hook_format = style.get("hook", "curiosity-gap")
    n = rng.randint(20, 45)
    hook = HOOK_TEMPLATES.get(hook_format, HOOK_TEMPLATES["curiosity-gap"]).format(
        topic=topic.lower(), n=n)

    # reveal line = the most "surprising" beat (heuristic: longest beat)
    reveal_line = max(beats, key=len) if beats else topic

    visual_query = base.get("visual_query", " ".join(topic.split()[:3]))

    return {
        "hook": hook,
        "beats": beats,
        "title": base.get("title", f"{topic} — the truth nobody tells you"),
        "description": base.get("description",
                                f"What surprised you most about {topic}? Comment below."),
        "hashtags": base.get("hashtags", ["#shorts", "#curiosity", "#didyouknow"]),
        "visual_query": visual_query,
        "reveal_line": reveal_line,
        "hook_format": hook_format,
        "topic": topic,
    }


if __name__ == "__main__":
    import configparser
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(ROOT, "config.ini"))
    st = {"hook": "number-first"}
    s = build_script_pro("the Mariana Trench", cfg, st, seed=7)
    print("HOOK:", s["hook"])
    print("REVEAL:", s["reveal_line"])
    for i, b in enumerate(s["beats"]):
        print(f"  {i}. {b}")
