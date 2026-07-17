# DESIGN.md — Faceless Viral Engine Visual + Audio Identity

> Source of truth for the look & feel of every video the engine outputs.
> The engine code (engine_pro.py, captions.py, style.py, edit.py) encodes
> these decisions. Change the system HERE, not in the code.

## North Star (the Memorable Thing)

**"Premium, credible discovery brand — not amateur AI."**

Every viewer, sound-off, in the first 1.5 seconds, should feel:
"This is a real, high-quality channel — not a templated AI slideshow."

Design decisions serve this. When two choices conflict, the one that reads
*premium + credible + human* wins over the one that is merely *convenient*.

## Design Principles (anti-slop rules)

1. **Restraint over decoration.** One accent color. No gradients, no neon, no
   purple, no decorative blobs. Premium = disciplined.
2. **Variety within a system.** The brand is consistent (font, voice, grade
   mood) but every video varies its exact look (LUT, transition, hook, pacing
   curve) so no two feel cloned. Sameness = AI slop; system+variation = brand.
3. **Editorial, not template.** Captions and overlays should feel like a
   documentary title sequence, not a text-to-video default.
4. **Sound-off readable.** Hook + captions must work muted (92% watch muted).
5. **Motion carries attention.** No dead frames. Cut 2.5-4s (irregular), real slow motion (Ken Burns), varied — 2026 premium = restraint; 1.5s spam reads as AI-slop.

## Typography

| Token | Value | Rationale |
|-------|-------|-----------|
| Caption display font (keywords/numbers) | **Anton** (primary), **Montserrat Black** (alt) | Condensed, heavy, editorial. NOT Arial/Inter/Roboto (default slop). |
| Caption body font (full sentences) | **Roboto Bold** (YouTube-native) or **Lato Bold** | Trusted, warm, editorial. Used for the running caption line. |
| Case | ALL-CAPS for **keywords/numbers only**; mixed-case for full sentences | All-caps everything reads as "shouting/AI"; mixed-case body reads credible (2026). |
| Weight | 900 (Black) for display; 700 (Bold) for body | Presence on busy footage. |
| Fill | `#FFFFFF` white | Max contrast. |
| Stroke | `#000000` black, 6px @1080p | Legibility over any visual. |
| Highlight keyword | `#F5C518` warm gold | ONE keyword per line, +25% size. Premium gold, distinct from cliché `#FFE600` YouTube yellow. |
| Reveal | word-by-word karaoke, scale pop 0.85→1.2→1.0 (~150ms) | Rhythmic pull; NOT a fade. |
| Position | lower-third, ~66% down (9:16) | Safe area, thumb-reachable, clears lower UI. |
| Size | ~7-8% screen height/line (caption), 18-22% for big stat overlay | Big but not covering the frame. |

## Color

| Token | Hex | Use |
|-------|-----|-----|
| Text fill | `#FFFFFF` | Captions, overlays. |
| Text stroke | `#000000` | Outline behind text. |
| Brand accent (highlight) | `#F5C518` warm gold | Keyword highlight, key stat, logo mark, end-card rule. |
| Grade — shadows | cool/teal lean | Cinematic depth. |
| Grade — highlights | warm/orange lean | Skin + light feel premium. |
| Vignette | subtle, ~PI/5 | Focus eye, "shot on camera" feel. |

- **No** heavy filters, no full-frame color wash, no neon, no gradient text.
- Per-video LUT drawn from a curated PREMIUM set (teal-orange, warm film,
  moody, clean-bright, desaturated-doc). Random one per video → variety within
  the consistent cinematic mood.

## Motion Language

| Token | Value |
|-------|-------|
| Cut interval | **2.5-4s target** (range 2-5s), irregular per-video pacing curve. 2026 premium = restraint; 1.5s spam reads as AI-slop (retention blindness). |
| Transition mix | hard cut ≥70%, one branded accent wipe (e.g. gold) used consistently, gentle crossfade only between major topic shifts, zoom-punch reserved for ONE intentional reveal per video |
| Camera | slow Ken Burns zoom (1.05-1.10x over the beat) on stills, subtle pan; NO frantic zoom-punch on every cut |
| Handheld | optional subtle micro-shake (3-5px) on b-roll only, not on stills |
| Grain | film grain 4-8 (light, random per video) — hides digital cleanliness without noise |
| Pattern interrupt | ONE zoom-punch / color flash / SFX stinger on the single key reveal (not every 4-6s) |
| Loop | seamless last→first frame; end re-triggers hook question |

## Audio Identity

| Token | Value |
|-------|-------|
| Voice | ONE consistent, warm, confident narrator (Chatterbox, voice-cloned once = brand voice). Varied across ≤5 ref voices per batch for life, but NEVER a different robot per video randomly. |
| Voice realism | per-sentence rate 0.94-1.08, pitch ±1.5-2 st, real pauses (comma 120-220ms, period 300-450ms, dramatic reveal 600-1000ms), spliced breaths -18dB, faint pink-noise room tone. Post: EQ/de-ess/compress. |
| Loudness | master to **-14 LUFS** integrated, true peak < -1 dBTP. |
| Music | ONE consistent branded bed per mood (lo-fi / cinematic-ambient / none+SFX). Peak ≈ -20 to -25 dBFS (ducked under voice via sidechain). Low-energy, not hype royalty-free pop. |
| SFX | RESTRAINED + consistent vocabulary: one soft whoosh on the SINGLE key reveal; one subtle tick on big number changes. NOT a whoosh on every cut (that reads as template spam). |

## Pacing & Structure

- Length: **20-40s** target, **70%+ completion**.
- Hook: curiosity-gap OR number-first, on screen + caption by **1.0s**, sound-off readable.
- Open loop: question in beat 1, payoff in final beat.
- Pacing curve per video (front-loaded fast / steady build / slow-fast-slow / accelerating).
- End: soft CTA that drives channel bridge ("Follow for part 2").

## Variation Engine (the system that prevents sameness)

A seeded `VideoStyle` object per video draws ONE from each pool:
- hook format (7 types, no-repeat state)
- intro style (hard cut / black-flash / punch-zoom / text-first / audio-first)
- caption animation (karaoke-pop / typewriter / slide-up / bounce)
- music mood (lofi / cinematic / ambient / phonk / none)
- transition profile (weighted mix above)
- LUT (curated premium set)
- pacing curve (4 profiles)
- grain + shake amounts (ranges)

**Anti-clone check:** reject any new video whose style fingerprint matches a
recent one on ≥3 of 5 axes (hook + LUT + music + transition + pacing). This
passes YouTube's reused-content / uniqueness policy.

## Do / Don't

DO: vary within the system, keep one brand accent, editorial captions, real
motion, consistent narrator, sound-off hook.

DON'T: use Arial/Inter/Roboto, neon/gradient/purple, identical zoom every clip,
crossfade everything, a different robot voice each video, full-sentence static
captions, heavy color washes, dead frames.
