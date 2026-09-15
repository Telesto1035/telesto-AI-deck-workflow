#!/usr/bin/env python3
"""qc_gate_hook.py: Claude Code Stop hook that runs qc_check.py on every PPTX touched in the session.

Wired in .claude/settings.json. Claude Code passes a JSON payload on stdin:
    {"session_id": ..., "transcript_path": ..., "cwd": ..., "hook_event_name": "Stop", "stop_hook_active": bool}

Behaviour:
  * Find PPTX files THIS SESSION WROTE: a path mentioned in the transcript, or any *.pptx under cwd, but in
    both cases only when its mtime is at or after the session start (first transcript timestamp, the floor
    for a first run). Naming a deck is not touching it — a deck the conversation read, quoted or discussed
    keeps its old mtime and is not gated, because gating someone else's file blocks this session's stop over
    work it did not do. With no transcript timestamp there is nothing to measure against, so nothing is gated.
    A file that gated clean has its mtime recorded in the state file and is not gated again until it changes;
    a file that blocked is always re-gated. A Cowork session that runs for days would otherwise gate the
    whole workspace.
  * Ignored: the path fragments in qc_rules.json `gate_exclude` (fixtures, asset folders, the .qc.pptx output
    of --fix-safe), any `worktrees` folder (another agent's session owns those files), and templates
    (*template*.pptx, *.potx, or a file with no slide parts), which are specimen layouts rather than decks.
    Every skip is logged, never silent.
  * Run qc_check on each. If any `block` finding exists, print the findings and exit 2 so the turn cannot end.
  * Keep a counter per session in a state file. After 3 blocked stops, exit 0 and print
    "gate cap reached, handing off with findings attached" so the loop terminates.
  * Render step: OFF by default and opt-in, because .claude/settings.json sets QC_GATE_NO_RENDER=1. The skill's
    stage 2 owns the render, run by hand on the pages an iteration changed; exporting a whole deck through
    PowerPoint at every Stop costs minutes and repeats what the consultant just did. Clear the env var and the
    block below runs on Windows, once per deck version, keyed on path and mtime in the state file. Raise the
    hook's timeout in settings.json above RENDER_TIMEOUT before doing that: 400 was sized for it, the current
    120 is sized for the gate alone, with room for a session that wrote several decks.
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
import zipfile
from functools import lru_cache
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3] if len(HERE.parents) >= 4 else HERE
CAP = 3
RENDER_TIMEOUT = 150  # seconds per deck; settings.json gives the whole hook 400
DEFAULT_EXCLUDE_PARTS = ("tests/fixtures", ".venv", "_handoff", "node_modules", "__pycache__")
TEMPLATE_NAME_RE = re.compile(r"template", re.I)
SLIDE_PART_RE = re.compile(r"^ppt/slides/slide\d+\.xml$")


@lru_cache(maxsize=1)
def exclude_parts() -> tuple:
    """Path fragments never gated. Lives in qc_rules.json so the list travels with the rules, not the code."""
    try:
        blob = json.loads((HERE / "qc_rules.json").read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return DEFAULT_EXCLUDE_PARTS
    v = blob.get("gate_exclude")
    return tuple(str(x) for x in v) if isinstance(v, list) and v else DEFAULT_EXCLUDE_PARTS


def exclude_dirs() -> set:
    """Folder names pruned before descending: the single-segment entries of the exclusion list, plus .git."""
    return {".git"} | {p.strip("/") for p in exclude_parts() if "/" not in p and not p.endswith(".pptx")}
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


def read_transcript(transcript_path: str | None) -> str:
    if not transcript_path:
        return ""
    p = Path(transcript_path)
    try:
        return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""
    except OSError:
        return ""


def session_start(transcript_path: str | None, text: str | None = None) -> float | None:
    if not transcript_path:
        return None
    p = Path(transcript_path)
    if not p.exists():
        return None
    text = read_transcript(transcript_path) if text is None else text
    m = re.search(r'"timestamp"\s*:\s*"([^"]+)"', text)
    if m:
        try:
            return datetime.fromisoformat(m.group(1).replace("Z", "+00:00")).timestamp()
        except ValueError:
            pass
    try:
        return p.stat().st_ctime
    except OSError:
        return None


def excluded(path: Path, cwd: Path) -> bool:
    try:
        resolved = path.resolve()
        rel = resolved.relative_to(cwd.resolve()).as_posix()
    except ValueError:
        resolved = path
        rel = path.as_posix()
    # A git worktree belongs to another agent's session, whether the path was walked or named in the
    # transcript. Checked on the whole path, not just the part under cwd, so a worktree elsewhere on
    # disk is skipped too.
    if "worktrees" in resolved.parts:
        return True
    return any(part in rel for part in exclude_parts())


def _walk_pptx(cwd: Path):
    """Every *.pptx under cwd, pruning the venv and other excluded folders before descending.

    `worktrees` is pruned because a git worktree under .claude/ belongs to another agent's session: its
    files carry fresh mtimes from work this session did not do and must not block this session's stop."""
    for root, dirnames, filenames in os.walk(cwd):
        prune = exclude_dirs() | {"worktrees"}
        dirnames[:] = [d for d in dirnames if d not in prune]
        for fn in filenames:
            if fn.lower().endswith(".pptx"):
                yield Path(root) / fn


def is_template(p: Path) -> bool:
    """A template is not a deck: its slides are specimen layouts, so its word counts and label rows mean
    nothing. Name, extension, or a file that carries masters and layouts but no slide parts."""
    if p.suffix.lower() == ".potx" or TEMPLATE_NAME_RE.search(p.name):
        return True
    try:
        with zipfile.ZipFile(p) as z:
            return not any(SLIDE_PART_RE.match(n) for n in z.namelist())
    except Exception:  # noqa: BLE001
        return False


def unchanged_since_last_gate(p: Path, gated: dict) -> bool:
    """True when this path gated clean at an earlier Stop and has not been written since."""
    prev = gated.get(str(p))
    if prev is None:
        return False
    try:
        return p.stat().st_mtime <= float(prev) + 0.001
    except OSError:
        return False


def written_since(p: Path, since: float) -> bool:
    """True when this file was written during the session. Naming a deck is not touching it: a deck the
    conversation only read or discussed keeps its old mtime and is not this session's to gate."""
    try:
        return p.stat().st_mtime >= since - 1
    except OSError:
        return False


def find_candidates(cwd: Path, transcript_path: str | None, since: float | None, text: str | None = None) -> list[Path]:
    """Decks this session wrote. Both sources are filtered on mtime, so a deck that was only mentioned,
    opened or read is never a candidate, and neither is one another session owns."""
    found: dict[str, Path] = {}
    if since is None:
        # No transcript timestamp: nothing establishes what this session wrote, and gating on a guess
        # would sweep in decks that belong to someone else. Gate nothing.
        return []
    # 1. paths named in the transcript, kept only if the session actually wrote them
    if transcript_path and Path(transcript_path).exists():
        text = read_transcript(transcript_path) if text is None else text
        for m in PPTX_PATH_RE.finditer(text):
            raw = m.group(0).strip().replace("\\\\", "\\")
            p = Path(raw)
            if not p.is_absolute():
                p = cwd / p
            if p.exists() and p.is_file() and not excluded(p, cwd) and written_since(p, since):
                found[str(p.resolve())] = p.resolve()
    # 2. anything under cwd written since the session started
    for p in _walk_pptx(cwd):
        if excluded(p, cwd):
            continue
        if written_since(p, since):
            found[str(p.resolve())] = p.resolve()
    return sorted(found.values())


def gate(paths: list[Path], session_id: str, out) -> int:
    """Run qc_check on paths. Returns the exit code for the hook."""
    sys.path.insert(0, str(HERE))
    import qc_check  # noqa: E402

    # Same resolution the consultant's own run uses: QC_RULES, else the repo default. Set QC_RULES in
    # .claude/settings.json env for an engagement and both gates read one rule set.
    rules = qc_check.load_rules(None)
    rp = qc_check.rules_path(None)
    if rp != qc_check.DEFAULT_RULES_PATH:
        out("qc gate: rules from %s" % rp)
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
    gated = st.setdefault("gated", {})
    # render step: on Windows with PowerPoint, a body page whose text is taller than its box blocks too.
    # Runs once per (path, mtime); a deck that has not changed since its last clean render is not re-exported.
    if sys.platform == "win32" and not os.environ.get("QC_GATE_NO_RENDER"):
        rendered = st.setdefault("rendered", {})
        for p in paths:
            if p in blocked:
                continue
            try:
                stamp = str(int(p.stat().st_mtime))
            except OSError:
                continue
            if rendered.get(str(p)) == stamp:
                continue
            try:
                r = subprocess.run([sys.executable, str(HERE / "render_check.py"), str(p), "--out", str(p.parent / ("render_" + p.stem))],
                                   capture_output=True, text=True, timeout=RENDER_TIMEOUT)
            except subprocess.TimeoutExpired:
                out("qc gate: render check timed out on %s after %ds; not blocking on it" % (p.name, RENDER_TIMEOUT))
                continue
            except Exception as exc:  # noqa: BLE001
                out("qc gate: render check skipped for %s (%s)" % (p.name, exc))
                continue
            if r.returncode == 1:
                lines = [ln for ln in r.stdout.splitlines() if ln.startswith("OVERFLOW")]
                blocked[p] = [qc_check.Finding("render-overflow", "block", None, None, None, ln[:200],
                                               "PowerPoint measures text taller than its box; look at the PNG", "resize", False)
                              for ln in lines[:20]]
            elif r.returncode == 0:
                rendered[str(p)] = stamp
                out("qc gate: rendered %s, no text overflow; PNGs in %s" % (p.name, p.parent / ("render_" + p.stem)))
            elif "PPTBUSY" in r.stdout:
                out("qc gate: render check skipped for %s, PowerPoint has unsaved changes open or "
                    "the deck itself is open in it; save or close that presentation and the next "
                    "write will render" % p.name)
    for p in paths:
        if p in blocked:
            gated.pop(str(p), None)  # always re-gate a file that is still blocking
            continue
        try:
            gated[str(p)] = p.stat().st_mtime
        except OSError:
            pass
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
    text = read_transcript(payload.get("transcript_path"))
    since = session_start(payload.get("transcript_path"), text)
    paths = find_candidates(cwd, payload.get("transcript_path"), since, text)
    session_id = payload.get("session_id", "")
    gated = load_state(state_path(session_id)).get("gated", {})
    keep = []
    for p in paths:
        if unchanged_since_last_gate(p, gated):
            continue  # gated clean at an earlier Stop and not written since
        if is_template(p):
            out("qc gate: skipped %s (template, not a deck)" % p.name)
            continue
        keep.append(p)
    if not keep:
        return 0
    return gate(keep, session_id, out)


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
