"""Tests for the Stop hook: a broken build cannot end its turn until fixed or capped."""
from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SCRIPTS = REPO / ".claude" / "skills" / "deck-qc" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(HERE))

import qc_gate_hook  # noqa: E402
import make_broken  # noqa: E402

FIXTURES = HERE / "fixtures"
CLEAN = FIXTURES / "Telesto_Standard_v2_P3-P5.pptx"


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    """A fake project dir with a transcript whose first timestamp predates the deck write."""
    monkeypatch.setenv("QC_GATE_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.delenv("QC_GATE_RENDER", raising=False)  # the render step is PowerPoint COM; tested by hand, not here
    (tmp_path / "state").mkdir()
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(json.dumps({"timestamp": "2020-01-01T00:00:00Z", "type": "user"}) + "\n", encoding="utf-8")
    return tmp_path


def payload(workdir: Path, session="sess-test") -> dict:
    return {"session_id": session, "transcript_path": str(workdir / "transcript.jsonl"), "cwd": str(workdir),
            "hook_event_name": "Stop", "stop_hook_active": False}


def test_no_pptx_means_silent_pass(workdir):
    out = []
    assert qc_gate_hook.run(payload(workdir), workdir, out.append) == 0
    assert out == []


def test_clean_deck_passes(workdir):
    shutil.copy(CLEAN, workdir / "out.pptx")
    out = []
    assert qc_gate_hook.run(payload(workdir), workdir, out.append) == 0


def test_render_is_off_without_opt_in(workdir, monkeypatch):
    # the plugin build carries the hook but no env block, so the default has to be off in code
    calls = []
    monkeypatch.setattr(qc_gate_hook.sys, "platform", "win32")
    monkeypatch.setattr(qc_gate_hook.subprocess, "run", lambda *a, **k: calls.append(a))
    shutil.copy(CLEAN, workdir / "out.pptx")
    assert qc_gate_hook.run(payload(workdir), workdir, lambda s: None) == 0
    assert calls == []


def test_broken_deck_blocks_then_caps(workdir):
    make_broken.make_broken(CLEAN, workdir / "out.pptx")
    codes, logs = [], []
    for _ in range(4):
        out = []
        codes.append(qc_gate_hook.run(payload(workdir), workdir, out.append))
        logs.append("\n".join(out))
    assert codes == [2, 2, 0, 0], codes
    assert "blocked stop 1 of 3" in logs[0]
    # author-empty is a hand-back condition now, so the mid-session gate warns rather than
    # blocks on it; a content fault is what holds the stop.
    assert "font-size-floor" in logs[0]
    assert "author-empty" not in logs[0], "property hygiene must not block the consultant mid-session"
    # nothing planted is auto-fixable since speaker notes became a warning, so no --fix-safe hint
    assert "--fix-safe" not in logs[0]
    assert "gate cap reached, handing off with findings attached" in logs[2]
    assert "gate cap reached" in logs[3]


def test_fix_resets_counter(workdir):
    make_broken.make_broken(CLEAN, workdir / "out.pptx")
    assert qc_gate_hook.run(payload(workdir), workdir, lambda s: None) == 2
    shutil.copy(CLEAN, workdir / "out.pptx")
    out = []
    assert qc_gate_hook.run(payload(workdir), workdir, out.append) == 0
    assert any("clean after 1 blocked stop" in line for line in out)
    st = json.loads(qc_gate_hook.state_path("sess-test").read_text())
    assert st["blocked"] == 0


def test_fixtures_are_ignored(workdir):
    dst = workdir / "tests" / "fixtures" / "broken"
    dst.mkdir(parents=True)
    make_broken.make_broken(CLEAN, dst / "x.broken.pptx")
    assert qc_gate_hook.run(payload(workdir), workdir, lambda s: None) == 0


def test_transcript_path_is_picked_up_outside_cwd(workdir, tmp_path_factory):
    elsewhere = tmp_path_factory.mktemp("elsewhere")
    make_broken.make_broken(CLEAN, elsewhere / "deck.pptx")
    transcript = workdir / "transcript.jsonl"
    transcript.write_text(
        json.dumps({"timestamp": "2020-01-01T00:00:00Z"}) + "\n"
        + json.dumps({"tool_input": {"file_path": str(elsewhere / "deck.pptx")}}) + "\n",
        encoding="utf-8",
    )
    out = []
    assert qc_gate_hook.run(payload(workdir), workdir, out.append) == 2
    assert "deck.pptx" in "\n".join(out)


def test_old_files_are_not_gated(workdir):
    shutil.copy(CLEAN, workdir / "old.pptx")
    make_broken.make_broken(CLEAN, workdir / "old.pptx")
    old = 946684800  # 2000-01-01, before the transcript's first timestamp
    os.utime(workdir / "old.pptx", (old, old))
    assert qc_gate_hook.run(payload(workdir), workdir, lambda s: None) == 0


# --- patch 2026-09-14: file selection (last stop, exclusions, templates, .qc.pptx) ---------------


TEMPLATE = FIXTURES / "telesto_v2_template.pptx"


def test_template_is_skipped_and_logged(workdir):
    shutil.copy(TEMPLATE, workdir / "telesto_v2_template.pptx")
    out = []
    assert qc_gate_hook.run(payload(workdir), workdir, out.append) == 0
    assert any("template, not a deck" in line for line in out)


def test_potx_is_skipped(workdir):
    shutil.copy(CLEAN, workdir / "house.potx")
    assert qc_gate_hook.is_template(workdir / "house.potx") is True


def test_fix_safe_output_is_not_gated(workdir):
    make_broken.make_broken(CLEAN, workdir / "out.qc.pptx")
    assert qc_gate_hook.run(payload(workdir), workdir, lambda s: None) == 0


def test_bare_fixture_and_asset_folders_are_ignored(workdir):
    for rel in ("handoff/fixtures", "manual-build/assets"):
        dst = workdir / rel
        dst.mkdir(parents=True)
        make_broken.make_broken(CLEAN, dst / "x.pptx")
    assert qc_gate_hook.run(payload(workdir), workdir, lambda s: None) == 0


def test_exclusions_come_from_qc_rules(workdir):
    parts = qc_gate_hook.exclude_parts()
    assert "assets" in parts and ".qc.pptx" in parts and "tests/fixtures" in parts


def test_clean_file_is_not_regated_until_it_changes(workdir):
    deck = workdir / "out.pptx"
    shutil.copy(CLEAN, deck)
    assert qc_gate_hook.run(payload(workdir), workdir, lambda s: None) == 0
    st = json.loads(qc_gate_hook.state_path("sess-test").read_text())
    assert str(deck.resolve()) in st["gated"]
    stamp = deck.stat().st_mtime
    # broken behind the gate's back, mtime restored: the file reads as untouched, so it is not re-gated
    make_broken.make_broken(CLEAN, deck)
    os.utime(deck, (stamp, stamp))
    assert qc_gate_hook.run(payload(workdir), workdir, lambda s: None) == 0
    # written again in this turn: gated, and it blocks
    now = time.time()
    os.utime(deck, (now, now))
    assert qc_gate_hook.run(payload(workdir), workdir, lambda s: None) == 2


def test_a_blocking_file_is_gated_on_every_stop(workdir):
    """The clean-file shortcut must never let a blocked deck through by standing still."""
    make_broken.make_broken(CLEAN, workdir / "out.pptx")
    codes = [qc_gate_hook.run(payload(workdir), workdir, lambda s: None) for _ in range(2)]
    assert codes == [2, 2]


# --- candidate scoping: only decks this session wrote -------------------------------------------
# The gate used to treat any .pptx path appearing in the transcript as a candidate, so merely naming
# a deck put it up for gating. That blocked stops over the reviewers' input file and over a deck in
# another agent's worktree, neither of which the session had written.

def _deck(path: Path, mtime: float) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(CLEAN, path)
    os.utime(path, (mtime, mtime))
    return path


def test_mentioned_but_unwritten_deck_is_not_a_candidate(tmp_path):
    since = time.time()
    stale = _deck(tmp_path / "reviewers_copy.pptx", since - 3600)
    text = "I read %s and quoted slide 4 from it." % stale
    assert find(tmp_path, text, since) == []


def test_mentioned_and_written_deck_is_a_candidate(tmp_path):
    since = time.time()
    fresh = _deck(tmp_path / "we_wrote_this.pptx", since + 5)
    text = "Saved %s" % fresh
    assert find(tmp_path, text, since) == [fresh.resolve()]


def test_deck_in_another_agents_worktree_is_pruned(tmp_path):
    since = time.time()
    other = _deck(tmp_path / ".claude" / "worktrees" / "abc123" / "manual" / "m.pptx", since + 5)
    mine = _deck(tmp_path / "mine.pptx", since + 5)
    got = find(tmp_path, "touched %s and %s" % (other, mine), since)
    assert mine.resolve() in got
    assert other.resolve() not in got, "a worktree deck belongs to another session"


def test_no_session_start_gates_nothing(tmp_path):
    _deck(tmp_path / "whatever.pptx", time.time())
    assert qc_gate_hook.find_candidates(tmp_path, None, None, text="whatever.pptx") == []


def find(cwd: Path, text: str, since: float) -> list:
    """find_candidates with a transcript that exists, so rule 1 runs against `text`."""
    t = cwd / "transcript.jsonl"
    t.write_text("{}\n", encoding="utf-8")
    return qc_gate_hook.find_candidates(cwd, str(t), since, text=text)


def test_missing_python_pptx_is_said_to_the_user(workdir, capsys):
    """Without python-pptx the gate cannot run. A deck written this session gets a systemMessage the user sees,
    with the install line; the stop is not blocked. A session with no deck gets nothing."""
    assert qc_gate_hook.run(payload(workdir), workdir, lambda s: None, have_pptx=False) == 0
    assert capsys.readouterr().out == "", "a session with no deck should hear nothing"
    shutil.copy(CLEAN, workdir / "deck.pptx")
    assert qc_gate_hook.run(payload(workdir), workdir, lambda s: None, have_pptx=False) == 0
    msg = json.loads(capsys.readouterr().out)["systemMessage"]
    assert "deck.pptx" in msg and qc_gate_hook.INSTALL_LINE in msg
