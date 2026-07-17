<!-- /autoplan restore point: /c/Users/Avishkar/.gstack/projects/faceless-engine/main-autoplan-restore-20260718-001517.md -->
---
status: ACTIVE
title: Faceless Engine — Full gstack Pipeline Plan (30-day earning goal)
---

# Faceless Engine — Full gstack Pipeline Plan (30-day earning goal)

Rewrite of PLAN_ceo_review.md. The earlier plan used ONE gstack skill
(/plan-ceo-review) + a partial /review. This version uses the FULL gstack
pipeline we had not wired: /autoplan (CEO+design+eng+DX in one), /plan-eng-review,
/plan-design-review, /plan-devex-review, /health gate, /review gate, /ship gate,
/context-save, /learn, /retro, /qa-only, plus our own measure.py loop.

Environment (verified 2026-07-17/18):
- Host: Windows 10, MSYS bash. Toolchain present: bun 1.3.14, codex 0.144.5 (NO
  API key), gh authed (avi5129), git 2.51, node v24, jq 1.8.2 (installed +
  added to Windows user PATH via setx).
- faceless-engine is now a LOCAL git repo on `main` (initial commit 1b92468) with
  remote `origin` -> https://github.com/avi5129/faceless-engine.git (PRIVATE).
  NO push performed yet (user directive: wire remote, do not push/build).
- codex_reviews = disabled (Claude-only reviews until a key is added).

====================================================================
## 1. THE 30-DAY CONSTRAINT (overrides long-horizon thinking)
- A new YouTube channel CANNOT be ad-monetized in 30 days (YT needs 1k subs AND
  (4k watch-hrs/365d OR 10M Shorts views/90d)). The 30-day target MUST be
  OFF-YouTube revenue, not YT ad-RPM.
- Off-platform revenue paths that pay in <=30 days (no YT approval):
  1. Affiliate/product links in description + pinned comment. Engine ALREADY has
     the slot: engine.py:492 `affiliate = "...<your-affiliate-or-link>"`.
  2. Own digital product (PDF/Notion pack) linked in every video — highest margin.
  3. Patreon/memberships (needs followers, no YT approval).
  4. Sponsors — unreliable by day 30, ignore for the gate.
- 30-day metric: (views x click_rate x conversion x payout) > 0 repeatedly.
  NOT watch-hours. YT ads become a month-4+ bonus.
- 30-day EARNING GATE: >=1 tracked conversion from channel videos within 30 days
  => revenue path works. Zero conversions despite decent views => fix the OFFER.

====================================================================
## 2. FULL GSTACK WORKFLOW (the features we missed, now sequenced)
Run in this order. Each gate blocks the next until green. NO push/build until
the user lifts the hold (current directive).

WAVE 0 — STRATEGY (done earlier, retained as inputs)
  - /office-hours  -> DESIGN_officehours_2026-07-17.md (wedge = History, finance
    deferred). DONE.
  - /plan-ceo-review -> this plan's predecessor (CEO findings F1-F7). DONE.
  - RESEARCH_faceless_niches_2026.md (real RPM tables). DONE.

WAVE 1 — LOCK THE PLAN (run NOW, gstack-native, single command)
  - /autoplan  -> runs CEO -> design -> eng -> DX review in one pass, single
    reviewer (Hermes CLI = single reviewer, no git branch/PR/Codex dual-voice).
    Produces a locked plan file with all 6 auto-decision principles applied.
    (Replaces the manual CEO-review we did; automates design/eng/DX we skipped.)
  - Then per-skill deep locks we SKIPPED earlier:
    - /plan-eng-review   : lock architecture, data flow, edge cases, TEST plan.
      Directly addresses F2 (caption hard-gate) + F1-p2 (beat/voice length
      conflict) as DESIGN CONTRACTS, not afterthoughts.
    - /plan-design-review: rate each design dimension 0-10 (visual floor, hook
      retention, caption legibility, brand consistency). F3 (gradient floor) is
      a design-dim failure -> becomes a hard gate.
    - /plan-devex-review : DX-mode. TTHW (time-to-first-video), friction for the
      human's once-daily publish step, persona traces (the "do nothing" promise).
      Confirms Level 1 (gen hands-off) and Level 2 (human publishes) boundary.

WAVE 2 — CODE QUALITY GATE (before any fix lands)
  - /health  -> type checker + linter + tests + dead-code dashboard. Establishes
    the pre-change baseline (12/12 tests currently pass). Any fix must not drop
    this below the baseline.
  - /review  (Claude-only) -> pre-landing review on each change vs `main`.
    Our earlier static review already found: F1 beat-duration bug (AUTO-FIXED in
    edit_pro.py), F2 caption hard-gate (P1, unfixed), F3 gradient shadow path
    (P2), F4 revenue-link placeholder (P3, needs your link), F7 config drift.

WAVE 3 — BUILD (HELD until user lifts hold)
  - Apply fixes as gstack issues: F1 (done), F2 caption-fallback, F1-p2
    beat/voice reconciliation, F3 persistent offline corpus, F4 revenue link,
    F7 config drift, long-form path (wedge B).
  - measure.py wired (API key or manual Studio ranking) — item 6.
  - /ship gate (HELD): test -> review -> workspace-aware version queue -> push ->
    open PR. Currently BLOCKED by user directive (no push/build yet).

WAVE 4 — OPERATE + LEARN (the compounding loop)
  - Scheduler already live 3/day -> publish/ (human publishes, Level 2).
  - measure.py promotes winning topics (self-improvement loop).
  - /context-save after each significant change; /context-restore on resume.
  - /learn to capture durable project quirks; /retro weekly.
  - /qa-only on a published Short to find real viewer-facing bugs (blank frames,
    caption desync) without changing code.

====================================================================
## 3. CARRIED FINDINGS (from the earlier review, must be resolved in WAVE 3)
F1  [AUTO-FIXED] edit_pro.py:38-39 beat-duration residual dumped on beat 0 ->
    20-44s monster first beats. Fixed: distributed across all beats.
F1-p2 [P2, OPEN] When voice duration/n > 4.0s, 2.5-4.0s spec is impossible +
    length==audio can't hold -> uniform >hi static beats. DESIGN CONTRACT needed
    in /plan-eng-review: cap beats OR shorten script voice.
F2  [P1, OPEN] edit_pro.py:174-183 captions are a SILENT-HARD-GATE (raise
    RuntimeError). Any caption glitch kills the whole run with no video, silently.
    Fix: catch -> fall back to beat-level captions from script text -> log WARN.
F3  [P2, OPEN] visuals_pro.py:317-319 gradient fallback reachable in normal ops
    (flaky Wikimedia) -> recurring 100%-gradient videos. Fix: persistent offline
    history corpus BEFORE Wikimedia (PLAN item 1).
F4  [P3, BLOCKER for 30-day] engine.py:492 revenue link is placeholder
    "<your-affiliate-or-link>". Needs your decision: Amazon Associates books /
    course link / own digital product. Wire as [revenue] affiliate_link in config.
F5  [P3, LOW] edit_pro.py:259 subtitles filter fragile on Windows path-colon;
    safe today (separate work_dirs). Harden later.
F6  [INFO] voice_pro.py:60/92 dead CPU-chatterbox path (docstring says never used,
    and it isn't wired). No bug; note for clarity.
F7  [P3, OPEN] config.ini `niche=curiosity` but wedge=History; voice_engine vs
    provider drift. Fix in build session (write niche=history, reconcile).

====================================================================
## 4. GATES (what blocks shipping — explicit)
G1  /autoplan + /plan-eng-review + /plan-design-review + /plan-devex-review all
    produce locked plan files. Until then, NO build. (user hold aligns with this)
G2  /health baseline must hold (>=12/12 tests, no new dead code) after each fix.
G3  /review (Claude-only) on each change vs main -> 0 unresolved P1 findings.
G4  30-day EARNING GATE: >=1 tracked conversion from channel videos.
G5  (future) YT monetization threshold met — month 4+, NOT a 30-day target.

====================================================================
## 5. DECISIONS NEEDED (user)
D1  Revenue link for F4 (blocks 30-day earning): A) Amazon Associates books,
    B) course/educational link, C) own digital product. (unresolved)
D2  Long-form cadence alongside 3 Shorts/day (suggest ~10-12/month). (unresolved)
D3  Finance expansion after History proves earning: yes or never? (unresolved)
D4  Push to GitHub? User said wire remote but "do not proceed" — confirm before
    any `git push` / /ship.

====================================================================
## 6. WHAT IS DONE vs HELD (status)
DONE:
  - Environment: jq installed+PATHed, gstack bins run on Windows bash, gh authed,
    faceless-engine is a git repo with `origin` remote (private), codex_reviews=disabled.
  - Strategy: office-hours (History wedge), CEO review (F1-F7), niche research.
  - F1 bug auto-fixed.
  - 12/12 tests pass; scheduler live 3/day.
HELD (user directive: do not proceed to build):
  - /autoplan + per-skill plan reviews (WAVE 1) — ready to RUN on your go.
  - All WAVE 3 build fixes (F2, F1-p2, F3, F4, F7, long-form).
  - /ship, /qa-only, measure.py wiring, push to GitHub.

====================================================================
## 7. NEXT ACTION (when user lifts hold)
Run /autoplan, then /plan-eng-review + /plan-design-review + /plan-devex-review
to lock the contracts for F1-p2/F2/F3. Then build against those contracts, gated
by /health + /review. No push until D4 confirmed.

================================================================
## 8. /autoplan PHASE 1 — CEO REVIEW (run 2026-07-18, dual voice: Hermes + OpenCode)
Mode: SELECTIVE EXPANSION (auto-decided, P6 bias-to-action but disciplined by P1).

### 8.0A — Premise challenge (specific premises, evaluated)
- P1 "Owner earns doing nothing." FALSE as stated. Code proves Level 2 = human
  manually publishes 3/day from publish/. The promise is "generate hands-off,
  human publishes." This is a marketing-vs-reality gap, not a code gap.
  → Challenge severity CRITICAL (it is the product's headline claim).
- P2 "History/Documentary is the defensible wedge." Supported by RPM tables
  ($4–9, low saturation, evergreen, PD-rich Wikimedia). ACCEPTED.
- P3 "30-day target needs OFF-YouTube revenue." TRUE by YouTube policy
  (1k subs + 4k watch-hrs/10M Shorts). Off-platform (affiliate/product) is the
  only <=30d path. ACCEPTED.
- P4 "'curiosity' is a niche." CHALLENGED HARDEST by OpenCode: curiosity is a
  TONE, not a market. Config still says niche=curiosity (F7 drift). A phantom
  audience until History wedge is proven. → severity HIGH.
- P5 "Sell engine later, earn first." OpenCode: sequencing the cost center
  (broad engine) ahead of the revenue center (History wedge). Partially wrong.
- P6 "Engine is the product." OpenCode: it's a publishing pipeline, not a
  business. Automates the cheap 20% (rendering), leaves the value 80%
  (distribution/audience/offer) manual or absent.

### 8.0B — Existing code leverage map
- edit_pro.py `_beat_durations` (F1) FIXED in code (distributes residual).
- edit_pro.py `edit_video_pro` → caption hard-gate at line 193 RAISES RuntimeError
  (F2 UNFIXED in code — contradicts plan).
- engine.py:492 affiliate placeholder (F4 UNFIXED — gate cannot fire).
- config.ini niche=curiosity vs History (F7 UNFIXED).
- voice_pro.py dead CPU-chatterbox path (F6, INFO).
- visuals_pro.py gradient fallback reachable on flaky Wikimedia (F3 OPEN).

### 8.0C — Dream state (CURRENT → THIS PLAN → 12-MONTH IDEAL)
CURRENT: 12/12 tests pass, scheduler live 3/day, but 0 videos published, 3 carried
  bugs (F2/F4/F7) unfixed, wedge undelivered.
THIS PLAN: gstack pipeline wired, market-pm says pursue B (sell) then test A.
12-MONTH IDEAL: a real earning channel OR a sold engine with paying builders;
  the "do nothing" promise honest (generate hands-off + scheduled publish, human
  does 1 tap/day or auto-publish after vetted).

### 8.0C-bis — Approaches (effort/risk)
A) Fix F2+F7, prove History wedge earns (off-platform) BEFORE any new feature.
   Effort: ~2-3 days. Risk: low. Coverage: HIGHEST (unblocks + proves market).
B) Build B (sell engine) first, skip wedge proof. Effort: ~1 wk. Risk: HIGH
   (selling an unproven engine to builders; trust gap).
C) Keep generalizing the engine (current drift). Effort: ongoing. Risk: CRITICAL
   (NO-GO stands; runway burned on breadth).
→ AUTO-DECIDED: A (P1 completeness + P2 boil-lakes). B deferred to after A.

### 8.0D — Mode-specific (SELECTIVE EXPANSION)
Hold scope. Cherry-pick only the unblocks: F2 caption-fallback, F7 History config,
F4 offer choice. Reject new features (long-form, measure.py AI rank) until wedge proven.

### 8.0E — Temporal interrogation
- HOUR 1: scheduler fires → edit_pro.py hits caption hard-gate on first real
  non-template run (stable-ts missing/incompatible) → RuntimeError → ZERO video.
  The 30-day clock starts ticking with no output. CRITICAL.
- HOUR 6+: 3 blank/gradient videos pile in publish/ (F3) because Wikimedia flaky
  and no offline corpus. Human publishes gradient slop → channel credibility dies.
- DAY 30: affiliate gate reads placeholder → 0 conversions by definition. FAIL.

### 8.0F — Mode select confirmation: SELECTIVE EXPANSION (auto-decided).

### 8.1-8.10 — Review sections (findings)
- Sec1 Strategy: NO-GO verdict reaffirmed by 2nd voice. (examined, flagged)
- Sec2 Failure modes: see registry below. (examined)
- Sec3 Market: market-pm memo (B pursue / A test) is the market evidence. (examined)
- Sec4 Scope: 3 carried bugs unfixed = scope leakage. (flagged)
- Sec5 30-day math: fails for cold channel ad-rev; off-platform is the only path
  and is BLOCKED by F4 placeholder. (flagged CRITICAL)
- Sec6 "Do nothing" claim: false as stated; needs honest reframe. (flagged)
- Sec7 Wedge: History undelivered in code (F7). (flagged)
- Sec8 Dual-voice: OpenCode ran, agreed NO-GO. (examined)
- Sec9 Config drift: niche=curiosity persists. (flagged)
- Sec10 Earning gate: structurally unmet (F4). (flagged)

### Error & Rescue Registry
| Failure | Trigger | Rescue | Status |
| F2 caption glitch | stable-ts fails | fall back to beat-level caps + WARN | UNFIXED (raises) |
| F3 gradient | Wikimedia flaky | offline History corpus first | UNFIXED |
| F4 no offer | affiliate placeholder | pick offer, wire config | UNFIXED (blocks gate) |
| F7 drift | config mismatch | niche=history | UNFIXED |

### Failure Modes Registry
| # | Mode | Likelihood | Impact | Critical? |
| F2 | caption RuntimeError → 0 video | HIGH (first real run) | CRITICAL | YES |
| F4 | gate can't fire | CERTAIN (placeholder) | CRITICAL | YES |
| F7 | wrong niche renders | HIGH | HIGH | YES |
| F3 | gradient slop published | MED | REPUTATION | NO |

### Dream-state delta
Plan leaves us WORSE than 12-mo ideal: still 0 shippable videos, still NO-GO,
until F2/F7 fixed. The pipeline wiring (gstack/opencode) is the ONE real gain.

### CEO Completion Summary
| Item | State |
| Premises | 4 accepted, 2 challenged (curiosity niche, do-nothing claim) |
| Wedge | History chosen, NOT delivered in code (F7) |
| 30-day gate | BLOCKED by F4 placeholder |
| Verdict | NO-GO (both voices) until F2+F7 fixed |

### 8.5 — DUAL VOICE CONSENSUS TABLE (CEO)
```
CEO DUAL VOICES — CONSENSUS TABLE:
═════════════════════════════════════════════════════════════
  Dimension                  Hermes     OpenCode   Consensus
  ───────────────────────── ────────── ────────── ─────────
  1. Premises valid?         Mixed      Mixed      CONFIRMED (2 challenged)
  2. Right problem?          No-GO      No-GO      CONFIRMED
  3. Scope calibration?      Leaky      Cost-first WRONG   DISAGREE (taste)
  4. Alternatives explored?  Yes        Yes        CONFIRMED
  5. Market risk covered?    Yes(mkt-pm) Yes       CONFIRMED
  6. 6-mo trajectory?        Risky      Regret     CONFIRMED
═════════════════════════════════════════════════════════════
CONFIRMED = 5/6. DISAGREE on scope sequence (taste — surfaced at gate).
Both voices: still NO-GO until F2+F7 fixed.
```

### 8 — DECISION AUDIT TRAIL (CEO)
| # | Phase | Decision | Class | Principle | Rationale | Rejected |
|---|-------|----------|--------|-----------|-----------|----------|
| 1 | CEO | Mode=SELECTIVE EXPANSION | Mech | P6 | hold scope, unblock only | broaden |
| 2 | CEO | Approach A (fix F2+F7 first) | Taste | P1/P2 | unblocks output + proves wedge | B (sell-first) |
| 3 | CEO | Challenge "curiosity niche" | User-Challenge | — | tone≠market, phantom audience | accept premise |
| 4 | CEO | Reframe "do nothing" claim | User-Challenge | — | human publishes=not nothing | accept claim |
| 5 | CEO | Premise gate: user confirms | Gate | — | human judgment required | — |

**PREMISE GATE (the one non-auto-decided AskUserQuestion): see Phase 4 clarifies.**

PHASE 1 COMPLETE. OpenCode: NO-GO + F2/F7 prescription. Hermes: NO-GO.
Consensus: 5/6 confirmed, 1 taste disagreement (scope sequence). Passing to Phase 2.

================================================================
## 9. /autoplan PHASE 2 — DESIGN REVIEW (UI scope=yes; vertical Shorts visual design)
Dual voice: Hermes + OpenCode (real, read visuals_pro.py/edit_pro.py).

### Design litmus scorecard (0-10, OpenCode)
| Dim | Score | Note |
| 1 Visual floor / no-empty-frames | 9 | CC-filter + designed title-card fallback = standout |
| 2 Caption legibility | 8 | gold #F5C518 per_page=2; risk gold-on-light-LUT contrast |
| 3 Hook retention first 3s | 6 | NO structural hook strategy; weakest designed dim |
| 4 Brand consistency | 9 | single gold accent across captions/wipe/title |
| 5 Motion restraint | 8 | hard-cut>=70%, KB capped 1.05-1.10x; fights AI-slop |
| 6 Audio mix / ducking | 4 | NO ducking spec given; music can bury VO |
| 7 Seamless-loop | 5 | no loop strategy stated; unverified |

Biggest design risk (OpenCode): **Audio mix (dim 6)** — absent ducking spec means
music likely buries voiceover, degrading the ONE element that carries retention.
(Note: edit_pro.py DOES implement sidechaincompress ducking at lines 248-253, but
it is conditional on bg_music file existing AND the design review couldn't confirm
it triggers; the spec being unstated = the risk.)

### Design decisions (auto-decided, P5 explicit + P1 completeness)
- D2.1 Add caption scrim behind gold text (fix dim-2 contrast risk). AUTO: approve
  (P1, <1 file). 
- D2.2 Add a structural HOOK beat (pattern-interrupt / text-on-title-card tease in
  first 2.5-4s). AUTO: approve as design contract (P1). 
- D2.3 Document the ducking spec explicitly + verify it fires (dim 6). AUTO: approve
  (P5 — explicit over clever; make the behavior a stated contract).
- D2.4 Seamless-loop strategy: only if used for feed-loop; mark OPTIONAL (P3 pragmatism).

PHASE 2 COMPLETE. OpenCode scored 7 dims; biggest risk = audio mix + hook. Passing to Phase 3.

================================================================
## 10. /autoplan PHASE 3 — ENG REVIEW (architecture, edge cases, tests)
Dual voice: Hermes + OpenCode (read engine.py/edit_pro.py/visuals_pro.py).

### 10.1 Architecture ASCII (current)
```
engine.py (orchestrator)
  ├─ script_pro.py  (topic/beats/hook)         [F7: niche=curiosity still]
  ├─ voice_pro.py   (kokoro->edge->silent)      [F6 dead CPU-chatterbox path]
  ├─ visuals_pro.py (CC-filter + title-card fb) [F3 gradient reachable]
  ├─ edit_pro.py    (beats + captions + audio)  [F2 RuntimeError hard-gate]
  ├─ captions.py    (stable-ts align)           [gate dependency]
  └─ engine.py:write_metadata  (affiliate slot) [F4 placeholder]
scheduler (schtasks 3/day) -> publish/ (HUMAN publishes = Level 2)
```
Coupling: edit_pro imports engine/captions/visuals_pro. Single point of total
failure = caption align (F2). 

### 10.2 Code quality
- F2 silent-hard-gate (edit_pro:193) = worst arch risk (OpenCode). Produces ZERO
  output, not bad output. Worse than the old 40s bug.
- config.ini hand-rolled comment-stripper (engine.py:39-59) preserves '#' in URLs
  but is silent-corruption risk (OpenCode).
- ffmpeg filtergraph built via 100+ lines string concat; one missing SFX file
  shifts input indices and SILENTLY MUTES audio (OpenCode).

### 10.3 Test review (NEVER compressed)
- tests.py: 12 pass. Coverage: _beat_durations (F1 fixed), script/voice/visuals
  happy paths.
- GAP (OpenCode + Hermes): NO test for degraded-but-valid path — captions absent
  but audio/visuals good SHOULD yield a publishable (caption-less) video. The gate
  only has an all-or-nothing branch.
- GAP: no caption-path coverage at all; F2's RuntimeError untested.
- Decision: add test_f2_caption_fallback (caption align fails -> video still
  produced) + test_f2_venv_missing. AUTO-approve (P1 completeness, <1 file).

### 10.4 Performance
- NVENC detection good. Beat residual distribution fixed. No N+1. OK.

### Eng consensus table
```
ENG DUAL VOICES — CONSENSUS TABLE:
  Dim                Hermes   OpenCode  Consensus
  1 Architecture     Fragile  Fragile   CONFIRMED (F2=SPOF)
  2 Test coverage    Gap      Gap       CONFIRMED
  3 Perf             OK       OK        CONFIRMED
  4 Security         local    local     CONFIRMED (low surface)
  5 Error paths      F2       F2        CONFIRMED (critical)
  6 Deploy risk      sched    sched     CONFIRMED
CONFIRMED = 6/6.
```

### Eng decisions (audit)
| # | Phase | Decision | Class | Principle | Rationale | Rejected |
|---|-------|----------|--------|-----------|-----------|----------|
| 6 | Eng | F2 -> fallback to beat-level caps + WARN (not RuntimeError) | Taste | P5 | unblock output | keep hard-gate |
| 7 | Eng | Add caption-fallback + venv-missing tests | Mech | P1 | close test gap | defer |
| 8 | Eng | Document ducking spec as contract | Mech | P5 | explicit | leave implicit |
| 9 | Eng | Keep ffmpeg index-math but add guard for missing SFX | Taste | P3 | avoid silent mute | rewrite filtergraph |

PHASE 3 COMPLETE. Both voices: F2 = critical SPOF. Passing to Phase 3.5 (DX).

================================================================
## 11. /autoplan PHASE 3.5 — DX REVIEW (dev-tool product, sell-to-builders)
Dual voice: Hermes + OpenCode (read engine.py/config/run_daily.bat/scheduler).

### DX scorecard (0-10, OpenCode)
| Dim | Score | Note |
| 1 Getting started <5min | 3 | no requirements.txt; manual deps; dual venv; font-to-system step |
| 2 CLI/config guessable | 8 | `python engine_pro.py --count N`; clear config.ini |
| 3 Error messages actionable | 4 | raw tracebacks; no problem+cause+fix |
| 4 Docs findable/complete | 5 | README exists but setup undocumented |
| 5 Upgrade path safe | 6 | git-based; no migration notes |
| 6 Dev env friction-free | 4 | dual venv, D: chatterbox, ffmpeg NVENC |
| 7 Escape hatches | 7 | config.ini overrides most defaults |
| 8 Persona fit (solo builder) | 8 | exactly the target buyer |

**TTHW: ~20-40 min (NOT <5).** Verified reality breaks the README's <5min claim.
Biggest DX friction (OpenCode): **no install manifest + dual-venv + manual font
step** — the one-time setup dominates and would generate support tickets, not sales.
OpenCode verdict: **selling this to other builders is NOT realistic until DX
friction is fixed.** This is a critical input to the B (sell-engine) strategy from
market-pm — B's feasibility depends on DX being fixed first.

### DX decisions (audit)
| # | Phase | Decision | Class | Principle | Rationale | Rejected |
|---|-------|----------|--------|-----------|-----------|----------|
| 10 | DX | Add requirements.txt + setup doc (TTHW-><10min) | Taste | P5 | unblock B-sale | leave manual |
| 11 | DX | Wrap setup in one script (venv+font+ffmpeg check) | Mech | P5 | fewer steps | manual steps |
| 12 | DX | Structured error messages (problem+cause+fix) | Mech | P1 | actionable | raw tracebacks |

PHASE 3.5 COMPLETE. OpenCode: DX must be fixed BEFORE selling engine (B). 

================================================================
## 12. CROSS-PHASE THEMES
- **THEME 1: F2 caption hard-gate is the universal blocker.** Flagged in CEO
  (temporal HOUR 1 = zero output), Eng (worst arch risk / SPOF), and implicitly DX
  (fresh-machine break). High-confidence, 3-phase independent signal.
- **THEME 2: "Do nothing / earn" promise is false as stated.** CEO (P1 challenged)
  + DX (human publishes = not nothing) + market-pm (off-platform only). 
- **THEME 3: Sell-engine (B) depends on fixing F2 + DX first.** CEO (sequence wrong)
  + DX (not saleable until DX fixed) + market-pm (B pursue but needs proof).

## 13. DECISION AUDIT TRAIL (full)
CEO: #1 mode, #2 approach A, #3 challenge curiosity-niche (USER-CHALLENGE),
#4 reframe do-nothing (USER-CHALLENGE), #5 premise gate.
ENG: #6 F2 fallback, #7 tests, #8 ducking doc, #9 sfz guard.
DX: #10 requirements.txt, #11 setup script, #12 structured errors.
(All non-gate decisions auto-decided via 6 principles; 2 user-challenges surfaced.)

## 14. GSTACK REVIEW REPORT
- Verdict: **NO-GO** (both voices, all 4 phases) until F2 + F7 fixed.
- Critical gaps: F2 (caption SPOF, zero output), F4 (earning gate blocked),
  F7 (niche drift, wedge undelivered).
- Taste decisions: 1 (scope sequence) + design/eng/dx micro-tastes (surfaced above).
- User challenges: 2 (curiosity-niche premise, do-nothing claim).
- DX blocks B (sell-engine) until fixed.

================================================================
## 15. FINAL GATE — APPROVED (2026-07-18)
User response: **Approve as reviewed** — accept both user-challenges; NO-GO until
F2 + F7 fixed.
- User-Challenge #3 (curiosity-niche): ACCEPTED. Plan wording updated — History is
  the niche; "curiosity" demoted to a tone. F7 fix (config niche=history) is now a
  REQUIRED pre-build step.
- User-Challenge #4 (do-nothing claim): ACCEPTED. Product claim reframed honestly:
  "generate hands-off + scheduled publish; human does 1 publish tap/day (or
  auto-publish after a vetted batch)." The headline promise will not say "do nothing."
- Taste decision #2 (scope sequence): user accepted Approach A (fix F2+F7 + prove
  wedge BEFORE any new feature / before selling engine).

NEXT (still HELD per user directive — no build until you lift it):
1. F2: edit_pro.py:193 → fall back to beat-level captions + WARN (not RuntimeError).
2. F7: config.ini niche=history; script_pro.py History tone.
3. F4: pick the offer (Amazon books / course / own product) + wire [revenue] config.
4. DX: requirements.txt + one-shot setup script (unblock B-sale; TTHW <10min).
5. THEN prove the History wedge earns off-platform (A test) and/or package for
   builders (B). 

Approved plan file: PLAN_gstack_pipeline.md (this file). No code changed.

================================================================
## 16. BUILD WAVE (hold partially lifted 2026-07-18 — F2+F7 only, per user "1.")
Gated by /health baseline (12/12 tests, compile clean) + /review per fix.

### F2 — caption hard-gate (DONE, /review passed)
- edit_pro.py: removed `raise RuntimeError("word-level caption timing unavailable")`.
- New behavior: try stable-ts word-level; on ANY failure (missing venv / model /
  exception) OR empty result, fall back to beat-level captions timed to the cut
  schedule; if no beats, emit a single topic hold-card. The pipeline NEVER dies
  on captions → first real scheduler run now produces a video (was ZERO output).
- /review: compile CLEAN, 12/12 tests pass, fallback path confirmed present.

### F7 — niche drift (DONE, /review passed)
- config.ini: `niche = curiosity` → `niche = history` (History/Documentary wedge).
- script_pro.py: de-hardcoded #curiosity/#didyouknow default; added `_niche()`
  (strips inline `#` comments, robust to raw configparser), `_hook_for_niche()`
  (History → myth-bust), `_hashtags_for_niche()`; guard overrides base script's
  leaked #curiosity tags when configured niche is history.
- /review end-to-end: hashtags `['#shorts','#history','#didyouknow']`, hook_format
  `myth-bust`, ON-NICHE=True. No #curiosity leak.
- NOTE: engine.build_script template/ollama still embed "curiosity" wording
  internally; out of scope for F7 (script_pro now overrides hashtags+hook at the
  Pro layer, which is what the engine actually ships via engine_pro). The base
  template curiosity text is cosmetic, not a published-tag leak.

### OUT OF SCOPE this wave (user picked "1." = F2+F7 only)
- F4 (affiliate offer) — needs user's offer choice; not done.
- DX (requirements.txt + setup script) — not done.
- /ship — blocked: user "do not proceed to build" still covers F4/DX + push.

### /health re-check after fixes
- Tests: 12 passed (unchanged from baseline). COMPILE: clean. Defects F2/F7 CLOSED.
- Remaining known: F3 (gradient corpus), F4 (offer), F6 (dead path, info), DX.
