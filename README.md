# telesto-deck-skills

Telesto's agentic PPT workflow: the skills, the code gate, the hook and the evaluator that turn a prompt and files into a partner-ready deck. Start with the chart, `docs/telesto_deck_chain.png`: it is the visual readme of the chain and is updated whenever the workflow changes (edit the HTML beside it and re-render). The consultant's path: `docs/team-manual.md`. Why the chain is shaped this way: `docs/workflow-and-skills.md`.

Install: `python scripts/build_plugin.py` builds `dist/telesto-deck-workflow.zip`, one plugin with skills, references, scripts, agent and hook, for Cowork and Claude Code alike. Bump `VERSION` when a change should reach the team.

Data governance: `GOVERNANCE.md` (data classes, what the skills may read, client statements, items for counsel).

## The chain

stakeholder-context (audience brief) → draft-deck (storyline in text, then build) → **qc_check.py** (code gate, loops back to the generator until clean, cap 3) → render (`render_check.py`, contact sheets) → deck-evaluator subagent (deck-qc Layer 2, fresh context) → FIX executed, SUGGEST by pop-up → human comments in the PPTX → draft-deck Revise → ship → draft-deck Learn.

## Layout

```
.claude/
  settings.json                 Stop hook runs the gate on every PPTX written in the session
  agents/deck-evaluator.md      Layer 2 evaluator, fresh context, never edits the file
  skills/
    draft-deck/                 SKILL.md + references/ (language rules, house register, client files, build rules, deck types)
    deck-qc/                    SKILL.md + references/ + scripts/
                                  qc_check.py, qc_rules.json   the gate and its thresholds
                                  qc_gate_hook.py              the Stop hook
                                  render_check.py              PowerPoint export, overflow, contact sheets
                                  pptx_comments.py             reviewer comments by slide; --resolve
                                  deck_diff.py                 version diff, comments joined to changes, ledger rows
    stakeholder-context/        SKILL.md
docs/                           team manual, workflow decisions, chain chart; archive/ holds superseded specs
manual/                         the Telesto Standard 2.0 manual: spec, storyline, build_manual.py
scripts/
  build_plugin.py               builds the plugin in dist/
  publish_skills.py             diffs repo skills against account (Cowork) copies; it cannot publish
  deck_diff.py                  shim for tests; use the deck-qc copy
tests/
  fixtures/                     clean fixtures; make_broken.py writes broken variants to fixtures/broken/
  test_*.py
```

## Run

```
.venv/Scripts/python .claude/skills/deck-qc/scripts/qc_check.py DECK.pptx [--json out.json] [--fix-safe] [--profile findings] [--handback]
.venv/Scripts/python .claude/skills/deck-qc/scripts/render_check.py DECK.pptx [--slides 4,7]
.venv/Scripts/python -m pytest tests/
.venv/Scripts/python tests/make_broken.py
.venv/Scripts/python scripts/build_plugin.py
```

Exit codes for `qc_check.py`: 0 pass, 1 blocking findings, 2 file could not be opened. `--fix-safe` writes `DECK.qc.pptx` beside the input; it strips speaker notes and generator fingerprints and never changes a number, a size or wording. `--handback` makes document properties block; run it after Document Inspector.

## Team setup (Claude Code users)

1. Get access to the private GitHub repo and clone it.
2. From the repo root create the venv and install: `python -m venv .venv` then `.venv/Scripts/pip install -r requirements.txt` (`.venv/bin/pip` on Mac).
3. Open the folder in Claude Code. The Stop hook, the `deck-evaluator` subagent and the skills load from `.claude/` automatically; approve the project hook when prompted.
4. Client decks stay local under `tests/fixtures/client/` (gitignored). Stakeholder names for the `client_names` check go in a local copy of `qc_rules.json`, passed with `--rules` and set as `QC_RULES` so the Stop gate reads it too. Client names themselves are fine in skill files.

Plugin users on Claude Code need Python 3.11+ and `python -m pip install python-pptx lxml` once per machine; without it the Stop hook tells the user the gate did not run. Cowork users install the plugin zip; the Stop hook and the subagent run in Claude Code, and in Cowork the skill runs the gate by instruction.

## Status

The version is in `VERSION`; what changed is in git. Open decisions are listed at the end of `docs/workflow-and-skills.md`.
