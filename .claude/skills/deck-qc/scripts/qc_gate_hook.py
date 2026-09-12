#!/usr/bin/env python3
"""qc_gate_hook.py: Claude Code Stop hook that runs qc_check.py on every PPTX touched in the session.

Wired in .claude/settings.json. Claude Code passes a JSON payload on stdin:
    {"session_id": ..., "transcript_path": ..., "cwd": ..., "hook_event_name": "Stop", "stop_hook_active": bool}

Behaviour:
  * Find PPTX files written or modified during the session: paths mentioned in the transcript that exist,
    plus any *.pptx under cwd whose mtime is at or after the session start (first transcript timestamp).
    Files under tests/fixtures/, .venv/, _handoff/ and node_modules/ are ignored.
  * Run qc_check on each. If any `block` finding exists, print the findings and exit 2 so the turn cannot end.
  * Keep a counter per session in a state file. After 3 blocked stops, exit 0 and print
    "gate cap reached, handing off with findings attached" so the loop terminates.
  * Never crash the stop: any internal error prints a note and exits 0.

Re-execs itself under the repo venv when python-pptx is not importable from the interpreter that started it.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3] if len(HERE.parents) >= 4 else HERE
CAP = 3
EXCLUDE_PARTS = ("tests/fixtures", ".venv", "_handoff", "node_modules", "__pycache__")
PPTX_PATH_RE = re.compile(r"""[A-Za-z]:\\[^"'<>|\n]*?\.pptx|(?:/|\./|\.\./)[^"'<>|\s]*?\.pptx|[\w./\\ -]+\.pptx""")


def _ensure_pptx():
    try:
        import pptx  # noqa: F401
        return True
    except ImportError:
        pass
    for cand in (REPO / ".venv" / "Scripts" / "python.exe", REPO / ".venv" / "bin" / "python"):
        if cand.exists() and Path(sys.executable).resolve() != cand.resolve():
            data = sys.stdin.read()
            proc = subprocess.run([str(cand), str(Path(__file__).resolve())] + sys.argv[1:], input=data, text=True)
            sys.exit(proc.returncode)
    return False


def state_path(session_id: str) -> Path:
    base = Path(os.environ.get("QC_GATE_STATE_DIR") or tempfile.gettempdir())
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id or "nosession")
    return base / ("qc_gate_%s.json" % safe)


def load_state(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {"blocked": 0}


def save_state(p: Path, st: dict) -> None:
    try:
        p.write_text(json.dumps(st), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass


def session_start(transcript_path: str | None) -> float | None:
    if not transcript_path:
        return None
    p = Path(transcript_path)
    if not p.exists():
        return None
    try:
        with open(p, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                m = re.search(r'"timestamp"\s*:\s*"([^"]+)"', line)
                if m:
                    ts = m.group(1).replace("Z", "+00:00")
                    try:
                        return datetime.fromisoformat(ts).timestamp()
                    except ValueError:
                        break
    except OSError:
        return None
    try:
        return p.stat().st_ctime
    except OSError:
        return None


def excluded(path: Path, cwd: Path) -> bool:
    try:
        rel = path.resolve().relative_to(cwd.resolve()).as_posix()
    except ValueError:
        rel = path.as_posix()
    return any(part in rel for part in EXCLUDE_PARTS)


def find_candidates(cwd: Path, transcript_path: str | None, since: float | None) -> list[Path]:
    found: dict[str, Path] = {}
    # 1. paths named in the transcript
    if transcript_path and Path(transcript_path).exists():
        try:
            text = Path(transcript_path).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            text = ""
        for m in PPTX_PATH_RE.finditer(text):
            raw = m.group(0).strip().replace("\\\\", "\\")
            p = Path(raw)
            if not p.is_absolute():
                p = cwd / p
            if p.exists() and p.is_file() and not excluded(p, cwd):
                found[str(p.resolve())] = p.resolve()
    # 2. anything under cwd modified since the session started
    if since is not None:
        for p in cwd.rglob("*.pptx"):
            if excluded(p, cwd):
                continue
            try:
                if p.stat().st_mtime >= since - 1:
                    found[str(p.resolve())] = p.resolve()
            except OSError:
                continue
    return sorted(found.values())


def gate(paths: list[Path], session_id: str, out) -> int:
    """Run qc_check on paths. Returns the exit code for the hook."""
    sys.path.insert(0, str(HERE))
    import qc_check  # noqa: E402

    rules = qc_check.load_rules(None)
    blocked: dict[Path, list] = {}
    for p in paths:
        try:
            _deck, findings = qc_check.run_checks(p, rules)
        except Exception as exc:  # noqa: BLE001
            out("qc gate: could not open %s (%s); not blocking on it" % (p.name, exc))
            continue
        blocks = [f for f in findings if f.severity == "block"]
        if blocks:
            blocked[p] = blocks
    sp = state_path(session_id)
    st = load_state(sp)
    if not blocked:
        if st.get("blocked"):
            out("qc gate: clean after %d blocked stop%s" % (st["blocked"], "s" if st["blocked"] != 1 else ""))
        st["blocked"] = 0
        save_state(sp, st)
        return 0
    st["blocked"] = int(st.get("blocked", 0)) + 1
    st["last"] = [str(p) for p in blocked]
    save_state(sp, st)
    out("qc gate: %d file%s with blocking findings (blocked stop %d of %d)" % (
        len(blocked), "s" if len(blocked) != 1 else "", st["blocked"], CAP
    ))
    for p, blocks in blocked.items():
        out("\n%s" % p)
        out(qc_check.format_table(blocks))
        fixable = [f for f in blocks if f.auto_fixable]
        if fixable:
            out("(%d of these are auto-fixable: python %s %s --fix-safe)" % (
                len(fixable), Path(qc_check.__file__).as_posix(), p.as_posix()
            ))
    if st["blocked"] >= CAP:
        out("\ngate cap reached, handing off with findings attached")
        return 0
    out("\nFix the blocking findings above and re-run qc_check.py before ending the turn.")
    return 2


def run(payload: dict, cwd: Path | None = None, out=None) -> int:
    out = out or (lambda s: print(s, file=sys.stderr))
    cwd = Path(cwd or payload.get("cwd") or os.getcwd())
    since = session_start(payload.get("transcript_path"))
    paths = find_candidates(cwd, payload.get("transcript_path"), since)
    if not paths:
        return 0
    return gate(paths, payload.get("session_id", ""), out)


def main() -> int:
    if not _ensure_pptx():
        print("qc gate: python-pptx not available and no .venv found; gate skipped", file=sys.stderr)
        return 0
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:  # noqa: BLE001
        payload = {}
    try:
        return run(payload)
    except Exception as exc:  # noqa: BLE001
        print("qc gate: internal error (%s); gate skipped" % exc, file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
