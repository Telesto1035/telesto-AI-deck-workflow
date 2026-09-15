"""Tests for deck-qc/scripts/pptx_comments.py: both comment stores, slide mapping, resolve round trip."""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import pytest
from pptx import Presentation

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SCRIPTS = REPO / ".claude" / "skills" / "deck-qc" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(HERE))

import pptx_comments  # noqa: E402
import plant_comments  # noqa: E402

CLEAN = HERE / "fixtures" / "Telesto_Standard_v2_P3-P5.pptx"


@pytest.fixture(scope="module")
def commented(tmp_path_factory) -> Path:
    return plant_comments.plant(CLEAN, tmp_path_factory.mktemp("comments") / "commented.pptx")


def test_clean_deck_has_no_comments():
    assert pptx_comments.read_comments(CLEAN) == []


def test_reads_both_stores_with_slide_author_status(commented):
    got = pptx_comments.read_comments(commented)
    assert [(c.slide, c.author, c.text, c.status, c.store) for c in got] == plant_comments.EXPECTED
    assert [c.n for c in got] == [1, 2, 3]
    assert got[0].shape_id == "2"
    assert got[0].replies and got[0].replies[0].text == "Agreed, will do"
    assert [c.open for c in got] == [True, False, True]


def test_cli_markdown_and_json(commented, tmp_path, capsys):
    out = tmp_path / "c.json"
    assert pptx_comments.main([str(commented), "--json", str(out), "--open-only"]) == 0
    text = capsys.readouterr().out
    assert "2 comments, 2 open" in text
    assert "Add the recommendation band" not in text  # resolved, filtered by --open-only
    data = json.loads(out.read_text(encoding="utf-8"))
    assert [d["n"] for d in data] == [1, 3]


def test_resolve_marks_modern_and_leaves_legacy(commented, tmp_path, capsys):
    out = tmp_path / "resolved.pptx"
    assert pptx_comments.main([str(commented), "--resolve", "all", "--out", str(out)]) == 0
    err = capsys.readouterr().err
    assert "2 comments marked resolved" in err
    assert "1 legacy comment left" in err
    got = pptx_comments.read_comments(out)
    assert [c.status for c in got] == ["resolved", "resolved", "active"]
    # nothing else in the package changed
    with zipfile.ZipFile(commented) as a, zipfile.ZipFile(out) as b:
        assert a.namelist() == b.namelist()
        for name in a.namelist():
            if "modernComment" not in name:
                assert a.read(name) == b.read(name), name


def test_resolve_unknown_number_fails(commented, tmp_path):
    assert pptx_comments.main([str(commented), "--resolve", "9", "--out", str(tmp_path / "x.pptx")]) == 1


def test_resolve_in_place_keeps_the_deck(commented, tmp_path, capsys):
    """--out pointing at the input deck must not truncate it while it is still being read."""
    deck = tmp_path / "in_place.pptx"
    deck.write_bytes(commented.read_bytes())
    size_before = deck.stat().st_size
    assert pptx_comments.main([str(deck), "--resolve", "all", "--out", str(deck)]) == 0
    capsys.readouterr()
    assert deck.stat().st_size > size_before / 2  # not truncated to a stub
    with zipfile.ZipFile(deck) as z:  # still a readable package
        assert z.testzip() is None
        assert "ppt/presentation.xml" in z.namelist()
    Presentation(str(deck))  # and still a valid PPTX
    assert [c.status for c in pptx_comments.read_comments(deck)] == ["resolved", "resolved", "active"]
    # no temp files left behind
    assert sorted(p.name for p in tmp_path.iterdir()) == ["in_place.pptx"]
