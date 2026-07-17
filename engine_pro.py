"""engine_pro.py — Orchestrator for the upgraded Faceless Viral Engine.

Wires together: script_pro -> voice_pro (Chatterbox) -> style -> edit_pro
(visuals + captions + minimal SFX). Same CLI as engine.py
(python engine_pro.py --topic "..." --count N). engine.py is untouched
(safe fallback). New behavior is gated behind config [quality].
"""
from __future__ import annotations

import os
import sys
import time
import shutil
import argparse

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import engine as ENG  # noqa: E402
import voice_pro  # noqa: E402
import style as STYLE  # noqa: E402
import script_pro  # noqa: E402
import edit_pro  # noqa: E402

WORK = os.path.join(ROOT, "work")
PUBLISH = os.path.join(ROOT, "publish")


def _log_run(name, topic, st, ok=True, error=""):
    log_path = os.path.join(ROOT, "run_status.log")
    with open(log_path, "a", encoding="utf-8") as f:
        status = "OK" if ok else f"FAIL:{error}"
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {name} topic={topic} "
                f"result={status} "
                f"lut={st.get('lut')} hook={st.get('hook')} "
                f"trans={st.get('transition')} music={st.get('music')} "
                f"caption={st.get('caption_anim')}\n")


def run_once(cfg, topic=None, seed=None):
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(PUBLISH, exist_ok=True)
    name = f"vid_{int(time.time())}"
    st = {}
    try:
        topic = topic or ENG.pick_topic()
        print(f"[topic] {topic}")

        # Wave 4: seeded style (brand constants fixed, varying axes rotated)
        st = STYLE.make_style(seed=seed)
        st["seed"] = seed
        print(f"[style] lut={st['lut']} hook={st['hook']} trans={st['transition']} "
              f"pacing={st['pacing']}")

        # Wave 4 writing: human, varied, non-cliche
        script = script_pro.build_script_pro(topic, cfg, st, seed=seed)
        print(f"[script] '{script.get('title','?')}' ({len(script['beats'])} beats) "
              f"hook='{script['hook']}'")

        # Wave 1 voice: Chatterbox + prosody + mastering
        voice = os.path.join(WORK, "voice.mp3")
        dur = voice_pro.render_voice(
            " ".join([script["hook"]] + script["beats"]), voice, cfg,
            reveal_line=script.get("reveal_line"))
        print(f"[voice] {dur:.1f}s")

        # Wave 2+3 edit: visuals (licensed) + captions + minimal SFX
        work_dir = os.path.join(WORK, name)
        os.makedirs(work_dir, exist_ok=True)
        out_mp4 = os.path.join(work_dir, name + ".mp4")
        edit_pro.edit_video_pro(script, voice, dur, cfg, work_dir, out_mp4, st)

        final_mp4 = os.path.join(PUBLISH, name + ".mp4")
        if os.path.exists(out_mp4):
            shutil.move(out_mp4, final_mp4)
            ENG.write_metadata(script, PUBLISH, name)
            # copy attributions for compliance
            attr = os.path.join(work_dir, "attributions.txt")
            if os.path.exists(attr):
                shutil.copy(attr, os.path.join(PUBLISH, name + "_attrib.txt"))
            print(f"[done] -> {final_mp4}")
            shutil.rmtree(work_dir, ignore_errors=True)
            _log_run(name, topic, st, ok=True)
            return final_mp4
        print("[ERROR] edit produced no file", file=sys.stderr)
        _log_run(name, topic, st, ok=False, error="no_output_file")
        return None
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
        print(f"[FATAL] {err}", file=sys.stderr)
        _log_run(name, topic, st, ok=False, error=err)
        return None


def main():
    p = argparse.ArgumentParser(description="Faceless Viral Engine (upgraded)")
    p.add_argument("--topic", help="override the random topic from topics.txt")
    p.add_argument("--count", type=int, default=None,
                   help="number of videos to produce (overrides config)")
    p.add_argument("--seed", type=int, default=None,
                   help="fixed seed for reproducible style (testing)")
    args = p.parse_args()

    cfg = ENG.load_config()
    n = args.count if args.count is not None else \
        cfg.getint("engine", "videos_per_run", fallback=1)
    for i in range(n):
        print(f"\n=== video {i+1}/{n} ===")
        run_once(cfg, topic=args.topic, seed=args.seed)


if __name__ == "__main__":
    main()
