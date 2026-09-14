# telesto-deck-skills

Telesto's agentic PPT workflow: the skills, the code gate, the hook and the evaluator that turn a prompt and files into a partner-ready deck. Spec: `docs/HANDOFF.md`. Start with the chart, `docs/telesto_deck_chain.png`: it is the visual readme of the chain and is updated whenever the workflow changes (edit the HTML beside it and re-render). One-page manual: `docs/team-manual.md`.


Install: `python scripts/build_plugin.py` builds `dist/telesto-deck-workflow.zip`, one plugin with skills, references, scripts, agent and hook, for Cowork and Claude Code alike.

Data governance: `GOVERNANCE.md` (data classes, what the skills may read, client statements, items for counsel).

## The chain

stakeholder-context (agent) → draft-deck (router, then generator) → **qc_check.py** (code gate, loops back to the generator until clean, cap 3) → deck-evaluator subagent (deck-qc Layer 2, fresh context) → human comments in the PPTX → draft-deck Revise → ship → draft-deck Learn.


## Layout

```
.claude/
  settings.json                 Stop hook runs the gate on every PPTX written in the session
  agents/deck-evaluator.md      Layer 2 evaluator, fresh context, never edits the file
  skills/
    draft-deck/                 SKILL.md v2.2 + references/
    deck-qc/                    SKILL.md v4 + scripts/qc_check.py, qc_rules.json, qc_gate_hook.py
    stakeholder-context/        SKILL.md v1 (rebuilt from docs/workflow-and-skills.md; review before publishing)
docs/                           handoff, QC design, workflow notes, chain chart
scripts/publish_skills.py       diff repo skills against the account (Cowork) copies
tests/
  fixtures/                     clean fixtures; make_broken.py writes broken variants to fixtures/broken/
  test_qc_check.py, test_qc_gate_hook.py
```

## Run

```
.venv/Scripts/python .claude/skills/deck-qc/scripts/qc_check.py DECK.pptx [--json out.json] [--fix-safe] [--profile findings]
.venv/Scripts/python -m pytest tests/
.venv/Scripts/python tests/make_broken.py
.venv/Scripts/python scripts/publish_skills.py --account-dir "PATH/TO/synced/skills"
```

Exit codes for `qc_check.py`: 0 pass, 1 blocking findings, 2 file could not be opened. `--fix-safe` writes `DECK.qc.pptx` beside the input and never changes a number, a size or wording.

## Team setup (Claude Code users)

1. Get access to the private GitHub repo and clone it.
2. From the repo root create the venv and install: `python -m venv .venv` then `.venv/Scripts/pip install -r requirements.txt` (`.venv/bin/pip` on Mac).
3. Open the folder in Claude Code. The Stop hook, the `deck-evaluator` subagent and the skills load from `.claude/` automatically; approve the project hook when prompted.
4. Client decks stay local under `tests/fixtures/client/` (gitignored). Real client names go in a local copy of `qc_rules.json` passed with `--rules`, never committed.

Cowork users get the skills only, published from this repo; the hook and the subagent run in Claude Code.

## Status (2026-09-12)

Steps 1 to 4 of `docs/HANDOFF.md` section 10 are built and tested. Step 5 has run on the EDR minipack and the public sector findings deck (local copies under `tests/fixtures/client/`); the gate was calibrated on them and the evaluator cold-read the findings deck (notes in `docs/client/`, gitignored). Step 5 still needs an AI draft that precedes the consultant edits to learn the polish step itself. Step 6's publish is a click in Cowork; the diff script is here. Step 7 is measurement on the next two live decks.
