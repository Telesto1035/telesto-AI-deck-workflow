# Telesto deck workflow: one-page manual

*What it is.* A set of Claude skills and one code gate that take a consultant's prompt and client context to a partner-ready first draft, then resolve the partner's comments. The skills are the instructions; the gate is a script that blocks a deck with mechanical faults; the evaluator is a second Claude that reads the deck cold.

## The chain

2. **Build.** "Draft the deck" or "build the findings report" triggers `draft-deck`. It confirms the deck type and the audience by pop-up, then shows the page plan as one title per line, then builds from a template or prior shipped deck. It never builds a file without one.
3. **Gate.** In Claude Code the Stop hook runs `qc_check.py` on every PPTX the session wrote and will not let the turn end while blocking findings remain: author field set, speaker notes, generator fingerprints, text below 10pt outside footnotes, placeholders, footnote markers without footnotes, totals that do not sum, chart labels that disagree with cached data. Three blocked stops and it hands off with the findings attached. In Cowork the `deck-qc` skill asks for the same checks by hand.
4. **Evaluate.** "Use the deck-evaluator subagent on OUT.pptx." It applies deck-qc Layer 2 in a fresh context: skeleton against the deck type, title chain, exec summary to body, conclusion follows exhibit, claim sizing, language, portability. It scores four dimensions 1 to 5 and returns suggestions. Voice is not scored: the standard is professional consulting writing, and what is checked is grammar, machine phrasing and the conventions a reader outside the firm could apply. It never edits the file. Anything that needs data or client context comes back marked QUESTION.
5. **Review.** The partner comments in PowerPoint, as usual. "Resolve these comments" triggers `draft-deck` Revise, which reads the comments from the file (`pptx_comments.py`), executes mechanical ones, proposes options for judgment ones, and returns a before-and-after log built from `deck_diff.py --comments`. A deck can join here without having gone through steps 1 to 4: a human-built draft with the CEO's comments on it is a valid starting point.
6. **Ship, then learn.** After shipping, `deck-qc/scripts/deck_diff.py DRAFT.pptx SHIPPED.pptx` lists every edit by class (number, structure, storyline, style). `draft-deck` Learn turns repeated edits into proposed skill patterns; nothing enters a skill without approval.

## What the AI phase builds

Three things per slide, and nothing else until the storyline has settled: the title and message (is this the right claim for this room and what can we realistically recommend), the exhibit that shows the data, and the recommendation (what this changes or informs). Callouts, colors and polish are a human's afterward. The storyline is always confirmed in text, one line per page, before a file is built or rebuilt.

## What the workflow is for

Two things. First, every draft is written for a named room: attach the roster and `stakeholder-context` maps who is there to the questions they need answered, and `draft-deck` orders the storyline around them. Second, revisions run themselves: `draft-deck` Revise reads the partner's comments from the file, executes the mechanical ones, proposes options for the judgment ones, asks only about the ambiguous ones ("make this pop"), and logs every comment to the engagement's revision ledger. Learn reads the ledgers and the shipped diffs and proposes rule changes, including loosening a rule partners no longer want. Every rule lives in a markdown skill or a JSON threshold, so any of it can be changed by hand when minds change.

## Decks that arrive mid-stream

A human-built deck can enter at Revise with no brief. draft-deck offers once to run stakeholder-context if you have the roster; say yes or no and it proceeds. Reviewer shorthand ("more strategic", "so what", "roll up", "sharpen", "fix", "this doesn't work") is never interpreted on its own: each raises a pop-up with two or three readings and the change each would make, and only your choice is applied. The list lives in `draft-deck/references/comment-shorthand.md`.

## Installing the workflow

One bundle carries everything: `dist/telesto-deck-workflow.zip`, built by `scripts/build_plugin.py`. It holds the three skills with their reference files and scripts, the evaluator agent and the Stop hook.

- **Cowork:** upload the zip as a plugin. Do not use the per-skill "save proposal" card for these skills: it writes SKILL.md alone and drops the scripts and references the skills call.
- **Claude Code:** `claude --plugin-dir dist/telesto-deck-workflow` to try it, or install the zip; skills appear as `/telesto-deck-workflow:draft-deck` and so on. Working inside this repo needs no install: the `.claude/` folder is the development copy.

Bump `VERSION` when a change should reach the team; the manifest reads it.

## Data rules

`GOVERNANCE.md` at the repo root: what the skills may read (only what you attach), where client data may live (the engagement folder, never a skill file or memory), what you may tell a client about AI use, and what counsel should confirm. Run client work on the firm's commercial Claude account only, with chat rating turned off.

## Rules that learn without growing

Writing conventions learned from shipped decks live in `draft-deck/references/house-register.md`, capped at 25 and entered only after a pattern recurs in two decks or the CEO rules. The file splits them: enforceable conventions, which a check may cite, and Preferences, which are house habit and no check may cite. Client formatting and voice live in `draft-deck/references/clients/<client>.md`, which never holds engagement content. Learn proposes at most three changes per pass; nothing enters without approval.

## Never remember the next step

Every stage (build or revision, gate and render, evaluator, SUGGEST pop-ups) ends with one line naming the next stage and the words that start it. Answer that line and the deck moves on; say "skip" or "stop here" to leave it.

## Commands (repo root, Claude Code users)

```
.venv/Scripts/python .claude/skills/deck-qc/scripts/qc_check.py DECK.pptx            # findings table, exit 1 if blocked
.venv/Scripts/python .claude/skills/deck-qc/scripts/qc_check.py DECK.pptx --fix-safe # writes DECK.qc.pptx with settled fixes only
.venv/Scripts/python scripts/deck_diff.py BEFORE.pptx AFTER.pptx --md diff.md        # what changed between versions
.venv/Scripts/python scripts/deck_diff.py BEFORE.pptx AFTER.pptx --comments --ledger-rows   # each reviewer comment next to what changed on its slide, plus ledger rows
.venv/Scripts/python .claude/skills/deck-qc/scripts/pptx_comments.py DECK.pptx       # the reviewer comments in a deck, by slide; --resolve all marks them done
.venv/Scripts/python -m pytest tests/                                                  # before committing a SKILL.md change
```

`--fix-safe` does two things: it strips speaker notes after printing them, and it removes generator fingerprint strings. That is all. It never edits slide text, formatting, a number, a size or a typeface, and it leaves document properties alone for Document Inspector. Anything that rewrites what you wrote goes through the fix pass, where you see it first.

## Rules of the house the gate enforces

Empty author field. Nothing below 10pt except footnotes, which stop at 8pt. Gray text outside footnotes in a color that is not in the palette is listed for the author, never blocked. The test behind it: title, body or footnote carries everything a reader needs in a five-second scan. No `[PLACEHOLDER]`, `TBD` or `XX` left in. Every footnote marker has its footnote on the same slide. Components sum to their stated total within one point. No client stakeholder named on a slide. Body pages stay under 200 words of title, body and chart labels (warned, never blocked); footnotes counted apart, appendix and quote pages exempt. Units are slides and pages.

## Seeing the page

On Windows with PowerPoint installed, `render_check.py DECK.pptx` exports every body page to PNG and lists text that is taller than its box, measured by PowerPoint. The Stop hook runs it and blocks the turn on overflow, so a Claude Code build cannot hand over an unrendered deck. Claude looks at the PNGs before handing a deck over; so should you. Cowork has LibreOffice in its sandbox and renders through that route; a machine with neither PowerPoint nor LibreOffice cannot run the render step. Appendix and crosstab pages are left alone by both the AI phase and the gate.

## Machine setup

Python 3.11+ with the repo venv (`pip install -r requirements.txt`). For the render checks the skills ask for (overflow, hanging words, overlaps) install LibreOffice (`soffice`) and poppler (`pdftoppm`); without them the skills fall back to XML checks and say so.

## Per-engagement setup

Copy `qc_rules.json` locally, fill `client_names` with the stakeholders who must not appear on a slide, and pass it with `--rules`. Set `QC_RULES` to that copy in `.claude/settings.json` `env` as well, so the Stop gate reads the same file: without it the gate runs on the repo default and its `client_names` list is empty, and one deck gets two answers. Brand colours need no setting: the gate reads them from the client template's own theme part, including a `custClrLst` palette. Set `active_client_palette` only to override the typeface allowlist for an engagement. Never commit the copy. Client decks live in `tests/fixtures/client/`, which git ignores.

## Where things live

Skills: `.claude/skills/<name>/SKILL.md`, the source of truth; Cowork copies are published from here (`scripts/publish_skills.py` shows what is stale). Gate: `.claude/skills/deck-qc/scripts/`. Hook: `.claude/settings.json`. Evaluator: `.claude/agents/deck-evaluator.md`. Spec and design notes: `docs/`.

## What the tools do not do

Judge visual excellence, client context or whether the storyline is right. Guess which of two disagreeing numbers is correct. Rewrite a title or recommendation without approval. Those stay with the consultant and the partner.

## Terms, in plain words

- **Repository (repo).** A folder whose full history git keeps in a hidden `.git` subfolder. Ours is `telesto-deck-skills`.
- **Commit.** A saved snapshot of the whole folder with a short message saying what changed. Nothing is in the history until it is committed.
- **Remote.** A copy of the repository on a server, here a private GitHub repository. It is the backup and the thing teammates copy from.
- **Push / pull.** Push uploads your new commits to the remote; pull downloads commits others made.
- **Clone.** Copying the remote to a new machine for the first time. After that, pull.
- **Branch.** A named line of work. Ours is `main`; ignore branches until you want to experiment.
- **.gitignore.** A list of paths git never records. Client decks and the venv are on it.
- **venv.** A private copy of Python with this project's libraries installed, in `.venv/`, so the tools run the same on every machine.
- **Hook.** A script Claude Code runs automatically at a moment you choose. Ours runs the gate when Claude tries to end its turn.
- **Subagent.** A second Claude with its own fresh memory, given one job. The evaluator is one, so it reads the deck without having written it.
- **Skill.** A markdown instruction file (`SKILL.md`) that Claude loads when a task matches its description.
