#!/usr/bin/env python3
"""deck_diff.py: diff two versions of a PPTX at the text level, for draft-deck Learn mode and deck-qc diffs.

Usage:
    python scripts/deck_diff.py BEFORE.pptx AFTER.pptx [--md out.md] [--json out.json]

Slides are matched by title similarity first, then by position. For each matched pair the script
lists title changes, body paragraph changes (before/after), number changes, added and removed
shapes, and chart cache changes. Unmatched slides are reported as added or removed. Each change is
classified with a coarse heuristic: number, structure, style, storyline. The classification is a
first cut for a human or the Learn mode to confirm, not a verdict.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
C = "{http://schemas.openxmlformats.org/drawingml/2006/chart}"
NUM_RE = re.compile(r"[-+]?\$?\d[\d,]*\.?\d*%?")


def para_texts(shape) -> list[str]:
    out = []
    if getattr(shape, "has_text_frame", False) and shape.has_text_frame:
        for p in shape._element.iter(A + "p"):
            t = "".join(x.text or "" for x in p.iter(A + "t")).strip()
            if t:
                out.append(t)
    elif getattr(shape, "has_table", False) and shape.has_table:
        for r in shape.table.rows:
            cells = [c.text.strip() for c in r.cells]
            if any(cells):
                out.append(" | ".join(cells))
    return out


def chart_cache(shape) -> list[str]:
    if not (getattr(shape, "has_chart", False) and shape.has_chart):
        return []
    cs = shape.chart._chartSpace
    out = []
    for ser in cs.iter(C + "ser"):
        name = "".join(t.text or "" for t in ser.iter(A + "t"))[:30]
        vals = [pt.findtext(C + "v") for pt in ser.iter(C + "pt") if pt.getparent().tag.endswith("numCache")]
        out.append("%s: %s" % (name or "series", ", ".join(v for v in vals if v is not None)))
    return out


def walk(shapes):
    for sh in shapes:
        if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from walk(sh.shapes)
        else:
            yield sh


EMU_PT = 12700


def run_formats(shape) -> dict:
    """Counts of run-level formatting inside a shape: sizes, bold, italic, colours, faces."""
    out = {"sizes": {}, "bold": 0, "italic": 0, "colours": {}, "faces": {}, "runs": 0}
    for r in shape._element.iter(A + "r"):
        t = r.findtext(A + "t") or ""
        if not t.strip():
            continue
        out["runs"] += 1
        rPr = r.find(A + "rPr")
        if rPr is None:
            continue
        if rPr.get("sz"):
            k = str(int(rPr.get("sz")) / 100)
            out["sizes"][k] = out["sizes"].get(k, 0) + 1
        if rPr.get("b") == "1":
            out["bold"] += 1
        if rPr.get("i") == "1":
            out["italic"] += 1
        clr = rPr.find(A + "solidFill/" + A + "srgbClr")
        if clr is not None and clr.get("val"):
            v = clr.get("val").upper()
            out["colours"][v] = out["colours"].get(v, 0) + 1
        lat = rPr.find(A + "latin")
        if lat is not None and lat.get("typeface"):
            f = lat.get("typeface")
            out["faces"][f] = out["faces"].get(f, 0) + 1
    return out


def shape_kind(sh) -> str:
    if getattr(sh, "has_chart", False) and sh.has_chart:
        return "chart"
    if getattr(sh, "has_table", False) and sh.has_table:
        return "table"
    if sh.shape_type == MSO_SHAPE_TYPE.PICTURE:
        return "picture"
    if getattr(sh, "has_text_frame", False) and sh.has_text_frame:
        return "text"
    return str(sh.shape_type or "shape")


def slide_model(slide, idx):
    title = ""
    if slide.shapes.title is not None and slide.shapes.title.has_text_frame:
        title = slide.shapes.title.text.strip()
    shapes = []
    inventory = []
    fmt = {"sizes": {}, "bold": 0, "italic": 0, "colours": {}, "faces": {}, "runs": 0}
    fills = {}
    for sh in walk(slide.shapes):
        box = (sh.left or 0, sh.top or 0, sh.width or 0, sh.height or 0)
        paras = para_texts(sh)
        inventory.append({"name": sh.name, "kind": shape_kind(sh), "box": box, "text": " ".join(paras)[:60]})
        rf = run_formats(sh)
        for k in ("sizes", "colours", "faces"):
            for kk, vv in rf[k].items():
                fmt[k][kk] = fmt[k].get(kk, 0) + vv
        for k in ("bold", "italic", "runs"):
            fmt[k] += rf[k]
        spPr = sh._element.find(".//{http://schemas.openxmlformats.org/presentationml/2006/main}spPr")
        if spPr is not None:
            for clr in spPr.iter(A + "srgbClr"):
                v = (clr.get("val") or "").upper()
                if v:
                    fills[v] = fills.get(v, 0) + 1
        cache = chart_cache(sh)
        if not paras and not cache:
            continue
        shapes.append({"name": sh.name, "id": sh.shape_id, "paras": paras, "chart": cache,
                       "top": sh.top or 0, "left": sh.left or 0})
    if not title:
        # largest-font first paragraph fallback: use the topmost text shape
        tops = sorted((s for s in shapes if s["paras"]), key=lambda s: (s["top"], s["left"]))
        if tops:
            title = tops[0]["paras"][0]
    body = [p for s in shapes for p in s["paras"] if p != title]
    return {"idx": idx, "title": title, "shapes": shapes, "body": body, "hidden": slide._element.get("show") == "0",
            "inventory": inventory, "fmt": fmt, "fills": fills, "layout": slide.slide_layout.name}


def load(path: Path):
    prs = Presentation(str(path))
    return [slide_model(s, i) for i, s in enumerate(prs.slides, 1)]


def sim(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def match_slides(before, after):
    pairs, used_b, used_a = [], set(), set()
    # 1. strong title matches
    for a in after:
        best, best_s = None, 0.0
        for b in before:
            if b["idx"] in used_b:
                continue
            s = sim(a["title"], b["title"]) if a["title"] and b["title"] else 0.0
            if s > best_s:
                best, best_s = b, s
        if best is not None and best_s >= 0.6:
            pairs.append((best, a, best_s))
            used_b.add(best["idx"])
            used_a.add(a["idx"])
    # 2. body similarity for the rest
    for a in after:
        if a["idx"] in used_a:
            continue
        best, best_s = None, 0.0
        for b in before:
            if b["idx"] in used_b:
                continue
            s = sim(" ".join(a["body"])[:2000], " ".join(b["body"])[:2000])
            if s > best_s:
                best, best_s = b, s
        if best is not None and best_s >= 0.5:
            pairs.append((best, a, best_s))
            used_b.add(best["idx"])
            used_a.add(a["idx"])
    # 3. same position, both unmatched: treat as a rewritten page rather than a remove + add
    for a in after:
        if a["idx"] in used_a:
            continue
        b = next((x for x in before if x["idx"] == a["idx"] and x["idx"] not in used_b), None)
        if b is not None:
            pairs.append((b, a, 0.0))
            used_b.add(b["idx"])
            used_a.add(a["idx"])
    removed = [b for b in before if b["idx"] not in used_b]
    added = [a for a in after if a["idx"] not in used_a]
    pairs.sort(key=lambda t: t[1]["idx"])
    return pairs, removed, added


def _dict_delta(before: dict, after: dict) -> str:
    keys = sorted(set(before) | set(after), key=lambda k: (-(after.get(k, 0) + before.get(k, 0)), k))
    parts = []
    for k in keys:
        b, a = before.get(k, 0), after.get(k, 0)
        if b != a:
            parts.append("%s %d->%d" % (k, b, a))
    return ", ".join(parts)


def format_changes(b, a) -> list[dict]:
    """Shape inventory and run-formatting deltas between two matched slides."""
    out = []
    if b["layout"] != a["layout"]:
        out.append({"kind": "format-layout", "before": b["layout"], "after": a["layout"], "class": "format"})
    # inventory: match shapes by name+kind, then by text
    bi = {(s["name"], s["kind"]): s for s in b["inventory"]}
    ai = {(s["name"], s["kind"]): s for s in a["inventory"]}
    added = [ai[k] for k in ai if k not in bi]
    removed = [bi[k] for k in bi if k not in ai]
    moved, resized = [], []
    for k in bi.keys() & ai.keys():
        bb, ab = bi[k]["box"], ai[k]["box"]
        if abs(bb[0] - ab[0]) > 2 * EMU_PT or abs(bb[1] - ab[1]) > 2 * EMU_PT:
            moved.append(k[0])
        if abs(bb[2] - ab[2]) > 2 * EMU_PT or abs(bb[3] - ab[3]) > 2 * EMU_PT:
            resized.append(k[0])
    if added or removed:
        out.append({"kind": "format-shapes", "class": "format",
                    "before": "; ".join("%s (%s) %s" % (s["name"], s["kind"], s["text"][:40]) for s in removed) or "",
                    "after": "; ".join("%s (%s) %s" % (s["name"], s["kind"], s["text"][:40]) for s in added) or ""})
    if moved or resized:
        out.append({"kind": "format-geometry", "class": "format", "before": "",
                    "after": "moved: %s | resized: %s" % (", ".join(moved[:12]) or "none", ", ".join(resized[:12]) or "none")})
    bf, af = b["fmt"], a["fmt"]
    sizes = _dict_delta(bf["sizes"], af["sizes"])
    if sizes:
        out.append({"kind": "format-sizes", "class": "format", "before": "", "after": "font size runs: " + sizes})
    if bf["bold"] != af["bold"] or bf["italic"] != af["italic"]:
        out.append({"kind": "format-emphasis", "class": "format", "before": "bold %d, italic %d" % (bf["bold"], bf["italic"]),
                    "after": "bold %d, italic %d (of %d runs)" % (af["bold"], af["italic"], af["runs"])})
    colours = _dict_delta(bf["colours"], af["colours"])
    if colours:
        out.append({"kind": "format-text-colours", "class": "format", "before": "", "after": colours})
    faces = _dict_delta(bf["faces"], af["faces"])
    if faces:
        out.append({"kind": "format-faces", "class": "format", "before": "", "after": faces})
    fills = _dict_delta(b["fills"], a["fills"])
    if fills:
        out.append({"kind": "format-fills", "class": "format", "before": "", "after": fills})
    return out


def numbers(s: str) -> list[str]:
    return NUM_RE.findall(s)


def classify(before: str, after: str, is_title: bool) -> str:
    nb, na = numbers(before), numbers(after)
    if nb != na:
        return "number"
    if is_title:
        return "storyline" if sim(before, after) < 0.6 else "style"
    return "style"


def diff_pair(b, a, s):
    changes = []
    if b["title"] != a["title"]:
        changes.append({"kind": "title", "before": b["title"], "after": a["title"],
                        "class": classify(b["title"], a["title"], True)})
    bp, ap = b["body"], a["body"]
    sm = difflib.SequenceMatcher(None, bp, ap)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        olds, news = bp[i1:i2], ap[j1:j2]
        # pair up replaced paragraphs by similarity
        if tag == "replace":
            for o in olds:
                best = max(news, key=lambda n: sim(o, n), default=None)
                if best is not None and sim(o, best) >= 0.35:
                    changes.append({"kind": "body", "before": o, "after": best, "class": classify(o, best, False)})
                    news.remove(best)
                else:
                    changes.append({"kind": "body-removed", "before": o, "after": "", "class": "structure"})
            for n in news:
                changes.append({"kind": "body-added", "before": "", "after": n, "class": "structure"})
        elif tag == "delete":
            for o in olds:
                changes.append({"kind": "body-removed", "before": o, "after": "", "class": "structure"})
        elif tag == "insert":
            for n in news:
                changes.append({"kind": "body-added", "before": "", "after": n, "class": "structure"})
    cb = [c for sh in b["shapes"] for c in sh["chart"]]
    ca = [c for sh in a["shapes"] for c in sh["chart"]]
    if cb != ca:
        changes.append({"kind": "chart-cache", "before": "; ".join(cb), "after": "; ".join(ca), "class": "number"})
    if b["hidden"] != a["hidden"]:
        changes.append({"kind": "hidden", "before": str(b["hidden"]), "after": str(a["hidden"]), "class": "structure"})
    changes.extend(format_changes(b, a))
    return {"before_slide": b["idx"], "after_slide": a["idx"], "match": round(s, 2), "title": a["title"], "changes": changes}


def render_md(result) -> str:
    out = ["# Deck diff", "", "before: %s" % result["before"], "after: %s" % result["after"], ""]
    counts = result["counts"]
    out.append("| class | count |\n|---|---|")
    for k in ("number", "structure", "storyline", "style", "format"):
        out.append("| %s | %d |" % (k, counts.get(k, 0)))
    out.append("")
    if result["removed"]:
        out.append("## Slides removed (in before only)")
        for s in result["removed"]:
            out.append("- before %d: %s" % (s["idx"], s["title"][:120]))
        out.append("")
    if result["added"]:
        out.append("## Slides added (in after only)")
        for s in result["added"]:
            out.append("- after %d: %s" % (s["idx"], s["title"][:120]))
        out.append("")
    moved = [p for p in result["pairs"] if p["before_slide"] != p["after_slide"]]
    if moved:
        out.append("## Slides moved")
        for p in moved:
            out.append("- before %d -> after %d: %s" % (p["before_slide"], p["after_slide"], p["title"][:100]))
        out.append("")
    out.append("## Changes by slide")
    for p in result["pairs"]:
        if not p["changes"]:
            continue
        out.append("\n### after %d (before %d): %s" % (p["after_slide"], p["before_slide"], p["title"][:110]))
        for c in p["changes"]:
            out.append("- **%s / %s**" % (c["kind"], c["class"]))
            if c["before"]:
                out.append("  - before: %s" % c["before"][:400])
            if c["after"]:
                out.append("  - after:  %s" % c["after"][:400])
    unchanged = [p["after_slide"] for p in result["pairs"] if not p["changes"]]
    out.append("\nUnchanged slides (after numbering): %s" % ", ".join(str(i) for i in unchanged))
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--md")
    ap.add_argument("--json", dest="json_out")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    before, after = load(Path(args.before)), load(Path(args.after))
    pairs, removed, added = match_slides(before, after)
    diffs = [diff_pair(b, a, s) for b, a, s in pairs]
    counts = {}
    for d in diffs:
        for c in d["changes"]:
            counts[c["class"]] = counts.get(c["class"], 0) + 1
    for s in removed + added:
        counts["structure"] = counts.get("structure", 0) + 1
    result = {"before": args.before, "after": args.after, "counts": counts, "pairs": diffs,
              "removed": [{"idx": s["idx"], "title": s["title"]} for s in removed],
              "added": [{"idx": s["idx"], "title": s["title"]} for s in added]}
    md = render_md(result)
    if args.md:
        Path(args.md).write_text(md, encoding="utf-8")
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
