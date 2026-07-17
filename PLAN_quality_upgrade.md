# Plan: Faceless Viral Engine — Top-Notch Quality Upgrade (4 Waves)

> **GOVERNING RULE (user-locked):** This plan — produced via /autoplan (gstack) —
> is the LOCKED STANDARD for the build. Build strictly to it; do NOT improvise or
> silently downgrade. At checkpoints (after build + periodically), re-audit EVERY
> locked decision below and report gaps honestly. Holding the standard is
> non-negotiable. Resilience chains in the plan (e.g. Chatterbox→Kokoro→edge→silent)
> are the ONLY permitted fallbacks, and only at the tier the environment forces.

> Status: APPROVED-WITH-TASKS (full /autoplan re-audit 2026-07-17). Source of truth for the build.
> Companion docs: SPEC.md (v1 product spec), DESIGN.md (visual+audio identity),
> research_2026_shorts_standards.md, karaoke_captions_audio_spec.md,
> faceless_realism_research.md, FREE_LLM_FALLBACK_RESEARCH.md.

## Problem

The v1 engine (engine.py) produces valid faceless Shorts but reads as "AI slop":
- Captions: one full sentence, static, whole beat (not word-by-word karaoke).
- Voice: flat Kokoro, no prosody variation, no audio mastering.
- Pacing: 4-6s beats (too slow; but 1.5s spam also reads as AI-slop — target 2.5-4s restrained).
- Editing: crossfade every beat (floaty, no creative variation).
- Visuals: identical Ken-Burns zoom on every still; occasional static look.
- Variation: one template hook, one structure, every video feels cloned.
- Monetization safety: Wikimedia visuals pulled with NO license check (strike risk).

The user explicitly wants the engine to feel premium, credible, human — not
amateur AI — and to clear YouTube's reused-content/uniqueness bar so it can
actually earn.

## Goal

Upgrade the engine to top-2026 faceless-Shorts quality while staying 100% free/
local on the existing Windows RTX 3050 6GB box, keeping the current engine.py as
a safe fallback, and keeping publishing in human hands (no auto-post).

## Locked decisions (from chat)

- Voice engine: Chatterbox primary (isolated venv .venv_voice, torch 2.6, no
  conflict with main Kokoro). Kokoro->edge-tts->silent kept as resilience chain.
- Build all 4 waves straight through, then show ONE fully-upgraded test video.
- Business model: Fork A (user posts own videos, earns from views).
- DESIGN.md is the source of truth for typography/color/motion/audio identity.

## Architecture

Keep engine.py untouched. Add new modules (imported by a new engine_pro.py):

- captions.py      (EXISTS, draft) — word-timings via stable-ts + Hormozi karaoke ASS
- style.py         (NEW) — seeded VideoStyle, pools, no-repeat state, anti-clone fingerprint
- voice_pro.py     (NEW) — Chatterbox render + prosody variation + audio mastering chain
- edit_pro.py      (NEW) — 2.5-4s restrained cuts, transition pool, minimal SFX, LUTs, grain, shake, keyword overlays
- script_pro.py    (NEW) — hook/structure rotation, banned-cliche list, humanizer pass
- visuals_pro.py   (NEW) — motion b-roll priority, slow Ken-Burns (capped 1.10x), license filter (Wikimedia extmetadata)
- engine_pro.py    (NEW) — orchestrates the above; same CLI (--topic/--count) as engine.py

Config: extend config.ini with [quality] section (voice_engine, captions_style,
luts_dir, music_dir, sfx_dir, variation_seed, anti_clone). No breaking changes.

## Wave 1 — Voice + Captions (the two loudest slop signals)

### Voice (voice_pro.py)
- Chatterbox primary: `ChatterboxTTS.from_pretrained(device="cuda")`,
  `generate(text, exaggeration=0.6, cfg=0.6)`. Optional one-time voice clone via
  audio_prompt_path (brand voice).
- Prosody variation: split script into sentences; per-sentence rate 0.94-1.08,
  pitch ±1.5-2 st, real silence pauses (comma 120-220ms, period 300-450ms,
  dramatic reveal 600-1000ms). Synthesize per sentence, concatenate with numpy +
  inserted silence. This also fixes Kokoro's chunk-truncation risk for the
  fallback path.
- Breaths: splice 3-4 sampled breath .wav clips at -18dB before ~30% of sentences.
- Room tone: faint pink noise (-45 to -50 dB) under whole track.
- Audio mastering (ffmpeg): highpass 80 -> lowpass 12k -> de-mud EQ (250Hz -2) ->
  presence (3k +2) -> warmth (180Hz +2) -> deesser -> acompressor ->
  loudnorm I=-14 TP=-1.0 LRA=11. Resample to 48k mono.
- Resilience: Chatterbox -> Kokoro -> edge-tts -> silent-track. Log which used.

### Captions (captions.py — extend)
- Word timings: stable-ts (base.en) on the rendered voice .wav -> (word,start,end).
  (aeneas alternative if exact-script alignment wanted.)
- Hormozi-style ASS: Anton font (installed), ALL-CAPS, white #FFFFFF fill +
  6px black stroke, one keyword per page highlighted warm gold #F5C518 (+25% size),
  word-by-word reveal with scale pop 0.85->1.2->1.0 (~150ms), position 66% down.
- 2-3 words per visible page. Lower-middle safe area.
- Verified earlier: ffmpeg has ass filter; Anton + Montserrat Black fonts installed.

## Wave 2 — Editing + Hook + Loop

### edit_pro.py
- Cut interval: target **2.5-4s** (range 2-5s), distributed with jitter so sum==
  audio length (a pacing curve, not flat). 2026 premium = restraint; 1.5s spam
  reads as AI-slop (retention blindness). N beats = round(audio_dur/3).
  Expose `cut_rate` and `sfx_density` as config flags for A/B.
- Transition mix (weighted): hard cut >=70%, one branded gold accent-wipe
  (consistent), gentle crossfade only between major topic shifts, zoom-punch
  reserved for ONE intentional reveal per video.
- Hook: curiosity-gap OR number-first forced on screen + caption by <=1.0s, sound-
  off readable. Optional soft riser SFX peaking at hook frame.
- Pattern interrupt: ONE zoom-punch / color flash / SFX stinger on the single
  key reveal (not every 4-6s).
- SFX (restrained + consistent vocabulary): one soft whoosh -15dB on the SINGLE
  key reveal; one subtle tick -20dB on big-number changes. NOT a whoosh per cut.
- Seamless loop: last frame matches first; end re-triggers hook question.
- Audio: sidechain-duck music under voice (sidechaincompress threshold=-28dB
  ratio=6); music peak -20 to -25 dBFS; then loudnorm pass on final mix.

## Wave 3 — Visual Realism

### visuals_pro.py
- Motion b-roll FIRST: Pexels video > Coverr/Mixkit (free) > Wikimedia still.
- Wikimedia license filter (monetization safety, P0): request iiprop=extmetadata,
  accept only CC0/PublicDomain/CC-BY/CC-BY-SA; skip NC/ND/non-free/unknown.
  On all rejected: fall back to always-safe gradient (never publish unlicensed).
- Attribution: auto-append CC-BY/CC-BY-SA credit (artist+license+URL) to the .txt
  metadata; optional small on-screen credit.
- Ken-Burns motion: slow, calm single-direction zoom (capped ~1.10x over the beat,
  gentle pan) — restraint per 2026 research; NOT the 2025 random move-pool
  (zoom 1.06-1.20 random focal point), which now reads as AI-slop.
- Handheld micro-shake: optional, subtle sinusoidal crop 3-5px, seeded (0 ~25% of videos), only on b-roll; NOT on stills.
- Film grain: noise 4-8 (light, random per video) — hides digital cleanliness without noise.
- Per-video LUT: random.choice from curated premium .cube set (teal-orange, warm
  film, moody, clean-bright, desaturated-doc) via ffmpeg lut3d.
- Vignette: subtle (~PI/5), low strength.
- Big keyword/number overlay: separate from captions; Anton, 18-22% screen height,
  white+black stroke, scale-pop 150ms on emphasis beats.

## Wave 4 — Variation Engine + Writing

### style.py
- **Brand constants (FIXED across the whole library — recognizability):**
  ONE consistent Chatterbox narrator voice (cloned once) + ONE gold #F5C518
  accent + ONE caption system (Anton keywords + Roboto body, white/black-stroke).
  Captions: **keyword-only ALL-CAPS** (mixed-case body) — the 2026 restraint
  reversal of the earlier ALL-CAPS-everything tactic; reads credible, not "shouting/AI".
  These NEVER vary — they ARE the channel's identity (2026 table stakes:
  one voice + one color + consistent captions = recognizable faceless brand).
- **Per-video variety (VARIES via seeded VideoStyle):**
  hook format (7 types) | intro style | caption animation | music mood |
  transition profile (incl. accent-wipe flavor) | LUT | pacing curve (2.5-4s
  jitter seed) | grain+shake amounts. All from ranges/pools, reproducible via seed.
- Anti-clone: state file tracks last N videos' fingerprints over the VARYING
  axes only; reject a new video matching a recent one on >=3 of 5 axes
  (hook+LUT+music+transition+pacing). Passes YouTube reused-content/uniqueness
  policy AND satisfies the "uniqueness is needed, creativity still needed" rule.
- Log style + seed to run_status.log.
- Net: each video is restrained/premium (per-video), yet distinct (cross-video)
  — premium AND unique, not template spam.

### script_pro.py
- Rotate hook formats + structures (listicle / deep-dive / myth-vs-truth / story /
  question->answer / then-vs-now / cause->effect) + tone per video.
- Banned cliche list: "You won't believe", "Did you know", "Little did they know",
  "In today's video". Temperature 0.8-1.0 if using Ollama; humanizer pass strips
  em-dash overuse, "moreover/furthermore", balanced hedging.
- Require >=1 concrete number + >=1 named place/person + >=1 surprising juxtaposition
  per script (specificity reads human).
- Varied CTA/ending.

## Out of scope (unchanged from SPEC.md)
- Auto-publishing (human publishes).
- Multi-tenant SaaS / billing.
- AI-generated video (Pika/Runway) — optional later.
- Copyrighted music — royalty-free only or none.

## Success metric
One real 25-35s Short produced end-to-end by engine_pro.py into publish/ that:
- uses Chatterbox voice with prosody + mastering,
- shows word-by-word Hormozi karaoke captions,
- cuts ~2.5-4s restrained with varied transitions + minimal reveal SFX,
- has a licensed/attributed visual per beat,
- carries a premium consistent look (DESIGN.md) but a distinct style seed,
- passes the anti-clone check.
Then (NOW IN SCOPE per revision 2026-07-17): (1) register the Windows Task
Scheduler job so engine_pro.py runs N/day hands-off (human still publishes from
publish/ — no auto-post), and (2) a measurement loop that pulls each video's
YouTube stats, then promotes winners / demotes losers back into topics.txt so the
channel self-improves. Both were previously DEFERRED; pulled in because the user
confirmed the north star (hands-off earning) requires them, and the scheduler
scaffolding already exists.

## Risks / open questions
- Chatterbox per-video render speed on RTX 3050 (fp16, ~1-3s/100 words expected).
- stable-ts word-alignment accuracy on Chatterbox output (regroup mitigates drift).
- Montserrat Black font fetch failed earlier (got corrupt); Anton is valid and
  installed — proceed with Anton, retry Montserrat later.
- LUTs: 6 free .cube files sourced locally into assets/luts/ (teal-orange, warm
  film, moody, clean-bright, desaturated-doc, vivid-gold) — RESOLVED (no licensing risk).
- SFX assets: whoosh/riser/text-pop/breath/roomtone sourced locally into assets/sfx/
  — RESOLVED (generated, no licensing risk).
- SCHEDULER CADENCE BUG (found in revision): `setup_scheduler.bat` line 12 uses
  `/SC DAILY /ST 00:00 /RI 240 /DU 24:00` — repeats every 4h from midnight
  (6 runs/day at 00/04/08/12/16/20), NOT the 3 runs at 09/13/19 the comment
  claims. The exact-times alternative (3 separate `schtasks /Create` lines) is
  correct and currently commented out. Fix: use the 3 explicit tasks.
- MEASUREMENT LOOP DEPENDENCY: pulling YT stats needs the YouTube Data API v3
  (OAuth client or API key) — a real external-auth dependency the v1 engine
  never had. Without it the loop can't run. Mitigation: `measure.py` must fail
  soft (skip promotion, log) when no creds, so the engine still runs unattended.
- config.ini [quality] comment (lines 53-60) is STALE: claims Chatterbox can't
  run due to disk; the engine now renders Chatterbox-GPU on `D:\venv_voice`. Fix
  the comment so it doesn't contradict `voice_engine = chatterbox`.

<!-- /autoplan restore point: N/A (no prior plan state; this file is the original plan) -->

<!-- AUTONOMOUS DECISION LOG -->
## Decision Audit Trail
| # | Phase | Decision | Classification | Principle | Rationale | Rejected |
|---|-------|----------|---------------|-----------|-----------|----------|
| 1 | CEO | Keep scope at 4 waves + license filter (Fork A) | Mechanical | P1 completeness | Plan already covers the full quality surface; no reduction needed | reduce-scope |
| 2 | CEO | Add free-asset sourcing (LUTs, SFX, Montserrat) as explicit tasks | Mechanical | P2 boil lakes | Assets are in blast radius (engine needs them); <1d CC effort | defer assets |
| 3 | Design | Adopt DESIGN.md gold #F5C518 (not cliche #FFE600) | Taste | P5 explicit | Distinct accent reads premium; user can override | cliche yellow |
| 4 | Design | Anton primary caption font (Montserrat retry later) | Mechanical | P6 pragmatic | Anton valid+installed; Montserrat fetch corrupted | Montserrat-now |
| 5 | Eng | Keep engine.py untouched; new modules + engine_pro.py | Mechanical | P4 DRY / safe fallback | No rewrite of working code; isolation limits blast radius | mutate engine.py |
| 6 | Eng | Isolated .venv_voice for Chatterbox (no torch bump on main) | Mechanical | P3 pragmatic | Prevents breaking Kokoro on main Py3.12 | merge into main venv |
| 7 | Eng | Word timings via stable-ts on rendered audio (not aeneas) | Taste | P5 explicit | stable-ts robust on any TTS; aeneas needs exact text match (fragile w/ prosody splice) | aeneas-only |
| 8 | Eng | Add run_status.log + anti-clone fingerprint check | Mechanical | P1 completeness | Unattended safety + YT uniqueness policy compliance | skip logging |
| 9 | DX | Keep same CLI (--topic/--count) as engine.py | Mechanical | P5 explicit | Zero new learning curve; progressive disclosure via config.ini | new CLI |
| 10 | DX | Document asset-setup step in README/run notes | Mechanical | P1 completeness | TTHW must stay <5 min after assets added | undocumented assets |
| 11 | Eng | REVERSAL: pivot edit style from the earlier 2025 1.5s hyper-edit tactic to 2026 restraint (2.5-4s cuts, minimal SFX, ALL-CAPS keywords only + Roboto body) | User Challenge (resolved) | P1 completeness + north star | Newest 2026 competitor research shows the 1.5s hyper-edit now reads as AI-slop; user's north star is "premium, credible, not AI-slop" — restraint serves it. | keep 1.5s hyper-edit |
| 12 | CEO | Pull Task Scheduler daily run into plan scope | Mechanical | P2 boil lakes | Scaffolding already exists; user confirmed hands-off earning is the north star | keep deferred |
| 13 | CEO | Pull measurement loop (YT stats -> topic promotion) into plan scope | User Challenge (scope add) | P1 completeness | User directed it; BUT adds YT Data API dependency (soft-fail mandated) | keep deferred |
| 14 | Eng | Fix setup_scheduler.bat cadence bug (3 explicit tasks, not /RI 240 loop) | Mechanical | P5 explicit | Active command produced 6 runs/day at wrong times vs commented intent | leave as-is |
| 15 | DX | Add scheduler-activation + YT-creds-config as documented setup steps | Mechanical | P1 completeness | Unattended operation needs one-time admin activation + a creds field | undocumented |
| 16 | Eng | RESTORE edge-tts tier in voice fallback chain (was dropped in build) | User Challenge (found defect) | P1 completeness | Full autoplan re-audit (2026-07-17) found render_voice only did Chatterbox->Kokoro->silent; plan locks Chatterbox->Kokoro->edge->silent (Decision #6). Restored edge-tts + fixed stale docstring | drop edge tier |
| 17 | Eng | Set caption body font to Roboto-Bold/Lato-Bold per DESIGN.md (not hard Anton) | Mechanical | P3 pragmatic | DESIGN.md specifies Roboto/Lato Bold body, ALL-CAPS keywords only; build used Anton for body (deviation) | Anton body |
| 18 | DX | Add unit test for voice fallback chain (Q8 gap) | Mechanical | P1 completeness | Earlier autoplan (Q8) listed a voice-fallback-chain test as "must add" but tests.py never had it; Q16 fix must be locked by a test | skip test |

---

# /autoplan Review — Faceless Viral Engine Quality Upgrade

> Methodology run on Hermes/Windows (non-git, no Codex CLI, no gstack logging
> binaries). Phases CEO→Design→Eng→DX executed at full analytical depth.
> Auto-decisions made via the 6 autoplan principles. Dual-voice Codex unavailable
> (no Codex CLI on this host) — Claude single-reviewer mode, supplemented by the
> three research agents already run this session (realism, 2026 standards, karaoke spec).

## Phase 1 — CEO Review (Strategy & Scope)

**0A — Premise challenge.** Premises restated and evaluated:
- P1 (fully automated faceless pipeline): VALID. Matches user's "minimal time" requirement and Fork A.
- P2 (free-tier stack, ~$0/mo): VALID. Chatterbox/F5/stable-ts all free/local; confirmed torch 2.6 fits 6GB.
- P3 (YouTube Shorts primary): VALID. Clearest faceless monetization; IG/TikTok repost deferred (human).
- P4 (scheduled N/day): VALID but DEPENDENT — depends on Wave 4 resilience + Task Scheduler, not yet built. Flagged: scheduling is a follow-up, not part of this plan's success metric.
- User premise (premium/credible, not AI slop): VALID and is the plan's true driver. The 4-wave structure directly serves it.

No premise is clearly wrong. Accept all (P6: accept reasonable premises).

**0B — Existing code leverage map.**
- `engine.py` run_once/build_script/media_duration/load_config → reused as-is by engine_pro.py (import, don't rewrite).
- `captions.py` build_ass + stable-ts align → extends existing (word-level added).
- `fetch_wikimedia_photo` → wrap with license filter in visuals_pro.py (don't replace).
- `make_voice` Kokoro/edge fallback → reused inside voice_pro.py resilience chain.
- ffmpeg NVENC detection → reused.

**0C — Dream state.** CURRENT: valid but templated MVP. THIS PLAN: premium, varied, monetization-safe faceless channel. 12-MONTH IDEAL: hands-off daily engine + measurement loop promoting winners. This plan covers the quality floor; measurement loop is correctly out of scope (deferred, not forgotten).

**0C-bis — Alternatives considered.**
- Alt A: Buy ElevenLabs + Pika video (paid). Rejected — violates P2 free-tier, user wants $0.
- Alt B: Just tune captions + voice, skip variation engine. Rejected — without Wave 4 the channel still reads cloned; fails the user's core premise (P1 completeness).
- Alt C: Rebuild as a single monolith engine_pro.py. Rejected — P4 DRY/safe-fallback; modular + untouched engine.py is lower risk.

**0D — Scope decisions.** In blast radius + <1d CC: asset sourcing (LUTs/SFX/fonts), run_status.log, anti-clone state file, config [quality] section. All APPROVED (P2). Out of blast radius: measurement loop, auto-publish, AI video — DEFERRED (P3), consistent with SPEC.md out-of-scope.

**0E — Temporal interrogation.** HOUR 1: one video renders with Chatterbox + Hormozi captions. HOUR 6+: batch of N with distinct style seeds, license-clean, logged. No hour where the plan leaves the user worse off than v1.

**0F — Mode: SELECTIVE EXPANSION.** Hold core scope, cherry-pick the asset-sourcing + logging expansions.

**Sections 1-10 (summary of evaluation):** Scope correct. Strategic risk = asset dependency (LUTs/SFX) — mitigated by explicit task + free sources identified. Competitive risk = YT reused-content policy — mitigated by anti-clone check (Wave 4). 6-month regret risk = "engine feels samey" — mitigated by variation engine. REVISION 2026-07-17: Task Scheduler + measurement loop pulled into scope (decisions #12, #13) — now the plan covers the full hands-off-earning path the user's north star requires. No critical strategic gaps.

**CEO completion summary:** Scope sound, premises valid, completeness-oriented. 1 taste decision (accent color), 0 open user challenges. 2 scope additions (scheduler, measurement) surfaced as mechanical/User-Challenge decisions #12-#13.

## Phase 2 — Design Review

UI scope: YES (this is a video product; typography/color/motion are the UI).
DESIGN.md exists → used as the system of record.

**Design dimensions (rated 0-10):**
1. Typography — 9. Anton/Montserrat Black, ALL-CAPS, specific, not default slop. (Montserrat fetch failed → Anton primary; -1 for missing alt.)
2. Color — 9. Single disciplined gold accent, teal-orange grade, explicit "no neon/gradient/purple" rule. Distinct from template.
3. Motion — 8. 2.5-4s restrained cuts, transition pool, move-pool, shake, grain specified. (LUT set not yet sourced → -1.)
4. Hierarchy — 8. Hook forced ≤1.0s sound-off; big keyword overlay separate track. Clear first/second/third read.
5. Specificity — 9. Exact hex, fonts, dB levels, cut rates in DESIGN.md + plan.
6. Missing states — 7. Video product has no loading/error UI, but engine failure states (voice fallback, encode retry, license-reject→gradient) ARE specified. (No "empty topic" UX — minor, deferred.)
7. Accessibility/contrast — 8. White-on-black-stroke caption spec meets contrast; sound-off readability required.

**Design consensus (single-reviewer, research-backed):** DESIGN.md is coherent and premium. One taste call (gold vs cliche yellow) — auto-picked gold. No structural redesign needed.

## Phase 3 — Eng Review

**Section 1 — Architecture (ASCII).**
```
engine_pro.py (orchestrator, same CLI)
  ├─ script_pro.py   (hook/structure rotation, humanizer, banned-cliches)
  ├─ voice_pro.py    (.venv_voice on D:\venv_voice: Chatterbox-GPU + prosody + mastering; fallback Kokoro→edge→silent)
  ├─ captions.py     (stable-ts word timings -> Hormozi ASS)   [extends existing]
  ├─ visuals_pro.py  (motion b-roll + license filter + slow Ken-Burns + LUT/grain/shake + keyword overlay)
  ├─ edit_pro.py     (2.5-4s restrained cuts, transition pool, minimal SFX, sidechain duck, loop)
  ├─ style.py        (seeded VideoStyle, no-repeat state, anti-clone fingerprint)
  ├─ measure.py      (NEW — YT Data API pull -> promote/demote topics.txt; soft-fail)
  ├─ run_daily.bat / setup_scheduler.bat (Task Scheduler activation; human publishes)
  ├─ run_status.log  (per-run audit)
engine.py (UNTOUCHED — safe fallback)
config.ini [quality] (additive section, no breaking change)
```
Coupling: low (each module has one job, engine_pro wires them). Blast radius: new files only + config.ini additive. Safe.

**Section 2 — Code quality.** DRY: reuses engine.py helpers (load_config, media_duration, make_voice fallback) rather than duplicating. Naming: module_function convention matches existing. No abstraction overload (P5 explicit).

**Section 3 — Test review (test diagram).**
| Codepath | Test | Exists? |
|----------|------|---------|
| build_ass (captions) | unit: ASS escaping, timestamp math, keyword highlight | partial (captions.py has build_ass; tests.py covers old ASS) |
| license filter (visuals_pro) | unit: accept CC0/CC-BY, reject NC/ND/unknown | NEW — must add |
| style seed/fingerprint (style.py) | unit: no-repeat + anti-clone ≥3/5 axes | NEW — must add |
| voice fallback chain | unit: Chatterbox fail → Kokoro → edge → silent | NEW — must add |
| config [quality] parse | unit: additive, no break | extend tests.py |
| end-to-end render | integration: one video produced | manual (publish/) |
Gaps identified: license filter, anti-clone, voice fallback, config parse need unit tests. Auto-decided: ADD (P1 completeness), CC effort <1 day. Test plan artifact: `~/.gstack/projects/unknown/quality-upgrade-test-plan.md` (written below).

**Section 4 — Performance.** Chatterbox fp16 on RTX 3050: ~1-3s/100 words expected (research-backed). stable-ts base.en: ~real-time. NVENC encodes fast. Batch of N is I/O + GPU serial; acceptable for N/day schedule. No N+1 / memory leak risk identified (per-run temp dirs rmtree'd like v1).

**Failure modes registry:**
| Failure | Impact | Mitigation |
|---------|--------|-----------|
| Chatterbox import/inference fails | run dies | fallback chain Kokoro→edge→silent (Wave 1) |
| stable-ts misaligns words | caption drift | regroup=True; fall back to per-sentence timing |
| All Wikimedia results reject license | no visual | gradient fallback (never publish unlicensed) |
| NVENC mux fails | no output | retry libx264 (Wave resilience) |
| Two videos share ≥3/5 style axes | YT reused-content flag | anti-clone check (Wave 4) |
| LUT/SFX asset missing | degraded look | graceful skip + log |

**Eng completion summary:** Architecture sound, low coupling, test gaps identified and scheduled. 0 user challenges, 1 taste (stable-ts vs aeneas). REVISION: added measure.py (YT API dependency, soft-fail) + scheduler cadence fix (#14); both in blast radius, <1d CC.

**Research-driven REVERSAL (recorded post-review):** the plan was initially scoped on an *earlier* 2025 faceless-explainer research that prescribed 1.5s hyper-cuts, a whoosh on every cut, and ALL-CAPS everywhere. The later 2026 competitor research (8 channels + r/NewTubers + 2026 creator threads) reversed this: the hyper-edit look now reads as AI-slop / retention-blindness, and premium = restraint (3-5s cuts, slow Ken Burns, ONE reveal zoom-punch, keyword-only ALL-CAPS, minimal consistent SFX). This reversal was absorbed as Decision #11 (pivot to 2026 restraint) and is now encoded in Wave 2 (2.5-4s cuts, `cut_rate`/`sfx_density` config flags), Wave 3 (slow Ken-Burns capped 1.10x), and DESIGN.md. The earlier 1.5s assumption is explicitly superseded — not a retained option.

## Phase 3.5 — DX Review

DX scope: YES (developer/operator is the user; CLI + config are the interface).
**DX dimensions (rated 0-10):**
1. Getting started — 8. Same `python engine_pro.py` CLI; config.ini additive. Asset setup (LUTs/SFX/font) is the only new step → document it (TTHW target <5 min).
2. CLI naming — 9. Reuses --topic/--count; guessable.
3. Error messages — 7. v1 prints stage progress; new modules must print which fallback fired + log to run_status.log. (Improve: single failure summary line.)
4. Docs — 7. README needs asset-setup section; DESIGN.md is the visual spec.
5. Upgrade path — 9. engine.py untouched → instant rollback; config additive.
6. Escape hatches — 8. config.ini [quality] toggles (voice_engine, captions on/off, variation_seed) let user override every opinionated default.
7. Env friction — 8. Isolated venv avoids dependency conflict with main Py3.12.
8. Config consistency — 9. Matches existing configparser style.

**DX scorecard overall: 8/10.** TTHW current ~3 min (after assets) → target <5 min. REVISION: scheduler-activation + YT-creds config are new documented setup steps (#15); TTHW stays <5 min. No critical DX gaps.

## Cross-Phase Themes
- **Asset dependency** flagged in CEO (scope), Eng (test gaps reference assets), DX (TTHW). High-confidence: the plan must include an explicit asset-sourcing task or first run will fail. → Added as task Q2.
- **Monetization safety** (license filter + anti-clone) appears in CEO (YT policy), Design (uniqueness), Eng (failure mode). High-confidence: this is the difference between demo and earner. → Kept as P0.
- **Hands-off operation** (new, revision 2026-07-17): spans CEO (#12/#13 scope add), Eng (#14 cadence bug + measure.py), DX (#15 setup steps). High-confidence: the user's confirmed north star (earn with minimal time) is only realized once the engine runs unattended AND learns from results. → Scheduler (Q10) + measurement loop (Q11) now in scope.

## Deferred to TODOS.md (rationale)
- AI-generated video (Pika/Runway) — paid; defer per SPEC.md.
- Multi-platform auto-repost (IG/TikTok) — human-publish requirement; defer.
- Auto-publishing — ALWAYS out of scope (user publishes; no auto-post).
NOTE: Task Scheduler daily run and the measurement loop were DEFERRED in v1 of
this plan but PULLED INTO SCOPE by revision 2026-07-17 (see Q10, Q11). They are
no longer deferred.

## Implementation Tasks (aggregated)
- [ ] **Q1 (P1, CC: ~2h) — voice_pro.py**: Chatterbox primary in .venv_voice + per-sentence prosody (rate 0.94-1.08, pitch ±1.5-2st, dramatic 600-1000ms pause) + breaths + room tone + ffmpeg mastering (loudnorm -14 LUFS) + fallback chain (Chatterbox→Kokoro→edge→silent).
- [ ] **Q2 (P1, CC: ~1h) — asset sourcing**: download 6 free .cube LUTs (teal-orange/warm/moody/clean/desat) + whoosh/riser/text-pop SFX (royalty-free) + retry Montserrat Black font; document in README.
- [ ] **Q3 (P1, CC: ~2h) — captions.py extend**: stable-ts word timings on rendered voice → Hormozi ASS (Anton, gold #F5C518 keyword, 2-3 words/page, scale-pop, 66% down).
- [ ] **Q4 (P1, CC: ~2h) — edit_pro.py**: 2.5-4s restrained cuts (configurable cut_rate for A/B), transition pool (hard≥70%/branded gold-wipe/crossfade≤15%/zoom-punch only on single reveal), hook≤1.0s sound-off, ONE reveal whoosh -15dB + subtle tick -20dB on number changes + optional riser -18dB@0, sidechain-duck music, seamless loop.
- [ ] **Q5 (P0, CC: ~1.5h) — visuals_pro.py**: motion b-roll priority (Pexels/Coverr/Mixkit) + Wikimedia license filter (extmetadata; accept CC0/CC-BY/CC-BY-SA; reject NC/ND/unknown→gradient) + attribution in .txt + slow Ken-Burns (capped 1.10x) + optional handheld shake (3-5px, b-roll only) + grain (6-12) + LUT + vignette + big keyword overlay.
- [ ] **Q6 (P1, CC: ~1.5h) — style.py + script_pro.py**: seeded VideoStyle (hook/intro/caption-anim/music/transition/LUT/pacing/grain pools) + no-repeat state + anti-clone fingerprint (≥3/5 axes) + hook/structure rotation + banned-cliche list + humanizer pass + require concrete number/named entity.
- [ ] **Q7 (P1, CC: ~1h) — engine_pro.py + config.ini [quality]**: wire modules, same --topic/--count CLI, additive config, run_status.log.
- [ ] **Q8 (P1, CC: ~1h) — tests.py extend**: license filter accept/reject, anti-clone ≥3/5, voice fallback chain, config [quality] parse, captions ASS escaping.
- [ ] **Q9 (P2, CC: ~30m) — verify**: produce ONE 25-35s video end-to-end; human review of look/voice/license.
- [ ] **Q10 (P1, CC: ~30m) — scheduler activate**: fix `setup_scheduler.bat` cadence bug (use 3 explicit `schtasks /Create` at 09/13/19, not the `/RI 240` loop); register Task Scheduler job `FacelessEngineDaily` once (admin); `run_daily.bat` already calls `engine_pro.py --count N` and logs to `work\scheduler.log`. Human publishes from `publish/`. Document in README.
- [ ] **Q11 (P1, CC: ~3h) — measurement loop (measure.py)**: YouTube Data API v3 pull (views/retention/likes per video) -> promote winners (move their topic to top of topics.txt, weight >1) and demote losers (drop or down-weight). Soft-fail when no YT creds (skip promotion, log). Writes back into `topics.txt`. Needs `youtube_api_key` or OAuth in config.ini.
- [ ] **Q12 (P2, CC: ~15m) — config.ini hygiene**: fix STALE [quality] comment (lines 53-60) that claims Chatterbox can't run on this box; it now renders GPU on `D:\venv_voice`. Keep `voice_engine = chatterbox`.

---

## Implementation Status (built 2026-07-17; FULL autoplan RE-AUDIT 2026-07-17)

### Prior build (Q1–Q9)
All 9 tasks implemented. Modules: `engine_pro.py` (orchestrator), `voice_pro.py`,
`captions.py`, `visuals_pro.py`, `edit_pro.py`, `style.py`, `script_pro.py`.
`engine.py` left untouched (safe fallback). `assets/` holds 6 .cube LUTs + 5 SFX
(generated locally, no licensing risk). `tests.py` = 11 passing at that point.

**Voice (per plan Wave 1, CHATTERBOX PRIMARY):** The plan locks Chatterbox as
primary. Its venv on **D:\\venv_voice** (`torch==2.6.0+cu124` + `chatterbox-tts`)
renders on GPU. `voice_pro.py` prefers `D:/venv_voice` and checks CUDA *inside the
venv*. `config.ini [quality] voice_engine = chatterbox` → renders on GPU when ready.
`engine.py` left untouched (safe fallback).

**Verified-met bars (audit against locked plan):** word-level stable-ts karaoke
captions (Anton, gold #F5C518, ALL-CAPS keywords only); 2.5–4s restrained cuts +
varied transitions + single reveal zoom-punch + minimal SFX; licensed/attributed
Wikimedia CC visual per beat (NC/ND rejected); curated 6-LUT premium set; seeded
VideoStyle variation + anti-clone fingerprint (≥3/5 axis reject) working;
engine.py untouched.

### Full-pass RE-AUDIT fixes (2026-07-17) — what the earlier passes MISSED
A from-scratch re-run of /autoplan caught real spec-vs-code violations and gaps:
- **Q16 / Decision #16 — voice fallback chain was broken.** The build's
  `render_voice` only did Chatterbox→Kokoro→**silent**; the plan-locked 4th tier
  **edge-tts** (Decision #6) had been silently dropped. FIXED: restored `_voice_edge()`
  tier + `_kokoro_cfg()` so the chain is exactly Chatterbox→Kokoro→edge-tts→silent.
  Also corrected a stale module docstring that wrongly claimed Chatterbox ran
  "CPU-safe to avoid the RTX 3050 CUDA init crash" (code is GPU-first).
- **Q17 / Decision #17 — caption body font deviation.** `captions.py` hard-coded
  `BODY_FONT = "Anton"`, but DESIGN.md specifies a mixed-case Roboto/Lato Bold body
  with Anton only for keywords. FIXED: body now prefers Roboto-Bold/Lato-Bold if
  present, else Anton (cohesion fallback) — never bare Anton contradicting DESIGN.md.
- **Q12 — STALE config comment.** `[quality]` comment still said Chatterbox "CANNOT
  run on this box" / "1.4GB free on C:". FIXED: comment now matches reality (GPU on
  D:\venv_voice; drops through Kokoro→edge→silent if CUDA absent).
- **Q18 / Decision #18 — missing unit test.** Q8 had listed a voice-fallback-chain
  test as "must add" but tests.py never contained it. ADDED: `test_voice_fallback_chain_order`
  asserts all 4 tiers are present and the chain ends in a silent pad. This was the
  gap that let Q16's defect ship undetected — now locked.
- **Q10 (DONE)** — `setup_scheduler.bat` cadence bug fixed (Decision #14): replaced
  the `/RI 240 /DU 24h` loop (6 runs/day at wrong times) with 3 explicit `schtasks`
  at 09/13/19. `run_daily.bat` already calls `engine_pro.py --count N` → `publish/`.
- **Q11 (DONE)** — `measure.py` written: YouTube Data API v3 pull → promotes winners /
  demotes losers into `topics.txt`. Soft-fail by contract (no key / empty map / API
  error → log + exit 0, never breaks the daily render). Needs `[youtube] api_key`
  + `work/upload_map.json` (human fills after uploading).

**Final state: 12/12 tests pass. Q1–Q12 built; Q16/Q17 code fixes applied; Q18 test added.**
One accepted deviation (unchanged): venv lives on D:\\venv_voice (C: had no room for
the 2.5GB wheel + 2.1GB model) — functionally identical isolated venv, isolation
(Decision #6) held.

**Known constraints for the first test video:**
- No Pexels API key → visuals use licensed Wikimedia stills (license-filtered)
  + Ken-Burns, falling back to animated gradient (never unlicensed).
- stable-ts word timing needs the voice venv (present); if it fails, beat-level
  caption fallback is used.
- Add `pexels_api_key` in config.ini for real motion b-roll (the premium look).
- Add `[youtube] api_key` + `work/upload_map.json` to activate the measurement loop.

## Review Scores
- CEO: sound scope, premises valid (Fork A confirmed), completeness-oriented. 1 taste (accent), 0 open user challenges. Scheduler + measurement loop added (D).
- Design: 8.4/10 avg. DESIGN.md coherent/premium. 1 taste (gold vs cliche yellow). Q17 body-font deviation found + fixed.
- Eng: architecture sound, low coupling. 2 defects found by full re-audit (Q16 edge-tts drop, Q18 missing test) — both closed. 1 taste (stable-ts vs aeneas).
- DX: 8/10. TTHW <5 min after asset docs. Scheduler + YT-creds are new setup steps (#15). measure.py soft-fail keeps unattended runs safe.
- Voices: single-reviewer (no Codex key on this host) + 3 research agents + fresh code re-read.

## GSTACK REVIEW REPORT
STATUS: APPROVED-WITH-TASKS (FULL RE-AUDIT 2026-07-17). Two prior autoplan runs were re-executed from scratch; the fresh pass caught 4 real defects/gaps the earlier passes missed (broken voice fallback chain, caption body-font deviation, stale config comment, missing fallback-chain test) and closed all of them — Q16/Q17 code fixes + Q18 test added (now 12/12 tests). Scheduler (Q10) cadence bug fixed; measurement loop (Q11) written with soft-fail. 18 audit-trail decisions (#1–#18). No open user challenges. 2 taste decisions (accent #F5C518, stable-ts) surfaced at the gate. No critical gaps remaining; measurement loop adds a YT API dependency with mandated soft-fail.

