# Deck workflow and skill chain (2026-09-12)

## Chain
stakeholder-context (optional, from roster) -> draft-deck (Build) -> deck-qc (consultant self-check, separate session) -> partner comments in PPTX -> draft-deck (Revise) -> ship -> draft-deck (Learn) against the shipped version.

The Build Brief (onepagebrief-builder) is a branch, not a gate: required when the package includes a product or engineer time; skipped for short decks. Decided 9/12 given short timelines and the CEO's limited review hours. Manual P4 will be revised when the manual is written, after the skills and workflow are tested.

## Skills and status
| Skill | Version | Status |
|---|---|---|
| onepagebrief-builder | v1 | saved; brief optional per above |
| draft-deck | v2.2 proposed 9/12 (v2.1 saved) | v2.2 adds: stakeholder context input, brief optional, Revise reads legacy and modern PPTX comments, Learn mode, typography floor (v2.1), minipack fixed shape (v2.1) |
| deck-qc | v1 proposed 9/11 | grammar checker; Layer 1 FIX incl. hanging words; Layer 2 SUGGEST then fix on approval, QUESTION when data or context is missing |
| stakeholder-context | v1 proposed 9/12 | roster -> room, 1-2 primaries, questions, question-to-data map; no conflicts or risk research |

## Interface changes agreed
- Fixes move from prompts to PowerPoint comments; Revise resolves them and returns a before/after log.
- CEO style: Learn mode diffs the last AI draft against the shipped deck and proposes patterns for the rewrite table; nothing added without approval.
- Reference files (deck-types.md) must be copied into the skill folder by hand.

## Measure
Prompts per deck from first draft to ship, counted on the next two decks. Mechanical prompts should fall to near zero; if not, log the missed flags as skill defects.
