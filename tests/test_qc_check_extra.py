"""Regression tests for the 2026-09-13 code-review fixes to qc_check.py."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pptx import Presentation
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SCRIPTS = REPO / ".claude" / "skills" / "deck-qc" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import qc_check  # noqa: E402

CLEAN = HERE / "fixtures" / "Telesto_Package_Types.pptx"


@pytest.fixture(scope="module")
def rules():
    return qc_check.load_rules(None)


def test_stype_survives_unknown_shapes():
    class Ink:
        @property
        def shape_type(self):
            raise NotImplementedError("unrecognized shape")

    class Box:
        shape_type = 17

    assert qc_check._stype(Ink()) is None
    assert qc_check._stype(Box()) == 17


def test_fingerprint_in_slide_prose_is_not_a_metadata_block(tmp_path, rules):
    """A client called Spire, or a page that mentions python-pptx, is prose, not a generator fingerprint."""
    prs = Presentation(str(CLEAN))
    slide = prs.slides[0]
    tb = slide.shapes.add_textbox(Inches(1), Inches(4), Inches(6), Inches(0.5))
    tb.text_frame.text = "Spire Healthcare chose the plan; the build used python-pptx."
    for r in tb.text_frame.paragraphs[0].runs:
        r.font.size = Pt(12)
    out = tmp_path / "prose.pptx"
    prs.save(str(out))
    _deck, findings = qc_check.run_checks(out, rules)
    fps = [f for f in findings if f.id == "metadata-scrub" and "fingerprint" in f.detail]
    assert all(not f.detail.endswith("slide1.xml") for f in fps), [f.detail for f in fps]
    assert not any("ppt/slides/" in f.detail for f in fps)


def test_fix_safe_never_edits_slide_prose_for_fingerprints(tmp_path, rules):
    prs = Presentation(str(CLEAN))
    tb = prs.slides[0].shapes.add_textbox(Inches(1), Inches(4), Inches(6), Inches(0.5))
    tb.text_frame.text = "Aspose is a client name here."
    for r in tb.text_frame.paragraphs[0].runs:
        r.font.size = Pt(12)
    src = tmp_path / "prose.pptx"
    prs.save(str(src))
    deck, findings = qc_check.run_checks(src, rules)
    # force the fingerprint fix path even though no metadata finding may exist
    findings.append(qc_check.Finding("metadata-scrub", "block", None, None, None, "x", "forced", "clear", True))
    fixed = qc_check.fix_safe(deck, findings, tmp_path / "prose.qc.pptx", lambda s: None)
    text = " ".join(sh.text_frame.text for sh in Presentation(str(fixed)).slides[0].shapes if sh.has_text_frame)
    assert "Aspose is a client name here." in text


def test_meta_part_regex_scope():
    yes = ["docProps/app.xml", "docProps/core.xml", "docProps/custom.xml", "[Content_Types].xml",
           "ppt/presentation.xml", "ppt/presProps.xml", "_rels/.rels", "ppt/slides/_rels/slide1.xml.rels"]
    no = ["ppt/slides/slide1.xml", "ppt/notesSlides/notesSlide1.xml", "ppt/charts/chart1.xml", "ppt/slideLayouts/slideLayout1.xml"]
    assert all(qc_check.META_PART_RE.search(n) for n in yes)
    assert not any(qc_check.META_PART_RE.search(n) for n in no)


def test_per_shape_caches_are_populated_once(rules):
    deck, _ = qc_check.run_checks(CLEAN, rules)
    n_shapes = sum(len(v) for v in deck.shapes_by_slide.values())
    assert 0 < len(deck._runs_cache) <= n_shapes
    assert 0 < len(deck._text_cache) <= n_shapes
    si = next(iter(deck.shapes_by_slide.values()))[0]
    assert deck.runs_of(si) is deck.runs_of(si)  # same object back: memoised, not recomputed


def test_profile_length_uses_appendix_start(rules):
    deck, findings = qc_check.run_checks(CLEAN, rules, profile="findings")
    body = (deck.appendix_start - 1) if deck.appendix_start else len(deck.slides)
    lens = [f for f in findings if f.id == "deck-length"]
    if lens:
        assert lens[0].text == "%d slides" % body


def test_rules_carry_the_moved_thresholds(rules):
    assert rules["overlap_tolerance_pt"] == 4
    assert rules["chart_label_tolerance"] == 0.5
    assert "manual" in rules["profiles"]
