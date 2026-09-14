#!/usr/bin/env python3
"""Shim: deck_diff.py lives in .claude/skills/deck-qc/scripts/ so the skill bundle carries it. This file keeps
`python scripts/deck_diff.py ...` and the tests working from the repo root."""
import runpy
import sys
from pathlib import Path

_TARGET = Path(__file__).resolve().parents[1] / ".claude" / "skills" / "deck-qc" / "scripts"
sys.path.insert(0, str(_TARGET))
if __name__ == "__main__":
    runpy.run_path(str(_TARGET / "deck_diff.py"), run_name="__main__")
else:
    from deck_diff import *  # noqa: F401,F403
    import deck_diff as _m
    main, numbers, classify, load, APPENDIX_RE = _m.main, _m.numbers, _m.classify, _m.load, _m.APPENDIX_RE
