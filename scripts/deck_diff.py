#!/usr/bin/env python3
"""Shim: deck_diff.py lives in .claude/skills/deck-qc/scripts/ so the skill bundle carries it. This file keeps
`python scripts/deck_diff.py ...` and the tests working from the repo root by loading that file and re-exporting it."""
import importlib.util
import sys
from pathlib import Path

_TARGET = Path(__file__).resolve().parents[1] / ".claude" / "skills" / "deck-qc" / "scripts" / "deck_diff.py"
_spec = importlib.util.spec_from_file_location("_deck_diff_impl", _TARGET)
_impl = importlib.util.module_from_spec(_spec)
sys.modules["_deck_diff_impl"] = _impl
_spec.loader.exec_module(_impl)

for _name in dir(_impl):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_impl, _name)

if __name__ == "__main__":
    sys.exit(_impl.main())
