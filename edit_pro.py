"""edit_pro.py — Restrained, premium edit assembly (Wave 2, 2026 playbook).

Per DESIGN.md / research:
  - 2.5-4s beats (NOT 1.5s spam). Distributed across the real voice duration
    with jitter so the video length == audio length.
  - Transitions: hard cut >=70%, one branded gold accent-wipe, gentle crossfade
    only between major beats, zoom-punch on the SINGLE reveal.
  - SFX: ONE soft whoosh on the reveal beat + subtle tick on number beats.
    NOT a whoosh on every cut.
  - Seamless loop: last frame matches first; end re-triggers the hook question.
"""
from __future__ import annotations

import os
import random
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
sys.path.insert(0, ROOT)
import engine as ENG  # noqa: E402
import captions as CAP  # noqa: E402
import visuals_pro as VIS  # noqa: E402


def _beat_durations(n, total, rng, lo=2.5, hi=4.0):
    """Split `total` seconds into `n` beats, each in [lo, hi], jittered."""
    if n <= 0:
        return []
    base = total / n
    durs = [min(hi, max(lo, base * rng.uniform(0.8, 1.2))) for _ in range(n)]
    s = sum(durs)
    if s > 0:
        durs = [d * total / s for d in durs]
    for i in range(n):
        durs[i] = min(hi, max(lo, durs[i]))
    residual = total - sum(durs)
    # Distribute the residual across ALL beats (not just beat 0). Dumping it on
    # beat 0 produced 20-44s monster first beats when duration/n exceeded hi,
    # breaking the 2.5-4.0s design spec. First try to absorb it within [lo,hi];
    # if the duration is simply too long for n beats at max length, spread the
    # raw excess uniformly (uniform >hi beats beat one 40s static shot).
    if n > 0:
        add = residual / n
        durs = [min(hi, max(lo, d + add)) for d in durs]
        remaining = total - sum(durs)
        if abs(remaining) > 1e-6:
            per = remaining / n
            durs = [d + per for d in durs]
    return durs


def _beat_query(beat_text, topic, fallback, broaden=False):
    """Derive a DISTINCT, relevant image-search query for one beat.

    Strategy: drop stopwords, keep content nouns/adjectives; prefer the
    LAST meaningful token group (usually the subject), but also try to
    differ from the topic so we don't re-pull the same map image every beat.
    `broaden=True` returns a single core noun (more likely to have a licensed
    image) for the query ladder's fallback rung.
    Falls back to the topic only if nothing usable is found.
    """
    import re
    txt = re.sub(r"[^a-z0-9 ]", " ", beat_text.lower())
    stop = {"the", "a", "an", "of", "to", "in", "on", "at", "by", "for", "and",
            "or", "but", "is", "are", "was", "were", "be", "been", "being", "it",
            "its", "this", "that", "these", "those", "we", "you", "they", "them",
            "their", "our", "us", "i", "he", "she", "have", "has", "had", "what",
            "when", "where", "which", "who", "why", "how", "from", "with", "about",
            "than", "any", "more", "most", "never", "almost", "nobody", "something",
            "anything", "everything", "around", "breaks", "found", "changes", "see",
            "know", "knew", "thought", "talking", "stranger", "story", "truth",
            "world", "people", "follow", "things", "didnt", "didn't", "us"}
    words = [w for w in txt.split() if len(w) > 2 and w not in stop]
    if not words:
        return fallback
    if broaden:
        # single most-specific content noun — broadest licensed coverage
        return words[-1]
    # prefer 2-3 trailing content words as the visual subject
    tail = words[-3:]
    q = " ".join(tail).strip()
    if not q:
        return fallback
    return q


def _assemble_timeline(beat_clips, durs, reveal_idx, transition_profile, w, h, fps, work_dir):
    """xfade chain. Returns path to visuals.mp4 or None."""
    xfade_dur = max(0.001, min(0.35, min(durs) / 2))
    hard = (transition_profile == "hard-only")
    parts = []
    inputs = []
    for idx, c in enumerate(beat_clips):
        inputs += ["-i", c]
        parts.append(f"[{idx}:v]format=yuv420p,setpts=PTS-STARTPTS[v{idx}]")
    prev = "v0"
    for k in range(1, len(beat_clips)):
        nxt = f"v{k}"
        out = "vx" if k == len(beat_clips) - 1 else f"vtmp{k}"
        if hard:
            offset = sum(durs[:k])
            xd = 0.001
        else:
            offset = sum(durs[:k]) - k * xfade_dur
            xd = xfade_dur
        parts.append(
            f"[{prev}][{nxt}]xfade=transition=fade:duration={xd:.3f}:"
            f"offset={offset:.3f}[{out}]"
        )
        prev = out
    visuals_tmp = os.path.join(work_dir, "visuals.mp4")
    r = subprocess.run(
        ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(parts),
         "-map", f"[{prev}]", "-r", str(fps), visuals_tmp],
        capture_output=True, cwd=work_dir)
    if not (r.returncode == 0 and os.path.exists(visuals_tmp)
            and os.path.getsize(visuals_tmp) > 1000):
        # fallback concat
        concat_list = os.path.join(work_dir, "concat.txt")
        with open(concat_list, "w") as f:
            for c in beat_clips:
                f.write(f"file '{os.path.abspath(c)}'\n")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
                        "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,"
                               f"crop={w}:{h},format=yuv420p", "-r", str(fps),
                        visuals_tmp], capture_output=True)
    return visuals_tmp if os.path.exists(visuals_tmp) and os.path.getsize(visuals_tmp) > 1000 else None


def edit_video_pro(script, voice_mp3, dur, cfg, work_dir, out_mp4, style):
    w = cfg.getint("output", "width", fallback=1080)
    h = cfg.getint("output", "height", fallback=1920)
    fps = cfg.getint("output", "fps", fallback=30)

    beats = script["beats"]
    n = max(1, len(beats))
    rng = random.Random(style.get("seed"))

    durs = _beat_durations(n, dur, rng, lo=2.5, hi=4.0)
    if sum(durs) < dur * 0.9:
        durs = _beat_durations(n, dur, rng, lo=1.8, hi=3.5)

    reveal_idx = None
    if script.get("reveal_line") in beats:
        reveal_idx = beats.index(script["reveal_line"])
    if reveal_idx is None and beats:
        reveal_idx = max(range(n), key=lambda i: len(beats[i]))

    # 1) graded beat visuals (+ zoom-punch on the single reveal)
    beat_clips, credits, sources = [], [], []
    for i in range(n):
        # vary the visual query per beat; build a ladder (specific -> broader)
        # so abstract topics still get a licensed image instead of gradient
        specific = _beat_query(beats[i], script["topic"], script["visual_query"])
        broad = _beat_query(beats[i], script["topic"], script["visual_query"],
                            broaden=True)
        ladder = [q for q in [specific, broad] if q and q != script["visual_query"]]
        ladder.append(script["visual_query"])
        clip, credit, src = VIS.build_beat_visual(
            ladder, i, durs[i], work_dir, cfg, style,
            fallback_query=script["visual_query"])
        if i == reveal_idx:
            punched = os.path.join(work_dir, f"punch_{i}.mp4")
            vf = (f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
                  f"zoompan=z='min(zoom+0.0008,1.12)':d={int(durs[i]*fps)}:"
                  f"s={w}x{h}:fps={fps}")
            r = subprocess.run(["ffmpeg", "-y", "-i", clip, "-vf", vf,
                                "-c:v", ENG.VENC, *ENG.VENC_OPTS, punched],
                               capture_output=True)
            if r.returncode == 0 and os.path.exists(punched):
                clip = punched
        beat_clips.append(clip)
        credits.append(credit)
        sources.append(src)

    visuals_tmp = _assemble_timeline(
        beat_clips, durs, reveal_idx, style.get("transition", "hard-wipe"),
        w, h, fps, work_dir)
    if not visuals_tmp:
        print("  [edit] visuals timeline failed")
        return out_mp4

    # 2) captions: word-level via stable-ts (the standard). If it fails, fall
    #    back to beat-level captions (one line per beat, timed to the edit) so
    #    the video STILL renders — never raise and produce zero output (F2).
    words = []
    venv_py = os.path.join(ROOT, ".venv_voice", "Scripts", "python.exe")
    if os.path.exists(venv_py):
        try:
            words = CAP.align_words_stable_ts(voice_mp3, venv_py, model="base.en")
        except Exception as e:  # stable-ts missing / venv broken / model fail
            print(f"  [edit] word-level align failed ({e}); "
                  f"falling back to beat-level captions")
            words = []
    if not words:
        # Beat-level fallback: one caption per beat, timed to the cut schedule.
        # Lower-standard than word-level, but a produced video beats no video.
        words = []
        t = 0.0
        for i, b in enumerate(beats):
            dur_i = durs[i] if i < len(durs) else (dur / max(1, len(beats)))
            words.append((b, t, t + dur_i))
            t += dur_i
        if words:
            print("  [edit] caption fallback: beat-level captions ("
                  f"{len(words)} beats)")
    if not words:
        # Truly nothing to caption (no beats) — still emit a single hold card
        # rather than crash, so the pipeline never dies on captions.
        words = [(script.get("topic", "Faceless"), 0.0, dur)]
        print("  [edit] caption fallback: topic hold-card (no beats)")
    ass = CAP.build_ass(words, os.path.join(work_dir, "caps.ass"), w, h,
                        per_page=2, seed=style.get("seed"))

    # 3) audio: voice + minimal SFX (reveal whoosh + number ticks) + ducked music
    # Input map: [0]=visuals (no audio), [1]=voice, [2..]=SFX/music files.
    voice_tmp = os.path.join(work_dir, "voice_adj.m4a")
    subprocess.run(["ffmpeg", "-y", "-i", voice_mp3, "-af", "volume=1.0",
                    "-c:a", "aac", voice_tmp], capture_output=True)

    sfx_inputs = []
    af_parts = ["[1:a]aresample=44100[a_v]"]   # voice is input index 1
    chain = "[a_v]"
    cnt = 1
    sfx_n = 0  # count of sfx files appended so far (-> input index 2 + sfx_n)

    # riser on the hook (start of video) — subtle, -18dB
    riser = os.path.join(SFX_DIR, "soft_riser.wav")
    if os.path.exists(riser):
        sfx_inputs += ["-i", riser]
        sfx_idx = 2 + sfx_n
        sfx_n += 1
        af_parts.append(f"[{sfx_idx}:a]volume=0.15,"
                        f"adelay=0|0[s{cnt}]")
        chain += f"[s{cnt}]"; cnt += 1

    whoosh = os.path.join(SFX_DIR, "reveal_whoosh.wav")
    if reveal_idx is not None and os.path.exists(whoosh):
        rp = sum(durs[:reveal_idx])
        sfx_inputs += ["-i", whoosh]
        sfx_idx = 2 + sfx_n
        sfx_n += 1
        af_parts.append(f"[{sfx_idx}:a]volume=0.5,"
                        f"adelay={int(rp*1000)}|{int(rp*1000)}[s{cnt}]")
        chain += f"[s{cnt}]"; cnt += 1
    tick = os.path.join(SFX_DIR, "number_tick.wav")
    if os.path.exists(tick):
        for i, b in enumerate(beats):
            if any(ch.isdigit() for ch in b) and rng.random() < 0.5:
                tp = sum(durs[:i]) + durs[i] * 0.5
                sfx_inputs += ["-i", tick]
                sfx_idx = 2 + sfx_n
                sfx_n += 1
                af_parts.append(f"[{sfx_idx}:a]volume=0.35,"
                                f"adelay={int(tp*1000)}|{int(tp*1000)}[s{cnt}]")
                chain += f"[s{cnt}]"; cnt += 1

    # branded music bed, sidechain-ducked under the voice (DESIGN.md / Wave 2)
    bg_music = cfg.get("music", "bg_music", fallback="").strip()
    if bg_music and os.path.exists(bg_music):
        sfx_inputs += ["-i", bg_music]
        m_idx = 2 + sfx_n
        sfx_n += 1
        # sidechaincompress: voice (input 1) triggers ducking of the music
        af_parts.append(
            f"[{m_idx}:a]volume=0.22[mraw];"
            f"[mraw][1:a]sidechaincompress=threshold=-24dB:ratio=4:"
            f"attack=15:release=250:level_in=1[mbed]"
        )
        chain += "[mbed]"; cnt += 1

    if cnt > 1:
        af_parts.append(f"{chain}amix=inputs={cnt}:normalize=0[a_out]")
    else:
        af_parts.append("[a_v]anull[a_out]")

    # subtitles filter: reference the .ass by BASENAME and run ffmpeg from
    # work_dir. This avoids Windows path/colon escaping bugs in ffmpeg's
    # subtitles filter (which otherwise mis-parses "C:/..." as options).
    ass_name = os.path.basename(ass)
    cmd = [
        "ffmpeg", "-y",
        "-i", visuals_tmp,
        "-i", voice_tmp,
        *sfx_inputs,
        "-filter_complex", ";".join(af_parts),
        "-vf", f"subtitles='{ass_name}'",
        "-map", "0:v", "-map", "[a_out]",
        "-c:v", ENG.VENC, *ENG.VENC_OPTS,
        "-c:a", "aac", "-shortest", out_mp4,
    ]
    r2 = subprocess.run(cmd, capture_output=True, cwd=work_dir)
    if not (os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 1000):
        print("  [edit] final mux failed:", r2.stderr.decode()[-400:])
        return out_mp4

    # 4) seamless loop: freeze the FIRST frame for ~0.6s and crossfade it in
    #    over the last 0.4s, so a looping Short returns smoothly to the hook.
    looped = os.path.join(work_dir, "looped.mp4")
    first_frame = os.path.join(work_dir, "frame0.png")
    ffr = subprocess.run(["ffmpeg", "-y", "-i", out_mp4, "-frames:v", "1",
                          "-q:v", "3", first_frame], capture_output=True)
    if ffr.returncode == 0 and os.path.exists(first_frame):
        tail = os.path.join(work_dir, "tail.mp4")
        ttl = subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-i", first_frame,
            "-f", "lavfi", "-i", "anullsrc=r=44100:d=0.6",
            "-t", "0.6", "-r", str(fps),
            "-c:v", ENG.VENC, *ENG.VENC_OPTS, "-c:a", "aac", "-shortest", tail
        ], capture_output=True)
        if ttl.returncode == 0 and os.path.exists(tail):
            # append tail, crossfade last 0.4s of main into tail
            xf = os.path.join(work_dir, "loopxf.mp4")
            xr = subprocess.run([
                "ffmpeg", "-y", "-i", out_mp4, "-i", tail,
                "-filter_complex",
                f"[0:v][1:v]xfade=transition=fade:duration=0.4:"
                f"offset={max(0.0, dur-0.4)}[v];"
                f"[0:a][1:a]acrossfade=duration=0.4[ao]",
                "-map", "[v]", "-map", "[ao]",
                "-c:v", ENG.VENC, *ENG.VENC_OPTS, "-c:a", "aac", xf
            ], capture_output=True)
            if xr.returncode == 0 and os.path.exists(xf):
                out_mp4 = xf  # return the looped version

    with open(os.path.join(work_dir, "attributions.txt"), "w", encoding="utf-8") as f:
        for i, (c, s) in enumerate(zip(credits, sources)):
            f.write(f"beat {i}: {s}" + (f" — CC credit: {c}" if c else "") + "\n")
    return out_mp4


if __name__ == "__main__":
    print("edit_pro loaded OK")
