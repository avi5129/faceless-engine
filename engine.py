"""
Faceless Viral Engine — core pipeline
Stages: topic -> script -> voice -> visuals -> edit -> metadata -> queue

Run:  python engine.py
Config: config.ini   Topics: topics.txt   Output: publish/
"""
import configparser
import os
import random
import re
import shutil
import subprocess
import sys
import textwrap
import time

# GPU detection: use NVIDIA NVENC encoder if ffmpeg supports it (much faster).
def has_nvenc():
    try:
        out = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"],
                             capture_output=True, text=True, timeout=10).stdout
        return "h264_nvenc" in out
    except Exception:
        return False

NVENC = has_nvenc()
VENC = "h264_nvenc" if NVENC else "libx264"
VENC_OPTS = ["-preset", "p1"] if NVENC else ["-preset", "veryfast"]
print(f"[gpu] NVENC encoder: {'ENABLED (' + VENC + ')' if NVENC else 'disabled (CPU libx264)'}")

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(ROOT, "work")
PUBLISH = os.path.join(ROOT, os.environ.get("PUBLISH_DIR", "publish"))

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
def load_config():
    # Strip only trailing "# comments" (a '#' preceded by whitespace), so values
    # that legitimately contain '#' (e.g. URLs like http://e.com/a#b) are kept.
    # Full-line comments (starting with '#') are skipped entirely.
    raw = []
    with open(os.path.join(ROOT, "config.ini"), encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue  # skip blank and full-line comment lines
            idx = line.find("#")
            while idx != -1:
                # treat '#' as a comment only if preceded by whitespace
                if idx == 0 or line[idx - 1] in (" ", "\t"):
                    line = line[:idx] + "\n"
                    break
                idx = line.find("#", idx + 1)
            raw.append(line)
    cp = configparser.ConfigParser()
    cp.read_string("".join(raw))
    return cp

# ---------------------------------------------------------------------------
# Stage 1: topic
# ---------------------------------------------------------------------------
def pick_topic():
    path = os.path.join(ROOT, "topics.txt")
    if not os.path.exists(path):
        raise FileNotFoundError(f"topics.txt not found at {path}")
    with open(path, encoding="utf-8") as f:
        topics = [t.strip() for t in f if t.strip() and not t.startswith("#")]
    if not topics:
        raise ValueError("topics.txt is empty — add topic lines to generate videos")
    return random.choice(topics)

# ---------------------------------------------------------------------------
# Stage 2: script
# ---------------------------------------------------------------------------
def script_via_ollama(topic, model):
    prompt = textwrap.dedent(f"""
    You are a writer for a faceless YouTube Shorts channel about curiosity and
    discovery facts. Write a viral 35-45 second script about: "{topic}".

    Rules:
    - Hook in the FIRST sentence that creates curiosity gap ("You won't believe...").
    - 6-9 short beats, each 1 sentence, surprising and specific.
    - End with an engagement cue ("Follow for more").
    - Plain English, no markdown, no brackets.

    Also return metadata. Respond ONLY with JSON:
    {{
      "hook": "<first line, max 12 words>",
      "beats": ["sentence 1", "sentence 2", ...],
      "title": "<clickable title, max 60 chars>",
      "description": "<2-3 sentences, include a question to boost comments>",
      "hashtags": ["#shorts", "#curiosity", ... up to 6],
      "visual_query": "<3-5 words for stock photo search, e.g. 'deep ocean floor'>"
    }}
    """)
    try:
        # RTX 3050 + Ollama 0.32.0 has a broken CUDA init path that crashes with
        # 0xc0000409. Forcing CPU mode (no CUDA devices) avoids it cleanly.
        env = dict(os.environ)
        env["CUDA_VISIBLE_DEVICES"] = "-1"
        out = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True, text=True, timeout=180, env=env,
        ).stdout
        # Ollama may emit unescaped newlines / control chars inside JSON values.
        # Strict json.loads is brittle here, so parse fields tolerantly via regex.
        raw = out.strip().replace("```json", "").replace("```", "")
        def field(key, default=""):
            m = re.search(rf'"{key}"\s*:\s*"((?:[^"\\]|\\.)*)"', raw, re.S)
            return m.group(1).replace("\\n", " ").strip() if m else default
        def arr_field(key):
            m = re.search(rf'"{key}"\s*:\s*\[(.*?)\]', raw, re.S)
            if not m:
                return []
            return [x.strip().strip('"').replace("\\n", " ")
                    for x in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))]
        title = field("title") or f"{topic} — the truth nobody tells you"
        hook = field("hook")
        beats = arr_field("beats")
        if not beats:
            # fallback: split on lines that look like script beats
            beats = [line.strip(" -") for line in raw.splitlines()
                     if line.strip() and not line.strip().startswith("{")
                     and not line.strip().startswith("}")][:9] or ["", ""]
        hashtags = arr_field("hashtags") or ["#shorts", "#curiosity", "#didyouknow"]
        return {
            "hook": hook or (beats[0] if beats else topic),
            "beats": beats or [topic],
            "title": title,
            "description": field("description") or f"Wait until you hear the real story behind {topic}.",
            "hashtags": hashtags,
            "visual_query": field("visual_query") or " ".join(topic.split()[:3]),
        }
    except Exception as e:
        print(f"  [script] ollama failed ({e}), using template fallback")
        return script_template(topic)

def script_template(topic):
    return {
        "hook": f"You won't believe what {topic.lower()} really means.",
        "beats": [
            f"Most people have never heard of {topic.lower()}.",
            "But the truth is stranger than any story.",
            "Scientists found something that breaks what we thought we knew.",
            "It changes how we see the world around us.",
            "And almost nobody is talking about it.",
            "Follow for more things you didn't know.",
        ],
        "title": f"{topic} — the truth nobody tells you",
        "description": f"Wait until you hear the real story behind {topic}. "
                       f"What surprised you most? Tell us in the comments.",
        "hashtags": ["#shorts", "#curiosity", "#didyouknow", "#facts", "#discovery"],
        "visual_query": " ".join(topic.split()[:3]),
    }

def build_script(topic, cfg):
    # Local Ollama (gemma4) is unstable on some machines (CUDA crash). The
    # template path is zero-cost, offline, and always works — use it by default.
    # Set provider=ollama in config.ini only if `ollama run gemma4` works for you.
    provider = cfg.get("script", "provider", fallback="template")
    if provider == "ollama":
        model = cfg.get("script", "ollama_model", fallback="gemma4")
        return script_via_ollama(topic, model)
    return script_template(topic)

# ---------------------------------------------------------------------------
# Stage 3: voice
# ---------------------------------------------------------------------------
def make_voice(text, cfg, out_mp3):
    provider = cfg.get("voice", "provider", fallback="kokoro")
    if provider == "elevenlabs":
        return _voice_elevenlabs(text, cfg, out_mp3)
    if provider == "edge-tts":
        return _voice_edge(text, cfg.get("voice", "voice", fallback="en-US-AndrewNeural"), out_mp3)
    return _voice_kokoro(text, cfg.get("voice", "kokoro_voice", fallback="af_heart"), out_mp3)

def _voice_kokoro(text, voice, out_mp3):
    """Kokoro-82M: open-source, realistic, runs fully locally (no API, no money)."""
    from kokoro import KPipeline
    import soundfile as sf
    import numpy as np
    pipe = KPipeline(lang_code='a')  # american english
    chunks = [audio for _, _, audio in pipe(text, voice=voice, speed=1.0)]
    wav = np.concatenate(chunks) if chunks else np.zeros(1)
    tmp = out_mp3 + ".tmp.wav"
    sf.write(tmp, wav, 24000)
    # normalize to mp3 for the editor
    subprocess.run(["ffmpeg", "-y", "-i", tmp, "-c:a", "libmp3lame",
                    "-q:a", "2", out_mp3], capture_output=True)
    os.remove(tmp)

def _voice_edge(text, voice, out_mp3):
    import asyncio
    import edge_tts
    async def _run():
        # slight rate tweak for a more natural, less robotic cadence
        comm = edge_tts.Communicate(text, voice, rate="-8%")
        await comm.save(out_mp3)
    asyncio.run(_run())

def _voice_elevenlabs(text, cfg, out_mp3):
    import requests
    key = cfg.get("voice", "eleven_api_key", fallback="")
    vid = cfg.get("voice", "eleven_voice_id", fallback="")
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{vid}",
        headers={"xi-api-key": key, "Content-Type": "application/json"},
        json={"text": text, "voice_settings": {"stability": 0.45, "similarity_boost": 0.75}},
        timeout=60,
    )
    r.raise_for_status()
    with open(out_mp3, "wb") as f:
        f.write(r.content)

def media_duration(path):
    """Duration of a media file in seconds (0.0 if it can't be probed)."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True,
    ).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0

# ---------------------------------------------------------------------------
# Stage 4: visuals  (realistic, moving stock footage)
# ---------------------------------------------------------------------------
def fetch_pexels_video(query, api_key, out_path, w=1080, h=1920):
    """Download a real, moving stock clip from Pexels that matches the query.
    Returns True on success. Clips are resized/cropped to vertical 9:16."""
    if not api_key:
        return False
    try:
        import requests
        r = requests.get("https://api.pexels.com/videos/search",
                         params={"query": query, "per_page": 10},
                         headers={"Authorization": api_key}, timeout=20)
        if r.status_code != 200:
            return False
        videos = r.json().get("videos", [])
        if not videos:
            return False
        # pick the first usable video file (prefer 720p+ for quality)
        for v in videos:
            files = sorted(v.get("video_files", []),
                           key=lambda f: f.get("height", 0), reverse=True)
            for f in files:
                if f.get("height", 0) >= 720:
                    dl = requests.get(f["link"], timeout=40)
                    if dl.status_code == 200 and len(dl.content) > 5000:
                        tmp = out_path + ".raw.mp4"
                        with open(tmp, "wb") as fh:
                            fh.write(dl.content)
                        # normalize to vertical 9:16, 30fps
                        subprocess.run([
                            "ffmpeg", "-y", "-i", tmp,
                            "-vf", f"scale={w}:{h}:force_original_aspect_ratio="
                                   f"increase,crop={w}:{h},format=yuv420p",
                            "-r", "30", "-an", "-c:v", "libx264",
                            "-preset", "veryfast", out_path,
                        ], capture_output=True)
                        os.remove(tmp)
                        return os.path.exists(out_path) and os.path.getsize(out_path) > 5000
        return False
    except Exception as e:
        print(f"  [visuals] pexels video error: {e}")
        return False

def fetch_pexels_photo(query, api_key, out_path):
    """Fallback: a real stock PHOTO (then we add motion via Ken-Burns)."""
    if not api_key:
        return False
    try:
        import requests
        r = requests.get("https://api.pexels.com/v1/search",
                         params={"query": query, "per_page": 5},
                         headers={"Authorization": api_key}, timeout=15)
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                img = requests.get(photos[0]["src"]["large"], timeout=20)
                with open(out_path, "wb") as f:
                    f.write(img.content)
                return os.path.getsize(out_path) > 1000
    except Exception:
        pass
    return False

def ken_burns(img_path, out_path, beat_sec, w=1080, h=1920, fps=30):
    """Turn a real photo into a slow zoom/pan clip (cinematic motion)."""
    frames = int(beat_sec * fps)
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
          f"zoompan=z='min(zoom+0.0018,1.25)':d={frames}:s={w}x{h}:fps={fps}")
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-i", img_path,
        "-vf", vf, "-t", str(beat_sec), out_path,
    ], capture_output=True)
    return out_path

def fetch_wikimedia_photo(query, out_path, w=1080):
    """Account-free, no-key real photos from Wikimedia Commons (free license).
    Returns True on success. Used as the default realistic visual source."""
    try:
        import requests
        import urllib.parse
        q = urllib.parse.quote(query)
        headers = {"User-Agent": "FacelessEngine/1.0 (https://example.com)"}
        api = ("https://commons.wikimedia.org/w/api.php?action=query"
               "&generator=search&gsrsearch=%s&gsrnamespace=6&gsrlimit=5"
               "&prop=imageinfo&iiprop=url|mime|size&iiurlwidth=%d&format=json" % (q, w))
        r = requests.get(api, headers=headers, timeout=20)
        if r.status_code != 200:
            return False
        pages = r.json().get("query", {}).get("pages", {})
        for p in pages.values():
            info = p.get("imageinfo", [{}])[0]
            mime = info.get("mime", "")
            if mime.startswith("image") and "thumburl" in info:
                img = requests.get(info["thumburl"], headers=headers, timeout=25)
                if img.status_code == 200 and len(img.content) > 3000:
                    with open(out_path, "wb") as f:
                        f.write(img.content)
                    return os.path.getsize(out_path) > 3000
        return False
    except Exception as e:
        print(f"  [visuals] wikimedia error: {e}")
        return False

def animated_bg(out_path, idx, w=1080, h=1920, dur=6):
    """Last-resort motion background (no API key): cinematic drifting gradient."""
    hues = ["0x1a2a6c", "0x2a5298", "0x16222a", "0x3a1c71", "0x0f2027", "0x232526"]
    c0 = hues[idx % len(hues)]
    c1 = hues[(idx + 2) % len(hues)]
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i",
        f"gradients=s={w}x{h}:c0={c0}:c1={c1}:x0=0:y0=0:"
        f"x1={w}:y1={h}:d={dur+1}:speed=0.02",
        "-t", str(dur), "-r", "30", out_path,
    ], capture_output=True)
    return out_path

# ---------------------------------------------------------------------------
# Stage 5: edit (ffmpeg assembly)
# ---------------------------------------------------------------------------
def edit_video(script, voice_mp3, dur, cfg, work_dir, out_mp4):
    w = cfg.getint("output", "width", fallback=1080)
    h = cfg.getint("output", "height", fallback=1920)
    fps = cfg.getint("output", "fps", fallback=30)

    beats = script["beats"]
    n = max(1, len(beats))
    # Make each visual beat span the real voice duration so video == audio length.
    beat_sec = dur / n
    xfade_dur = min(0.4, beat_sec / 2)
    api_key = cfg.get("visuals", "pexels_api_key", fallback="")
    query = script.get("visual_query", "space")

    clips = []
    for i, _ in enumerate(beats):
        clip = os.path.join(work_dir, f"bg_{i}.mp4")
        src = "gradient"
        # 1) Real moving stock footage (Pexels video, free key)
        if fetch_pexels_video(query, api_key, clip, w, h):
            src = "pexels-video"
        # 2) Real stock photo (Wikimedia Commons, NO key, free license) + motion
        elif fetch_wikimedia_photo(query, os.path.join(work_dir, f"img_{i}.jpg"), w):
            ken_burns(os.path.join(work_dir, f"img_{i}.jpg"), clip, beat_sec, w, h, fps)
            src = "wikimedia"
        # 3) Real stock photo (Pexels, free key) + motion
        elif fetch_pexels_photo(query, api_key, os.path.join(work_dir, f"img_{i}.jpg")):
            ken_burns(os.path.join(work_dir, f"img_{i}.jpg"), clip, beat_sec, w, h, fps)
            src = "pexels-photo"
        # 4) Last resort: drifting gradient (still moving)
        if src == "gradient":
            animated_bg(clip, i, w, h, dur=max(2.0, beat_sec))
        clips.append(clip)
        print(f"  [visual {i}] {src}")

    # Crossfade between beats. Each beat clip is `beat_sec` long; offsets must
    # accumulate (k-th xfade starts at k*beat_sec - k*xfade_dur).
    if len(clips) > 1:
        fc_parts = []
        inputs = []
        for idx, c in enumerate(clips):
            inputs += ["-i", c]
            fc_parts.append(f"[{idx}:v]format=yuv420p,setpts=PTS-STARTPTS[v{idx}]")
        prev = "v0"
        for k in range(1, len(clips)):
            nxt = f"v{k}"
            out = "vx" if k == len(clips) - 1 else f"vtmp{k}"
            offset = k * beat_sec - k * xfade_dur
            fc_parts.append(
                f"[{prev}][{nxt}]xfade=transition=fade:duration={xfade_dur}:"
                f"offset={offset:.3f}[{out}]")
            prev = out
        fc = ";".join(fc_parts)
        visuals_tmp = os.path.join(work_dir, "visuals.mp4")
        subprocess.run(
            ["ffmpeg", "-y", *inputs, "-filter_complex", fc,
             "-map", f"[{prev}]", "-r", str(fps), visuals_tmp],
            capture_output=True, cwd=work_dir)
        # Fallback: if xfade produced a too-short clip, use concat demuxer.
        if not (os.path.exists(visuals_tmp) and os.path.getsize(visuals_tmp) > 1000
                and abs(media_duration(visuals_tmp) - dur) < beat_sec):
            concat_list = os.path.join(work_dir, "concat.txt")
            with open(concat_list, "w") as f:
                for c in clips:
                    f.write(f"file '{os.path.abspath(c)}'\n")
            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
                "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,"
                       f"crop={w}:{h},format=yuv420p",
                "-r", str(fps), visuals_tmp], capture_output=True)
    else:
        visuals_tmp = clips[0]

    if not os.path.exists(visuals_tmp) or os.path.getsize(visuals_tmp) < 1000:
        print("  [edit] visuals concat failed")
        return out_mp4

    # captions: one beat per timed segment, subtitle overlay
    ass = build_ass(beats, dur, w, h)
    ass_path = os.path.join(work_dir, "caps.ass")
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass)

    bg_music = cfg.get("music", "bg_music", fallback="")
    filter_chain = "subtitles=filename='caps.ass'"
    venc_args = ["-c:v", VENC, *VENC_OPTS]
    if bg_music and os.path.exists(bg_music):
        r2 = subprocess.run([
            "ffmpeg", "-y", "-i", "visuals.mp4", "-i", voice_mp3, "-i", bg_music,
            "-filter_complex",
            f"[0:v]{filter_chain}[v];[1:a]volume=1.0[a1];"
            f"[2:a]volume=0.15[a2];[a1][a2]amix=inputs=2[a]",
            "-map", "[v]", "-map", "[a]", *venc_args,
            "-c:a", "aac", "-shortest", out_mp4,
        ], capture_output=True, cwd=work_dir)
    else:
        r2 = subprocess.run([
            "ffmpeg", "-y", "-i", "visuals.mp4", "-i", voice_mp3,
            "-filter_complex", f"[0:v]{filter_chain}[v]",
            "-map", "[v]", "-map", "1:a", *venc_args,
            "-c:a", "aac", "-shortest", out_mp4,
        ], capture_output=True, cwd=work_dir)
    if not os.path.exists(out_mp4) or os.path.getsize(out_mp4) < 1000:
        print("  [edit] final mux failed:", r2.stderr.decode()[-300:])
    return out_mp4

def _ass_ts(t):
    """ASS timestamp: H:MM:SS.cc (handles >60s correctly)."""
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:04.1f}"

def build_ass(beats, total_dur, w, h):
    n = len(beats)
    seg = total_dur / n
    lines = [
        "[Script Info]",
        "ScriptType: v4.00",
        "PlayResX: %d" % w,
        "PlayResY: %d" % h,
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, Bold, "
        "Italic, Alignment, MarginL, MarginR, MarginV, BorderStyle, Outline",
        "Style: C, Arial Black, 64, &H00FFFFFF, &H00000000, 1, 0, 2, 60, 60, 220, 1, 4",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Text",
    ]
    for i, b in enumerate(beats):
        start = i * seg
        end = (i + 1) * seg
        text = b.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
        lines.append(f"Dialogue: 0,{_ass_ts(start)},{_ass_ts(end)},C,{text}")
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Stage 6-7: metadata + queue
# ---------------------------------------------------------------------------
def write_metadata(script, out_dir, name, cfg=None):
    title = script.get("title", name)
    desc = script.get("description", "")
    tags = " ".join(script.get("hashtags", ["#shorts"]))
    # F4: revenue line is config-driven. Only emit it when the user has set a
    # real offer_url — never ship a placeholder/broken link.
    if cfg is None:
        try:
            cfg = load_config()
        except Exception:
            cfg = None
    offer = ""
    if cfg is not None:
        url = (cfg.get("revenue", "offer_url", fallback="") or "").strip()
        cta = (cfg.get("revenue", "offer_cta", fallback="") or "").strip()
        if url:
            offer = f"\n\n{cta} {url}".rstrip()
    txt = f"TITLE:\n{title}\n\nDESCRIPTION:\n{desc}{offer}\n\nHASHTAGS:\n{tags}\n"
    with open(os.path.join(out_dir, name + ".txt"), "w", encoding="utf-8") as f:
        f.write(txt)

# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def run_once(cfg, topic=None):
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(PUBLISH, exist_ok=True)
    topic = topic or pick_topic()
    print(f"[topic] {topic}")
    script = build_script(topic, cfg)
    print(f"[script] '{script.get('title','?')}' ({len(script['beats'])} beats)")

    voice = os.path.join(WORK, "voice.mp3")
    full_text = " ".join([script["hook"]] + script["beats"])
    make_voice(full_text, cfg, voice)
    dur = media_duration(voice)
    print(f"[voice] {dur:.1f}s")

    name = f"vid_{int(time.time())}"
    work_dir = os.path.join(WORK, name)
    os.makedirs(work_dir, exist_ok=True)
    out_mp4 = os.path.join(work_dir, name + ".mp4")
    edit_video(script, voice, dur, cfg, work_dir, out_mp4)

    # move finished product into publish/
    final_mp4 = os.path.join(PUBLISH, name + ".mp4")
    if os.path.exists(out_mp4):
        shutil.move(out_mp4, final_mp4)
        write_metadata(script, PUBLISH, name, cfg)
        print(f"[done] -> {final_mp4}")
        print(f"       metadata -> {os.path.join(PUBLISH, name + '.txt')}")
        # clean the per-run temp dir; keep publish/ and the engine outputs
        shutil.rmtree(work_dir, ignore_errors=True)
        return final_mp4
    print("[ERROR] edit produced no file", file=sys.stderr)
    return None

def main():
    import argparse
    p = argparse.ArgumentParser(description="Faceless Viral Engine")
    p.add_argument("--topic", help="override the random topic from topics.txt")
    p.add_argument("--count", type=int, default=None,
                   help="number of videos to produce (overrides config)")
    args = p.parse_args()

    cfg = load_config()
    n = args.count if args.count is not None else \
        cfg.getint("engine", "videos_per_run", fallback=1)
    for i in range(n):
        print(f"\n=== video {i+1}/{n} ===")
        run_once(cfg, topic=args.topic)

if __name__ == "__main__":
    main()
