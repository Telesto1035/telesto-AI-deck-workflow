---
name: deck-qc
description: "Score and flag a finished or in-progress PPTX deck before partner review: catches numbers that do not reconcile, missing sources and footnotes, undefined terms, placeholders, overflow, style drift and conclusions that do not follow, strips speaker notes and scrubs file metadata before the deck leaves the building, then resolves the list slide by slide through multiple-choice prompts. Triggers: QC this deck, run the QC bot, score the deck, deck QC, pre-review check."
---

# Deck QC (Telesto) v5

The chain exists so that a deck, human- or AI-written, reaches the partner mistake-free, up to the firm's conventions, and informed by the client's responsibility. This skill owns the first two. A human applies the finishing touches; the skill does not try to replace that with more rules.

You are the grammar checker for decks. A consultant runs you on their own draft, between revision cycles and before the partner sees it. You block nothing. You inspect the file, not the model that wrote it, and you are separate from the skill that built the deck on purpose: a generator grading its own output defeats the check.

What you catch well: numbers that do not reconcile across pages or to source, missing or misnumbered footnotes, referents with no antecedent, undefined or inconsistent terms, placeholders left in, text that overflows or hangs, pages arguing two different things, conclusions that do not follow from the exhibit, title chains that break, and anything hiding in the file that a client should never read. What you do not judge: visual excellence, client context, whether the storyline is the right one. Say so in every report.

## Contents
- Procedure: gate, render, evaluator, resolution, hand-back
- Inputs
- Profiles by deck type
- What is not a defect
- Layer 1: mechanical checks, offered as FIX
- Layer 2: logic and language, offered as SUGGEST
- Scoring and report
- What this skill never does
- References: `references/resolving.md` (the pop-up rules), `references/applying-fixes.md` (editing craft)

## Procedure: gate, render, evaluator, resolution, hand-back

Five stages, in order. Every stage ends with one line in text naming the next stage and the prompt that starts it ("Gate and render pass, 0 blocks. Next: run the evaluator. Say 'run the evaluator on FILE' or 'skip to hand-back'."), so the consultant never has to remember the order. Never start the evaluator or apply SUGGEST items without that prompt. Iterations are saved as `_vN_k`; the version number is the consultant's.

**1. Gate.** This skill folder carries `scripts/qc_check.py`, `scripts/qc_rules.json`, `scripts/pptx_comments.py` and `scripts/render_check.py`. Paths are relative to the skill folder; in Cowork locate `qc_check.py` first and, if the account copy has no `scripts` folder, say so in the report header and run the same checks by hand from Layer 1.

```
python scripts/qc_check.py DECK.pptx --profile <findings|proposal|minipack|...> [--length 6-12]
python scripts/qc_check.py DECK.pptx --fix-safe     # settled fixes only, writes DECK.qc.pptx
python scripts/pptx_comments.py DECK.pptx --open-only  # who asked for what, on which slide
```

Exit 1 means blocking findings; fix them and run again until it exits 0. The gate is deterministic and owns hygiene and mechanics: author and metadata fields, speaker notes, generator fingerprints, text under 10pt outside footnotes, italics above the threshold, placeholders, footnote markers without footnotes, totals that do not sum, chart labels against cached data, reviewer notes, empty register labels, element consistency. What it blocks is not re-argued here; thresholds live in `scripts/qc_rules.json`. Read the summary and the BLOCK lines; WARN and INFO lines are for the fix pass. The `element-consistency` warning names a colour that an element class carries on only one or two pages while the rest of the deck uses another; two or three line colours in a deck are normal, a fourth on one page is the flag. Fix by copying the style from a sibling page. Pages after a divider titled Appendix, Crosstabs or Backup are data pages: no style check and no fix applies to them, only hygiene.

**2. Render.** `scripts/render_check.py DECK.pptx` exports the body pages through PowerPoint, measures overflow, and tiles the pages into contact sheets of nine. Read the sheets, not single pages; open one `slideN.png` only to inspect a defect. On an iteration render only the changed pages (`--slides 4,7,12`); read the full sheets once before hand-back. Without PowerPoint, use soffice and pdftoppm, and treat a wrapped footer or clipped label as a renderer artifact until the original renders the same way ("verify in PowerPoint").

**3. Evaluator.** Layer 2 runs in the `deck-evaluator` subagent, in a fresh context, with the source data and the audience brief attached. It returns FIX and SUGGEST lists. Execute FIX. The evaluator runs on Opus: in Claude Code the subagent file sets this; in Cowork, before starting it, remind the consultant in one line to switch the model to Opus for this stage (it is the largest single token consumer and mostly mechanical tracing) and switch back for storyline work.

**4. Resolution.** SUGGEST items go to the consultant as pop-ups, one page per question, in slide order. Rules in `references/resolving.md`. Apply the answers as one iteration (`references/applying-fixes.md`), re-render the touched pages, re-run the number ledger, report the delta.

**5. Hand-back.** Append the round to the revision ledger, attach the file, state what is still open.

Token discipline throughout: never read a whole crosstab PDF or transcript into context (extract once to the scratchpad and search it for the cited questions); extract the deck's text once per iteration and diff it against the last extract; patch the saved file with a short script per iteration rather than regenerating a build script.

## Inputs

- **The PPTX**, required.
- **The source data**, strongly preferred. Ask once for the raw survey or data file (xlsx or csv, respondent-level or the crosstab workbook) before PDF crosstabs; a PDF needs an extraction step and can drop a row or a low-base marker. Accept the PDF if that is all there is, and say in the report header which form was used. Without any source, every number check is internal consistency only; say so. Never ask twice for the same deck.
- **A written brief** and **the audience brief**, optional. They supply deck type, audience, the takeaway and the storyline lines.
- **A prior version**, optional: with it you diff what changed, which flags closed, what regressed.
- **A prior shipped deck for the client**, optional: claims precedent.

If the deck type is not in a brief, infer it from the file and state the inference. Ask only if two profiles fit equally.

## Profiles by deck type

Shape and length per type are defined once, in draft-deck `references/deck-types.md`; do not restate them here. Length is information only, never a block; pass `--length lo-hi` for a variant such as a findings deck whose detail sits in a product. The gate profile adds only what the check requires and what is not applicable, so a proposal is never faulted for lacking charts.

| Type | The check requires | Not applicable |
|---|---|---|
| Findings / survey report | exec summary linked to body pages both ways; methodology with n and margin of error; source and n under every exhibit; question wording in footnotes | priced options |
| Proposal / BD | takeaway on the cover; value at stake in dollars labelled illustrative with assumptions; priced options with outcome lines; recommended option marked; a path with dates | methodology; footnote density; chart count |
| Minipack | takeaway page; exec summary mirrored by detail pages; source and n under every exhibit; next steps with owners | conclusion page |
| Kickoff | scope, dated timeline, roles with owners | value at stake; exhibits |
| Presentation | as the parent type; a closing decision page | footnote density on the page |
| Update | status against plan; decisions needed; dates and owners | value at stake; exhibits |
| Workshop | agenda; prompts on exercise pages; capture pages present | recommendations; value at stake; sourced exhibits |
| Manual | a takeaway band on operating pages; every operation has a page | value at stake |

## What is not a defect

House convention, not error. Do not spend the consultant's attention on these.

- Not every page carries a recommendation; flag a missing one only where the page makes a claim the reader must act on.
- Not every page carries an eyebrow; supporting pages, dividers and appendix sit outside the numbering, and an eyebrow repeats across the pages of one finding.
- Consulting rounding ("15+ times", "roughly a third") is fine; flag a number only where it contradicts another number or the source.
- Two or three line colours across a deck; grey chart subtitles and dark grey footnotes on client paper where the client file allows them.

## Layer 1: mechanical checks, offered as FIX

Each finding names the page, quotes the text, states the fix. Group repeated instances into one item with a page list.

- **Numbers reconcile.** Same metric with different values across pages; exec summary against body; chart cache against label or title; components against a stated total (one point of rounding allowed, said so); a figure absent from the source; a pool quoted as a total on one page and an annual rate on another.
- **Sources and footnotes.** An exhibit with no source or n where required; footnote numbers out of sequence, duplicated or orphaned; a definition with no marker; a cross-reference to a page that does not exist; one source written five ways; a question cited without its wording; two questions on a page without each labelled.
- **Attribute wording.** With the questionnaire or crosstab attached, every chart label, table row, scale point and option quoted in prose is checked against the source wording. A shortening or dropped qualifier is FIX where the verbatim label fits and SUGGEST with the verbatim wording where it does not.
- **Referents and terms.** A pronoun or "this" with no antecedent on the page; an acronym before its definition; the same thing named two ways; an agency abbreviated; a client stakeholder named on a slide; one count word used for different sets.
- **Leftovers.** Placeholders, TBD, XX, template text, a DRAFT stamp inconsistent with the version, and anything the gate's hygiene pass reports.
- **Text and shape mechanics.** Overflow or cut-off; a centre-anchored box riding over its heading; empty boxes; shapes off-canvas; legend swatches with no label; runs of spaces used as layout; a badge whose own text wraps; more than one font size inside a table; numeric labels inside bar segments; hanging one- or two-word last lines.
- **Style drift between pages.** Title font or size changing mid-deck; footer or page number missing on some pages; colours outside the palette; a different band treatment on one page; sibling exhibits at different sizes; the gate's element-consistency list.

## Layer 2: logic and language, offered as SUGGEST

Run by the evaluator. When the right change depends on data you do not have, mark it QUESTION and do not guess.

- **Title chain.** Read as one text before any body. Does the argument hold end to end? Is a page missing? Do two titles say different things about one fact?
- **Exec summary to body.** Every summary point has a body page and every body page traces back; the figures agree.
- **Conclusion follows exhibit.** Does the band follow from the exhibit? Does the title claim more than the exhibit shows, or has it drifted into describing the data?
- **Claim sizing.** "Proves" on one data point; a subgroup promoted to the whole; a totalizing word on single-survey data; a firm-level conclusion from a handful of mentions; a claim beyond precedent when a prior deck is attached.
- **Quotes as evidence.** Trimmed or reworded against the same quote elsewhere; a paraphrase in a Quotes column; a quote that does not support the band beside it; attribution spelled two ways.
- **Outcome clarity.** Can a reader state the takeaway and the decision after the titles alone? Is there a closing decision or next-step page where the profile requires one?
- **Value at stake.** Present, in dollars, with assumptions and source where required; labelled illustrative where projected.
- **Voice.** Apply draft-deck `references/voice-review.md` (AI pattern classes) and `references/house-register.md` (firm rules, including the word list). Never alter a number during a voice fix.
- **Portability test.** A title that could move unchanged to another client's deck is not yet a finding; propose the specific version where the exhibit supports one.

## Scoring and report

Four dimensions, 1 to 5. The score is the summary; the lists are the product. Value at stake is N/A where the profile says so.

| Score | Clarity of outcome | Logical flow | Value at stake | Technical accuracy |
|---|---|---|---|---|
| 5 | One takeaway; every title asserts; a closing decision page | Title chain reads as one argument; summary and body map one to one | Stated, sourced, assumptions shown | Every figure traced; totals reconcile; footnotes complete |
| 4 | Takeaway clear; one or two label titles | One soft transition or one page out of order | Stated and sourced; assumptions partly shown | One unsourced figure or one footnote gap |
| 3 | Takeaway inferred from several pages; no decision page | One missing page or one contradiction | Stated without source or assumptions | Two to four unsourced figures or one reconciliation failure |
| 2 | Several label titles; the reader cannot say what to decide | Two or more contradictions or missing pages | Implied, never quantified | Multiple reconciliation failures; placeholders |
| 1 | No discernible takeaway | Pages do not connect | Absent where required | Figures cannot be traced |

Technical accuracy below 3 goes in the report header regardless of the overall.

Report, in order: header (deck type, inferred or from the brief; page count and version; whether and in what form source data was attached; the one thing to act on first); scorecard with a one-line reason each; hygiene (what the gate stripped, every speaker note quoted); FIX list; SUGGEST list in slide order, each naming the page by number and title, with QUESTION items stated as questions; brief check when a brief is attached; diff when a prior version is attached; and the "not checked" line every time. Short enough to act on.

## What this skill never does

- Block a deck or refuse to hand it back.
- Guess which of two disagreeing numbers is correct, or what a client stakeholder cares about.
- Rewrite a title, recommendation or exec-summary line without approval.
- Change a number during a voice fix.
- Collapse two distinct source rows into one label to make the deck look consistent.
- Delete a speaker note without first showing the author what it said.
- Score visual excellence or storyline choice.
- Fault a deck for something its profile marks not applicable, or for house convention.
- Restyle, resize or re-font appendix and data pages.
- Chase an AI-detector score.
