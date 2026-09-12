# Telesto deck workflow: one-page manual

*What it is.* A set of Claude skills and one code gate that take a consultant's prompt and client context to a partner-ready first draft, then resolve the partner's comments. The skills are the instructions; the gate is a script that blocks a deck with mechanical faults; the evaluator is a second Claude that reads the deck cold.

## The chain

1. **Context.** Give Claude the prompt, the client files (survey export, crosstabs, transcripts, prior decks) and the meeting roster. Ask for `stakeholder-context` if you want the room mapped to questions first. A one-page Build Brief (`onepagebrief-builder`) is optional; ask for it when the package includes a product or engineer time.
2. **Build.** "Draft the deck" or "build the findings report" triggers `draft-deck`. It infers package, deck type and paper, shows the page plan as one title per line, then builds from a template or prior shipped deck. It never builds a file without one.
3. **Gate.** In Claude Code the Stop hook runs `qc_check.py` on every PPTX the session wrote and will not let the turn end while blocking findings remain: author field set, speaker notes, generator fingerprints, text below 10pt outside footnotes, italics, placeholders, footnote markers without footnotes, totals that do not sum, chart labels that disagree with cached data. Three blocked stops and it hands off with the findings attached. In Cowork the `deck-qc` skill asks for the same checks by hand.
4. **Evaluate.** "Use the deck-evaluator subagent on OUT.pptx." It applies deck-qc Layer 2 in a fresh context: skeleton against the deck type, title chain, exec summary to body, conclusion follows exhibit, claim sizing, voice, portability. It scores four dimensions 1 to 5 and returns suggestions. It never edits the file. Anything that needs data or client context comes back marked QUESTION.
5. **Review.** The partner comments in PowerPoint, as usual. "Resolve these comments" triggers `draft-deck` Revise, which reads the comments from the file, executes mechanical ones, proposes options for judgment ones, and returns a before-and-after log.
6. **Ship, then learn.** After shipping, `scripts/deck_diff.py DRAFT.pptx SHIPPED.pptx` lists every edit by class (number, structure, storyline, style). `draft-deck` Learn turns repeated edits into proposed skill patterns; nothing enters a skill without approval.

## What the workflow is for

Two things. First, every draft is written for a named room: attach the roster and `stakeholder-context` maps who is there to the questions they need answered, and `draft-deck` orders the storyline around them. Second, revisions run themselves: `draft-deck` Revise reads the partner's comments from the file, executes the mechanical ones, proposes options for the judgment ones, asks only about the ambiguous ones ("make this pop"), and logs every comment to the engagement's revision ledger. Learn reads the ledgers and the shipped diffs and proposes rule changes, including loosening a rule partners no longer want. Every rule lives in a markdown skill or a JSON threshold, so any of it can be changed by hand when minds change.

## Commands (repo root, Claude Code users)

```
.venv/Scripts/python .claude/skills/deck-qc/scripts/qc_check.py DECK.pptx            # findings table, exit 1 if blocked
.venv/Scripts/python .claude/skills/deck-qc/scripts/qc_check.py DECK.pptx --fix-safe # writes DECK.qc.pptx with settled fixes only
.venv/Scripts/python scripts/deck_diff.py BEFORE.pptx AFTER.pptx --md diff.md        # what changed between versions
.venv/Scripts/python -m pytest tests/                                                  # before committing a SKILL.md change
```

`--fix-safe` clears author and metadata, strips speaker notes after printing them, removes generator strings, curls straight quote marks and splits semicolon runs in table cells. It never changes a number, a size, a typeface or wording; italics are left for the author to decide.

## Rules of the house the gate enforces

Empty author field. Nothing below 10pt except footnotes, which stop at 8pt. Italics only as rare exceptions: a few are listed, more than four in a deck blocks. Grey text outside footnotes in a colour that is not in the palette is listed for the author, never blocked. The test behind both rules: title, body or footnote carries everything a reader needs in a five-second scan. No `[PLACEHOLDER]`, `TBD` or `XX` left in. Every footnote marker has its footnote on the same slide. Components sum to their stated total within one point. No client stakeholder named on a slide. Small tables are text boxes and horizontal lines, not the native table (warned). Text boxes zero-margin and top-anchored, section subtitles bold 14 or 16pt with a rule beneath (listed as information). Units are slides and pages.

## Machine setup

Python 3.11+ with the repo venv (`pip install -r requirements.txt`). For the render checks the skills ask for (overflow, hanging words, overlaps) install LibreOffice (`soffice`) and poppler (`pdftoppm`); without them the skills fall back to XML checks and say so.

## Per-engagement setup

Copy `qc_rules.json` locally, fill `client_names` with the stakeholders who must not appear on a slide and set `active_client_palette`, and pass it with `--rules`. Never commit the copy. Client decks live in `tests/fixtures/client/`, which git ignores.

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
