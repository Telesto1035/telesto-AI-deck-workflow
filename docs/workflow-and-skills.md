# Workflow decisions

Why the chain is shaped the way it is. Each entry is a call that was made, the constraint behind it, and what it ruled out — the part a diff cannot show. What the chain *does* is in the skill files and `team-manual.md` (the consultant's path); the original build spec is `archive/HANDOFF.md`, superseded; this file does not restate either, and nothing here should need editing when a skill's version changes.

## The chain, for orientation only

`stakeholder-context` (optional, from a roster) → `draft-deck` Build → the gate (`qc_check.py`, plus the Stop hook) → the render → the `deck-evaluator` subagent → resolution by pop-up → hand-back → partner comments in the PPTX → `draft-deck` Revise → ship → `draft-deck` Learn against the shipped version.

Stages, prompts and exit codes: `deck-qc/SKILL.md`, "Procedure". Versions live in each skill's own header.

## Decisions

**A deck can enter at any stage** (9/12). A human-built draft, a deck already carrying the CEO's comments, a v6 a colleague edited by hand — nothing upstream is required. The alternative, a pipeline with a mandatory front door, would have meant refusing the decks that most need checking.

**Fixes come back as PowerPoint comments, not prompts** (9/12). Reviewers mark the file; Revise resolves each and returns a before/after log. Describing fixes in chat loses the slide they belong to and cannot be audited afterwards.

**The evaluator classes every item FIX, SUGGEST or QUESTION** (9/12, extended 9/15). FIX has one correct answer and is executed without asking. SUGGEST is the consultant's call and is never applied unasked — titles, recommendation bands and exec-summary lines are always SUGGEST. QUESTION is for what depends on data or client context the evaluator does not have, including a claim that reaches past its exhibit: the gap is visible, whether other evidence closes it is not.

**The builder does not grade its own output** (9/12). Layer 2 runs in a subagent with a fresh context. A generator scoring its own deck defeats the check, which is the whole reason the chain has two skills rather than one.

**Learn proposes at most three rule changes per engagement, none applied without approval** (9/13, capped 9/14). A single edit is an observation, not a rule; promotion into the house register needs the pattern in two decks or a ruling. Without the cap the register grows faster than anyone reads it, and an unread rule file is a rule file that gets ignored wholesale.

**stakeholder-context researches the primaries' remit** (9/13). Reversed from v1, which forbade it. A brief that does not know what the primary is paid to do produces generic recommendations downstream. Scope is the public record on the topic and nothing else — no conflicts, compensation, risk or private life.

**The register is a test, not a word list** (9/13, scored 9/15, score retired 9/15). "Would a consultant write this in an email to the CEO?" The named phrases are examples; the recurring failure they miss is an abstraction handed a verb a person should own. The test stands as a drafting aid. It stopped being a score the same day it became one.

**Voice is not scored; the standard is professional consulting writing** (9/15). The register dimension is retired and the scorecard is four dimensions. Mimicking how one firm writes is a moving target: it needs an owner ruling on every new rule and re-ruling as taste shifts, and it cannot be applied at all by a team the skills are shared with, who have never read a Telesto deck. Grammar, machine phrasing and logic across titles survive as unscored items, because any professional reader applies those the same way. `house-register.md` now splits its rules in two: enforceable conventions, which pass an outside-reader test and a check may cite, and Preferences, which are house habit and no check may cite. The command-verb recommendation rule moved to Preferences, which is where the evaluator's inverted finding came from in the first place. What is left unsolved: a rule entered from one CEO edit still sits at the same weight as one distilled from a dozen decks, and at 13 conventions the cap of 25 is pressuring nothing out.

**Token economy is a design constraint, not an optimization** (9/13). Contact sheets at nine pages per image, render only the pages an iteration changed, grep crosstab extracts rather than reading PDFs into context. The evaluator is the largest single consumer in the chain and it is mostly mechanical tracing.

**onepagebrief-builder is retired** (9/14). The Build Brief is a one-slide artifact the gate recognizes as a profile, not a separate skill with its own step. Build opens instead with a pop-up round confirming deck type, audience and materials.

**Nothing client-specific lives in a rule file** (9/14). Names, figures, palettes and findings are engagement data; rule files, the register, the client style file, tests and memory stay clean of them. A test enforces it. Client brand colours are read from the template's own theme part, which is a better source than a copied hex list anyway.

**Attachment is permission to read, not to write** (9/14). A skill writes only the deliverable it was asked for, at a path the consultant named. It never writes back to a source file, metadata included.

**Document properties are a hand-back condition, not a draft defect** (9/14). PowerPoint restamps them on every save, so blocking mid-session interrupts the consultant over something that is not yet wrong. They block under `--handback` only. The scrub belongs to PowerPoint's Document Inspector, run by a human; the gate verifies it was run rather than doing it.

**The Stop gate blocks, the skills do not** (9/14). deck-qc blocks nothing on its own — it reports and the consultant decides. Enforcement lives in the hook, which is the thing Cowork cannot do, and it gates only decks this session wrote, only once per version, with a cap of three blocked stops so the loop always terminates.

**The Stop gate does not render** (9/14). Exporting a deck through PowerPoint costs minutes and repeats what stage 2 just did by hand. Opt-in behind an env var.

**render_check never closes a presentation the consultant is working in** (9/14). PowerPoint is a single-instance COM server: attaching and quitting would shut their windows and lose unsaved work. The guard refuses and retries on the next write rather than risking it.

**One rule set for both gates** (9/15). `QC_RULES` points the Stop gate at the same engagement copy the consultant passes with `--rules`. Before it, the enforced gate ran on defaults with an empty `client_names` — two answers on one deck, and the weaker one was the one that blocked.

## Open

- Ownership of shipped work: marked open for the CEO in `GOVERNANCE.md`, with a suggested contract position.
