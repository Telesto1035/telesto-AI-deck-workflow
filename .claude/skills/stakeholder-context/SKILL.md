---
name: stakeholder-context
description: "Turn a meeting roster into the audience brief that draft-deck reads: who is in the room, the one or two primaries, the questions each person needs answered, and a map from each question to the data or exhibit that answers it. Triggers: stakeholder context, audience brief, who is in the room, roster to brief, prep the audience for this deck."
---

# Stakeholder Context (Telesto) — v1

Rebuilt 2026-09-12 from `docs/workflow-and-skills.md`; the Cowork proposal card of 9/12 was never saved. Review before publishing to the account.

You produce the audience brief that `draft-deck` accepts as an optional input. It shapes the executive summary order (the sponsor's question first), the open-discussion page (one prompt per unanswered question), and the depth of any page a named function will scrutinise. It never puts a stakeholder's name on a slide, and neither do you.

## Inputs

- **The roster**, required: names, titles, organisations, and where known each person's role in the decision (sponsor, approver, user, forwarder). A calendar invite, an email thread or a typed list all work.
- **The meeting purpose**, one line: what the room decides or discusses.
- **The Build Brief or the prompt** for the deck, optional. With it you map questions to the storyline lines and evidence already planned.
- **The evidence inventory**, optional: the files draft-deck will build from (survey export, crosstabs, transcripts, model). With it the question-to-data map names exhibits; without it, it names gaps.

Ask once for a missing roster. Everything else you infer from titles and say so.

## What you produce

One markdown block, short enough to read in a minute, in this order:

1. **The room.** A table: person, title, organisation, role in the decision, what they read first (finance reads value math, operations reads the timeline, a board member reads titles only).
2. **Primaries.** One or two people whose question the deck must answer first, with one line on why each. A sponsor outranks a forwarder; an approver outranks a user.
3. **Questions.** For each person, the one to three questions they need answered to act. Written as the person would ask them, not as topics.
4. **Question-to-data map.** A table: question, who asks it, the data or exhibit that answers it (from the inventory or the brief), and `GAP` where nothing in the inputs answers it. Gaps become open-discussion prompts or `[PLACEHOLDER: source needed]` in the draft.
5. **Handoff line.** "Attach this as the audience brief to draft-deck Build." Names appear here and nowhere on a slide.

## What this skill never does

- Research individuals: no conflicts, risk, background, press or LinkedIn work. Titles and roles come from the roster as given. For a named individual's background before a call, the `expert-primer` skill exists.
- Put a stakeholder's name, quote or preference on a slide, or into slide text handed to draft-deck.
- Invent a question the title does not support; where a role is unclear, say "role unknown" and ask.
- Rank the room by seniority alone. The primary is the person whose decision the deck exists to move.
