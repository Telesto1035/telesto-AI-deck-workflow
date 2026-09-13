#!/usr/bin/env python3
"""qc_check.py: the deterministic gate of deck-qc Layer 1 plus the hygiene pass.

Usage:
    python qc_check.py DECK.pptx [--rules qc_rules.json] [--json out.json] [--fix-safe]
                        [--profile findings|proposal|kickoff|minipack|presentation|update|workshop]

Exit 0: no blocking findings. Exit 1: blocking findings present. Exit 2: file could not be opened.

Everything a model has to judge (numbers vs source, referents, title chain, voice) stays in the
deck-qc skill. This script reads the XML and reports what it can prove. Hanging words and true
overflow need the render and are confirmed by the skill.
"""
from __future__ import annotations

import argparse
import io
import json
import math
import re
import sys
import time
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Optional

from lxml import etree
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE, PP_PLACEHOLDER
from pptx.opc.constants import RELATIONSHIP_TYPE as RT

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "ep": "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties",
    "vt": "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    "p188": "http://schemas.microsoft.com/office/powerpoint/2018/8/main",
}
EMU_PER_PT = 12700
SUPERSCRIPT_DIGITS = {"⁰": 0, "¹": 1, "²": 2, "³": 3, "⁴": 4, "⁵": 5, "⁶": 6, "⁷": 7, "⁸": 8, "⁹": 9}
TITLE_TYPES = (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE)
NUMBER_RE = re.compile(r"(?<![\w.])[-+]?\$?(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?\s?(%|pts?|pp)?(?![\w.])")
DEFAULT_RULES_PATH = Path(__file__).with_name("qc_rules.json")


def q(tag: str) -> str:
    prefix, local = tag.split(":")
    return "{%s}%s" % (NS[prefix], local)


# --------------------------------------------------------------------------------------
# Findings
# --------------------------------------------------------------------------------------


@dataclass
class Finding:
    id: str
    severity: str  # block | warn | info
    slide: Optional[int]
    shape: Optional[str]
    shape_id: Optional[int]
    text: str
    detail: str
    fix: str = "none"  # resize | reword | clear | delete | none
    auto_fixable: bool = False

    def as_dict(self) -> dict:
        return asdict(self)


SEVERITY_ORDER = {"block": 0, "warn": 1, "info": 2}


# --------------------------------------------------------------------------------------
# Shape and run views
# --------------------------------------------------------------------------------------


@dataclass
class ShapeInfo:
    shape: object  # python-pptx shape
    slide_no: int
    box: Optional[tuple]  # (x, y, w, h) absolute EMU, or None when unknown
    in_group: bool
    group_key: Optional[int]  # shape_id of the nearest enclosing group

    @property
    def name(self) -> str:
        return self.shape.name

    @property
    def shape_id(self) -> int:
        return self.shape.shape_id


@dataclass
class RunInfo:
    text: str
    size: Optional[float]  # effective size in pt after fontScale, None when unknown
    italic: bool
    superscript: bool
    latin: Optional[str]
    para_index: int
    para_text: str
    elm: object
    in_table_cell: bool = False


def visible(text: str) -> bool:
    return bool(text) and bool(text.strip())


def parse_number(s: str):
    """Return (value, is_percent) for the first number in s, or None."""
    m = NUMBER_RE.search(s)
    if not m:
        return None
    whole = m.group(1).replace(",", "")
    frac = m.group(2) or ""
    try:
        val = float(whole + frac)
    except ValueError:
        return None
    if m.group(0).lstrip().startswith("-"):
        val = -val
    return val, (m.group(3) or "").startswith("%")


def all_numbers(s: str) -> list:
    out = []
    for m in NUMBER_RE.finditer(s):
        whole = m.group(1).replace(",", "")
        frac = m.group(2) or ""
        try:
            val = float(whole + frac)
        except ValueError:
            continue
        if m.group(0).lstrip().startswith("-"):
            val = -val
        out.append((val, (m.group(3) or "").startswith("%")))
    return out


def hex_distance_ok(color: str, palette: Iterable[str], tol: int) -> bool:
    try:
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
    except ValueError:
        return True
    for p in palette:
        try:
            pr, pg, pb = int(p[0:2], 16), int(p[2:4], 16), int(p[4:6], 16)
        except (ValueError, IndexError):
            continue
        if abs(r - pr) <= tol and abs(g - pg) <= tol and abs(b - pb) <= tol:
            return True
    return False


# --------------------------------------------------------------------------------------
# Deck model
# --------------------------------------------------------------------------------------


class Deck:
    def __init__(self, path: Path, rules: dict):
        self.path = Path(path)
        self.rules = rules
        with zipfile.ZipFile(self.path) as z:
            self.parts = {n: z.read(n) for n in z.namelist()}
        self.prs = Presentation(str(self.path))
        self.W = self.prs.slide_width
        self.H = self.prs.slide_height
        self.findings: list[Finding] = []
        self._xml_cache: dict = {}
        self.footnote_name_re = re.compile(rules.get("footnote_name_regex", "foot|source|note"), re.I)
        self.slides = list(self.prs.slides)
        self.shapes_by_slide: dict[int, list[ShapeInfo]] = {}
        for i, slide in enumerate(self.slides, 1):
            self.shapes_by_slide[i] = self._walk(slide, i)
        self._theme_cache: dict = {}
        self._default_style = self._presentation_default_style()
        self.appendix_start = self._find_appendix_start()  # 1-based slide number of the first appendix page, or None

    def _find_appendix_start(self):
        for i, slide in enumerate(self.slides, 1):
            t = slide.shapes.title
            txt = t.text.strip() if t is not None and t.has_text_frame else ""
            if re.match(r"^(appendix|crosstabs?|backup)\b", txt, re.I):
                return i
        return None

    def is_appendix(self, sno: int) -> bool:
        return self.appendix_start is not None and sno >= self.appendix_start

    # ---- parts -------------------------------------------------------------------------

    def xml(self, name: str):
        if name in self._xml_cache:
            return self._xml_cache[name]
        blob = self.parts.get(name)
        elm = None
        if blob is not None:
            try:
                elm = etree.fromstring(blob)
            except etree.XMLSyntaxError:
                elm = None
        self._xml_cache[name] = elm
        return elm

    def _presentation_default_style(self):
        pres = self.xml("ppt/presentation.xml")
        if pres is None:
            return None
        return pres.find(q("p:defaultTextStyle"))

    def theme_for(self, master):
        key = id(master)
        if key in self._theme_cache:
            return self._theme_cache[key]
        theme = None
        try:
            part = master.part.part_related_by(RT.THEME)
            theme = etree.fromstring(part.blob)
        except Exception:  # noqa: BLE001 - a deck without a theme part is still checkable
            theme = None
        self._theme_cache[key] = theme
        return theme

    def theme_colors(self, master) -> set:
        theme = self.theme_for(master)
        out = set()
        if theme is None:
            return out
        scheme = theme.find(".//" + q("a:clrScheme"))
        if scheme is None:
            return out
        for child in scheme:
            srgb = child.find(q("a:srgbClr"))
            sysc = child.find(q("a:sysClr"))
            if srgb is not None and srgb.get("val"):
                out.add(srgb.get("val").upper())
            elif sysc is not None and sysc.get("lastClr"):
                out.add(sysc.get("lastClr").upper())
        return out

    def theme_font(self, master, major: bool) -> Optional[str]:
        theme = self.theme_for(master)
        if theme is None:
            return None
        tag = "a:majorFont" if major else "a:minorFont"
        node = theme.find(".//" + q(tag) + "/" + q("a:latin"))
        return node.get("typeface") if node is not None else None

    # ---- shapes ------------------------------------------------------------------------

    def _walk(self, slide, slide_no: int) -> list[ShapeInfo]:
        out: list[ShapeInfo] = []

        def rec(shapes, ax, ay, sx, sy, in_group, group_key):
            for sh in shapes:
                try:
                    l, t, w, h = sh.left, sh.top, sh.width, sh.height
                except Exception:  # noqa: BLE001
                    l = t = w = h = None
                box = None
                if None not in (l, t, w, h):
                    box = (ax + sx * l, ay + sy * t, sx * w, sy * h)
                out.append(ShapeInfo(sh, slide_no, box, in_group, group_key))
                if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
                    xfrm = sh._element.find(q("p:grpSpPr") + "/" + q("a:xfrm"))
                    nax, nay, nsx, nsy = ax, ay, sx, sy
                    if xfrm is not None:
                        off = xfrm.find(q("a:off"))
                        ext = xfrm.find(q("a:ext"))
                        choff = xfrm.find(q("a:chOff"))
                        chext = xfrm.find(q("a:chExt"))
                        if None not in (off, ext, choff, chext):
                            ox, oy = int(off.get("x", 0)), int(off.get("y", 0))
                            ex, ey = int(ext.get("cx", 0)), int(ext.get("cy", 0))
                            cox, coy = int(choff.get("x", 0)), int(choff.get("y", 0))
                            cex, cey = int(chext.get("cx", 0)), int(chext.get("cy", 0))
                            fx = ex / cex if cex else 1.0
                            fy = ey / cey if cey else 1.0
                            nsx, nsy = sx * fx, sy * fy
                            nax = ax + sx * (ox - cox * fx)
                            nay = ay + sy * (oy - coy * fy)
                    rec(sh.shapes, nax, nay, nsx, nsy, True, sh.shape_id)

        rec(slide.shapes, 0, 0, 1.0, 1.0, False, None)
        return out

    def is_footnote_home(self, si: ShapeInfo) -> bool:
        if self.footnote_name_re.search(si.name or ""):
            return True
        if si.box is None:
            return False
        band = float(self.rules.get("footnote_band", 0.12))
        return si.box[1] >= self.H * (1 - band)

    def is_text_shape(self, si: ShapeInfo) -> bool:
        return getattr(si.shape, "has_text_frame", False) and si.shape.has_text_frame

    def is_textbox(self, si: ShapeInfo) -> bool:
        cnv = si.shape._element.find(".//" + q("p:cNvSpPr"))
        return cnv is not None and cnv.get("txBox") == "1"

    # ---- text ---------------------------------------------------------------------------

    def _lst_sz(self, txBody, lvl: int):
        if txBody is None:
            return None
        node = txBody.find(q("a:lstStyle") + "/" + q("a:lvl%dpPr" % (lvl + 1)) + "/" + q("a:defRPr"))
        return node.get("sz") if node is not None else None

    def _lst_latin(self, txBody, lvl: int):
        if txBody is None:
            return None
        node = txBody.find(
            q("a:lstStyle") + "/" + q("a:lvl%dpPr" % (lvl + 1)) + "/" + q("a:defRPr") + "/" + q("a:latin")
        )
        return node.get("typeface") if node is not None else None

    def _match_ph(self, shape, container):
        pf = shape.placeholder_format
        phs = list(container.placeholders)
        for ph in phs:
            if ph.placeholder_format.idx == pf.idx:
                return ph
        if pf.type in TITLE_TYPES:
            for ph in phs:
                if ph.placeholder_format.type in TITLE_TYPES:
                    return ph
        else:
            for ph in phs:
                if ph.placeholder_format.type == pf.type:
                    return ph
            for ph in phs:
                if ph.placeholder_format.type == PP_PLACEHOLDER.BODY:
                    return ph
        return None

    def _master_style_attr(self, master, is_title: bool, lvl: int, attr: str, latin=False):
        styles = master._element.find(q("p:txStyles"))
        if styles is None:
            return None
        style = styles.find(q("p:titleStyle" if is_title else "p:bodyStyle"))
        if style is None:
            return None
        node = style.find(q("a:lvl%dpPr" % (lvl + 1)) + "/" + q("a:defRPr"))
        if node is None:
            return None
        if latin:
            lat = node.find(q("a:latin"))
            return lat.get("typeface") if lat is not None else None
        return node.get(attr)

    def inherited_sz(self, shape, slide, lvl: int):
        txBody = shape._element.find(q("p:txBody"))
        sz = self._lst_sz(txBody, lvl)
        if sz:
            return sz
        if shape.is_placeholder:
            layout = slide.slide_layout
            master = layout.slide_master
            lph = self._match_ph(shape, layout)
            if lph is not None:
                sz = self._lst_sz(lph._element.find(q("p:txBody")), lvl)
                if sz:
                    return sz
            mph = self._match_ph(shape, master)
            if mph is not None:
                sz = self._lst_sz(mph._element.find(q("p:txBody")), lvl)
                if sz:
                    return sz
            sz = self._master_style_attr(master, shape.placeholder_format.type in TITLE_TYPES, lvl, "sz")
            if sz:
                return sz
            return None
        if self._default_style is not None:
            node = self._default_style.find(q("a:lvl%dpPr" % (lvl + 1)) + "/" + q("a:defRPr"))
            if node is not None and node.get("sz"):
                return node.get("sz")
        return None

    def inherited_latin(self, shape, slide, lvl: int):
        txBody = shape._element.find(q("p:txBody"))
        face = self._lst_latin(txBody, lvl)
        master = slide.slide_layout.slide_master
        if not face and shape.is_placeholder:
            lph = self._match_ph(shape, slide.slide_layout)
            if lph is not None:
                face = self._lst_latin(lph._element.find(q("p:txBody")), lvl)
            if not face:
                mph = self._match_ph(shape, master)
                if mph is not None:
                    face = self._lst_latin(mph._element.find(q("p:txBody")), lvl)
            if not face:
                face = self._master_style_attr(
                    master, shape.placeholder_format.type in TITLE_TYPES, lvl, "latin", latin=True
                )
        if not face and self._default_style is not None:
            node = self._default_style.find(
                q("a:lvl%dpPr" % (lvl + 1)) + "/" + q("a:defRPr") + "/" + q("a:latin")
            )
            face = node.get("typeface") if node is not None else None
        return self.resolve_theme_font(face, master, shape)

    def resolve_theme_font(self, face, master, shape):
        if not face:
            return None
        if face.startswith("+mj"):
            return self.theme_font(master, True) or face
        if face.startswith("+mn"):
            return self.theme_font(master, False) or face
        return face

    def _font_scale(self, txBody) -> float:
        if txBody is None:
            return 1.0
        bodyPr = txBody.find(q("a:bodyPr"))
        if bodyPr is None:
            return 1.0
        norm = bodyPr.find(q("a:normAutofit"))
        if norm is not None and norm.get("fontScale"):
            try:
                return int(norm.get("fontScale")) / 100000.0
            except ValueError:
                return 1.0
        return 1.0

    def runs_of_txbody(self, txBody, shape, slide, in_cell=False) -> list[RunInfo]:
        out: list[RunInfo] = []
        if txBody is None:
            return out
        scale = self._font_scale(txBody)
        for pi, p in enumerate(txBody.findall(q("a:p"))):
            pPr = p.find(q("a:pPr"))
            lvl = int(pPr.get("lvl", "0")) if pPr is not None else 0
            para_text = "".join(t.text or "" for t in p.iter(q("a:t")))
            for r in p:
                if r.tag not in (q("a:r"), q("a:fld")):
                    continue
                t = r.find(q("a:t"))
                text = t.text if t is not None and t.text else ""
                rPr = r.find(q("a:rPr"))
                sz = rPr.get("sz") if rPr is not None else None
                if sz is None and not in_cell:
                    sz = self.inherited_sz(shape, slide, lvl)
                if sz is None and in_cell:
                    sz = self._lst_sz(txBody, lvl)
                    if sz is None and self._default_style is not None:
                        node = self._default_style.find(q("a:lvl%dpPr" % (lvl + 1)) + "/" + q("a:defRPr"))
                        sz = node.get("sz") if node is not None else None
                size = None
                if sz:
                    try:
                        size = int(sz) / 100.0 * scale
                    except ValueError:
                        size = None
                italic = rPr is not None and rPr.get("i") == "1"
                sup = False
                if rPr is not None and rPr.get("baseline"):
                    try:
                        sup = int(rPr.get("baseline")) > 0
                    except ValueError:
                        sup = False
                latin = None
                if rPr is not None:
                    lat = rPr.find(q("a:latin"))
                    latin = lat.get("typeface") if lat is not None else None
                out.append(RunInfo(text, size, italic, sup, latin, pi, para_text, r, in_cell))
        return out

    def runs_of(self, si: ShapeInfo) -> list[RunInfo]:
        sh = si.shape
        slide = self.slides[si.slide_no - 1]
        if getattr(sh, "has_text_frame", False) and sh.has_text_frame:
            return self.runs_of_txbody(sh._element.find(q("p:txBody")), sh, slide)
        return []

    def table_cells(self, si: ShapeInfo):
        """Yield (row, col, cell_txBody, cell_text) for a native table shape."""
        sh = si.shape
        if not (getattr(sh, "has_table", False) and sh.has_table):
            return
        tbl = sh._element.find(".//" + q("a:tbl"))
        if tbl is None:
            return
        for ri, tr in enumerate(tbl.findall(q("a:tr"))):
            for ci, tc in enumerate(tr.findall(q("a:tc"))):
                txBody = tc.find(q("a:txBody"))
                text = "".join(t.text or "" for t in tc.iter(q("a:t")))
                yield ri, ci, txBody, text

    def shape_text(self, si: ShapeInfo) -> str:
        return "".join(t.text or "" for t in si.shape._element.iter(q("a:t")))

    def slide_texts(self, slide_no: int) -> list[tuple[ShapeInfo, str]]:
        out = []
        for si in self.shapes_by_slide[slide_no]:
            if si.shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                continue
            txt = self.shape_text(si)
            if visible(txt):
                out.append((si, txt))
        return out

    def slide_xml_name(self, slide) -> str:
        return slide.part.partname.lstrip("/")

    # ---- findings ------------------------------------------------------------------------

    def add(self, **kw):
        self.findings.append(Finding(**kw))


# --------------------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------------------


def check_font_size_floor(d: Deck):
    """One finding per slide: the shapes below the floor, the smallest size, a sample line."""
    floor = float(d.rules.get("size_floor_pt", 10))
    fn_floor = float(d.rules.get("footnote_floor_pt", 8))
    for sno, shapes in d.shapes_by_slide.items():
        offenders = []  # (shape, min_size, sample, home, run_count)
        for si in shapes:
            runs = list(d.runs_of(si))
            if getattr(si.shape, "has_table", False) and si.shape.has_table:
                for _r, _c, txBody, _t in d.table_cells(si):
                    runs.extend(d.runs_of_txbody(txBody, si.shape, d.slides[sno - 1], in_cell=True))
            small = [r for r in runs if visible(r.text) and r.size is not None and r.size < floor]
            if not small:
                continue
            home = d.is_footnote_home(si)
            limit = fn_floor if home else floor
            bad = [r for r in small if r.size < limit]
            if not bad:
                continue
            min_size = min(r.size for r in bad)
            sample = next(r for r in bad if r.size == min_size)
            offenders.append((si, min_size, sample.para_text.strip()[:80], home, len(bad)))
        if not offenders:
            continue
        offenders.sort(key=lambda t: t[1])
        si, min_size, sample, home, _cnt = offenders[0]
        body = [o for o in offenders if not o[3]]
        homes = [o for o in offenders if o[3]]
        parts = []
        if body:
            parts.append("%d shape%s below %gpt outside a footnote home (smallest %.1fpt)" % (
                len(body), "s" if len(body) != 1 else "", floor, min(o[1] for o in body)))
        if homes:
            parts.append("%d footnote shape%s below %gpt (smallest %.1fpt)" % (
                len(homes), "s" if len(homes) != 1 else "", fn_floor, min(o[1] for o in homes)))
        names = ", ".join(sorted({o[0].name for o in offenders}))[:120]
        d.add(
            id="font-size-floor",
            severity="block",
            slide=sno,
            shape=si.name if len(offenders) == 1 else "%d shapes" % len(offenders),
            shape_id=si.shape_id if len(offenders) == 1 else None,
            text=sample,
            detail="; ".join(parts) + " [" + names + "]",
            fix="resize",
            auto_fixable=False,
        )


def _text_colour_is_grey(val: str) -> bool:
    try:
        r, g, b = int(val[0:2], 16), int(val[2:4], 16), int(val[4:6], 16)
    except (ValueError, IndexError):
        return False
    lum = (r + g + b) / 3
    return 0x60 <= lum <= 0xB8 and max(r, g, b) - min(r, g, b) <= 18


def check_italics(d: Deck):
    """Italics are an exception, not a style. A few per deck are listed as warn; above the threshold the deck
    is blocked, because recurring italic detail text is the AI habit that works against a five-second scan."""
    threshold = int(d.rules.get("italics_threshold", 4))
    found = []  # (slide, si, runs)
    for sno, shapes in d.shapes_by_slide.items():
        for si in shapes:
            runs = [r for r in d.runs_of(si) if r.italic and visible(r.text)]
            if getattr(si.shape, "has_table", False) and si.shape.has_table:
                for _r, _c, txBody, _t in d.table_cells(si):
                    runs.extend(
                        r for r in d.runs_of_txbody(txBody, si.shape, d.slides[sno - 1], in_cell=True)
                        if r.italic and visible(r.text)
                    )
            if runs:
                found.append((sno, si, runs))
    if not found:
        return
    total = sum(len(runs) for _s, _si, runs in found)
    severity = "block" if total > threshold else "warn"
    for sno, si, runs in found:
        d.add(
            id="italics",
            severity=severity,
            slide=sno,
            shape=si.name,
            shape_id=si.shape_id,
            text=runs[0].para_text.strip()[:120],
            detail="%d italic run%s here, %d in the deck (a rare exception is allowed up to %d; above that the deck is blocked)" % (
                len(runs), "s" if len(runs) != 1 else "", total, threshold
            ),
            fix="reword",
            auto_fixable=False,
        )


def check_grey_text(d: Deck):
    """Grey text outside a footnote home. Muted detail text is the other AI habit that defeats the scan;
    a few runs are listed, above the threshold the deck is blocked."""
    threshold = int(d.rules.get("grey_text_threshold", 4))
    palette = set(c.upper() for c in d.rules.get("palette", []))
    active = d.rules.get("active_client_palette")
    client = (d.rules.get("client_palettes") or {}).get(active) if active else None
    if isinstance(client, dict):
        palette |= set(c.upper() for c in client.get("colours", []))
    found = []
    for sno, shapes in d.shapes_by_slide.items():
        allowed = palette | d.theme_colors(d.slides[sno - 1].slide_layout.slide_master)
        for si in shapes:
            if not d.is_text_shape(si) or d.is_footnote_home(si):
                continue
            hits = []
            for r in d.runs_of(si):
                if not visible(r.text):
                    continue
                rPr = r.elm.find(q("a:rPr"))
                if rPr is None:
                    continue
                clr = rPr.find(q("a:solidFill") + "/" + q("a:srgbClr"))
                val = (clr.get("val") or "").upper() if clr is not None else ""
                # a muted colour that belongs to the theme or the house palette is a deliberate choice
                # (inactive navigation, a denominator line); anything else grey is the detail-text habit
                if val and val not in allowed and _text_colour_is_grey(val):
                    hits.append(r)
            if hits:
                found.append((sno, si, hits))
    if not found:
        return
    total = sum(len(h) for _s, _si, h in found)
    # grey is reported for the skill's judgment; it never blocks on its own, italics does
    severity = "warn" if total > threshold else "info"
    for sno, si, hits in found:
        d.add(
            id="grey-text",
            severity=severity,
            slide=sno,
            shape=si.name,
            shape_id=si.shape_id,
            text=hits[0].para_text.strip()[:120],
            detail="%d grey run%s outside a footnote home in a colour outside the palette, %d in the deck (threshold %d); title, body or footnote should carry it" % (
                len(hits), "s" if len(hits) != 1 else "", total, threshold
            ),
            fix="reword",
            auto_fixable=False,
        )


def check_table_one_size(d: Deck):
    for sno, shapes in d.shapes_by_slide.items():
        # native tables
        for si in shapes:
            if getattr(si.shape, "has_table", False) and si.shape.has_table:
                sizes = set()
                for _r, _c, txBody, _t in d.table_cells(si):
                    for r in d.runs_of_txbody(txBody, si.shape, d.slides[sno - 1], in_cell=True):
                        if visible(r.text) and r.size is not None:
                            sizes.add(round(r.size, 1))
                if len(sizes) > 1:
                    d.add(
                        id="table-one-size",
                        severity="warn",
                        slide=sno,
                        shape=si.name,
                        shape_id=si.shape_id,
                        text="",
                        detail="native table uses %d font sizes: %s" % (
                            len(sizes), ", ".join("%gpt" % s for s in sorted(sizes))
                        ),
                        fix="resize",
                    )
        # shape-built table groups: a group with four or more text-bearing children
        groups = {}
        for si in shapes:
            if si.in_group and si.group_key is not None and d.is_text_shape(si) and visible(d.shape_text(si)):
                groups.setdefault(si.group_key, []).append(si)
        for gkey, members in groups.items():
            if len(members) < 4:
                continue
            sizes = set()
            for si in members:
                for r in d.runs_of(si):
                    if visible(r.text) and r.size is not None:
                        sizes.add(round(r.size, 1))
            if len(sizes) > 1:
                gshape = next((s for s in shapes if s.shape_id == gkey), None)
                d.add(
                    id="table-one-size",
                    severity="warn",
                    slide=sno,
                    shape=gshape.name if gshape else "Group %s" % gkey,
                    shape_id=gkey,
                    text="",
                    detail="shape-built table group uses %d font sizes: %s" % (
                        len(sizes), ", ".join("%gpt" % s for s in sorted(sizes))
                    ),
                    fix="resize",
                )


def check_metadata(d: Deck):
    core = d.xml("docProps/core.xml")
    app = d.xml("docProps/app.xml")
    if core is not None:
        for tag, fid in (("dc:creator", "author-empty"), ("cp:lastModifiedBy", "author-empty")):
            node = core.find(q(tag))
            if node is not None and visible(node.text or ""):
                d.add(
                    id=fid, severity="block", slide=None, shape=None, shape_id=None,
                    text=(node.text or "").strip(),
                    detail="docProps/core.xml %s must be empty" % tag,
                    fix="clear", auto_fixable=True,
                )
        for tag in ("dc:title", "dc:subject", "cp:keywords", "dc:description", "cp:category", "cp:contentStatus"):
            node = core.find(q(tag))
            if node is not None and visible(node.text or ""):
                d.add(
                    id="metadata-scrub", severity="block", slide=None, shape=None, shape_id=None,
                    text=(node.text or "").strip()[:120],
                    detail="docProps/core.xml %s is set" % tag,
                    fix="clear", auto_fixable=True,
                )
    if app is not None:
        tt = app.find(q("ep:TotalTime"))
        if tt is not None and (tt.text or "").strip() not in ("", "0"):
            d.add(
                id="metadata-scrub", severity="block", slide=None, shape=None, shape_id=None,
                text=tt.text.strip(), detail="docProps/app.xml TotalTime > 0 (minutes of editing leak)",
                fix="clear", auto_fixable=True,
            )
        tpl = app.find(q("ep:Template"))
        if tpl is not None and visible(tpl.text or ""):
            d.add(
                id="metadata-scrub", severity="block", slide=None, shape=None, shape_id=None,
                text=tpl.text.strip(), detail="docProps/app.xml Template is set",
                fix="clear", auto_fixable=True,
            )
        comp = app.find(q("ep:Company"))
        if comp is not None and visible(comp.text or ""):
            d.add(
                id="metadata-scrub", severity="warn", slide=None, shape=None, shape_id=None,
                text=comp.text.strip(), detail="docProps/app.xml Company is set",
                fix="clear", auto_fixable=True,
            )
    if "docProps/custom.xml" in d.parts:
        custom = d.xml("docProps/custom.xml")
        names = []
        if custom is not None:
            names = [p.get("name") for p in custom if p.get("name")]
        d.add(
            id="metadata-scrub", severity="block", slide=None, shape=None, shape_id=None,
            text=", ".join(names)[:160],
            detail="docProps/custom.xml present (%d custom propert%s)" % (len(names), "y" if len(names) == 1 else "ies"),
            fix="delete", auto_fixable=True,
        )
    # generator fingerprints
    fps = d.rules.get("generator_fingerprints", [])
    phrases = d.rules.get("generator_phrases_docprops_only", [])
    seen = set()
    for name, blob in d.parts.items():
        if not (name.endswith(".xml") or name.endswith(".rels")):
            continue
        try:
            text = blob.decode("utf-8", errors="ignore")
        except Exception:  # noqa: BLE001
            continue
        low = text.lower()
        candidates = list(fps) + (list(phrases) if name.startswith("docProps/") else [])
        for fp in candidates:
            if fp.lower() in low and (name, fp) not in seen:
                seen.add((name, fp))
                d.add(
                    id="metadata-scrub", severity="block", slide=None, shape=None, shape_id=None,
                    text=fp, detail="generator fingerprint in %s" % name,
                    fix="clear", auto_fixable=True,
                )


def notes_text(notes_elm) -> str:
    """Text of the body placeholder(s) on a notes slide, ignoring slide number and image placeholders."""
    parts = []
    for sp in notes_elm.iter(q("p:sp")):
        ph = sp.find(".//" + q("p:nvPr") + "/" + q("p:ph"))
        if ph is not None and ph.get("type") in ("sldNum", "sldImg", "hdr", "ftr", "dt"):
            continue
        for p in sp.iter(q("a:p")):
            line = "".join(t.text or "" for t in p.iter(q("a:t")))
            if visible(line):
                parts.append(line.strip())
    return "\n".join(parts)


def check_speaker_notes(d: Deck):
    for sno, slide in enumerate(d.slides, 1):
        rels = d.xml("ppt/slides/_rels/%s.rels" % d.slide_xml_name(slide).split("/")[-1])
        if rels is None:
            continue
        for rel in rels:
            if rel.get("Type", "").endswith("/notesSlide"):
                target = rel.get("Target", "")
                name = "ppt/" + target.replace("../", "")
                notes = d.xml(name)
                if notes is None:
                    continue
                text = notes_text(notes)
                if visible(text):
                    d.add(
                        id="speaker-notes", severity="block", slide=sno, shape="notes", shape_id=None,
                        text=text, detail="speaker note present in %s; text reported in full before it is stripped" % name,
                        fix="delete", auto_fixable=True,
                    )


def check_hidden_slides(d: Deck):
    for sno, slide in enumerate(d.slides, 1):
        if slide._element.get("show") == "0":
            title = slide.shapes.title.text.strip()[:80] if slide.shapes.title is not None and slide.shapes.title.has_text_frame else ""
            d.add(
                id="hidden-slides", severity="warn", slide=sno, shape=None, shape_id=None,
                text=title, detail="slide is hidden (show=0); ship or delete, ask the author",
                fix="none",
            )


def check_comments(d: Deck):
    for name in sorted(d.parts):
        if not name.startswith("ppt/comments/") or not name.endswith(".xml"):
            continue
        elm = d.xml(name)
        if elm is None:
            continue
        open_items = []
        if "modernComment" in name:
            for cm in elm.iter(q("p188:cm")):
                status = cm.get("status", "active")
                if status in ("resolved", "closed"):
                    continue
                txt = "".join(t.text or "" for t in cm.iter(q("a:t"))).strip()
                open_items.append(txt)
        else:
            for cm in elm.iter(q("p:cm")):
                txt = (cm.findtext(q("p:text")) or "").strip()
                open_items.append(txt)
        if open_items:
            d.add(
                id="comments-open", severity="warn", slide=None, shape=None, shape_id=None,
                text=" | ".join(t[:80] for t in open_items[:5]),
                detail="%d unresolved comment%s in %s; resolve or remove, ask the author" % (
                    len(open_items), "s" if len(open_items) != 1 else "", name
                ),
                fix="none",
            )


def check_placeholders(d: Deck):
    pats = [re.compile(p) for p in d.rules.get("placeholder_patterns", [])]
    for sno in d.shapes_by_slide:
        for si, txt in d.slide_texts(sno):
            hits = []
            for pat in pats:
                for m in pat.finditer(txt):
                    hits.append(m.group(0))
            if hits:
                d.add(
                    id="placeholders", severity="block", slide=sno, shape=si.name, shape_id=si.shape_id,
                    text=txt.strip()[:120], detail="leftover token(s): %s" % ", ".join(sorted(set(hits))),
                    fix="reword",
                )


def check_leftover_notes_and_labels(d: Deck):
    """Reviewer notes left as slide text ("DL 11-Sep-26: fix the logo order") and register labels with
    nothing after them ("Takeaway:" on its own line). Both came from shipped decks; both are deterministic."""
    note_pats = [re.compile(p) for p in d.rules.get("reviewer_note_patterns", [])]
    label_pats = [re.compile(p, re.I) for p in d.rules.get("empty_label_patterns", [])]
    for sno, shapes in d.shapes_by_slide.items():
        for si in shapes:
            if not d.is_text_shape(si):
                continue
            paras: dict[int, str] = {}
            for r in d.runs_of(si):
                paras.setdefault(r.para_index, r.para_text)
            texts = [t for _i, t in sorted(paras.items())]
            for pat in note_pats:
                for t in texts:
                    if pat.search(t):
                        d.add(
                            id="reviewer-note", severity="block", slide=sno, shape=si.name, shape_id=si.shape_id,
                            text=t.strip()[:120], detail="reviewer note left as slide text; resolve and delete",
                            fix="delete",
                        )
                        break
            for pat in label_pats:
                for t in texts:
                    if pat.match(t):
                        d.add(
                            id="empty-label", severity="block", slide=sno, shape=si.name, shape_id=si.shape_id,
                            text=t.strip()[:60], detail="register label with nothing after it; fill it or remove the line",
                            fix="reword",
                        )
                        break


STRAIGHT_QUOTE_RE = re.compile(r'(?<!\d)"|(?<=\w)\'(?=\w)')


def curly_quotes(text: str) -> str:
    """Straight double quotes to curly by position; apostrophes between letters to a right single quote."""
    out = []
    for i, ch in enumerate(text):
        if ch == '"' and not (i > 0 and text[i - 1].isdigit()):
            prev = text[i - 1] if i > 0 else " "
            out.append("“" if prev.isspace() or prev in "([{" else "”")
        elif ch == "'" and 0 < i < len(text) - 1 and text[i - 1].isalnum() and text[i + 1].isalnum():
            out.append("’")
        else:
            out.append(ch)
    return "".join(out)


def check_quote_marks(d: Deck):
    """Straight quote marks; shipped decks use curly ones. Inch marks after a digit are left alone."""
    for sno, shapes in d.shapes_by_slide.items():
        for si in shapes:
            hits = []
            texts = []
            if d.is_text_shape(si):
                paras: dict[int, str] = {}
                for r in d.runs_of(si):
                    paras.setdefault(r.para_index, r.para_text)
                texts = list(paras.values())
            elif getattr(si.shape, "has_table", False) and si.shape.has_table:
                texts = [t for _r, _c, _tx, t in d.table_cells(si)]
            for t in texts:
                if STRAIGHT_QUOTE_RE.search(t or ""):
                    hits.append(t.strip())
            if hits:
                d.add(
                    id="quote-marks", severity="warn", slide=sno, shape=si.name, shape_id=si.shape_id,
                    text=hits[0][:120], detail="%d paragraph%s with straight quote marks; house style is curly" % (
                        len(hits), "s" if len(hits) != 1 else ""
                    ),
                    fix="reword", auto_fixable=True,
                )


def check_textbox_conventions(d: Deck):
    """House construction: text boxes have zero insets and top anchoring. Reported per slide as information,
    because a shipped client deck may carry the template's defaults and the rule targets what the draft builds."""
    for sno, shapes in d.shapes_by_slide.items():
        insets = 0
        anchors = 0
        boxes = 0
        for si in shapes:
            if not d.is_text_shape(si) or not d.is_textbox(si) or not visible(d.shape_text(si)):
                continue
            boxes += 1
            bodyPr = si.shape._element.find(q("p:txBody") + "/" + q("a:bodyPr"))
            if bodyPr is None:
                insets += 1
                anchors += 1
                continue
            if any(int(bodyPr.get(k, "91440" if k in ("lIns", "rIns") else "45720")) != 0 for k in ("lIns", "rIns", "tIns", "bIns")):
                insets += 1
            if bodyPr.get("anchor", "t") != "t":
                anchors += 1
        if insets or anchors:
            d.add(
                id="textbox-conventions", severity="info", slide=sno, shape=None, shape_id=None,
                text="", detail="%d of %d text boxes with non-zero insets, %d not top-anchored; house style is zero-margin, top-aligned" % (
                    insets, boxes, anchors
                ),
                fix="resize",
            )


def check_native_table_small(d: Deck):
    """A small native table where the house builds lines and text boxes. Heatmaps (most cells filled) are exempt."""
    max_rows = int(d.rules.get("small_table_max_rows", 6))
    max_cols = int(d.rules.get("small_table_max_cols", 5))
    for sno, shapes in d.shapes_by_slide.items():
        for si in shapes:
            if not (getattr(si.shape, "has_table", False) and si.shape.has_table):
                continue
            tbl = si.shape._element.find(".//" + q("a:tbl"))
            if tbl is None:
                continue
            rows = tbl.findall(q("a:tr"))
            nrows = len(rows)
            ncols = max((len(tr.findall(q("a:tc"))) for tr in rows), default=0)
            if nrows == 0 or nrows > max_rows or ncols > max_cols:
                continue
            cells = [tc for tr in rows for tc in tr.findall(q("a:tc"))]
            filled = sum(1 for tc in cells if tc.find(q("a:tcPr") + "/" + q("a:solidFill")) is not None)
            if cells and filled / len(cells) >= 0.5:
                continue  # heatmap: fills carry the data
            d.add(
                id="native-table-small", severity="warn", slide=sno, shape=si.name, shape_id=si.shape_id,
                text="", detail="native table of %d rows x %d columns; house style builds this size from text boxes and horizontal divider lines" % (
                    nrows, ncols
                ),
                fix="none",
            )


def check_shape_overlap(d: Deck):
    """Two text-bearing or chart shapes whose boxes intersect by more than a sliver, where neither contains the
    other: the collision a render would show. Group children, footers and page numbers are skipped."""
    tol = 4 * EMU_PER_PT
    for sno, shapes in d.shapes_by_slide.items():
        items = []
        for si in shapes:
            if si.box is None or si.in_group or si.shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                continue
            if si.shape.is_placeholder and si.shape.placeholder_format.type in (
                PP_PLACEHOLDER.FOOTER, PP_PLACEHOLDER.SLIDE_NUMBER, PP_PLACEHOLDER.DATE
            ):
                continue
            if re.search(r"footer|slide number", si.name or "", re.I):
                continue
            has_chart = getattr(si.shape, "has_chart", False) and si.shape.has_chart
            has_table = getattr(si.shape, "has_table", False) and si.shape.has_table
            if not (has_chart or has_table or (d.is_text_shape(si) and visible(d.shape_text(si)))):
                continue
            items.append(si)
        seen = set()
        for i, a in enumerate(items):
            ax, ay, aw, ah = a.box
            for b in items[i + 1:]:
                bx, by, bw, bh = b.box
                ix = min(ax + aw, bx + bw) - max(ax, bx)
                iy = min(ay + ah, by + bh) - max(ay, by)
                if ix <= tol or iy <= tol:
                    continue
                a_in_b = ax >= bx - tol and ay >= by - tol and ax + aw <= bx + bw + tol and ay + ah <= by + bh + tol
                b_in_a = bx >= ax - tol and by >= ay - tol and bx + bw <= ax + aw + tol and by + bh <= ay + ah + tol
                if a_in_b or b_in_a:
                    continue  # text on a band or a label inside a card is deliberate nesting
                smaller = min(aw * ah, bw * bh) or 1
                if (ix * iy) / smaller < 0.30:
                    continue
                # a short label riding on a chart frame edge (segment headers, axis captions) is a layout convention
                a_chart = getattr(a.shape, "has_chart", False) and a.shape.has_chart
                b_chart = getattr(b.shape, "has_chart", False) and b.shape.has_chart
                if (a_chart and len(d.shape_text(b).strip()) <= 15) or (b_chart and len(d.shape_text(a).strip()) <= 15):
                    continue
                key = (a.shape_id, b.shape_id)
                if key in seen:
                    continue
                seen.add(key)
                d.add(
                    id="shape-overlap", severity="warn", slide=sno, shape=a.name, shape_id=a.shape_id,
                    text=(d.shape_text(a).strip()[:50] or a.name) + "  x  " + (d.shape_text(b).strip()[:50] or b.name),
                    detail="'%s' and '%s' overlap by %.0f%% of the smaller shape; confirm in the render" % (
                        a.name, b.name, 100 * (ix * iy) / smaller
                    ),
                    fix="resize",
                )


WORD_RE = re.compile(r"[A-Za-z0-9][\w'\u2019%$.,-]*")
QUOTED_RE = re.compile(r"[\u201c\"]([^\u201d\"]{12,})[\u201d\"]")


def check_word_count(d: Deck):
    """Title + body + chart labels per page against the rules' thresholds; footnotes counted apart; appendix exempt."""
    warn = int(d.rules.get("words_warn", 200))
    block = int(d.rules.get("words_block", 275))
    fn_warn = int(d.rules.get("footnote_words_warn", 100))
    for sno, shapes in d.shapes_by_slide.items():
        if d.is_appendix(sno):
            continue
        body = fn = 0
        quoted = 0
        for si in shapes:
            sh = si.shape
            if sh.is_placeholder and sh.placeholder_format.type in (
                PP_PLACEHOLDER.FOOTER, PP_PLACEHOLDER.SLIDE_NUMBER, PP_PLACEHOLDER.DATE
            ):
                continue
            if re.search(r"footer|slide number", si.name or "", re.I):
                continue
            txt = ""
            if d.is_text_shape(si):
                txt = d.shape_text(si)
            elif getattr(sh, "has_table", False) and sh.has_table:
                txt = " ".join(t for _r, _c, _tx, t in d.table_cells(si))
            if not visible(txt):
                continue
            n = len(WORD_RE.findall(txt))
            if d.is_footnote_home(si):
                fn += n
            else:
                body += n
                quoted += sum(len(WORD_RE.findall(m)) for m in QUOTED_RE.findall(txt))
        if body == 0:
            continue
        if quoted >= body / 2:
            continue  # a quotes page carries verbatim text by design
        if body > warn:
            d.add(
                id="word-count", severity="block" if body > block else "warn", slide=sno, shape=None, shape_id=None,
                text="%d words" % body,
                detail="%d words of title, body and chart labels (warn above %d, block above %d); footnotes %d counted apart" % (
                    body, warn, block, fn
                ),
                fix="reword",
            )
        if fn > fn_warn:
            d.add(
                id="footnote-words", severity="warn", slide=sno, shape=None, shape_id=None,
                text="%d words" % fn, detail="footnotes run %d words (warn above %d); trim question wording or move detail to the appendix" % (fn, fn_warn),
                fix="reword",
            )


def check_empty_textbox(d: Deck):
    for sno, shapes in d.shapes_by_slide.items():
        for si in shapes:
            if not d.is_text_shape(si):
                continue
            if not (d.is_textbox(si) or si.shape.is_placeholder):
                continue
            if not visible(d.shape_text(si)):
                kind = "placeholder" if si.shape.is_placeholder else "text box"
                d.add(
                    id="empty-textbox", severity="warn", slide=sno, shape=si.name, shape_id=si.shape_id,
                    text="", detail="%s with no visible characters" % kind, fix="delete",
                )


def check_off_canvas(d: Deck):
    tol = EMU_PER_PT
    for sno, shapes in d.shapes_by_slide.items():
        for si in shapes:
            if si.box is None or si.shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                continue
            x, y, w, h = si.box
            over = []
            if x < -tol:
                over.append("left by %.1fpt" % (-x / EMU_PER_PT))
            if y < -tol:
                over.append("top by %.1fpt" % (-y / EMU_PER_PT))
            if x + w > d.W + tol:
                over.append("right by %.1fpt" % ((x + w - d.W) / EMU_PER_PT))
            if y + h > d.H + tol:
                over.append("bottom by %.1fpt" % ((y + h - d.H) / EMU_PER_PT))
            if over:
                d.add(
                    id="off-canvas", severity="warn", slide=sno, shape=si.name, shape_id=si.shape_id,
                    text=d.shape_text(si).strip()[:80], detail="shape extends past the slide edge: " + ", ".join(over),
                    fix="resize",
                )


def _autofit_kind(d: Deck, si: ShapeInfo) -> str:
    """'norm' | 'sp' | 'none' for the effective autofit of a text shape, inheriting through placeholders."""
    def kind(txBody):
        if txBody is None:
            return None
        bodyPr = txBody.find(q("a:bodyPr"))
        if bodyPr is None:
            return None
        if bodyPr.find(q("a:normAutofit")) is not None:
            return "norm"
        if bodyPr.find(q("a:spAutoFit")) is not None:
            return "sp"
        if bodyPr.find(q("a:noAutofit")) is not None:
            return "none"
        return None

    k = kind(si.shape._element.find(q("p:txBody")))
    if k is None and si.shape.is_placeholder:
        slide = d.slides[si.slide_no - 1]
        for container in (slide.slide_layout, slide.slide_layout.slide_master):
            ph = d._match_ph(si.shape, container)
            if ph is not None:
                k = kind(ph._element.find(q("p:txBody")))
                if k is not None:
                    break
    return k or "none"


def check_overflow_estimate(d: Deck):
    for sno, shapes in d.shapes_by_slide.items():
        for si in shapes:
            if not d.is_text_shape(si) or si.box is None:
                continue
            if si.shape.is_placeholder and si.shape.placeholder_format.type in (
                PP_PLACEHOLDER.FOOTER, PP_PLACEHOLDER.SLIDE_NUMBER, PP_PLACEHOLDER.DATE
            ):
                continue  # furniture sized by the layout; their slide-level frame is often a zero-height stub
            txBody = si.shape._element.find(q("p:txBody"))
            if txBody is None:
                continue
            if _autofit_kind(d, si) != "none":
                continue
            bodyPr = txBody.find(q("a:bodyPr"))
            if bodyPr is None:
                bodyPr = etree.Element(q("a:bodyPr"))
            runs = d.runs_of(si)
            if not any(visible(r.text) for r in runs):
                continue
            x, y, w, h = si.box
            lIns = int(bodyPr.get("lIns", 91440))
            rIns = int(bodyPr.get("rIns", 91440))
            tIns = int(bodyPr.get("tIns", 45720))
            bIns = int(bodyPr.get("bIns", 45720))
            inner_w = max(w - lIns - rIns, 1)
            inner_h = max(h - tIns - bIns, 1)
            wrap = bodyPr.get("wrap", "square") != "none"
            paras: dict[int, list] = {}
            for r in runs:
                paras.setdefault(r.para_index, []).append(r)
            p_elms = txBody.findall(q("a:p"))
            total = 0.0
            for pi, prs in paras.items():
                size = max((r.size for r in prs if r.size), default=None)
                if size is None:
                    size = 18.0
                factor = 1.2
                if pi < len(p_elms):
                    pct = p_elms[pi].find(q("a:pPr") + "/" + q("a:lnSpc") + "/" + q("a:spcPct"))
                    if pct is not None and pct.get("val"):
                        try:
                            factor = 1.2 * int(pct.get("val")) / 100000.0
                        except ValueError:
                            factor = 1.2
                text = "".join(r.text for r in prs)
                if not visible(text):
                    total += size * factor * EMU_PER_PT
                    continue
                char_w = 0.5 * size * EMU_PER_PT
                lines = max(1, math.ceil(len(text) * char_w / inner_w)) if wrap else 1
                total += lines * size * factor * EMU_PER_PT
            if total > inner_h * 1.20 and total - inner_h > 6 * EMU_PER_PT:
                d.add(
                    id="overflow-estimate", severity="warn", slide=sno, shape=si.name, shape_id=si.shape_id,
                    text=d.shape_text(si).strip()[:80],
                    detail="estimated text height %.0fpt exceeds frame %.0fpt with no autofit; confirm in the render" % (
                        total / EMU_PER_PT, inner_h / EMU_PER_PT
                    ),
                    fix="resize", auto_fixable=False,
                )


# A footnote definition starts a paragraph, or follows two or more spaces, or is glued to the end of the previous
# sentence ("...award text.2  Health = ..."). Forms: "1. text", "1) text", "1  text", "[1] text", "¹ text".
FOOTNOTE_DEF_RE = re.compile(
    r"(?:^|\s{2,}|(?<=[.!?\]|;]))\s*(?:\[(\d{1,2})\]|(\d{1,2})[.)](?=\s)|(\d{1,2})(?=\s{2,})|(\d{1,2})(?=\s+[A-Z(“\"$])|([⁰¹²³⁴⁵⁶⁷⁸⁹]{1,2}))"
)
BRACKET_MARK_RE = re.compile(r"\[(\d{1,2})\]")


def footnote_defs_in(ptxt: str) -> list[int]:
    out = []
    for m in FOOTNOTE_DEF_RE.finditer(ptxt or ""):
        n = m.group(1) or m.group(2) or m.group(3) or m.group(4)
        val = int(n) if n else superscript_value(m.group(5) or "")
        if val is not None and (not out or val != out[-1]):
            out.append(val)
    return out
SUP_RUN_RE = re.compile(r"^\s*(\d{1,2})(\s*,\s*\d{1,2})*\s*$")  # "4" or "4,5" as one superscript run


def sup_values(text: str) -> list[int]:
    return [int(x) for x in re.findall(r"\d{1,2}", text or "")]


def superscript_value(s: str) -> Optional[int]:
    digits = [SUPERSCRIPT_DIGITS[ch] for ch in s if ch in SUPERSCRIPT_DIGITS]
    if not digits:
        return None
    return int("".join(str(x) for x in digits))


def check_footnote_sequence(d: Deck):
    for sno, shapes in d.shapes_by_slide.items():
        markers: list[int] = []
        defs: list[int] = []
        def_shape = None
        for si in shapes:
            if getattr(si.shape, "has_table", False) and si.shape.has_table:
                for _r, _c, txBody, _t in d.table_cells(si):
                    for r in d.runs_of_txbody(txBody, si.shape, d.slides[sno - 1], in_cell=True):
                        if r.superscript and SUP_RUN_RE.match(r.text or ""):
                            markers.extend(sup_values(r.text))
                        for ch_group in re.findall(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]+", r.text or ""):
                            v = superscript_value(ch_group)
                            if v is not None:
                                markers.append(v)
                continue
            if not d.is_text_shape(si):
                continue
            home = d.is_footnote_home(si)
            runs = d.runs_of(si)
            if home:
                paras = {}
                sup_defs = []
                for r in runs:
                    paras.setdefault(r.para_index, r.para_text)
                    if r.superscript and SUP_RUN_RE.match(r.text or ""):
                        sup_defs.extend(sup_values(r.text))
                    for ch_group in re.findall(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]+", r.text or ""):
                        v = superscript_value(ch_group)
                        if v is not None:
                            sup_defs.append(v)
                if sup_defs:
                    defs.extend(sup_defs)
                    def_shape = si
                for _pi, ptxt in sorted(paras.items()):
                    found = [v for v in footnote_defs_in(ptxt) if v not in sup_defs]
                    if found:
                        defs.extend(found)
                        def_shape = si
            else:
                for r in runs:
                    if r.superscript and SUP_RUN_RE.match(r.text or ""):
                        markers.extend(sup_values(r.text))
                    for ch_group in re.findall(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]+", r.text or ""):
                        v = superscript_value(ch_group)
                        if v is not None:
                            markers.append(v)
                    for m in BRACKET_MARK_RE.finditer(r.text or ""):
                        markers.append(int(m.group(1)))
        if not markers and not defs:
            continue
        mset, dset = set(markers), set(defs)
        shape_name = def_shape.name if def_shape else None
        shape_id = def_shape.shape_id if def_shape else None
        orphan_marks = sorted(mset - dset)
        unref_defs = sorted(dset - mset)
        dupe_defs = sorted({n for n in defs if defs.count(n) > 1})
        gaps = []
        if mset:
            gaps = sorted(set(range(1, max(mset) + 1)) - mset)
        if orphan_marks:
            d.add(
                id="footnote-sequence", severity="block", slide=sno, shape=shape_name, shape_id=shape_id,
                text="markers %s" % ", ".join(str(n) for n in orphan_marks),
                detail="marker(s) %s have no footnote on the slide (footnotes present: %s)" % (
                    ", ".join(str(n) for n in orphan_marks), ", ".join(str(n) for n in sorted(dset)) or "none"
                ),
                fix="reword",
            )
        if gaps:
            d.add(
                id="footnote-sequence", severity="block", slide=sno, shape=shape_name, shape_id=shape_id,
                text="markers %s" % ", ".join(str(n) for n in sorted(mset)),
                detail="marker sequence skips %s" % ", ".join(str(n) for n in gaps),
                fix="reword",
            )
        if unref_defs:
            d.add(
                id="footnote-sequence", severity="block" if mset else "warn", slide=sno, shape=shape_name, shape_id=shape_id,
                text="footnotes %s" % ", ".join(str(n) for n in unref_defs),
                detail="footnote(s) %s defined but never marked on the slide%s" % (
                    ", ".join(str(n) for n in unref_defs), "" if mset else " (no markers found at all; verify this is a footnote list)"
                ),
                fix="reword",
            )
        if dupe_defs:
            d.add(
                id="footnote-sequence", severity="block", slide=sno, shape=shape_name, shape_id=shape_id,
                text="footnotes %s" % ", ".join(str(n) for n in dupe_defs),
                detail="duplicate footnote number(s) %s" % ", ".join(str(n) for n in dupe_defs),
                fix="reword",
            )


TOTAL_RE = re.compile(r"\btotal\b|\bsum\b|\boverall\b", re.I)


def _check_matrix(d: Deck, sno: int, matrix: list[list], si_for_cell, label: str):
    """matrix[r][c] = text or None. si_for_cell(r, c) returns a ShapeInfo or None."""
    if not matrix or len(matrix) < 2:
        return
    ncols = max(len(r) for r in matrix)
    for row in matrix:
        while len(row) < ncols:
            row.append(None)
    header = matrix[0]
    tol = 1.0 + 1e-6
    window_pct = float(d.rules.get("totals_window_pct", 10)) / 100.0

    def off(s_, tot_):
        """True when the sum misses the stated total by more than rounding but less than the window.
        A miss far outside the window means the 'Total' is a different quantity (a crosstab total column),
        not a mis-sum, and is left to the skill."""
        if tot_ == 0:
            return False  # a zero 'total' beside non-zero components is a different quantity, not a sum
        gap = abs(s_ - tot_)
        return tol < gap <= max(abs(tot_) * window_pct, 5.0)

    def num(cell):
        if cell is None:
            return None
        return parse_number(cell)

    def is_label_col(c: int) -> bool:
        # a column is a label column when its header is text without a number and the cells below carry letters
        h = header[c] or ""
        if c == 0 and visible(h) and num(h) is None:
            return True
        return False

    total_cols = [c for c in range(ncols) if header[c] and TOTAL_RE.search(header[c])]
    for r in range(1, len(matrix)):
        row = matrix[r]
        if row[0] and TOTAL_RE.search(row[0]):
            continue  # total row handled below
        for tc in total_cols:
            tot = num(row[tc])
            if tot is None:
                continue
            comps = []
            for c in range(ncols):
                if c == tc or c in total_cols or is_label_col(c):
                    continue
                v = num(row[c])
                if v is not None:
                    comps.append(v[0])
            if len(comps) < 2:
                continue
            s = sum(comps)
            if off(s, tot[0]):
                si = si_for_cell(r, tc)
                d.add(
                    id="totals-sum", severity="block", slide=sno,
                    shape=si.name if si else label, shape_id=si.shape_id if si else None,
                    text=(row[0] or "row %d" % (r + 1)).strip()[:80],
                    detail="%s components sum to %g against a stated total of %g" % (label, round(s, 3), tot[0]),
                    fix="reword",
                )
    total_rows = [r for r in range(1, len(matrix)) if matrix[r][0] and TOTAL_RE.search(matrix[r][0])]
    for tr in total_rows:
        for c in range(1, ncols):
            tot = num(matrix[tr][c])
            if tot is None:
                continue
            comps = []
            for r in range(1, tr):
                if r in total_rows:
                    comps = []  # a new block starts after a previous total row
                    continue
                v = num(matrix[r][c])
                if v is not None:
                    comps.append(v[0])
            if len(comps) < 2:
                continue
            s = sum(comps)
            if off(s, tot[0]):
                si = si_for_cell(tr, c)
                d.add(
                    id="totals-sum", severity="block", slide=sno,
                    shape=si.name if si else label, shape_id=si.shape_id if si else None,
                    text=(header[c] or "column %d" % (c + 1)).strip()[:80],
                    detail="%s column components sum to %g against a stated total of %g" % (label, round(s, 3), tot[0]),
                    fix="reword",
                )


def check_totals(d: Deck):
    for sno, shapes in d.shapes_by_slide.items():
        # native tables
        for si in shapes:
            if getattr(si.shape, "has_table", False) and si.shape.has_table:
                rows: dict[int, dict[int, str]] = {}
                for r, c, _tx, text in d.table_cells(si):
                    rows.setdefault(r, {})[c] = text
                if not rows:
                    continue
                ncols = max(max(cols) for cols in rows.values()) + 1
                matrix = [[rows.get(r, {}).get(c) for c in range(ncols)] for r in range(max(rows) + 1)]
                _check_matrix(d, sno, matrix, lambda r, c, si=si: si, "native table")
        # shape-built tables: text shapes aligned into rows and columns
        cells = []
        for si in shapes:
            if si.box is None or not d.is_text_shape(si):
                continue
            if si.shape.is_placeholder or si.shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                continue
            txt = d.shape_text(si).strip()
            if not visible(txt) or si.box[3] > d.H * 0.15:
                continue
            cells.append((si, txt))
        if len(cells) < 6:
            continue
        ytol = d.H * 0.012
        xtol = d.W * 0.012
        rows_cl: list[list] = []
        for si, txt in sorted(cells, key=lambda t: t[0].box[1]):
            y = si.box[1]
            if rows_cl and abs(rows_cl[-1][0] - y) <= ytol:
                rows_cl[-1][1].append((si, txt))
            else:
                rows_cl.append([y, [(si, txt)]])
        rows_cl = [r for r in rows_cl if len(r[1]) >= 2]
        if len(rows_cl) < 2:
            continue
        cols_cl: list[float] = []
        for _y, members in rows_cl:
            for si, _t in members:
                x = si.box[0]
                if not any(abs(cx - x) <= xtol for cx in cols_cl):
                    cols_cl.append(x)
        cols_cl.sort()
        if len(cols_cl) < 3:
            continue
        matrix = []
        lookup = {}
        for ri, (_y, members) in enumerate(rows_cl):
            row = [None] * len(cols_cl)
            for si, txt in members:
                ci = min(range(len(cols_cl)), key=lambda i: abs(cols_cl[i] - si.box[0]))
                if row[ci] is None:
                    row[ci] = txt
                    lookup[(ri, ci)] = si
            matrix.append(row)
        _check_matrix(d, sno, matrix, lambda r, c: lookup.get((r, c)), "shape-built table")


def chart_values(chart_elm) -> list[float]:
    vals = []
    for ser in chart_elm.iter(q("c:ser")):
        val = ser.find(q("c:val"))
        if val is None:
            continue
        cache = val.find(".//" + q("c:numCache"))
        if cache is None:
            cache = val.find(q("c:numLit"))
        if cache is None:
            continue
        fmt = (cache.findtext(q("c:formatCode")) or "")
        pct = "%" in fmt
        for pt in cache.iter(q("c:pt")):
            v = pt.findtext(q("c:v"))
            try:
                f = float(v)
            except (TypeError, ValueError):
                continue
            vals.append(f * 100 if pct else f)
    return vals


def check_charts(d: Deck):
    for sno, shapes in d.shapes_by_slide.items():
        for si in shapes:
            if not (getattr(si.shape, "has_chart", False) and si.shape.has_chart):
                continue
            try:
                cs = si.shape.chart._chartSpace
            except Exception:  # noqa: BLE001
                continue
            values = chart_values(cs)
            scaled = values + [v / 100 for v in values]
            # custom rich labels
            for dlbl in cs.iter(q("c:dLbl")):
                rich = dlbl.find(q("c:tx") + "/" + q("c:rich"))
                if rich is None:
                    continue
                label = "".join(t.text or "" for t in rich.iter(q("a:t"))).strip()
                nums = all_numbers(label)
                if not nums or not values:
                    continue
                for lv, _pct in nums:
                    nearest = min(scaled, key=lambda v: abs(v - lv)) if scaled else None
                    if nearest is None or abs(nearest - lv) > 0.5:
                        d.add(
                            id="chart-cache-label", severity="block", slide=sno, shape=si.name, shape_id=si.shape_id,
                            text=label[:80],
                            detail="data label figure %g has no matching cached value (nearest cached %s)" % (
                                lv, "%g" % nearest if nearest is not None else "none"
                            ),
                            fix="reword",
                        )
            # labels inside bars
            positions = set()
            for pos in cs.iter(q("c:dLblPos")):
                if pos.get("val") in ("ctr", "inBase", "inEnd"):
                    positions.add(pos.get("val"))
            is_bar = cs.find(".//" + q("c:barChart")) is not None or cs.find(".//" + q("c:bar3DChart")) is not None
            if positions and is_bar:
                d.add(
                    id="label-in-bar", severity="warn", slide=sno, shape=si.name, shape_id=si.shape_id,
                    text="", detail="data labels positioned inside bar segments (%s); house style puts labels outside" % ", ".join(sorted(positions)),
                    fix="none",
                )


def check_semicolon_runs(d: Deck):
    for sno, shapes in d.shapes_by_slide.items():
        for si in shapes:
            if not (getattr(si.shape, "has_table", False) and si.shape.has_table):
                continue
            hits = []
            for r, c, txBody, _text in d.table_cells(si):
                if txBody is None:
                    continue
                for p in txBody.findall(q("a:p")):
                    ptxt = "".join(t.text or "" for t in p.iter(q("a:t")))
                    if ptxt.count(";") >= 2:
                        hits.append((r, c, ptxt.strip()))
            if hits:
                d.add(
                    id="semicolon-runs", severity="warn", slide=sno, shape=si.name, shape_id=si.shape_id,
                    text=hits[0][2][:120],
                    detail="%d cell paragraph%s with 2+ semicolons (rows %s); split into bullets" % (
                        len(hits), "s" if len(hits) != 1 else "", ", ".join(str(h[0] + 1) for h in hits)
                    ),
                    fix="reword", auto_fixable=True,
                )


def check_abbreviations(d: Deck):
    expand = d.rules.get("expand", {}) or {}
    if not expand:
        return
    compiled = []
    for token, full in expand.items():
        if " " in token or not token[:1].isupper():
            pat = re.compile(r"(?<![\w-])" + re.escape(token) + r"(?![\w-])")
        else:
            pat = re.compile(r"(?<![\w-])" + re.escape(token) + r"(?![\w-])")
        compiled.append((token, full, pat))
    for sno, shapes in d.shapes_by_slide.items():
        for si in shapes:
            if not d.is_text_shape(si):
                continue
            runs = d.runs_of(si)
            paras = {}
            for r in runs:
                paras.setdefault(r.para_index, r.para_text)
            for _pi, ptxt in paras.items():
                if not visible(ptxt):
                    continue
                for token, full, pat in compiled:
                    for m in pat.finditer(ptxt):
                        # a single capitalised word at the start of a sentence is not an abbreviation
                        if " " not in token and token[:1].isupper():
                            before = ptxt[: m.start()].rstrip()
                            if not before or before.endswith((".", ":", ";", "!", "?")):
                                continue
                        d.add(
                            id="abbreviation-list", severity="warn", slide=sno, shape=si.name, shape_id=si.shape_id,
                            text=ptxt.strip()[:120],
                            detail="'%s' on a slide; house term is '%s'" % (token, full),
                            fix="reword",
                        )
                        break


def check_stakeholder_names(d: Deck):
    names = [n for n in (d.rules.get("client_names") or []) if visible(n)]
    if not names:
        return
    pats = [(n, re.compile(r"(?<!\w)" + re.escape(n) + r"(?!\w)", re.I)) for n in names]
    for sno in d.shapes_by_slide:
        for si, txt in d.slide_texts(sno):
            for n, pat in pats:
                if pat.search(txt):
                    d.add(
                        id="stakeholder-name", severity="block", slide=sno, shape=si.name, shape_id=si.shape_id,
                        text=txt.strip()[:120], detail="client stakeholder '%s' named on a slide" % n,
                        fix="reword",
                    )


def check_voice_words(d: Deck):
    words = d.rules.get("words") or []
    if not words:
        return
    pats = [(w, re.compile(r"(?<!\w)" + re.escape(w) + r"(?!\w)", re.I)) for w in words]
    for sno in d.shapes_by_slide:
        for si, txt in d.slide_texts(sno):
            hits = sorted({w for w, pat in pats if pat.search(txt)})
            if hits:
                d.add(
                    id="voice-word", severity="info", slide=sno, shape=si.name, shape_id=si.shape_id,
                    text=txt.strip()[:120], detail="dated word(s): %s (judgment stays with the skill)" % ", ".join(hits),
                    fix="reword",
                )


def _has_page_number(d: Deck, slide) -> bool:
    for sh in slide.shapes:
        if sh.is_placeholder and sh.placeholder_format.type == PP_PLACEHOLDER.SLIDE_NUMBER:
            return True
    layout = slide.slide_layout
    for container in (layout, layout.slide_master):
        for sp in container._element.iter(q("p:sp")):
            ph = sp.find(".//" + q("p:nvPr") + "/" + q("p:ph"))
            if ph is not None:
                continue  # placeholders on layout/master do not render on slides
            for fld in sp.iter(q("a:fld")):
                if fld.get("type") == "slidenum":
                    return True
        break_layout = layout._element.find(q("p:cSld"))
        _ = break_layout
    return False


def _has_footer(d: Deck, slide) -> bool:
    for sh in slide.shapes:
        if sh.is_placeholder and sh.placeholder_format.type == PP_PLACEHOLDER.FOOTER:
            return True
    layout = slide.slide_layout
    for container in (layout, layout.slide_master):
        for sp in container._element.iter(q("p:sp")):
            ph = sp.find(".//" + q("p:nvPr") + "/" + q("p:ph"))
            if ph is not None:
                continue
            txt = "".join(t.text or "" for t in sp.iter(q("a:t")))
            if "©" in txt or re.search(r"\bcopyright\b|\bconfidential\b", txt, re.I):
                return True
    return False


def check_style_drift(d: Deck):
    n = len(d.slides)
    # title face and size across content slides sharing a layout (slide 1 is the cover)
    by_layout: dict[str, dict[tuple, list[int]]] = {}
    for sno, slide in enumerate(d.slides, 1):
        if sno == 1:
            continue
        title = slide.shapes.title
        if title is None or not title.has_text_frame:
            continue
        si = next((s for s in d.shapes_by_slide[sno] if s.shape_id == title.shape_id), None)
        if si is None:
            continue
        runs = [r for r in d.runs_of(si) if visible(r.text)]
        if not runs:
            continue
        r0 = runs[0]
        face = d.resolve_theme_font(r0.latin, slide.slide_layout.slide_master, title) or d.inherited_latin(title, slide, 0)
        key = (round(r0.size, 1) if r0.size else None, face)
        by_layout.setdefault(slide.slide_layout.name, {}).setdefault(key, []).append(sno)
    for layout_name, variants in by_layout.items():
        if len(variants) > 1:
            desc = "; ".join(
                "%s/%s on slides %s" % ("%gpt" % k[0] if k[0] else "?", k[1] or "?", ", ".join(str(s) for s in v))
                for k, v in sorted(variants.items(), key=lambda kv: -len(kv[1]))
            )
            d.add(
                id="style-drift", severity="warn", slide=None, shape="title", shape_id=None,
                text="", detail="title size or face differs across slides on layout '%s': %s" % (layout_name, desc),
                fix="resize",
            )
    # page number and footer presence on content slides
    if n >= 3:
        with_num = [s for s in range(2, n + 1) if _has_page_number(d, d.slides[s - 1])]
        without_num = [s for s in range(2, n + 1) if s not in with_num]
        if with_num and without_num:
            d.add(
                id="style-drift", severity="warn", slide=None, shape=None, shape_id=None,
                text="", detail="page number missing on slides %s" % ", ".join(str(s) for s in without_num), fix="none",
            )
        with_ft = [s for s in range(2, n + 1) if _has_footer(d, d.slides[s - 1])]
        without_ft = [s for s in range(2, n + 1) if s not in with_ft]
        if with_ft and without_ft:
            d.add(
                id="style-drift", severity="warn", slide=None, shape=None, shape_id=None,
                text="", detail="footer missing on slides %s" % ", ".join(str(s) for s in without_ft), fix="none",
            )
    # fill colours outside the palette, and typefaces outside the allowlist
    palette = set(c.upper() for c in d.rules.get("palette", []))
    fonts = set(d.rules.get("fonts", []))
    active = d.rules.get("active_client_palette")
    client = (d.rules.get("client_palettes") or {}).get(active) if active else None
    if isinstance(client, dict):
        palette |= set(c.upper() for c in client.get("colours", []))
        fonts = set(client.get("fonts", [])) or fonts
    elif isinstance(client, list):
        palette |= set(c.upper() for c in client)
    client_fonts = set(client.get("fonts", [])) if isinstance(client, dict) else set()
    if fonts:
        # With a client palette the allowlist is exactly its fonts. Without one, allow the rules fonts, the theme
        # fonts and the deck's own dominant face, so only the minority faces (the leaks) are reported.
        dominant = None
        if not client_fonts:
            tally: dict[str, int] = {}
            for slide in d.slides:
                for lat in slide._element.iter(q("a:latin")):
                    face = lat.get("typeface") or ""
                    if face and not face.startswith("+"):
                        tally[face] = tally.get(face, 0) + 1
            if tally:
                dominant = max(tally, key=tally.get)
        for sno, slide in enumerate(d.slides, 1):
            master = slide.slide_layout.slide_master
            if client_fonts:
                allowed_faces = set(client_fonts)
            else:
                allowed_faces = set(fonts) | {f for f in (d.theme_font(master, True), d.theme_font(master, False)) if f}
                if dominant:
                    allowed_faces.add(dominant)
            off: dict[str, int] = {}
            for lat in slide._element.iter(q("a:latin")):
                face = lat.get("typeface") or ""
                if not face or face.startswith("+"):
                    continue
                if face not in allowed_faces:
                    off[face] = off.get(face, 0) + 1
            if off:
                d.add(
                    id="style-drift", severity="warn", slide=sno, shape=None, shape_id=None,
                    text="", detail="typeface(s) outside the allowlist (%s): %s" % (
                        ", ".join(sorted(allowed_faces)), ", ".join("%s x%d" % kv for kv in sorted(off.items()))
                    ),
                    fix="none",
                )
    tol = int(d.rules.get("palette_tolerance", 0))
    for sno, slide in enumerate(d.slides, 1):
        allowed = palette | d.theme_colors(slide.slide_layout.slide_master)
        offenders: dict[str, int] = {}
        for sp in slide._element.iter(q("p:spPr")):
            for fill in list(sp.findall(q("a:solidFill"))) + list(sp.findall(q("a:gradFill"))):
                for clr in fill.iter(q("a:srgbClr")):
                    val = (clr.get("val") or "").upper()
                    if len(val) != 6:
                        continue
                    if val in allowed or hex_distance_ok(val, allowed, tol):
                        continue
                    offenders[val] = offenders.get(val, 0) + 1
        if offenders:
            d.add(
                id="style-drift", severity="warn", slide=sno, shape=None, shape_id=None,
                text="", detail="fill colour(s) outside theme palette (+/-%d per channel): %s" % (
                    tol, ", ".join("%s x%d" % kv for kv in sorted(offenders.items()))
                ),
                fix="none",
            )


def check_draft_stamp(d: Deck):
    n = len(d.slides)
    if n < 2:
        return
    with_stamp = []
    for sno in d.shapes_by_slide:
        if any(re.search(r"\bDRAFT\b", txt) for _si, txt in d.slide_texts(sno)):
            with_stamp.append(sno)
    if not with_stamp:
        return
    without = [s for s in range(1, n + 1) if s not in with_stamp]
    if without:
        d.add(
            id="draft-stamp", severity="warn", slide=None, shape=None, shape_id=None,
            text="DRAFT", detail="DRAFT stamp on slides %s but not on %s" % (
                ", ".join(str(s) for s in with_stamp), ", ".join(str(s) for s in without)
            ),
            fix="none",
        )


def check_profile_length(d: Deck, profile: Optional[str]):
    if not profile:
        return
    prof = (d.rules.get("profiles") or {}).get(profile)
    if not prof or "length" not in prof:
        return
    lo, hi = prof["length"]
    n = len(d.slides)
    # appendix pages do not count: stop at the first divider titled Appendix or Crosstabs
    for i, slide in enumerate(d.slides):
        t = slide.shapes.title
        txt = t.text.strip() if t is not None and t.has_text_frame else ""
        if re.match(r"^(appendix|crosstabs?|backup)", txt, re.I):
            n = i
            break
    if n < lo or n > hi:
        d.add(
            id="deck-length", severity="info", slide=None, shape=None, shape_id=None,
            text="%d slides" % n, detail="%s profile expects %d-%d pages (appendix after a divider not counted)" % (profile, lo, hi), fix="none",
        )


ALL_CHECKS = [
    check_font_size_floor,
    check_italics,
    check_grey_text,
    check_table_one_size,
    check_metadata,
    check_speaker_notes,
    check_hidden_slides,
    check_comments,
    check_placeholders,
    check_leftover_notes_and_labels,
    check_quote_marks,
    check_textbox_conventions,
    check_native_table_small,
    check_shape_overlap,
    check_word_count,
    check_empty_textbox,
    check_off_canvas,
    check_overflow_estimate,
    check_footnote_sequence,
    check_totals,
    check_charts,
    check_semicolon_runs,
    check_abbreviations,
    check_stakeholder_names,
    check_style_drift,
    check_draft_stamp,
    check_voice_words,
]


def run_checks(path: Path, rules: dict, profile: Optional[str] = None) -> tuple[Deck, list[Finding]]:
    deck = Deck(path, rules)
    for fn in ALL_CHECKS:
        fn(deck)
    check_profile_length(deck, profile)
    if deck.appendix_start is not None:
        keep_ids = {"speaker-notes", "hidden-slides", "comments-open", "placeholders", "reviewer-note",
                    "stakeholder-name", "chart-cache-label", "totals-sum"}
        deck.findings = [f for f in deck.findings if f.slide is None or not deck.is_appendix(f.slide) or f.id in keep_ids]
    deck.findings.sort(key=lambda f: (SEVERITY_ORDER.get(f.severity, 9), f.slide or 0, f.id))
    return deck, deck.findings


# --------------------------------------------------------------------------------------
# --fix-safe
# --------------------------------------------------------------------------------------


def _set_text(parent, tag: str, text: str):
    node = parent.find(q(tag))
    if node is not None:
        node.text = text


def fix_safe(deck: Deck, findings: list[Finding], out_path: Path, log) -> Path:
    """Apply findings with exactly one correct answer. Never changes a number, a size or wording."""
    parts = dict(deck.parts)
    applied = []

    def load(name):
        return etree.fromstring(parts[name]) if name in parts else None

    def store(name, elm):
        parts[name] = etree.tostring(elm, xml_declaration=True, encoding="UTF-8", standalone=True)

    ids = {f.id for f in findings if f.auto_fixable}

    # core.xml
    core = load("docProps/core.xml")
    if core is not None and ({"author-empty", "metadata-scrub"} & ids):
        for tag in ("dc:creator", "cp:lastModifiedBy", "dc:title", "dc:subject", "cp:keywords",
                    "dc:description", "cp:category", "cp:contentStatus"):
            node = core.find(q(tag))
            if node is not None and visible(node.text or ""):
                node.text = ""
                applied.append("cleared core.xml %s" % tag)
        rev = core.find(q("cp:revision"))
        if rev is not None and (rev.text or "").strip() not in ("", "1"):
            rev.text = "1"
            applied.append("reset core.xml revision")
        store("docProps/core.xml", core)

    # app.xml
    app = load("docProps/app.xml")
    if app is not None and "metadata-scrub" in ids:
        tt = app.find(q("ep:TotalTime"))
        if tt is not None and (tt.text or "").strip() not in ("", "0"):
            tt.text = "0"
            applied.append("app.xml TotalTime -> 0")
        tpl = app.find(q("ep:Template"))
        if tpl is not None and visible(tpl.text or ""):
            tpl.text = ""
            applied.append("app.xml Template cleared")
        comp = app.find(q("ep:Company"))
        if comp is not None and visible(comp.text or ""):
            comp.text = ""
            applied.append("app.xml Company cleared")
        store("docProps/app.xml", app)

    # custom.xml
    if "docProps/custom.xml" in parts and "metadata-scrub" in ids:
        del parts["docProps/custom.xml"]
        rels = load("_rels/.rels")
        if rels is not None:
            for rel in list(rels):
                if rel.get("Type", "").endswith("/custom-properties"):
                    rels.remove(rel)
            store("_rels/.rels", rels)
        ct = load("[Content_Types].xml")
        if ct is not None:
            for ov in list(ct):
                if ov.get("PartName") == "/docProps/custom.xml":
                    ct.remove(ov)
            store("[Content_Types].xml", ct)
        applied.append("removed docProps/custom.xml and its relationship")

    # speaker notes
    if "speaker-notes" in ids:
        ct = load("[Content_Types].xml")
        removed = 0
        for name in list(parts):
            if name.startswith("ppt/slides/_rels/") and name.endswith(".rels"):
                rels = load(name)
                changed = False
                for rel in list(rels):
                    if rel.get("Type", "").endswith("/notesSlide"):
                        target = "ppt/" + rel.get("Target", "").replace("../", "")
                        notes = load(target)
                        if notes is not None:
                            txt = notes_text(notes)
                            if visible(txt):
                                log("  stripped note (%s):\n    %s" % (target, txt.replace("\n", "\n    ")))
                        rels.remove(rel)
                        changed = True
                        parts.pop(target, None)
                        parts.pop(target.replace("notesSlides/", "notesSlides/_rels/") + ".rels", None)
                        if ct is not None:
                            for ov in list(ct):
                                if ov.get("PartName") == "/" + target:
                                    ct.remove(ov)
                        removed += 1
                if changed:
                    store(name, rels)
        if ct is not None:
            store("[Content_Types].xml", ct)
        app = load("docProps/app.xml")
        if app is not None:
            notes_ct = app.find(q("ep:Notes"))
            if notes_ct is not None:
                notes_ct.text = "0"
            store("docProps/app.xml", app)
        if removed:
            applied.append("stripped %d notes slide%s" % (removed, "s" if removed != 1 else ""))

    # generator fingerprints
    if "metadata-scrub" in ids:
        fps = list(deck.rules.get("generator_fingerprints", []))
        phrases = list(deck.rules.get("generator_phrases_docprops_only", []))
        for name in list(parts):
            if not (name.endswith(".xml") or name.endswith(".rels")):
                continue
            text = parts[name].decode("utf-8", errors="ignore")
            new = text
            for fp in fps + (phrases if name.startswith("docProps/") else []):
                new = re.sub(re.escape(fp), "", new, flags=re.I)
            if new != text:
                parts[name] = new.encode("utf-8")
                applied.append("removed generator fingerprint from %s" % name)

    # straight quote marks -> curly, text nodes in slide parts only
    if "quote-marks" in ids:
        count = 0
        for name in list(parts):
            if not (name.startswith("ppt/slides/slide") and name.endswith(".xml")):
                continue
            elm = load(name)
            changed = False
            for p in elm.iter(q("a:p")):
                ts = [t for t in p.iter(q("a:t")) if t.text]
                joined = "".join(t.text for t in ts)
                if not STRAIGHT_QUOTE_RE.search(joined):
                    continue
                fixed = curly_quotes(joined)
                if fixed == joined:
                    continue
                pos = 0
                for t in ts:
                    n = len(t.text)
                    t.text = fixed[pos:pos + n]
                    pos += n
                changed = True
                count += 1
            if changed:
                store(name, elm)
        if count:
            applied.append("curled quote marks in %d paragraph%s" % (count, "s" if count != 1 else ""))

    # semicolon runs in native table cells -> one paragraph per item
    if "semicolon-runs" in ids:
        count = 0
        for name in list(parts):
            if not (name.startswith("ppt/slides/slide") and name.endswith(".xml")):
                continue
            elm = load(name)
            changed = False
            for tc in elm.iter(q("a:tc")):
                txBody = tc.find(q("a:txBody"))
                if txBody is None:
                    continue
                for p in list(txBody.findall(q("a:p"))):
                    ptxt = "".join(t.text or "" for t in p.iter(q("a:t")))
                    if ptxt.count(";") < 2:
                        continue
                    items = [s.strip() for s in ptxt.split(";") if s.strip()]
                    first_r = p.find(q("a:r"))
                    rPr = first_r.find(q("a:rPr")) if first_r is not None else None
                    pPr = p.find(q("a:pPr"))
                    endPr = p.find(q("a:endParaRPr"))
                    idx = list(txBody).index(p)
                    txBody.remove(p)
                    for k, item in enumerate(items):
                        np_ = etree.Element(q("a:p"))
                        if pPr is not None:
                            np_.append(etree.fromstring(etree.tostring(pPr)))
                        r = etree.SubElement(np_, q("a:r"))
                        if rPr is not None:
                            r.append(etree.fromstring(etree.tostring(rPr)))
                        t = etree.SubElement(r, q("a:t"))
                        t.text = item
                        if endPr is not None:
                            np_.append(etree.fromstring(etree.tostring(endPr)))
                        txBody.insert(idx + k, np_)
                    changed = True
                    count += 1
            if changed:
                store(name, elm)
        if count:
            applied.append("split %d semicolon run%s into paragraphs" % (count, "s" if count != 1 else ""))

    # write, [Content_Types].xml first
    order = ["[Content_Types].xml"] + [n for n in deck.parts if n in parts and n != "[Content_Types].xml"]
    order += [n for n in parts if n not in order]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name in order:
            if name in parts:
                z.writestr(name, parts[name])
    out_path.write_bytes(buf.getvalue())
    # validate: the saved file must open
    Presentation(str(out_path))
    for line in applied:
        log("  " + line)
    if not applied:
        log("  nothing to apply")
    return out_path


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def load_rules(path: Optional[Path]) -> dict:
    p = Path(path) if path else DEFAULT_RULES_PATH
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def format_table(findings: list[Finding]) -> str:
    if not findings:
        return "no findings"
    rows = []
    for f in findings:
        where = "-" if f.slide is None else str(f.slide)
        shape = (f.shape or "-")[:22]
        detail = f.detail
        if f.text:
            detail += '  |  "%s"' % (f.text.replace("\n", " / ")[:70])
        rows.append((f.severity.upper(), f.id, where, shape, detail))
    widths = [max(len(r[i]) for r in rows + [("SEV", "ID", "SLIDE", "SHAPE", "DETAIL")]) for i in range(4)]
    out = []
    hdr = ("SEV", "ID", "SLIDE", "SHAPE", "DETAIL")
    fmt = "%%-%ds  %%-%ds  %%%ds  %%-%ds  %%s" % tuple(widths)
    out.append(fmt % hdr)
    out.append("-" * (sum(widths) + 8 + 40))
    for r in rows:
        out.append(fmt % r)
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Deterministic QC gate for PPTX decks (deck-qc Layer 1 subset).")
    ap.add_argument("deck")
    ap.add_argument("--rules", default=None)
    ap.add_argument("--json", dest="json_out", default=None)
    ap.add_argument("--fix-safe", action="store_true")
    ap.add_argument("--profile", choices=["findings", "proposal", "kickoff", "minipack", "presentation", "update", "workshop"])
    args = ap.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    t0 = time.time()
    path = Path(args.deck)
    try:
        rules = load_rules(args.rules)
    except Exception as exc:  # noqa: BLE001
        print("cannot read rules: %s" % exc)
        return 2
    try:
        deck, findings = run_checks(path, rules, args.profile)
    except Exception as exc:  # noqa: BLE001
        print("cannot open %s: %s" % (path, exc))
        return 2
    elapsed = time.time() - t0

    counts = {s: sum(1 for f in findings if f.severity == s) for s in ("block", "warn", "info")}
    print("qc_check  %s  (%d slides, %.2fs%s)" % (path.name, len(deck.slides), elapsed, ", profile=%s" % args.profile if args.profile else ""))
    print(format_table(findings))
    print()
    print("block %d   warn %d   info %d   ->  %s" % (
        counts["block"], counts["warn"], counts["info"], "PASS" if counts["block"] == 0 else "BLOCKED"
    ))

    fixed_path = None
    if args.fix_safe:
        fixed_path = path.with_name(path.stem + ".qc.pptx")
        print("\n--fix-safe -> %s" % fixed_path.name)
        try:
            fix_safe(deck, findings, fixed_path, print)
        except Exception as exc:  # noqa: BLE001
            print("  fix-safe failed: %s" % exc)
            fixed_path = None

    if args.json_out:
        payload = {
            "deck": str(path),
            "slides": len(deck.slides),
            "profile": args.profile,
            "elapsed_s": round(elapsed, 3),
            "counts": counts,
            "pass": counts["block"] == 0,
            "fixed_file": str(fixed_path) if fixed_path else None,
            "findings": [f.as_dict() for f in findings],
        }
        Path(args.json_out).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    return 0 if counts["block"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
