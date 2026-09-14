---
name: deck-chain
description: "Walk a PPTX through the Telesto workflow with a pop-up at every stage: gate, render, evaluator, slide-by-slide SUGGEST resolution, ledger. Use so the consultant never has to remember the next step. Triggers: run the chain, take this deck through the workflow, next step on this deck, what is left on this deck, also whenever draft-deck finishes a build or revision."
---

# Deck chain (Telesto) v1

You drive a deck through the workflow one stage at a time and ask, with the AskUserQuestion tool, before every stage. The consultant answers pop-ups; they never have to remember what comes next. draft-deck hands over to this skill the moment a build or revision is saved.

## Stages, in order

1. **Gate.** Run `deck-qc/scripts/qc_check.py DECK --profile <type>`. Execute FIX items (`--fix-safe`, then the remaining blocks that have one correct answer) as an iteration `_vN_k`. Report the block count, word-count warnings and any `element-consistency` warnings.
2. **Render.** Run `deck-qc/scripts/render_check.py` (PowerPoint on Windows) or the soffice route; look at every body page for overflow, collisions and pages that differ in colour or line style from their neighbours; fix as the same iteration.
3. **Evaluator.** Run the `deck-evaluator` subagent with the crosstabs and the audience brief attached. Report scores and the FIX count; execute FIX items.
4. **SUGGEST resolution.** Pop-ups in slide order, one page per question, page number and title named, current and proposed line quoted, "leave as drafted" always offered. Apply the accepted items as one iteration; log accepted and rejected.
5. **Ledger and hand-back.** Append the round to `docs/client/revision-ledger.md`; attach the file; state what is still open.

## The pop-up between stages

After each stage, one AskUserQuestion: what was just done in one line, then the options "Run <next stage> (Recommended)", "Skip to <the stage after>", "Stop here". Never run the evaluator or apply SUGGEST items without that answer. Never bump the version number; iterations only (see draft-deck, Versioning).

## When a consultant edit comes back

Diff it against the last AI iteration (`scripts/deck_diff.py`), write the Learn pass into the draft-deck references, then start again from the gate on the new file.
