"""visuals_pro.py — Premium, monetization-safe visuals (Wave 3).

For each beat: pick a source, add cinematic motion, then grade it.
Priority: motion b-roll (Pexels video, needs key) -> Wikimedia still + Ken-Burns.
LICENSE FILTER (P0, monetization safety): when pulling Wikimedia, only accept
free licenses (CC0 / CC-BY / CC-BY-SA). If a result's license is NonCommercial /
NoDerivatives / unknown / missing, SKIP it. If every candidate is rejected, fall
back to the always-safe animated gradient (never publish unlicensed material).

Also: per-video LUT (from assets/luts), film grain, subtle handheld shake,
vignette, and a big keyword/number overlay (separate from captions).

Reuses engine.py: fetch_pexels_video, fetch_wikimedia_photo, ken_burns,
animated_bg, fetch_pexels_photo.
"""
from __future__ import annotations

import os
import random
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))


def ken_burns_restrained(img_path, out_path, beat_sec, w=1080, h=1920, fps=30,
                          zmax=1.10, rate=0.0012):
    """Slow, calm Ken Burns — matches DESIGN.md (1.05-1.10x over the beat).

    The engine.py helper zooms to 1.25x on every still, which reads as the
    busy 2025 hyper-motion look the 2026 research warns against. This restrained
    version caps the zoom low and slows the rate so stills feel cinematic, not
    jittery. (engine.py is intentionally NOT modified — Decision #5.)
    """
    frames = int(beat_sec * fps)
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
          f"zoompan=z='min(zoom+{rate},{zmax})':d={frames}:s={w}x{h}:fps={fps}")
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-i", img_path,
        "-vf", vf, "-t", str(beat_sec), out_path,
    ], capture_output=True)
    return out_path


# --- Typographic title card (premium fallback when NO licensed image is found) ---
# A blank gradient reads as "AI slop / abandoned". A designed title card — big
# keyword in brand gold + the beat sentence in white, on a graded/grained LUT
# background — reads as an intentional editorial beat. This is the earnings-grade
# fallback (no API key required) so every beat looks produced, never empty.
_FONT_PATH = os.path.join(ROOT, "fonts", "Anton-Regular.ttf")
_LUT_DIR = os.path.join(ROOT, "assets", "luts")
# curated premium LUT set (subset safe for abstract/text beats)
_TITLE_LUTS = ["teal_orange.cube", "warm_film.cube", "moody.cube",
               "clean_bright.cube", "desaturated_doc.cube", "vivid_gold.cube"]
GOLD = "0xF5C518"


def _escape_drawtext(text: str) -> str:
    """Escape chars ffmpeg drawtext mis-parses."""
    return (text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
            .replace("%", "\\%").replace(",", "\\,").replace("(", "\\(")
            .replace(")", "\\)"))


def _title_card(keyword, sentence, out_path, beat_sec, w=1080, h=1920, fps=30,
                rng=None, seed=0):
    """Render a designed title-card beat: keyword (gold, big) + sentence (white)
    over a graded + LUT + grain + vignette background. Returns out_path or None."""
    rng = rng or random.Random(seed)
    lut = os.path.join(_LUT_DIR, rng.choice(_TITLE_LUTS))
    hue_a = rng.choice(["0x10243f", "0x241023", "0x0f2027", "0x2a1a3a", "0x14233a"])
    hue_b = rng.choice(["0x1a3a5a", "0x3a2a1a", "0x223044", "0x3a1c2a", "0x1f3a4a"])
    kw = _escape_drawtext(keyword[:28].upper())
    # keep sentence short for the card (first ~8 words)
    short = " ".join(sentence.split()[:9])
    body = _escape_drawtext(short)
    font = _FONT_PATH if os.path.exists(_FONT_PATH) else "Arial"
    # drawtext: keyword (gold, ~12% h) at 40% down; sentence (white, ~5% h) at 56%.
    vf = (
        f"gradients=s={w}x{h}:c0={hue_a}:c1={hue_b}:x0=0:y0=0:x1={w}:y1={h}:"
        f"d={max(2.0,beat_sec)}:speed=0.015,"
        f"format=yuv420p,"
        f"drawtext=fontfile='{font}':text='{kw}':fontcolor={GOLD}:"
        f"fontsize={int(h*0.12)}:x=(w-text_w)/2:y={int(h*0.34)}:"
        f"box=0:alpha=0:shadowcolor=black:shadowx=3:shadowy=3,"
        f"drawtext=fontfile='{font}':text='{body}':fontcolor=white:"
        f"fontsize={int(h*0.05)}:x=(w-text_w)/2:y={int(h*0.54)}:"
        f"box=0:alpha=0:shadowcolor=black:shadowx=2:shadowy=2,"
        f"grain=size=6,"
        f"vignette=angle=PI/5"
    )
    if os.path.exists(lut):
        vf += f",lut3d=file='{lut}'"
    r = subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", vf,
        "-t", str(beat_sec), "-r", str(fps), "-pix_fmt", "yuv420p", out_path,
    ], capture_output=True)
    if r.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        return out_path
    # absolute fallback: plain gradient (last resort, never blank-unlicensed)
    r2 = subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"gradients=s={w}x{h}:c0={hue_a}:c1={hue_b}:d={max(2.0,beat_sec)}:speed=0.015",
        "-t", str(beat_sec), "-r", str(fps), "-pix_fmt", "yuv420p", out_path,
    ], capture_output=True)
    return out_path if (r2.returncode == 0 and os.path.exists(out_path)) else None

import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import engine as ENG  # noqa: E402

LUT_DIR = os.path.join(ROOT, "assets", "luts")
ACCEPTED_LICENSES = {"cc0", "publicdomain", "public-domain", "cc-by", "cc-by-sa",
                     "cc-by-4.0", "cc-by-sa-4.0", "cc0-1.0"}

# --- Wikimedia license filter (P0) ---

def _wikimedia_candidates(query, w=1080, limit=6):
    """Return list of dicts {url,thumb,license,mime,title} from Commons search."""
    import requests
    import urllib.parse
    q = urllib.parse.quote(query)
    headers = {"User-Agent": "FacelessEngine/2.0 (https://example.com)"}
    api = ("https://commons.wikimedia.org/w/api.php?action=query"
           "&generator=search&gsrsearch=%s&gsrnamespace=6&gsrlimit=%d"
           "&prop=imageinfo&iiprop=url|mime|extmetadata|size"
           "&iiurlwidth=%d&format=json" % (q, limit, w))
    r = requests.get(api, headers=headers, timeout=20)
    if r.status_code != 200:
        return []
    pages = r.json().get("query", {}).get("pages", {})
    out = []
    for p in pages.values():
        info = p.get("imageinfo", [{}])[0]
        meta = info.get("extmetadata", {})
        lic = (meta.get("LicenseShortName", {}).get("value", "") or "").lower()
        out.append({
            "title": p.get("title", ""),
            "thumb": info.get("thumburl", ""),
            "mime": info.get("mime", ""),
            "license": lic,
        })
    return out

def _license_ok(lic: str) -> bool:
    """Accept only free-for-commercial, derivative-allowed licenses.
    REJECT NonCommercial (NC) and NoDerivatives (ND) — those fail YT monetization.
    """
    l = " " + lic.lower().replace(" ", "-").replace("_", "-") + " "
    if not l.strip():
        return False
    # hard rejects first (NC / ND fail monetization + derivative reuse)
    if "nc" in l or "non-commercial" in l or "nd" in l or "no-derivatives" in l \
       or "noncommercial" in l:
        return False
    return any(tok in l for tok in ACCEPTED_LICENSES)

def fetch_wikimedia_licensed(query, out_path, w=1080, work_dir=None, pick=0):
    """Like engine.fetch_wikimedia_photo but LICENSE-FILTERED. Returns (ok, license, credit).
    `pick` skips that many accepted (licensed) candidates so different beats grab
    DIFFERENT images for the same/similar query (per-beat visual variety)."""
    creds = []
    try:
        skipped = 0
        for c in _wikimedia_candidates(query, w):
            lic = c["license"]
            if not _license_ok(lic):
                continue  # skip NC/ND/unknown
            if not c["mime"].startswith("image") or not c["thumb"]:
                continue
            if skipped < pick:
                skipped += 1
                continue  # already used by an earlier beat
            import requests
            headers = {"User-Agent": "FacelessEngine/2.0"}
            img = requests.get(c["thumb"], headers=headers, timeout=25)
            if img.status_code == 200 and len(img.content) > 3000:
                with open(out_path, "wb") as f:
                    f.write(img.content)
                if os.path.getsize(out_path) > 3000:
                    credit = c["title"].replace("File:", "")
                    return True, lic, credit
    except Exception as e:
        print(f"  [visuals] wikimedia error: {e}")
    return False, "", ""


# --- grading / motion ---

def _grade(clip, out_path, lut_name=None, grain=7, shake=0, vignette=True):
    """Apply LUT + grain + optional shake + vignette to a beat clip."""
    vf = []
    if lut_name:
        lut_path = os.path.join(LUT_DIR, lut_name)
        if os.path.exists(lut_path):
            vf.append(f"lut3d={lut_path}")
    vf.append("format=yuv420p")
    if shake and shake > 0:
        # subtle handheld via crop shake
        vf.append(f"crop=in_w-8:in_h-8:x='8*sin(t*{shake})':y='8*cos(t*{shake})'")
    if grain:
        vf.append(f"noise=alls={grain}:allf=t")
    if vignette:
        vf.append("vignette=PI/5")
    cmd = ["ffmpeg", "-y", "-i", clip, "-vf", ",".join(vf), "-c:v",
           ENG.VENC, *ENG.VENC_OPTS, out_path]
    r = subprocess.run(cmd, capture_output=True)
    return r.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 1000


def build_beat_visual(query, idx, dur, work_dir, cfg, style, fallback_query=None):
    """Build one graded beat clip. Returns (clip_path, credit, source).

    Source priority (per the locked plan; gradient is the LAST-RESORT safety net
    so we NEVER publish unlicensed):
      1) Pexels motion b-roll (needs API key)
      2) Licensed Wikimedia still (CC0/CC-BY/CC-BY-SA) + Ken-Burns — tries the
         per-beat query ladder (specific -> broader) so abstract topics still get
         a licensed image instead of gradient
      3) Pexels photo
      4) only then: always-safe animated gradient (never publish unlicensed)
    `query` may be a single string or a list (query ladder, tried in order).
    """
    w = cfg.getint("output", "width", fallback=1080)
    h = cfg.getint("output", "height", fallback=1920)
    fps = cfg.getint("output", "fps", fallback=30)
    api_key = cfg.get("visuals", "pexels_api_key", fallback="")

    if isinstance(query, (list, tuple)):
        ladder = list(query)
    else:
        ladder = [query]
    if fallback_query and fallback_query not in ladder:
        ladder.append(fallback_query)

    raw = os.path.join(work_dir, f"raw_{idx}.mp4")
    credit = ""
    src = "gradient"

    def _try_wikimedia(q, pick=0):
        nonlocal credit
        if not q:
            return False
        lic_ok, lic, cr = fetch_wikimedia_licensed(
            q, os.path.join(work_dir, f"img_{idx}.jpg"), w, pick=pick)
        if lic_ok:
            ken_burns_restrained(os.path.join(work_dir, f"img_{idx}.jpg"), raw, dur, w, h, fps)
            credit = cr
            return True
        return False

    # 1) motion b-roll (uses the most specific query)
    if ENG.fetch_pexels_video(ladder[0], api_key, raw, w, h):
        src = "pexels-video"
    else:
        # 2) licensed Wikimedia — try each rung of the ladder, varying pick so
        #    different beats pull different licensed images
        for qi, q in enumerate(ladder):
            if _try_wikimedia(q, pick=idx + qi):
                src = "wikimedia-licensed"
                break
        # 3) Pexels photo (most specific query)
        if src == "gradient" and ENG.fetch_pexels_photo(
                ladder[0], api_key, os.path.join(work_dir, f"img_{idx}.jpg")):
            ken_burns_restrained(os.path.join(work_dir, f"img_{idx}.jpg"), raw, dur, w, h, fps)
            src = "pexels-photo"
    # 4) always-safe gradient (last resort only)
    if src == "gradient":
        ENG.animated_bg(raw, idx, w, h, dur=max(2.0, dur))

    # grade
    graded = os.path.join(work_dir, f"beat_{idx}.mp4")
    ok = _grade(graded, graded, lut_name=style.get("lut"),
                grain=style.get("grain", 7), shake=style.get("shake", 0),
                vignette=True)
    if not ok:
        graded = raw
    print(f"  [visual {idx}] {src}" + (f"  (credit: {credit})" if credit else ""))
    return graded, credit, src


if __name__ == "__main__":
    import configparser
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(ROOT, "config.ini"))
    # quick license-filter sanity: confirm it rejects NC and accepts CC-BY
    print("license_ok cc-by:", _license_ok("cc-by-4.0"))
    print("license_ok cc-by-nc:", _license_ok("cc-by-nc-4.0"))
    print("license_ok public domain:", _license_ok("public domain"))
    print("license_ok (empty):", _license_ok(""))
