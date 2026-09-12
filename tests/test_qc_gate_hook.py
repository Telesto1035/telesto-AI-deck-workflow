"""Tests for the Stop hook: a broken build cannot end its turn until fixed or capped."""
from __future__ import annotations

import json
import os
import shutil
import sys
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


def test_broken_deck_blocks_then_caps(workdir):
    make_broken.make_broken(CLEAN, workdir / "out.pptx")
    codes, logs = [], []
    for _ in range(4):
        out = []
        codes.append(qc_gate_hook.run(payload(workdir), workdir, out.append))
        logs.append("\n".join(out))
    assert codes == [2, 2, 0, 0], codes
    assert "blocked stop 1 of 3" in logs[0]
    assert "author-empty" in logs[0] and "font-size-floor" in logs[0]
    assert "--fix-safe" in logs[0]
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
