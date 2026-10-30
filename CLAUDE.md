# telesto-deck-skills

- Skills live in `.claude/skills/`. The repo is the source of truth; the team gets them as the telesto-deck-workflow plugin, built with `scripts/build_plugin.py` (bump `VERSION` first) and published to the org plugin library. `scripts/publish_skills.py` only diffs the repo against account copies.
- Never commit client decks or client templates; they live outside the repo, one folder per paper (`draft-deck/references/template-contract.md`). Telesto's own template may sit in `tests/fixtures/` while the repo is private. Client names are fine in skill files and examples; the stakeholder names in `qc_rules.json` `client_names` are people and stay in a local copy. `tests/fixtures/` holds the Telesto template and internal fixtures only; the repo stays private or local.
- A template meets the template contract: `qc_check.py TEMPLATE.pptx --template` exits 0. List local templates in `tests/fixtures/client/templates.json` (gitignored) so `pytest tests/` checks them; bump `template_contract_version` in `qc_rules.json` with any contract change.
- Run `pytest tests/` before committing a `SKILL.md` change. Interpreter: `.venv/Scripts/python` (Windows) or `.venv/bin/python`.
- Generated PPTX files must have an empty author field at hand-back; `qc_check.py --handback` blocks on it (mid-session it warns), and the Stop hook in `.claude/settings.json` runs the gate on every PPTX written in a session that used draft-deck or deck-qc (cap: 3 blocked stops; `QC_GATE_ALWAYS=1` gates every session).
- Fonts 10pt or larger except footnotes (8pt floor). Small tables from shapes; a native table is fine for a large table or a heatmap.
- Units are slides and pages, never beats.
- Scratch files go in the session scratchpad, never inside this OneDrive-synced folder.
- Layer 2 of deck-qc runs in the `deck-evaluator` subagent after the gate passes: "Use the deck-evaluator subagent on OUT.pptx."
- Data rules in `GOVERNANCE.md`: read only attached or engagement-folder files; write only what was asked for, where it was asked for (never modify an attached source, metadata included); no client content in skill files, rule files, tests or memory; one engagement per session.
