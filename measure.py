"""measure.py — Measurement loop for the Faceless Viral Engine (Plan Q11).

Pulls each published video's YouTube stats via the YouTube Data API v3, then
promotes winners / demotes losers back into topics.txt so the channel
self-improves. This is the "earn with minimal time" half of the north star:
the engine runs unattended (Task Scheduler) AND learns from results.

DESIGN (soft-fail by contract — must NEVER break the daily render):
  - If no YouTube API key is configured -> skip quietly, log, exit 0.
  - If the upload map is missing/empty -> skip quietly, log, exit 0.
  - If any API call fails -> log the error, continue with what we have.
  - Never raises; the scheduler must not die because YouTube is unreachable.

Mapping: the engine writes publish/<vid>.txt metadata (TITLE/DESCRIPTION/...).
The human records, in work/upload_map.json, the mapping
  { "<youtube_video_id>": "<vid_XXXX.mp4>" }
measure.py reads that map, resolves the topic from the local .txt, pulls stats,
and rewrites topics.txt so winning topics rise and losing topics sink.

Usage:  python measure.py            # uses config + work/upload_map.json
"""

from __future__ import annotations

import configparser
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(ROOT, "work")
PUBLISH = os.path.join(ROOT, "publish")
MAP_PATH = os.path.join(WORK, "upload_map.json")
LOG_PATH = os.path.join(WORK, "measure.log")
TOPICS_PATH = os.path.join(ROOT, "topics.txt")

# Promotion thresholds (views in first ~7 days is a fine proxy for Shorts wins).
WIN_VIEWS = 5000      # at/above -> promote (move topic toward top)
LOSE_VIEWS = 300      # at/below -> demote (move toward bottom)


def _log(msg: str):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(f"[measure] {msg}")
    try:
        os.makedirs(WORK, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def _api_key(cfg: configparser.ConfigParser) -> str:
    if cfg.has_section("youtube"):
        return cfg.get("youtube", "api_key", fallback="").strip()
    return ""


def _topic_from_metadata(vid_name: str) -> str:
    """Pull the TITLE line from the engine's publish/<vid>.txt metadata."""
    txt = os.path.join(PUBLISH, vid_name.replace(".mp4", "") + ".txt")
    if not os.path.exists(txt):
        return ""
    try:
        with open(txt, encoding="utf-8") as f:
            for line in f:
                if line.startswith("TITLE:"):
                    return line[len("TITLE:"):].strip()
    except Exception:
        pass
    return ""


def _pull_stats(video_id: str, api_key: str) -> dict | None:
    """YouTube Data API v3 videos.list?part=statistics. Returns stats dict or None."""
    try:
        import requests
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={"part": "statistics", "id": video_id, "key": api_key},
            timeout=20,
        )
        if r.status_code != 200:
            _log(f"API {video_id} -> HTTP {r.status_code}; skipping")
            return None
        items = r.json().get("items", [])
        if not items:
            return None
        return items[0].get("statistics", {})
    except Exception as e:
        _log(f"API {video_id} error: {e}; skipping")
        return None


def _read_topics() -> list[str]:
    if not os.path.exists(TOPICS_PATH):
        return []
    with open(TOPICS_PATH, encoding="utf-8") as f:
        return [t.strip() for t in f if t.strip() and not t.startswith("#")]


def _write_topics(topics: list[str]):
    with open(TOPICS_PATH, "w", encoding="utf-8") as f:
        f.write("# Topic seeds (auto-ranked by measure.py: winners rise, losers sink)\n")
        for t in topics:
            f.write(t + "\n")


def run(cfg: configparser.ConfigParser):
    api_key = _api_key(cfg)
    if not api_key:
        _log("no [youtube] api_key in config.ini -> measurement loop skipped (soft-fail)")
        return
    if not os.path.exists(MAP_PATH):
        _log("no work/upload_map.json -> nothing to measure yet (soft-fail)")
        return
    try:
        with open(MAP_PATH, encoding="utf-8") as f:
            upload_map = json.load(f)
    except Exception as e:
        _log(f"upload_map.json unreadable: {e} (soft-fail)")
        return

    if not upload_map:
        _log("upload_map.json empty -> nothing to measure (soft-fail)")
        return

    scored: list[tuple[str, int]] = []  # (topic, views)
    for vid_id, vid_name in upload_map.items():
        topic = _topic_from_metadata(vid_name)
        if not topic:
            continue
        stats = _pull_stats(vid_id, api_key)
        views = int(stats.get("viewCount", 0)) if stats else 0
        scored.append((topic, views))
        _log(f"{vid_id}: views={views} topic='{topic[:50]}'")

    if not scored:
        _log("no scorable videos this run")
        return

    # Sort: winners (>=WIN_VIEWS) first, losers (<=LOSE_VIEWS) last, middle by views.
    def _key(item):
        topic, views = item
        if views >= WIN_VIEWS:
            return (0, -views)
        if views <= LOSE_VIEWS:
            return (2, views)
        return (1, -views)

    scored.sort(key=_key)

    # Merge with existing topics.txt so we don't lose human-added seeds.
    existing = _read_topics()
    existing_set = {t.lower() for t in existing}
    promoted = [t for t, _ in scored if t.lower() not in existing_set]
    new_topics = promoted + existing  # winners/topics first, then the rest

    _write_topics(new_topics)
    winners = [t for t, v in scored if v >= WIN_VIEWS]
    _log(f"rewrote topics.txt: {len(new_topics)} topics, "
         f"{len(winners)} promoted this run")


def main():
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(ROOT, "config.ini"))
    try:
        run(cfg)
    except Exception as e:
        # Hard guarantee: measurement loop never crashes the pipeline.
        _log(f"unexpected error (ignored): {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
