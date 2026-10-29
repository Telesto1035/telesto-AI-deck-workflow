"""Regression tests for the 2026-09-13 code-review fixes to qc_check.py."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pptx import Presentation
from pptx.util import Emu, Inches, Pt

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


# --- patch 2026-09-14: the brief profile ---------------------------------------------------------


def _build_brief(path: Path, heading: str = "Build Brief: engagement setup") -> Path:
    """One dense slide: 320-odd words of body and a 9pt header strip. The approved Build Brief format."""
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    head = slide.shapes.add_textbox(Inches(0.4), Inches(0.2), Inches(12.5), Inches(0.4))
    head.name = "header strip"
    r = head.text_frame.paragraphs[0].add_run()
    r.text = "Engagement  |  Owner  |  Draft date  |  Version"
    r.font.size = Pt(9)

    body = slide.shapes.add_textbox(Inches(0.4), Inches(0.8), Inches(12.5), Inches(6.0))
    body.name = "brief body"
    tf = body.text_frame
    tf.text = heading
    tf.paragraphs[0].runs[0].font.size = Pt(14)
    for i in range(20):
        p = tf.add_paragraph()
        run = p.add_run()
        run.text = "Line %d of the brief states the scope, the owner and the data the page plan rests on." % i
        run.font.size = Pt(11)
    prs.core_properties.author = ""
    prs.save(str(path))
    return path


def test_brief_profile_is_inferred_from_one_slide_and_the_heading(tmp_path, rules):
    deck, _findings = qc_check.run_checks(_build_brief(tmp_path / "brief.pptx"), rules)
    assert deck.profile == "brief"


def test_brief_is_exempt_from_page_density_and_the_header_strip(tmp_path, rules):
    deck, findings = qc_check.run_checks(_build_brief(tmp_path / "brief.pptx"), rules)
    ids = {f.id for f in findings}
    assert "word-count" not in ids, [f for f in findings if f.id == "word-count"]
    assert "font-size-floor" not in ids, [f for f in findings if f.id == "font-size-floor"]
    # hygiene still blocks on a python-pptx build (author, fingerprint); the density rules are what the profile lifts
    assert not [f for f in findings if f.severity == "block" and f.id in ("word-count", "font-size-floor")], findings


def test_the_same_page_without_the_brief_heading_is_gated_as_usual(tmp_path, rules):
    """The exemption rides on the profile, not on the shape name: no brief heading, no exemption."""
    deck, findings = qc_check.run_checks(_build_brief(tmp_path / "page.pptx", heading="Scope and owners"), rules)
    assert deck.profile is None
    assert "font-size-floor" in {f.id for f in findings}


def test_brief_still_gates_hygiene(tmp_path, rules):
    """Author, placeholders and metadata are not what the profile switches off.

    Properties block at hand-back rather than mid-session, so this asserts both halves."""
    p = _build_brief(tmp_path / "brief.pptx")
    from pptx import Presentation as _P
    prs = _P(str(p))
    prs.core_properties.author = "Doyoung Lim"
    tb = prs.slides[0].shapes.add_textbox(Inches(0.4), Inches(6.9), Inches(6), Inches(0.3))
    tb.text_frame.text = "[PLACEHOLDER: fee to confirm]"
    tb.text_frame.paragraphs[0].runs[0].font.size = Pt(11)
    prs.save(str(p))
    _deck, findings = qc_check.run_checks(p, rules, handback=True)
    ids = {f.id for f in findings if f.severity == "block"}
    assert "author-empty" in ids and "placeholders" in ids, findings
    _d2, mid = qc_check.run_checks(p, rules)
    assert "author-empty" not in {f.id for f in mid if f.severity == "block"}
    assert "author-empty" in {f.id for f in mid if f.severity == "warn"}
    assert "placeholders" in {f.id for f in mid if f.severity == "block"}, "content faults still block"


def test_brief_profile_can_be_asked_for_by_name(tmp_path, rules):
    deck, findings = qc_check.run_checks(_build_brief(tmp_path / "b.pptx", heading="Scope and owners"), rules, profile="brief")
    assert deck.profile == "brief"
    assert "word-count" not in {f.id for f in findings}


# ---- custom (non-theme) brand colours ------------------------------------------------

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
RT_THEME = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme"
BRAND_HEX = "5D013A"


def _deck_on_brand_fill(path: Path, declare_custom: bool) -> Path:
    """A one-slide deck with a shape filled in a brand colour; optionally the theme
    declares that colour in a custClrLst, the way a client template does."""
    from lxml import etree
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE

    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1), Inches(1), Inches(2), Inches(1))
    sh.fill.solid()
    sh.fill.fore_color.rgb = RGBColor.from_string(BRAND_HEX)
    sh.line.fill.background()
    if declare_custom:
        part = prs.slide_masters[0].part.part_related_by(RT_THEME)
        root = etree.fromstring(part.blob)
        lst = etree.SubElement(root, "{%s}custClrLst" % A_NS)
        cc = etree.SubElement(lst, "{%s}custClr" % A_NS)
        cc.set("name", "Brand")
        etree.SubElement(cc, "{%s}srgbClr" % A_NS).set("val", BRAND_HEX)
        part._blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    prs.save(str(path))
    return path


def test_brand_colour_outside_the_theme_is_style_drift(tmp_path, rules):
    """Control: a colour the template declares nowhere is drift, as before."""
    path = _deck_on_brand_fill(tmp_path / "undeclared.pptx", declare_custom=False)
    _deck, findings = qc_check.run_checks(path, rules)
    drift = [f for f in findings if f.id == "style-drift" and f.slide == 1]
    assert drift and BRAND_HEX in drift[0].detail, findings


def test_custom_colour_declared_by_the_template_is_not_style_drift(tmp_path, rules):
    """A client template may declare its palette in custClrLst rather than clrScheme --
    Huron's own instruction slide says to use custom colours only. The gate reads both,
    so a deck built correctly on client paper raises no colour warning."""
    path = _deck_on_brand_fill(tmp_path / "declared.pptx", declare_custom=True)
    deck, findings = qc_check.run_checks(path, rules)
    assert BRAND_HEX in deck.theme_colors(deck.slides[0].slide_layout.slide_master)
    drift = [f for f in findings if f.id == "style-drift" and f.slide == 1]
    assert not drift, drift


def test_em_dash_flags_prose_but_not_a_verbatim_quote(tmp_path, rules):
    """language-rules.md line 54: no em dashes in original prose; quoted material keeps its punctuation."""
    prs = Presentation(str(CLEAN))
    slide = prs.slides[0]
    for top, text in (
        (Inches(3), "Buyers shifted spend \u2014 and budgets followed"),
        (Inches(4), "\u201cWe moved the budget \u2014 all of it \u2014 to the new vendor.\u201d"),
        # straight quotes are no less verbatim: a quote pasted from a transcript arrives this way
        (Inches(5), '"We moved the budget \u2014 all of it \u2014 to the new vendor." (CFO, R4)'),
    ):
        tb = slide.shapes.add_textbox(Inches(1), top, Inches(7), Inches(0.5))
        tb.text_frame.text = text
        for r in tb.text_frame.paragraphs[0].runs:
            r.font.size = Pt(12)
    out = tmp_path / "emdash.pptx"
    prs.save(str(out))
    _deck, findings = qc_check.run_checks(out, rules)
    hits = [f for f in findings if f.id == "em-dash"]
    assert len(hits) == 1, [f.text for f in hits]
    assert hits[0].text.startswith("Buyers shifted spend")
    assert hits[0].severity == "warn"


# --- patch 2026-09-15: a profile's rules reach every check ---------------------------------------


def test_profile_overrides_reach_rules_consumed_at_construction(rules):
    """run_checks overlays the profile after the Deck is built, so anything derived in __init__ would keep
    the base value and the profile would be silently half-applied. footnote_name_regex was the one such key."""
    deck = qc_check.Deck(CLEAN, rules)
    assert deck.footnote_name_re.search("Footnote 1")
    deck.rules = qc_check.apply_profile(
        dict(rules, profiles=dict(rules.get("profiles") or {}, quellen={"footnote_name_regex": "quelle"})),
        "quellen",
    )
    assert deck.footnote_name_re.search("Quelle 1")
    assert not deck.footnote_name_re.search("Footnote 1")


def test_apply_profile_leaves_the_base_rules_alone(rules):
    """The overlay is per run. A profile that edited the shared dict would leak into the next deck the
    gate checks in the same process, which is every deck after the first at a Stop."""
    before = dict(rules)
    merged = qc_check.apply_profile(rules, "brief")
    assert merged["words_warn"] is None
    assert rules == before
    assert rules["words_warn"] == before["words_warn"] is not None


# --- patch 2026-09-15: the language check is sourced from the files, and voice is not scored -----
# Two failures, one week apart. First the register dimension cited two house rules that do not
# exist and inverted the one that does, because nothing told the evaluator to open the files.
# Then the deeper one: scoring how a firm sounds needs an owner arbitrating taste every week, and
# it cannot be applied by anyone the skills are shared with. The dimension is retired. What is
# checked now is what any professional reader applies the same way: grammar, machine phrasing,
# the conventions a stranger could enforce, and logic across titles.

AGENT = REPO / ".claude" / "agents" / "deck-evaluator.md"
DECK_QC_SKILL = REPO / ".claude" / "skills" / "deck-qc" / "SKILL.md"
HOUSE_REGISTER = REPO / ".claude" / "skills" / "draft-deck" / "references" / "house-register.md"
RULE_FILES = ("language-rules.md", "house-register.md")
INSTRUCTIONS = [AGENT, DECK_QC_SKILL]


def _language_section(text: str) -> str:
    """The part of a file that governs the language check."""
    low = text.lower()
    for marker in ("## the language check", "**language, and why it carries no score.**"):
        i = low.find(marker)
        if i >= 0:
            break
    assert i >= 0, "no language section to check"
    j = low.find("\n## ", i + 1)
    return text[i: j if j > 0 else None]


@pytest.mark.parametrize("path", INSTRUCTIONS, ids=["evaluator", "deck-qc"])
def test_language_instruction_names_the_rule_files(path):
    """The language check is the one with no evidence in the deck, so an unread rule becomes an
    invented one. Both instructions must send the reader to the files by name."""
    section = _language_section(path.read_text(encoding="utf-8"))
    missing = [f for f in RULE_FILES if f not in section]
    assert not missing, "%s language section does not name %s" % (path.name, missing)
    assert "client brief" in section.lower() and "deck style" in section.lower(), (
        "%s language section does not name the client brief's Deck style section" % path.name)


@pytest.mark.parametrize("path", INSTRUCTIONS, ids=["evaluator", "deck-qc"])
def test_language_findings_must_quote_their_rule(path):
    """A finding that cannot quote its rule is what fabrication looks like in the report."""
    section = _language_section(path.read_text(encoding="utf-8")).lower()
    assert "quote" in section, "%s does not require the rule to be quoted" % path.name
    assert "not a language finding" in section, (
        "%s does not say what to do with an item that cannot be sourced" % path.name
    )


@pytest.mark.parametrize("path", INSTRUCTIONS, ids=["evaluator", "deck-qc"])
def test_no_voice_dimension_is_scored(path):
    """Voice differs between competent consultants. Scoring it needs a permanent arbiter and
    cannot be enforced once the skills are shared, so the dimension is gone, not renamed."""
    text = path.read_text(encoding="utf-8")
    low = text.lower()
    assert "five dimensions" not in low, "%s still scores five dimensions" % path.name
    assert "four dimensions" in low, "%s does not state the four scored dimensions" % path.name
    header_row = [ln for ln in text.splitlines() if ln.startswith("| Score |")]
    for row in header_row:
        assert "Register" not in row, "%s scorecard still carries a Register column" % path.name


@pytest.mark.parametrize("path", INSTRUCTIONS, ids=["evaluator", "deck-qc"])
def test_preferences_are_not_a_source_of_findings(path):
    """The taste rules survive as house habit. A check that cites them re-creates the problem the
    retirement was meant to remove, so both instructions must rule them out by name."""
    section = _language_section(path.read_text(encoding="utf-8")).lower()
    assert "preferences" in section, (
        "%s language section does not mention the Preferences section" % path.name
    )


def test_house_register_separates_enforceable_from_preference():
    """The file is the source both instructions read. It has to carry the split itself, or the
    instruction not to cite preferences has nothing to point at."""
    text = HOUSE_REGISTER.read_text(encoding="utf-8")
    low = text.lower()
    assert "## enforceable conventions" in low, "house-register has no enforceable section"
    assert "## preferences, not enforced" in low, "house-register has no preferences section"
    prefs = text[low.find("## preferences, not enforced"):]
    prefs = prefs[: prefs.find("\n## ") if "\n## " in prefs else None]
    assert "no check may cite" in prefs.lower(), (
        "the Preferences section does not say that no check may cite it"
    )


def test_house_register_states_the_outside_reader_standard():
    """The whole point of the change: the bar is professional consulting writing, which a stranger
    can apply, not an imitation of one firm's voice, which needs a maintainer."""
    low = HOUSE_REGISTER.read_text(encoding="utf-8").lower()
    assert "nothing in this file is scored" in low, (
        "house-register does not say that it carries no score"
    )
    assert "outside the firm" in low, (
        "house-register does not state the outside-reader test a convention must pass"
    )


def test_evaluator_paths_resolve_in_any_install():
    """The evaluator runs in the repo, from a plugin and in Cowork, so it names skill files relative to the
    skills folder and finds that folder first. A `.claude/skills/` path would resolve only in the repo, and an
    evaluator that cannot find the rule files reviews from memory."""
    import re
    text = AGENT.read_text(encoding="utf-8")
    skills = REPO / ".claude" / "skills"
    named = set(re.findall(r"`((?:deck-qc|draft-deck|stakeholder-context)/[\w./-]+\.md)`", text))
    assert named, "the evaluator names no skill files"
    missing = sorted(p for p in named if not (skills / p).exists())
    assert not missing, "evaluator names files that do not exist: %s" % missing
    body = text.split("**Find the skill files first.**", 1)
    assert len(body) == 2, "the evaluator does not say how to find the skill files"
    assert ".claude/skills/" not in body[1].split("\n\n", 1)[1], "a repo-only path is used after the finding step"


# ---- patch 2026-09-23: false positives found on a second client's shipped decks ----------------

HAND_HEX = "12A45C"


def _blank_deck(n_slides: int):
    prs = Presentation()
    for _ in range(n_slides):
        prs.slides.add_slide(prs.slide_layouts[6])
    return prs


def _box(slide, x, y, w, h, text, size=12):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tb.text_frame.text = text
    for p in tb.text_frame.paragraphs:
        for r in p.runs:
            r.font.size = Pt(size)
    return tb


def _fill(slide, hex_, top=Inches(1)):
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE

    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1), top, Inches(1), Inches(0.5))
    sh.fill.solid()
    sh.fill.fore_color.rgb = RGBColor.from_string(hex_)
    sh.line.fill.background()


def test_a_brand_color_applied_by_hand_on_most_slides_is_the_decks_palette(tmp_path, rules):
    """A client template can apply its brand color by hand instead of through the theme. A fill that recurs
    on three or more slides is the deck's palette; a color on one slide is still reported."""
    prs = _blank_deck(4)
    for s in prs.slides:
        _fill(s, HAND_HEX)
    _fill(prs.slides[2], "C81E1E", top=Inches(3))
    out = tmp_path / "hand_palette.pptx"
    prs.save(str(out))
    _deck, findings = qc_check.run_checks(out, rules)
    fills = [f for f in findings if f.id == "style-drift" and "fill color" in f.detail]
    assert len(fills) == 1 and fills[0].slide == 3 and "C81E1E" in fills[0].detail, [f.detail for f in fills]
    assert not any(HAND_HEX in f.detail for f in fills)


def test_rules_carry_no_client_palette(rules):
    """Client colors come from the deck (theme or recurrence) or from a screenshot the consultant supplies;
    no rule file codifies one."""
    assert "client_palettes" not in rules and "active_client_palette" not in rules


def test_vertical_label_is_not_off_canvas(tmp_path, rules):
    """A 270-degree label near the left edge: its stored box starts left of the slide, its drawn box does not."""
    prs = _blank_deck(1)
    tb = _box(prs.slides[0], Emu(-450000), Inches(3), Inches(1.7), Inches(0.3), "1. Select inputs")
    tb.rotation = 270
    out = tmp_path / "vertical.pptx"
    prs.save(str(out))
    _deck, findings = qc_check.run_checks(out, rules)
    assert not [f for f in findings if f.id == "off-canvas"], findings


def test_badge_smaller_than_its_insets_is_not_an_overflow(tmp_path, rules):
    """A 10pt numbered chip: default insets exceed its width, so no text-height estimate is meaningful."""
    prs = _blank_deck(1)
    from pptx.enum.text import MSO_AUTO_SIZE

    chip = _box(prs.slides[0], Inches(1), Inches(1), Pt(10), Pt(10), "2", size=9)
    chip.text_frame.word_wrap = True
    chip.text_frame.auto_size = MSO_AUTO_SIZE.NONE
    out = tmp_path / "badge.pptx"
    prs.save(str(out))
    _deck, findings = qc_check.run_checks(out, rules)
    assert not [f for f in findings if f.id == "overflow-estimate"], [f.detail for f in findings]


def _superscript(run):
    run.font._rPr.set("baseline", "30000")


def test_superscript_opening_a_paragraph_is_a_footnote_not_a_marker(tmp_path, rules):
    """A two-paragraph note box sits above the footnote band; its second paragraph opens with a superscript 1.
    That run is the footnote for the body's marker, not a second marker."""
    prs = _blank_deck(1)
    s = prs.slides[0]
    body = _box(s, Inches(1), Inches(2), Inches(6), Inches(0.6), "Out of scope such as certification.")
    _superscript(body.text_frame.paragraphs[0].add_run())
    body.text_frame.paragraphs[0].runs[-1].text = "1"
    note = _box(s, Inches(1), Inches(6.2), Inches(8), Inches(0.6), "Only category with procedural standing.", size=9)
    p2 = note.text_frame.add_paragraph()
    r1 = p2.add_run()
    r1.text = "1"
    _superscript(r1)
    p2.add_run().text = "A negative vote on a non-germane item counts as an abstention."
    out = tmp_path / "sup_def.pptx"
    prs.save(str(out))
    _deck, findings = qc_check.run_checks(out, rules)
    assert not [f for f in findings if f.id == "footnote-sequence"], [f.detail for f in findings]


def test_value_label_in_the_footnote_band_is_not_a_footnote(tmp_path, rules):
    """'90 (max)' at the foot of a table column is a value, not footnote 90."""
    prs = _blank_deck(1)
    s = prs.slides[0]
    body = _box(s, Inches(1), Inches(2), Inches(3), Inches(0.4), "Stakeholders involved")
    r = body.text_frame.paragraphs[0].add_run()
    r.text = "1"
    _superscript(r)
    _box(s, Inches(5), Inches(6.9), Inches(0.8), Inches(0.2), "90 (max)", size=9)
    _box(s, Inches(1), Inches(7.2), Inches(8), Inches(0.25), "1. Additional stakeholders for harmonized standards.", size=8)
    out = tmp_path / "band_value.pptx"
    prs.save(str(out))
    _deck, findings = qc_check.run_checks(out, rules)
    assert not [f for f in findings if f.id == "footnote-sequence"], [f.detail for f in findings]


def test_fill_in_field_in_quoted_sample_text_warns_and_a_bare_token_blocks(tmp_path, rules):
    prs = _blank_deck(1)
    s = prs.slides[0]
    _box(s, Inches(1), Inches(1), Inches(8), Inches(0.5),
         "\u201cThe ballot for [Proposal XXX] is now open as of [date].\u201d")
    _box(s, Inches(1), Inches(3), Inches(8), Inches(0.5), "Spend grew XX points against the plan.")
    out = tmp_path / "fields.pptx"
    prs.save(str(out))
    _deck, findings = qc_check.run_checks(out, rules)
    ph = sorted((f.severity, f.text[:4]) for f in findings if f.id == "placeholders")
    assert ph == [("block", "Spen"), ("warn", "\u201cThe")], ph


def _one_box(tmp_path, text: str, top_in: float, size_pt: int, name: str = "Text 19") -> Path:
    prs = Presentation(str(CLEAN))
    tb = prs.slides[0].shapes.add_textbox(Inches(1), Inches(top_in), Inches(6), Inches(0.3))
    tb.name = name
    tb.text_frame.text = text
    for r in tb.text_frame.paragraphs[0].runs:
        r.font.size = Pt(size_pt)
    out = tmp_path / "box.pptx"
    prs.save(str(out))
    return out


def test_source_line_above_the_band_is_a_footnote(tmp_path, rules):
    """A 9pt "Source:" box a few points above the bottom band is a footnote, not 9pt body text."""
    out = _one_box(tmp_path, "Source: Annual Workforce Survey, 2025", 5.6, 9)
    _deck, findings = qc_check.run_checks(out, rules)
    assert not [f for f in findings if f.id == "font-size-floor" and "Workforce" in (f.text or "")], findings


def test_nine_point_body_text_still_blocks(tmp_path, rules):
    out = _one_box(tmp_path, "Enrollment rose across every segment", 3.0, 9)
    _deck, findings = qc_check.run_checks(out, rules)
    assert [f for f in findings if f.id == "font-size-floor" and f.severity == "block"]


@pytest.mark.parametrize("token", ["[~X weeks]", "[X weeks]", "[x weeks]", "[$X]", "[X%]"])
def test_bracketed_x_is_a_placeholder(tmp_path, rules, token):
    out = _one_box(tmp_path, "Phase 1 runs %s from kickoff" % token, 3.0, 12)
    _deck, findings = qc_check.run_checks(out, rules)
    assert any(f.id == "placeholders" and f.severity == "block" for f in findings), token


def test_a_word_starting_with_x_is_not_a_placeholder(tmp_path, rules):
    out = _one_box(tmp_path, "As the [Xerox study] showed", 3.0, 12)
    _deck, findings = qc_check.run_checks(out, rules)
    assert not any(f.id == "placeholders" for f in findings)
