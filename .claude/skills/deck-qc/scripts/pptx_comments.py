#!/usr/bin/env python3
"""pptx_comments.py: list the reviewer comments in a PPTX, from both comment stores, with the slide each sits on.

Usage:
    python pptx_comments.py DECK.pptx                      # markdown table on stdout
    python pptx_comments.py DECK.pptx --json out.json      # machine-readable
    python pptx_comments.py DECK.pptx --open-only          # skip comments already marked resolved
    python pptx_comments.py DECK.pptx --resolve all --out DECK.resolved.pptx
    python pptx_comments.py DECK.pptx --resolve 3,5 --out DECK.resolved.pptx

Stores read:
    modern  ppt/comments/modernComment_*.xml   (PowerPoint 2019+/365; authors in ppt/authors.xml; status="resolved")
    legacy  ppt/comments/comment*.xml          (PowerPoint 2007-2016; authors in ppt/commentAuthors.xml; no status)

Each comment carries: running number, slide number, author, created, text, status, anchored shape id, replies.
Slide numbers follow presentation order (the number PowerPoint shows), not the part name.

--resolve sets status="resolved" on the chosen modern comments and writes a new file; nothing else in the
package is touched. Legacy comments have no status attribute and are left as they are (say so in the log).
Exit 0 always for listing; exit 1 when --resolve names a comment that does not exist.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

from lxml import etree

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p188": "http://schemas.microsoft.com/office/powerpoint/2018/8/main",
    "ac": "http://schemas.microsoft.com/office/drawing/2013/main/command",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}
RESOLVED = ("resolved", "closed")


def q(tag: str) -> str:
    pre, local = tag.split(":")
    return "{%s}%s" % (NS[pre], local)


@dataclass
class Reply:
    author: str
    created: str
    text: str


@dataclass
class Comment:
    n: int
    slide: int
    author: str
    created: str
    text: str
    status: str
    shape_id: str
    store: str
    part: str
    cid: str
    replies: list[Reply] = field(default_factory=list)

    @property
    def open(self) -> bool:
        return self.status not in RESOLVED


def _norm(part: str, target: str) -> str:
    """Resolve a relationship Target against the directory of the source part."""
    if target.startswith("/"):
        return target.lstrip("/")
    base = part.rsplit("/", 1)[0] if "/" in part else ""
    segs = (base.split("/") if base else []) + target.split("/")
    out: list[str] = []
    for s in segs:
        if s == "..":
            if out:
                out.pop()
        elif s and s != ".":
            out.append(s)
    return "/".join(out)


def _rels(z: zipfile.ZipFile, part: str) -> dict[str, str]:
    d, _, f = part.rpartition("/")
    name = "%s/_rels/%s.rels" % (d, f) if d else "_rels/%s.rels" % f
    if name not in z.namelist():
        return {}
    root = etree.fromstring(z.read(name))
    return {r.get("Id"): _norm(part, r.get("Target")) for r in root.iter(q("rel:Relationship")) if r.get("TargetMode") != "External"}


def slide_parts_in_order(z: zipfile.ZipFile) -> list[str]:
    pres = etree.fromstring(z.read("ppt/presentation.xml"))
    rels = _rels(z, "ppt/presentation.xml")
    out = []
    for sid in pres.iter(q("p:sldId")):
        rid = sid.get(q("r:id"))
        if rid in rels:
            out.append(rels[rid])
    return out


def _authors(z: zipfile.ZipFile) -> dict[str, str]:
    names: dict[str, str] = {}
    if "ppt/authors.xml" in z.namelist():
        for a in etree.fromstring(z.read("ppt/authors.xml")).iter(q("p188:author")):
            names[a.get("id")] = a.get("name") or a.get("initials") or "?"
    if "ppt/commentAuthors.xml" in z.namelist():
        for a in etree.fromstring(z.read("ppt/commentAuthors.xml")).iter(q("p:cmAuthor")):
            names[a.get("id")] = a.get("name") or a.get("initials") or "?"
    return names


def _text(elm) -> str:
    return " ".join("".join(t.text or "" for t in p.iter(q("a:t"))).strip() for p in elm.iter(q("a:p"))).strip()


def read_comments(path: Path) -> list[Comment]:
    out: list[Comment] = []
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        authors = _authors(z)
        for sno, spart in enumerate(slide_parts_in_order(z), 1):
            for target in _rels(z, spart).values():
                if not target.startswith("ppt/comments/") or target not in names:
                    continue
                root = etree.fromstring(z.read(target))
                if "modernComment" in target:
                    for cm in root.iter(q("p188:cm")):
                        sp = cm.find(".//" + q("ac:spMk"))
                        tx = cm.find(q("p188:txBody"))
                        replies = [
                            Reply(authors.get(r.get("authorId"), "?"), r.get("created", ""), _text(r))
                            for r in cm.iter(q("p188:reply"))
                        ]
                        out.append(Comment(
                            n=0, slide=sno, author=authors.get(cm.get("authorId"), "?"),
                            created=cm.get("created", ""), text=_text(tx) if tx is not None else "",
                            status=cm.get("status", "active"), shape_id=sp.get("id", "") if sp is not None else "",
                            store="modern", part=target, cid=cm.get("id", ""), replies=replies,
                        ))
                else:
                    for cm in root.iter(q("p:cm")):
                        out.append(Comment(
                            n=0, slide=sno, author=authors.get(cm.get("authorId"), "?"),
                            created=cm.get("dt", ""), text=(cm.findtext(q("p:text")) or "").strip(),
                            status="active", shape_id="", store="legacy", part=target, cid=cm.get("idx", ""),
                        ))
    out.sort(key=lambda c: (c.slide, c.created, c.cid))
    for i, c in enumerate(out, 1):
        c.n = i
    return out


def render_md(comments: list[Comment], path: Path) -> str:
    rows = ["# Comments in %s" % path.name, "",
            "%d comment%s, %d open" % (len(comments), "" if len(comments) == 1 else "s", sum(c.open for c in comments)), "",
            "| # | Slide | Author | Created | Status | Comment |", "|---|---|---|---|---|---|"]
    for c in comments:
        text = c.text.replace("|", "\\|").replace("\n", " ")
        if c.replies:
            text += " *(%d repl%s: %s)*" % (len(c.replies), "y" if len(c.replies) == 1 else "ies",
                                             "; ".join("%s: %s" % (r.author, r.text[:80]) for r in c.replies))
        rows.append("| %d | %d | %s | %s | %s | %s |" % (c.n, c.slide, c.author, c.created[:10], c.status, text))
    return "\n".join(rows)


def resolve(path: Path, out_path: Path, which: set[int] | None, comments: list[Comment], log) -> int:
    """Write a copy of the deck with status="resolved" on the chosen modern comments."""
    chosen = [c for c in comments if which is None or c.n in which]
    if which is not None and len(chosen) != len(which):
        log("unknown comment number(s): %s" % sorted(which - {c.n for c in chosen}))
        return 1
    by_part: dict[str, set[str]] = {}
    skipped = 0
    for c in chosen:
        if c.store != "modern":
            skipped += 1
            continue
        by_part.setdefault(c.part, set()).add(c.cid)
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename in by_part:
                root = etree.fromstring(data)
                for cm in root.iter(q("p188:cm")):
                    if cm.get("id") in by_part[item.filename]:
                        cm.set("status", "resolved")
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
            zout.writestr(item, data)
    done = sum(len(v) for v in by_part.values())
    log("%d comment%s marked resolved -> %s" % (done, "" if done == 1 else "s", out_path))
    if skipped:
        log("%d legacy comment%s left as they were (no status field in that format)" % (skipped, "" if skipped == 1 else "s"))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("deck")
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--md")
    ap.add_argument("--open-only", action="store_true")
    ap.add_argument("--resolve", help="'all' or comma-separated comment numbers from the listing")
    ap.add_argument("--out", help="output PPTX for --resolve (default: DECK.resolved.pptx)")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    path = Path(args.deck)
    comments = read_comments(path)
    shown = [c for c in comments if c.open] if args.open_only else comments
    md = render_md(shown, path)
    print(md)
    if args.md:
        Path(args.md).write_text(md, encoding="utf-8")
    if args.json_out:
        Path(args.json_out).write_text(json.dumps([asdict(c) | {"open": c.open} for c in shown], indent=2, ensure_ascii=False), encoding="utf-8")
    if args.resolve:
        which = None if args.resolve.strip().lower() == "all" else {int(x) for x in re.split(r"[,\s]+", args.resolve.strip()) if x}
        out = Path(args.out) if args.out else path.with_name(path.stem + ".resolved.pptx")
        return resolve(path, out, which, comments, log=lambda s: print(s, file=sys.stderr))
    return 0


if __name__ == "__main__":
    sys.exit(main())
