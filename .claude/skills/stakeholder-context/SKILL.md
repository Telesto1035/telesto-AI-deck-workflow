---
name: stakeholder-context
description: "Turn a meeting roster into the audience brief that draft-deck reads: who is in the room, the one or two primaries, the questions each person needs answered, and a map from each question to the data or exhibit that answers it. Triggers: stakeholder context, audience brief, who is in the room, roster to brief, prep the audience for this deck."
---

# Stakeholder Context (Telesto) — v1.1

v1.1, 2026-09-13: research on the primaries' remit is now required, not forbidden. A brief that does not know what the primary is paid to do produces generic recommendations downstream.

You produce the audience brief that `draft-deck` accepts as an optional input. It shapes the executive summary order (the sponsor's question first), the open-discussion page (one prompt per unanswered question), and the depth of any page a named function will scrutinise. It never puts a stakeholder's name on a slide, and neither do you.

## Inputs

- **The roster**, required: names, titles, organisations, and where known each person's role in the decision (sponsor, approver, user, forwarder). A calendar invite, an email thread or a typed list all work.
- **The meeting purpose**, one line: what the room decides or discusses.
- **The Build Brief or the prompt** for the deck, optional. With it you map questions to the storyline lines and evidence already planned.
- **The evidence inventory**, optional: the files draft-deck will build from (survey export, crosstabs, transcripts, model). With it the question-to-data map names exhibits; without it, it names gaps.

Ask once for a missing roster.

## Research the remit of the primaries

For each primary, and for any attendee whose title is ambiguous, establish what the person is tasked to do before writing their questions. A title alone is not enough: an "Industry Marketing Manager" may own channel mix, paid media, conference presence and thought-leadership topics, and if so every one of those is a question the deck must answer. Sources, in order:

1. The client's own job descriptions for the role, open or filled, on its careers site or job boards; they list responsibilities and budgets in the client's words.
2. The person's public profile (LinkedIn headline and role summary, company bio page, conference speaker bios).
3. Recent public statements or posts on the deck's topic.

Record the remit as three to six concrete responsibilities ("places paid media", "chooses conference sponsorships", "commissions thought leadership"), with the source. Do not research conflicts, risk, compensation or private life; the remit and the public record on the topic are the whole scope. Where nothing can be found, say "remit unknown, inferred from title" so the consultant can fill it.

The remit sets the depth of the downstream recommendation. A person who places ads wants channel mix and named conferences; a practice leader wants service implications. State the depth you recommend ("name two conferences" or "prioritise conference presence") and let the consultant adjust it.

## What you produce

One markdown block, short enough to read in a minute, in this order:

1. **The room.** A table: person, title, organisation, role in the decision, remit (three to six responsibilities, sourced), what they read first (finance reads value math, operations reads the timeline, a board member reads titles only).
2. **Primaries.** One or two people whose question the deck must answer first, with one line on why each. A sponsor outranks a forwarder; an approver outranks a user.
3. **Questions.** For each person, the one to three questions they need answered to act, derived from the remit. Written as the person would ask them, not as topics: a marketing manager who owns paid media asks "which channels and which conferences", not "what are the marketing implications".
4. **Question-to-data map.** A table: question, who asks it, the data or exhibit that answers it (from the inventory or the brief), and `GAP` where nothing in the inputs answers it. Gaps become open-discussion prompts or `[PLACEHOLDER: source needed]` in the draft.
5. **Handoff line.** "Attach this as the audience brief to draft-deck Build." Names appear here and nowhere on a slide.

## What this skill never does

- Research beyond the remit: no conflicts, risk, compensation or private life. For a full background primer on an individual before a call, the `expert-primer` skill exists.
- Put a stakeholder's name, quote or preference on a slide, or into slide text handed to draft-deck.
- Invent a question the title does not support; where a role is unclear, say "role unknown" and ask.
- Rank the room by seniority alone. The primary is the person whose decision the deck exists to move.

## Next stage

The audience brief is an input to `draft-deck`. Close with one line: "Audience brief saved as FILE. Next: build or revise the deck with it attached. Say 'draft the deck from BRIEF and DATA' or 'revise DECK with the audience brief'."
