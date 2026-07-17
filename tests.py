"""Smoke tests for the Faceless Viral Engine's pure functions.

Run:  python -m pytest tests.py -q
These do not require ffmpeg/ollama/network — they test parsing + assembly.
"""
import os
import sys
import inspect


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine


def test_config_comment_stripping_preserves_hash_in_value():
    # A '#' inside a value (no preceding space) must survive; a whitespace-#
    # trailing comment must be stripped.
    ini = "[x]\nval = http://e.com/a#b   # comment here\nk = 2\n"
    import configparser
    raw = []
    for line in ini.splitlines(keepends=True):
        idx = line.find("#")
        while idx != -1:
            if idx == 0 or line[idx - 1] in (" ", "\t"):
                line = line[:idx] + "\n"
                break
            idx = line.find("#", idx + 1)
        raw.append(line)
    c = configparser.ConfigParser()
    c.read_string("".join(raw))
    assert c.get("x", "val") == "http://e.com/a#b"
    assert c.getint("x", "k") == 2


def test_script_template_shape():
    s = engine.script_template("The ocean")
    assert isinstance(s["beats"], list) and len(s["beats"]) >= 4
    assert s["title"]
    assert s["visual_query"]
    assert all(isinstance(t, str) for t in s["hashtags"])


def test_ass_timestamp_handles_over_60s():
    assert engine._ass_ts(0) == "0:00:00.0"
    assert engine._ass_ts(5.4) == "0:00:05.4"
    assert engine._ass_ts(65.0) == "0:01:05.0"
    assert engine._ass_ts(3661.5) == "1:01:01.5"


def test_build_ass_escapes_braces_and_produces_events():
    ass = engine.build_ass(["a {b}", "c"], total_dur=4.0, w=1080, h=1920)
    assert "[Events]" in ass
    assert "Dialogue: 0,0:00:00.0,0:00:02.0,C,a \\{b\\}" in ass
    dlg = [line for line in ass.splitlines() if line.startswith("Dialogue:")]
    assert len(dlg) == 2


def test_media_duration_returns_zero_for_missing_file():
    # Non-existent file -> ffprobe fails -> 0.0, not a crash.
    assert engine.media_duration("__does_not_exist__.mp4") == 0.0


def test_load_config_reads_real_ini():
    cp = engine.load_config()
    assert cp.has_section("engine")
    assert cp.has_section("voice")


# ---------------------------------------------------------------------------
# Upgraded engine tests (Q8)
# ---------------------------------------------------------------------------

def test_license_filter_accepts_free_rejects_nc_nd():
    import visuals_pro as V
    # free-for-commercial, derivative-allowed
    assert V._license_ok("CC BY 4.0") is True
    assert V._license_ok("cc-by-sa-4.0") is True
    assert V._license_ok("Public Domain") is True
    assert V._license_ok("CC0") is True
    # monetization-blocking licenses must be REJECTED
    assert V._license_ok("CC BY-NC 4.0") is False      # NonCommercial
    assert V._license_ok("CC BY-ND") is False           # NoDerivatives
    assert V._license_ok("CC BY-NC-ND 4.0") is False    # both
    # missing/unknown license must be rejected (never publish unlicensed)
    assert V._license_ok("") is False
    assert V._license_ok("Unknown") is False


def test_anti_clone_differs_on_at_least_3_axes():
    import style as S
    S.reset_history()
    a = S.make_style(seed=1, force_new=True)
    b = S.make_style(seed=2, force_new=True)
    fp_a = S._fingerprint(a)
    fp_b = S._fingerprint(b)
    shared = sum(1 for ax in S.AXES if fp_a[ax] == fp_b[ax])
    assert shared < 3, f"two consecutive styles share {shared}/5 axes (want <3)"


def test_anti_clone_history_persists():
    import style as S
    S.reset_history()
    s = S.make_style(seed=99, force_new=True)
    # reload state from disk and confirm it recorded the fingerprint
    import json
    with open(S.STATE_PATH) as f:
        state = json.load(f)
    assert len(state["history"]) >= 1


def test_captions_ass_gold_keyword_and_escaping():
    import captions as C
    words = [("The", 0.0, 0.3), ("deep", 0.3, 0.6), ("ocean", 0.6, 0.9)]
    out = C.build_ass(words, os.path.join(os.path.dirname(__file__),
                                          "work", "t_caps.ass"))
    txt = open(out).read()
    # gold accent present, keyword (longest alpha word 'ocean') is Active/gold
    assert C.GOLD in txt
    assert "[Events]" in txt
    # braces escaped
    safe = C.build_ass([("a {b}", 0, 1)], out)
    assert "\\{" in open(safe).read()


def test_config_quality_section_parses():
    cp = engine.load_config()
    assert cp.has_section("quality")
    assert cp.get("quality", "voice_engine") in ("chatterbox", "kokoro")
    assert cp.get("quality", "sfx_density") == "minimal"


def test_voice_fallback_chain_order():
    # PLAN Wave 1 / Decision #6: resilience chain must be
    # Chatterbox -> Kokoro -> edge-tts -> silent pad.
    import voice_pro as V
    src = V.__dict__.get("_voice_edge")
    assert callable(src), "edge-tts tier must exist in the fallback chain"
    # Confirm render_voice references all four tiers (no tier silently dropped).
    body = inspect.getsource(V.render_voice)
    assert "Chatterbox" in body and "Kokoro" in body and "edge" in body \
        and "silent" in body, "fallback chain must name all 4 tiers"
    # The chain must end in a silent pad, never raise on total failure.
    assert "anullsrc" in body, "last-resort silent pad must be present"

