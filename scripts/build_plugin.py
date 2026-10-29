#!/usr/bin/env python3
"""build_plugin.py: assemble the Telesto deck workflow as one Claude plugin, for Claude Code and Cowork alike.

Usage:
    python scripts/build_plugin.py            # writes dist/telesto-deck-workflow/ and dist/telesto-deck-workflow.zip

The repo's .claude/ folder stays the development copy (tests and the Stop hook point at it). This script copies
skills/, agents/ and the Stop hook into a plugin directory with a .claude-plugin/plugin.json manifest, so one
bundle carries every SKILL.md, reference file and script. Cowork's per-skill "save proposal" path writes SKILL.md
only, which is how scripts and references went missing on the account side; the plugin is the fix.

Install:
    Claude Code (test):  claude --plugin-dir dist/telesto-deck-workflow
    Claude Code (team):  add the repo as a plugin marketplace, or install the zip; skills appear as
                         /telesto-deck-workflow:draft-deck and so on
    Cowork:              upload dist/telesto-deck-workflow.zip as a plugin
"""
from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NAME = "telesto-deck-workflow"
OUT = REPO / "dist" / NAME
VERSION_FILE = REPO / "VERSION"


def version() -> str:
    return VERSION_FILE.read_text(encoding="utf-8").strip() if VERSION_FILE.exists() else "1.0.0"


def copy_tree(src: Path, dst: Path) -> None:
    for p in src.rglob("*"):
        if p.is_dir() or "__pycache__" in p.parts or p.suffix == ".pyc":
            continue
        rel = p.relative_to(src)
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst / rel)


def plugin_command(dev_command: str) -> str:
    """The repo's `python .claude/skills/X.py` as a plugin hook. Hook commands run under sh (Git Bash on
    Windows), so the plugin path is quoted (a profile folder with a space splits it otherwise), and the first
    interpreter that runs is used: a Mac often has no `python`, and the Windows Store `python3` stub exits 9009.
    With none, the hook exits 0 so no teammate's turn shows a hook error."""
    script = dev_command.split(".claude/skills/", 1)[1]
    target = '"${CLAUDE_PLUGIN_ROOT}/skills/%s"' % script
    return ('for py in python3 python py; do "$py" -c "" >/dev/null 2>&1 && exec "$py" %s; done; exit 0' % target)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / ".claude-plugin").mkdir(parents=True)
    manifest = {
        "name": NAME,
        "description": "Telesto's deck workflow: draft-deck (build, revise, learn), deck-qc (code gate, render, evaluator), stakeholder-context (audience brief). One bundle with every reference file and script.",
        "version": version(),
        "author": {"name": "Telesto Strategy"},
    }
    (OUT / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    copy_tree(REPO / ".claude" / "skills", OUT / "skills")
    copy_tree(REPO / ".claude" / "agents", OUT / "agents")
    # the Stop hook, with the path resolved against the plugin root wherever it is installed
    settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    hooks = settings.get("hooks", {})
    for event in hooks.values():
        for entry in event:
            for h in entry.get("hooks", []):
                h["command"] = plugin_command(h["command"])
    (OUT / "hooks").mkdir()
    (OUT / "hooks" / "hooks.json").write_text(json.dumps({"hooks": hooks}, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(REPO / "GOVERNANCE.md", OUT / "GOVERNANCE.md")
    (OUT / "README.md").write_text(
        "# %s\n\nTelesto's deck workflow as one plugin: skills, the evaluator agent, the Stop hook and every script.\n\n"
        "Skills: draft-deck, deck-qc, stakeholder-context. Agent: deck-evaluator. Data rules: GOVERNANCE.md.\n\n"
        "Built from the telesto-deck-skills repo by scripts/build_plugin.py; edit there, not here.\n" % NAME,
        encoding="utf-8",
    )
    zpath = REPO / "dist" / (NAME + ".zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(OUT.parent))
    n = sum(1 for p in OUT.rglob("*") if p.is_file())
    print("plugin %s v%s: %d files -> %s" % (NAME, version(), n, zpath))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
