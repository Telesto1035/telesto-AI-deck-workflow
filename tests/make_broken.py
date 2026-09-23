#!/usr/bin/env python3
"""make_broken.py: plant known faults into a clean deck so test_qc_check.py can assert each is found.

Usage:
    python tests/make_broken.py SRC.pptx DST.pptx
    python tests/make_broken.py            # every clean fixture -> tests/fixtures/broken/<name>.broken.pptx

Planted faults (all on slide 1 unless noted), each mapped to the qc_check.py finding it must trigger:
    body run at 9pt .................... font-size-floor  (shape "QC body 9pt")
    footnote list at 7pt ............... font-size-floor  (shape "QC footnotes", bottom band)
    italic quote in straight quotes .... nothing (italics check removed 2026-09-23)
    author "Reviewer One" ............... author-empty (x2: creator and lastModifiedBy)
    TotalTime 214 ...................... metadata-scrub
    custom.xml with SharePoint fields .. metadata-scrub
    speaker note "Build sequence: ..." . speaker-notes
    [PLACEHOLDER: source needed] ....... placeholders
    table row 40+30+28 vs Total 100 .... totals-sum (3x5 native table)
    chart cache 34 with label "36%" .... chart-cache-label
    data labels centred in bars ........ label-in-bar
    markers 1 2 4 vs footnotes 1 2 3 ... footnote-sequence
    "State" for Department of State .... abbreviation-list
    "Jane Q. Stakeholder" .............. stakeholder-name (when rules carry the name)
    empty text box ..................... empty-textbox
    "DL 11-Sep-26: ..." note ............ reviewer-note
    "Takeaway:" with nothing after ..... empty-label
    two colliding text boxes ........... shape-overlap
    300 words of body text ............. word-count (warn only)
    shape past the right edge .......... off-canvas
    hidden last slide .................. hidden-slides
    DRAFT on slide 1 only .............. draft-stamp (multi-slide decks only)
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"

AUTHOR = "Reviewer One"
TOTAL_TIME = "214"
NOTE_TEXT = "Build sequence: title first, then the exhibit, then the recommendation band. Do not ship this note."
STAKEHOLDER = "Jane Q. Stakeholder"

# The faults as (finding id, severity) pairs, so the test can assert the exact block set.
PLANTED_BLOCK_IDS = {
    "font-size-floor",
    "author-empty",
    "metadata-scrub",
    "speaker-notes",
    "placeholders",
    "totals-sum",
    "chart-cache-label",
    "footnote-sequence",
    "reviewer-note",
    "empty-label",
}
PLANTED_WARN_IDS = {
    "shape-overlap",
    "word-count",
    "label-in-bar",
    "abbreviation-list",
    "empty-textbox",
    "off-canvas",
    "hidden-slides",
}
PLANTED_WITH_NAME_RULES = {"stakeholder-name"}
PLANTED_MULTISLIDE_WARN_IDS = {"draft-stamp"}


def _textbox(slide, left, top, width, height, text, size=12, name=None, italic=False, autofit=True, bold=False):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    if autofit:
        tf.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT
    para = tf.paragraphs[0]
    run = para.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold or None
    if italic:
        run.font.italic = True
    if name:
        box.name = name
    return box


def plant_slide_faults(prs: Presentation) -> None:
    slide = prs.slides[0]
    W, H = prs.slide_width, prs.slide_height
    col_w = Inches(3.6)
    x1, x2, x3 = Inches(0.5), Inches(4.4), Inches(8.3)
    y = Inches(1.6)

    # 1. body run at 9pt (outside the footnote band)
    _textbox(slide, x1, y, col_w, Inches(0.4), "Body copy set at nine point to test the floor.", size=9, name="QC body 9pt")

    # 2. italic quote
    _textbox(slide, x1, y + Inches(0.5), col_w, Inches(0.4), '"We would fund the next phase" (VP Operations)', size=12,
             name="QC italic quote", italic=True)

    # 3. placeholder token
    _textbox(slide, x1, y + Inches(1.0), col_w, Inches(0.4), "Ridership grew 12% in 2025 [PLACEHOLDER: source needed]",
             size=12, name="QC placeholder")

    # 4. footnote markers 1 2 4 in the body ...
    _textbox(slide, x1, y + Inches(1.5), col_w, Inches(0.6),
             "Ridership rose 12%¹ while adoption lagged² and unit costs fell⁴ across the four settings.",
             size=12, name="QC markers")

    # ... against footnotes 1 2 3 at 7pt in the bottom band
    fn = slide.shapes.add_textbox(Inches(0.5), int(H * 0.90), Inches(9), Inches(0.5))
    fn.name = "QC footnotes"
    tf = fn.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT
    lines = [
        "1. Source: Institution Priorities survey, n=250",
        "2. Source: Competitive Intelligence survey, n=302",
        "3. Source: APTA ridership report, 2025",
    ]
    for i, line in enumerate(lines):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        run = para.add_run()
        run.text = line
        run.font.size = Pt(7)

    # 5. agency abbreviation (not at sentence start)
    _textbox(slide, x2, y, col_w, Inches(0.4), "Funding from State covers the gap in year two.", size=12,
             name="QC abbreviation")

    # 6. stakeholder name (flagged only when rules carry it)
    _textbox(slide, x2, y + Inches(0.5), col_w, Inches(0.4), "Prepared for %s" % STAKEHOLDER, size=12,
             name="QC stakeholder")

    # 7. empty text box
    empty = slide.shapes.add_textbox(x2, y + Inches(1.0), col_w, Inches(0.4))
    empty.name = "QC empty"

    # 7b. reviewer note left as slide text, and a register label with nothing after it
    _textbox(slide, x2, y + Inches(1.3), col_w, Inches(0.3), "DL 11-Sep-26: logo order is wrong, reorder", size=12,
             name="QC reviewer note")
    _textbox(slide, x3, y + Inches(3.1), Inches(2.5), Inches(0.3), "Takeaway:", size=12, name="QC empty label")

    # 7c. two text boxes that collide
    _textbox(slide, x3, y + Inches(2.75), Inches(2.4), Inches(0.4), "Overlap A: this box sits under the next", size=12, name="QC overlap A")
    _textbox(slide, x3 + Inches(0.6), y + Inches(2.85), Inches(2.4), Inches(0.4), "Overlap B: this box sits on the previous", size=12, name="QC overlap B")

    # 7d. a wordy page: 300 words of body text
    _textbox(slide, x1, y + Inches(2.3), Inches(3.4), Inches(1.2),
             " ".join("word%d" % i for i in range(300)), size=12, name="QC wordy")

    # 8. off-canvas shape
    _textbox(slide, W + Inches(0.5), y, Inches(2), Inches(0.4), "Off the right edge", size=12, name="QC off-canvas")

    # 9. native table: components 40 + 30 + 28 against a stated total of 100. The semicolon cell is
    # left in on purpose: nothing may flag it, and test_qc_check guards that.
    rows, cols = 3, 5
    gf = slide.shapes.add_table(rows, cols, x2, y + Inches(1.6), Inches(4.5), Inches(1.0))
    gf.name = "QC table"
    tbl = gf.table
    data = [
        ["Segment", "A", "B", "C", "Total"],
        ["Share", "40%", "30%", "28%", "100%"],
        ["Items", "alpha; beta; gamma", "", "", ""],
    ]
    for r in range(rows):
        for c in range(cols):
            cell = tbl.cell(r, c)
            cell.text = data[r][c]
            for para in cell.text_frame.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(12)

    # 10. chart: cached value 34 with a custom label "36%", labels centred inside the bars
    cd = CategoryChartData()
    cd.categories = ["Rail", "Bus", "Ferry"]
    cd.add_series("Share", (34, 40, 26))
    gf2 = slide.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, x3, y, Inches(3.5), Inches(2.5), cd)
    gf2.name = "QC chart"
    chart = gf2.chart
    plot = chart.plots[0]
    plot.has_data_labels = True
    plot.data_labels.position = XL_LABEL_POSITION.CENTER
    plot.data_labels.font.size = Pt(12)
    point = plot.series[0].points[0]
    point.data_label.text_frame.text = "36%"
    point.data_label.text_frame.paragraphs[0].runs[0].font.size = Pt(12)

    # 11. speaker note
    slide.notes_slide.notes_text_frame.text = NOTE_TEXT

    # 12. DRAFT stamp on slide 1 only (multi-slide decks)
    if len(prs.slides) > 1:
        _textbox(slide, x3, y + Inches(2.7), Inches(1.5), Inches(0.4), "DRAFT", size=12, name="QC draft stamp", bold=True)

    # 13. hide the last slide
    prs.slides[-1]._element.set("show", "0")


NS_CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
NS_DC = "http://purl.org/dc/elements/1.1/"
NS_EP = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
NS_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_CT = "http://schemas.openxmlformats.org/package/2006/content-types"

CUSTOM_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/custom-properties" '
    'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
    '<property fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="2" name="ContentTypeId">'
    "<vt:lpwstr>0x010100B2C4D6E8F0A2B4C6D8E0F2A4B6C8D0</vt:lpwstr></property>"
    '<property fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="3" name="TemplateUrl"><vt:lpwstr></vt:lpwstr></property>'
    '<property fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="4" name="TriggerFlowInfo"><vt:lpwstr></vt:lpwstr></property>'
    '<property fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="5" name="ComplianceAssetId"><vt:lpwstr></vt:lpwstr></property>'
    '<property fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="6" name="MediaServiceImageTags"><vt:lpwstr></vt:lpwstr></property>'
    "</Properties>"
).encode("utf-8")


def plant_package_faults(pptx_bytes: bytes) -> bytes:
    """Author, TotalTime and custom.xml, edited at the zip level."""
    with zipfile.ZipFile(io.BytesIO(pptx_bytes)) as z:
        parts = {n: z.read(n) for n in z.namelist()}
        order = z.namelist()

    core = etree.fromstring(parts["docProps/core.xml"])
    for tag in ("{%s}creator" % NS_DC, "{%s}lastModifiedBy" % NS_CP):
        node = core.find(tag)
        if node is None:
            node = etree.SubElement(core, tag)
        node.text = AUTHOR
    parts["docProps/core.xml"] = etree.tostring(core, xml_declaration=True, encoding="UTF-8", standalone=True)

    app = etree.fromstring(parts["docProps/app.xml"])
    tt = app.find("{%s}TotalTime" % NS_EP)
    if tt is None:
        tt = etree.Element("{%s}TotalTime" % NS_EP)
        app.insert(0, tt)
    tt.text = TOTAL_TIME
    parts["docProps/app.xml"] = etree.tostring(app, xml_declaration=True, encoding="UTF-8", standalone=True)

    parts["docProps/custom.xml"] = CUSTOM_XML
    order.append("docProps/custom.xml")
    rels = etree.fromstring(parts["_rels/.rels"])
    ids = {r.get("Id") for r in rels}
    n = 1
    while "rId%d" % n in ids:
        n += 1
    etree.SubElement(
        rels, "{%s}Relationship" % NS_REL,
        Id="rId%d" % n,
        Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/custom-properties",
        Target="docProps/custom.xml",
    )
    parts["_rels/.rels"] = etree.tostring(rels, xml_declaration=True, encoding="UTF-8", standalone=True)
    ct = etree.fromstring(parts["[Content_Types].xml"])
    etree.SubElement(
        ct, "{%s}Override" % NS_CT,
        PartName="/docProps/custom.xml",
        ContentType="application/vnd.openxmlformats-officedocument.custom-properties+xml",
    )
    parts["[Content_Types].xml"] = etree.tostring(ct, xml_declaration=True, encoding="UTF-8", standalone=True)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name in order:
            z.writestr(name, parts[name])
    return buf.getvalue()


def make_broken(src: Path, dst: Path) -> Path:
    prs = Presentation(str(src))
    plant_slide_faults(prs)
    buf = io.BytesIO()
    prs.save(buf)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(plant_package_faults(buf.getvalue()))
    Presentation(str(dst))  # must re-open
    return dst


def clean_fixtures() -> list[Path]:
    return sorted(p for p in FIXTURES.glob("*.pptx"))


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) == 2:
        out = make_broken(Path(argv[0]), Path(argv[1]))
        print(out)
        return 0
    if argv:
        print(__doc__)
        return 2
    out_dir = FIXTURES / "broken"
    for src in clean_fixtures():
        out = make_broken(src, out_dir / (src.stem + ".broken.pptx"))
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
