"""plant_comments.py: add reviewer comments to a copy of a clean deck, in both PowerPoint comment formats.

Used by test_pptx_comments.py and test_deck_diff.py. The client decks that carry real comments are gitignored, so the
tests build their own: one modern comment part (PowerPoint 2019+/365 format, with an authors part and a resolved
comment) on slide 1, and one legacy comment part (2007-2016 format) on slide 2.

Usage:
    python tests/plant_comments.py SRC.pptx DST.pptx
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

MODERN_AUTHOR_ID = "{3DFEABE6-BCA7-74ED-8139-C572E198BF06}"
MODERN_CT = "application/vnd.ms-powerpoint.comments+xml"
AUTHORS_CT = "application/vnd.ms-powerpoint.authors+xml"
LEGACY_CT = "application/vnd.openxmlformats-officedocument.presentationml.comments+xml"
LEGACY_AUTHORS_CT = "application/vnd.openxmlformats-officedocument.presentationml.commentAuthors+xml"
MODERN_REL = "http://schemas.microsoft.com/office/2018/10/relationships/comments"
AUTHORS_REL = "http://schemas.microsoft.com/office/2018/10/relationships/authors"
LEGACY_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
LEGACY_AUTHORS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/commentAuthors"

# what the tests expect to read back, in slide order
EXPECTED = [
    # (slide, author, text, status, store)
    (1, "Alex Kruzel", "Make this title more descriptive", "active", "modern"),
    (1, "Alex Kruzel", "Add the recommendation band", "resolved", "modern"),
    (2, "Fiona Kalensky", "Please add the footnotes", "active", "legacy"),
]

MODERN_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<p188:cmLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:p188="http://schemas.microsoft.com/office/powerpoint/2018/8/main">'
    '<p188:cm id="{11111111-0000-0000-0000-000000000001}" authorId="%s" created="2026-09-12T16:33:50.834">'
    '<ac:deMkLst xmlns:ac="http://schemas.microsoft.com/office/drawing/2013/main/command">'
    '<pc:docMk xmlns:pc="http://schemas.microsoft.com/office/powerpoint/2013/main/command"/>'
    '<pc:sldMk xmlns:pc="http://schemas.microsoft.com/office/powerpoint/2013/main/command" cId="1" sldId="256"/>'
    '<ac:spMk id="2" creationId="{00000000-0000-0000-0000-000000000000}"/></ac:deMkLst>'
    '<p188:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="en-US"/><a:t>Make this title more descriptive</a:t></a:r></a:p></p188:txBody>'
    '<p188:replyLst><p188:reply id="{11111111-0000-0000-0000-000000000009}" authorId="%s" created="2026-09-12T17:00:00.000">'
    '<p188:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="en-US"/><a:t>Agreed, will do</a:t></a:r></a:p></p188:txBody></p188:reply></p188:replyLst>'
    '</p188:cm>'
    '<p188:cm id="{11111111-0000-0000-0000-000000000002}" authorId="%s" created="2026-09-12T16:35:03.478" status="resolved">'
    '<pc:sldMkLst xmlns:pc="http://schemas.microsoft.com/office/powerpoint/2013/main/command"><pc:docMk/><pc:sldMk cId="1" sldId="256"/></pc:sldMkLst>'
    '<p188:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="en-US"/><a:t>Add the recommendation band</a:t></a:r></a:p></p188:txBody>'
    '</p188:cm></p188:cmLst>'
) % (MODERN_AUTHOR_ID, MODERN_AUTHOR_ID, MODERN_AUTHOR_ID)

AUTHORS_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<p188:authorLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:p188="http://schemas.microsoft.com/office/powerpoint/2018/8/main">'
    '<p188:author id="%s" name="Alex Kruzel" initials="AK" userId="test" providerId="None"/>'
    '</p188:authorLst>'
) % MODERN_AUTHOR_ID

LEGACY_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<p:cmLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
    '<p:cm authorId="0" dt="2026-09-10T09:00:00.000" idx="1"><p:pos x="10" y="10"/><p:text>Please add the footnotes</p:text></p:cm>'
    '</p:cmLst>'
)

LEGACY_AUTHORS_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<p:cmAuthorLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
    '<p:cmAuthor id="0" name="Fiona Kalensky" initials="FK" lastIdx="1" clrIdx="0"/>'
    '</p:cmAuthorLst>'
)


def _add_rel(rels_xml: str, rel_type: str, target: str) -> str:
    ids = [int(m) for m in re.findall(r'Id="rId(\d+)"', rels_xml)]
    rid = "rId%d" % (max(ids) + 1 if ids else 1)
    rel = '<Relationship Id="%s" Type="%s" Target="%s"/>' % (rid, rel_type, target)
    return rels_xml.replace("</Relationships>", rel + "</Relationships>")


def _add_override(ct_xml: str, part: str, ctype: str) -> str:
    ov = '<Override PartName="/%s" ContentType="%s"/>' % (part, ctype)
    return ct_xml.replace("</Types>", ov + "</Types>")


def plant(src: Path, dst: Path) -> Path:
    with zipfile.ZipFile(src) as zin:
        parts = {i.filename: zin.read(i.filename) for i in zin.infolist()}
        infos = {i.filename: i for i in zin.infolist()}
    ct = parts["[Content_Types].xml"].decode("utf-8")
    pres_rels = parts["ppt/_rels/presentation.xml.rels"].decode("utf-8")
    s1 = parts.get("ppt/slides/_rels/slide1.xml.rels", b"").decode("utf-8") or (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>')
    s2 = parts.get("ppt/slides/_rels/slide2.xml.rels", b"").decode("utf-8") or s1.split("<Relationship ")[0] + "</Relationships>"

    parts["ppt/comments/modernComment_TEST_0001.xml"] = MODERN_XML.encode("utf-8")
    parts["ppt/authors.xml"] = AUTHORS_XML.encode("utf-8")
    parts["ppt/comments/comment1.xml"] = LEGACY_XML.encode("utf-8")
    parts["ppt/commentAuthors.xml"] = LEGACY_AUTHORS_XML.encode("utf-8")
    ct = _add_override(ct, "ppt/comments/modernComment_TEST_0001.xml", MODERN_CT)
    ct = _add_override(ct, "ppt/authors.xml", AUTHORS_CT)
    ct = _add_override(ct, "ppt/comments/comment1.xml", LEGACY_CT)
    ct = _add_override(ct, "ppt/commentAuthors.xml", LEGACY_AUTHORS_CT)
    pres_rels = _add_rel(pres_rels, AUTHORS_REL, "authors.xml")
    pres_rels = _add_rel(pres_rels, LEGACY_AUTHORS_REL, "commentAuthors.xml")
    s1 = _add_rel(s1, MODERN_REL, "../comments/modernComment_TEST_0001.xml")
    s2 = _add_rel(s2, LEGACY_REL, "../comments/comment1.xml")
    parts["[Content_Types].xml"] = ct.encode("utf-8")
    parts["ppt/_rels/presentation.xml.rels"] = pres_rels.encode("utf-8")
    parts["ppt/slides/_rels/slide1.xml.rels"] = s1.encode("utf-8")
    parts["ppt/slides/_rels/slide2.xml.rels"] = s2.encode("utf-8")

    dst.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in parts.items():
            if name in infos:
                zout.writestr(infos[name], data)
            else:
                zout.writestr(name, data)
    return dst


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(__doc__)
        return 2
    out = plant(Path(argv[0]), Path(argv[1]))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
