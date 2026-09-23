# telesto-deck-skills

- Skills live in `.claude/skills/`. The repo is the source of truth; account (Cowork) copies are published from here with `scripts/publish_skills.py`.
- Never commit client decks or the Telesto template. Client names are fine in skill files and examples; the stakeholder names in `qc_rules.json` `client_names` are people and stay in a local copy. `tests/fixtures/` holds the template and internal fixtures only; the repo stays private or local.
- Run `pytest tests/` before committing a `SKILL.md` change. Interpreter: `.venv/Scripts/python` (Windows) or `.venv/bin/python`.
- Generated PPTX files must have an empty author field; `qc_check.py` enforces it, and the Stop hook in `.claude/settings.json` runs the gate on every PPTX written in a session (cap: 3 blocked stops).
- Fonts 10pt or larger except footnotes (8pt floor). Small tables from shapes; a native table is fine for a large table or a heatmap.
- Units are slides and pages, never beats.
- Scratch files go in the session scratchpad, never inside this OneDrive-synced folder.
- Layer 2 of deck-qc runs in the `deck-evaluator` subagent after the gate passes: "Use the deck-evaluator subagent on OUT.pptx."
- Data rules in `GOVERNANCE.md`: read only attached or engagement-folder files; write only what was asked for, where it was asked for (never modify an attached source, metadata included); no client content in skill files, rule files, tests or memory; one engagement per session.
