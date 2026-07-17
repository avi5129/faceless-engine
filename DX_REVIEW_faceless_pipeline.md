# Independent DX Review — faceless-engine

Adversarial DX audit of `PLAN_gstack_pipeline.md` against the actual code
(`engine_pro.py`, `edit_pro.py`, `visuals_pro.py`, `measure.py`, the `.bat`
files, `config.ini`, `README.md`, `run_status.log`). The "do nothing" promise
is the bar; silent failure is the crime.

## Scores (0–10)
1. **Getting started — 3.** README claims TTHW <5 min, but reality needs a
   ~4.6 GB Chatterbox venv on D:, 3 asset-gen scripts, a font install, *and*
   a C: drive that is already full. `run_status.log` shows a live
   `OSError: [Errno 28] No space left on device` FAIL — TTHW is fiction.
2. **API/CLI ergonomics — 5.** Split-brain config: `[voice] provider=kokoro`
   ("BEST FREE" default) vs `[quality] voice_engine=chatterbox` (primary, needs
   GPU venv). `niche=curiosity` contradicts the History wedge (F7). Same knob,
   two keys, two defaults.
3. **Error messages — 3.** `edit_pro` raises `RuntimeError` on a caption miss —
   a *hard gate* whose message only a dev reads. `run_daily.bat` pipes
   everything to a hidden log; the operator never sees it.
4. **Docs — 5.** Copy-pasteable, but the TTHW claim is false, there is no
   disk-space warning, and the `[youtube]` section `measure.py` requires is
   absent from the sample config (verified: no `[youtube]` in `config.ini`).
5. **Upgrade path — 4.** Plan is permanently "HELD"; `engine.py` vs
   `engine_pro.py` config drift (F7) means an edit can silently degrade. No
   migration note. Tests pass (12/12) but guard nothing about config.
6. **Dev friction — 4.** Hardcoded `D:\venv_voice` + `D:/hf_cache` +
   `C:\Users\...\Python312\python.exe`. No main venv; zero portability; C: full
   already broke a real run.
7. **Observability — 2.** THE core DX failure. Caption gate fails silently
   (F2); gradient-only videos ship with no flag (F3); `measure.py` soft-fails
   "quietly" to an unread log; `engine_pro.main()` never `sys.exit(1)`, so Task
   Scheduler sees exit 0 and reports success. The operator has no signal a run
   degraded or died.
8. **Escape hatches — 3.** Caption gate has NO override despite README claiming
   "captions on/off" (verified: no such key in `config.ini`). The nicer
   `_title_card()` fallback exists but is **DEAD CODE** (defined, never called)
   — gradient is still what ships on a Wikimedia flake (F3 unfixed). Voice chain
   is the one genuine escape hatch.

## Top adversarial findings
- **Silent success theater:** `engine_pro.main()` returns normally on
  per-video failure → `run_daily.bat` logs `done (exit 0)` → Task Scheduler
  believes it won. A killed run looks identical to a win.
- **Gradient fallback is invisible (F3):** `src="gradient"` is printed to
  stdout only; `run_status.log` records no visual source, so a 100%-gradient
  "AI slop" day is indistinguishable from a good day in the operator's only
  dashboard.
- **measure.py never runs** (no `[youtube]` key) yet logs nothing actionable to
  a place anyone reads — the "self-improving" promise is silently false.
- **Dead `_title_card()`:** the designed editorial fallback the plan praises is
  defined but never called; `build_beat_visual` drops straight to
  `ENG.animated_bg`. The fix is half-shipped.

## Developer journey map (Operator: scheduler runs, I publish daily)
1. Admin runs `setup_scheduler.bat` → 3 silent tasks at 09/13/19. Edits `COUNT`.
2. Daily: tasks fire `run_daily.bat` → appends to `work/scheduler.log` →
   `engine_pro.py` drops mp4s in `publish/`.
3. Operator opens `publish/` each morning, uploads the mp4s to YT. **No other
   check.**
4. Failure is invisible at every step:
   - Caption glitch (F2) → no mp4, but `scheduler.log` says exit 0. Operator
     assumes "off day."
   - Wikimedia flake (F3) → gradient video *does* appear, looks abandoned, ships
     anyway.
   - measure.py → silent no-op; operator believes the channel is "learning."
5. Only way to discover anything wrong: manually open `run_status.log` /
   `work/measure.log`. Nobody does. The "do nothing" promise is violated by
   design.

## Fixes (cheapest first)
- `engine_pro.main()`: `sys.exit(1)` if any `run_once` returns None; let the .bat
  propagate `%errorlevel%` into Task Scheduler history.
- Add `[youtube] api_key` to sample config + a `run_status.log` WARN line when
  `src=="gradient"` (count gradient beats per run).
- Wire `_title_card()` into `build_beat_visual` (kill the dead code, fix F3 for
  real).
- Add `captions = on|off` to config; on off, fall back to beat-level text
  instead of raising.
- Add a failure signal (`work/LAST_RUN_FAILED` flag / toast / email) so "do
  nothing" is actually safe.
