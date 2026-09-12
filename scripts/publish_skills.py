#!/usr/bin/env python3
"""publish_skills.py: diff repo skills against the account (Cowork) copies synced to this machine.

Usage:
    python scripts/publish_skills.py --account-dir "PATH/TO/synced/skills" [--skill draft-deck]

For each skill under .claude/skills/, compares SKILL.md and references/* with the copy under
<account-dir>/<skill>/. Prints which files are identical, which differ and which side is newer by
mtime, and which are missing on either side. It cannot write to account storage; the publish is a
click in Cowork (proposal card or skills settings upload). Exit 1 when anything is stale.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / ".claude" / "skills"


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]


def skill_files(skill_dir: Path) -> list[Path]:
    out = [skill_dir / "SKILL.md"]
    refs = skill_dir / "references"
    if refs.is_dir():
        out += sorted(p for p in refs.iterdir() if p.is_file())
    return [p for p in out if p.exists()]


def stamp(p: Path) -> str:
    return datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")


def compare(account_dir: Path, only: str | None) -> int:
    stale = 0
    rows = []
    for skill_dir in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        if only and skill_dir.name != only:
            continue
        acct = account_dir / skill_dir.name
        for repo_file in skill_files(skill_dir):
            rel = repo_file.relative_to(skill_dir).as_posix()
            acct_file = acct / rel
            if not acct_file.exists():
                rows.append((skill_dir.name, rel, "MISSING IN ACCOUNT", stamp(repo_file), "-"))
                stale += 1
                continue
            if digest(repo_file) == digest(acct_file):
                rows.append((skill_dir.name, rel, "same", stamp(repo_file), stamp(acct_file)))
                continue
            newer = "repo newer -> publish" if repo_file.stat().st_mtime >= acct_file.stat().st_mtime else "ACCOUNT NEWER -> copy back to repo"
            rows.append((skill_dir.name, rel, newer, stamp(repo_file), stamp(acct_file)))
            stale += 1
        if acct.is_dir():
            for acct_file in sorted(acct.rglob("*")):
                if acct_file.is_file() and not (skill_dir / acct_file.relative_to(acct)).exists():
                    rows.append((skill_dir.name, acct_file.relative_to(acct).as_posix(), "ONLY IN ACCOUNT", "-", stamp(acct_file)))
                    stale += 1
    widths = [max(len(str(r[i])) for r in rows + [("SKILL", "FILE", "STATUS", "REPO MTIME", "ACCOUNT MTIME")]) for i in range(5)]
    fmt = "  ".join("%%-%ds" % w for w in widths)
    print(fmt % ("SKILL", "FILE", "STATUS", "REPO MTIME", "ACCOUNT MTIME"))
    for r in rows:
        print(fmt % r)
    print("\n%d file%s stale" % (stale, "s" if stale != 1 else ""))
    return 1 if stale else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--account-dir", required=True, help="the synced Cowork skills folder on this machine")
    ap.add_argument("--skill", default=None)
    args = ap.parse_args(argv)
    acct = Path(args.account_dir)
    if not acct.is_dir():
        print("account dir not found: %s" % acct)
        return 2
    return compare(acct, args.skill)


if __name__ == "__main__":
    sys.exit(main())
