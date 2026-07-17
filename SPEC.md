# Faceless Viral Engine — Spec

Generated via gstack `/office-hours` -> `/spec` handoff.

## The one-line product
A hands-off pipeline that turns a niche idea into a finished, publish-ready
vertical video (voice + visuals + retention-tuned edit + drafted title/description)
and drops it into a `publish/` queue. You press publish.

## Locked premises
- P1: Fully automated faceless pipeline. Niche -> AI script -> AI voice -> visuals
  -> auto-edit (retention recipe) -> drafted title/description/hashtags -> lands
  in `publish/` for human approval.
- P2: Free-tier stack first, ~$0/month. Script: local Ollama (gemma4). Voice:
  edge-tts (free). Visuals: animated gradient + kinetic captions, OR optional
  Pexels stock (free API key). Paid upgrades (ElevenLabs, AI video) are optional.
- P3: Primary engine = YouTube Shorts (clearest faceless monetization). IG/TikTok
  handled as auto-draft reposts (publish kept in human hands).
- P4: Runs on a schedule, produces N videos/day into the queue.

## Honest claim (do NOT oversell)
Editing + proven retention patterns raise watch-time. Watch-time is what the
algorithm rewards. This raises *odds*, not a millions guarantee. Money comes from
consistency + YT monetization + affiliate links in description, over months.
Any marketing says "the retention system top faceless channels use, automated."

## Pipeline stages
1. topic     — rotate through niche seed topics (topics.txt)
2. script    — Ollama gemma4 -> structured JSON (hook, beats, title, description,
               hashtags, visual_query). Falls back to template if Ollama down.
3. voice     — edge-tts -> voice.mp3 + word-level timings (for karaoke captions)
4. visuals   — Pexels images if key set; else animated gradient backgrounds
5. edit      — ffmpeg: 9:16, per-beat image cuts w/ Ken Burns, crossfade,
               karaoke caption overlay, optional bg music ducking
6. metadata  — title/description/hashtags -> publish/<name>.txt
7. queue     — finished mp4 + txt sit in publish/ until human publishes

## Retention recipe (the actual value)
- Hook in first 2 seconds (the script's `hook` field is forced on screen first)
- Cut every 2-4 seconds (one visual per beat)
- Large kinetic captions, current word highlighted
- Vertical 9:16, safe-area safe
- Ends with a loopable engagement cue ("follow for more")

## Out of scope (v1)
- Auto-publishing (explicit user requirement: publishing stays human)
- Multi-tenant SaaS / billing
- AI-generated video (Pika/Runway) — optional later upgrade
- Copyrighted music — use royalty-free only or none

## Success metric
One real, watchable 30-45s Short produced end-to-end into publish/ with correct
metadata. Then: schedule N/day, publish consistently, track RPM.
