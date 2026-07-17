# Office Hours Design Doc — Faceless Engine Income Play

Generated: 2026-07-17 (office-hours / YC diagnostic mode)
Project: C:\Users\Avishkar\faceless-engine
Mode: Startup (goal = income, not hobby). Stage: pre-product.

## What I understand about the project
- You built a fully-local, free faceless-Shorts pipeline on Windows RTX 3050 6GB.
  It generates premium videos hands-off: Chatterbox voice (-14 LUFS), word-level
  gold karaoke captions, licensed Wikimedia visuals, seeded variation.
- Scheduler is LIVE: 3 videos/day at 09:00 / 13:00 / 19:00 land in publish/.
- 12/12 tests pass. Generation is genuinely automated.
- Publishing is MANUAL by your choice (no auto-post).
- You have ZERO demand evidence: nothing published, no channel, no views.
- Your own honest verdict as a viewer: the output isn't watchable yet — the
  visual floor collapses (latest 2 videos are 100% gradient placeholder).

## Two real signals from this session
1. NO PROOF: you checked online, got "evergreen niche" (generic, not evidence).
   You have no data that anyone will watch. Normal for pre-launch; must be fixed
   by a real test, not more research.
2. ENGINE FLOOR FAILS THE VIEWER TEST: you put yourself in the viewer's shoes and
   rejected the output. Disk confirms it: the latest two runs are 100% gradient
   beats = instant swipe. The pro features (voice/captions) are fine; the visual
   baseline collapses under real (unattended, flaky-network) conditions.

## Research synthesis (faceless-YT niche landscape, 2026)
Sources pulled live: YouTube search "faceless youtube niches 2026".
- Nate Curtiss — "The ONLY Faceless AI Niches You Should Try in 2026" (39K views):
  8 niches framed around retention + revenue structure. Credible.
- Sonuji Technical — "40+ High RPM AI Faceless Niches" (11h old): high-RPM angle.
- Ayushman Pandita — "Best AI Faceless Channel Niches To Make Money 2026" (113K).
- Satish K — "9 Unique Faceless Ideas 2026" (275K) = Hostinger affiliate bait; ignore.

Niche themes that recur across credible channels:
  A. Money/Finance breakdowns — high RPM, accuracy-sensitive
  B. Curiosity / "did you know" facts — YOUR niche: low RPM ($1-4), max competition,
     retention is everything
  C. Reddit/relationship story narration (AITA etc.) — high retention, reused-content risk
  D. History / "what if" alternate history — strong retention, needs B-roll
  E. Tech / AI explainers — high RPM, fast-moving
  F. Luxury / real-estate tours — high RPM, competitive
  G. Motivation / self-improvement — saturated, low differentiation
  H. Productivity — medium

HONEST READ: your current niche (B) is the HARDEST to earn in. Lowest RPM, most
competition, and it dies in the first 2 seconds. That is precisely why your
"looks bad to me" instinct is right — in this niche a gradient = instant swipe.

RESEARCH IS NOT PROOF. It shortens the plausible niche list. It does not tell you
you will earn. Only a 30-day publish test does.

## PREMISES (must agree before any build)
P1. The pipeline must never ship a video a human would swipe past in 2s. Today it
    can (100% gradient). This is a BASELINE defect, not a pro feature. — agree?
P2. Earning requires real viewer signal we do not have. The next step is a measured
    test, not more features. — agree?
P3. Publishing stays manual (your choice). The machine makes; you click upload. — agree?
P4. Niche should be narrowed to a wedge before the test, not kept broad. — agree?

## ALTERNATIVES (Phase 4)
APPROACH A — Baseline-first, then 30-day wedge test (RECOMMENDED)
  Summary: Fix the visual floor so a run NEVER produces gradient-only; pick ONE
    narrow wedge from topics; publish daily 30 days; read retention/views.
  Effort: S (baseline fix is small; test is just you clicking upload)
  Risk: Low
  Pros: Closes the exact defect you named; produces real demand data fast;
    keeps the machine you already built.
  Cons: Requires YOU to publish daily (no auto-post, by choice); 30 days of
    low/no income while testing.
  Reuses: engine_pro.py, scheduler, measure.py (wire the API key).

APPROACH B — Keep building pro features, publish later
  Summary: More captions styles, LUTs, motion; ship when "perfect."
  Effort: M
  Risk: High (builds a car no one has driven; zero proof it earns)
  Pros: Feels productive.
  Cons: Delays the only thing that matters (viewer signal); perfection is a
    delay tactic. REJECTED by office-hours discipline.

APPROACH C — Pay/outsource the test (agency or thumbnails)
  Summary: Hire edits or buy a course to skip the learning curve.
  Effort: $ (not code)
  Risk: Med (money before proof)
  Pros: Faster if the niche works.
  Cons: You still have no proof the niche earns; cost before signal.
  Reuses: nothing local.

RECOMMENDATION: A. It targets the defect you personally identified (P1) and
produces the missing evidence (P2) without more speculative building.

## THE ASSIGNMENT (mandatory, real-world)
1. (Baseline fix — later session, not now) Make build_beat_visual never fall back
   to 100% gradient: cache a local licensed-image pool at build time so an
   unattended run always has watchable footage. Confirm by generating a video and
   checking publish/<vid>.txt shows zero "gradient" beats.
2. (You, this week) Create one channel. Pick ONE wedge from topics.txt (e.g.
   "deep-sea / ocean mysteries" or "space facts") — not the whole 16-topic list.
3. (You, 30 days) Publish the 3 daily videos to that channel. Track: views at 7
   days, average view duration %, swipe-away in first 2s (YouTube shows this).
4. (Decision gate, day 30) If a wedge clears ~5k views/7d and >40% avg view
   duration, double down. If not, switch wedge (measure.py promotes winners).
   If nothing earns after 2 wedges, the niche thesis is wrong — pivot, don't build.

## DECISION (2026-07-17, user choice B)
Switch the wedge to a higher-RPM niche the engine already serves. Within B, the
chosen wedge is HISTORY / DOCUMENTARY, with Finance explainers deferred as a
later expansion.

Rationale (from RESEARCH_faceless_niches_2026.md):
- History/Documentary RPM $4–9, SATURATION: LOW (ReelPilot). Finance $12–22 but
  SATURATION: HIGH + accuracy/ad-sensitive (wrong advice burns trust; YouTube
  restricts financial content). For a hands-off pipeline, low-saturation +
  low-accuracy-liability wins.
- Evergreen: NicheRoza notes history "ages slowly, meaning videos keep earning
  for years" — matches the passive-income goal better than any high-RPM flash.
- Fixes the gradient defect by side-effect: Wikimedia is rich in public-domain
  history imagery (CC0/CC-BY), so the licensed-visual ladder has abundant
  sources -> fewer gradient fallbacks in unattended runs.

## Actions for the NEXT build session (not this one — office-hours hard gate)
1. Fix visual floor: build_beat_visual must never ship 100% gradient. Cache a
   local licensed-image pool at build time so an unattended run always has
   watchable footage. Verify: generate a video, confirm publish/<vid>.txt shows
   zero "gradient" beats.
2. Prune topics.txt to the History/Documentary wedge (e.g. lost civilizations,
   bizarre historical events, lesser-known wars, historical "what if"). Keep
   script_pro tone + visual query ladder aligned to history.
3. Wire measure.py: get a free YouTube Data API v3 key, record upload->video_id
   in work/upload_map.json, so winners auto-promote.
4. You publish the 3 daily videos to one channel for 30 days. Track views@7d,
   avg view duration %, swipe-away in first 2s.
5. Day-30 gate: wedge clears ~5k views/7d AND >40% avg view duration -> double
   down; else switch wedge (measure.py promotes winners); two dead wedges ->
   niche thesis wrong, pivot.

## Open questions (carried)
- YouTube Data API v3 key: yes (auto-rank) or manual rank from Studio?
- Finance expansion later: yes after History proves it can earn, or never?

## Status
DONE — design doc + research complete; wedge decision (History/Documentary)
made with data-backed rationale. No code written this session (office-hours
hard gate). Build session owns the gradient fix + topics.txt prune.
