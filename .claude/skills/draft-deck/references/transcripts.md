# Meeting transcripts: one read, an ask register, then the ordinary machinery

A recording of an internal or client meeting is an **instruction source**, not evidence. It carries asks — reword this, add a recommendation, move that page up, change the colour — and it usually explains what a written comment left implicit. A research interview or focus group transcript is the other thing entirely: evidence, quoted and cited under the ordinary rules. Decide which kind is in front of you before reading, and say which in one line.

Nothing from a meeting recording reaches a slide. Not a phrase, not a claim, not a number spoken aloud. A figure someone says in a meeting is not a source; language rule 4 governs, so it becomes a placeholder or a held comment, never a cited figure.

## Read it once

The transcript is read in full exactly once, and the register below is what the rest of the session works from. Do not re-read it to check a detail; the register carries a verbatim anchor for every row, and if a row is disputed, that one passage is the only thing reopened. For a long recording, extract the text to the scratchpad once and work from the extract.

## Segment first, extract second

Meetings run one subject, then the next. Before extracting anything, mark the topic boundaries in time order and name each segment in a line. Every register row then carries its segment.

Only rows in the segment matching the deck in hand are carried forward. Rows from other segments are counted and named — "nine asks in the AI minipack segment, five in the pipeline review, not carried" — and dropped. They are never merged, never guessed at, and never applied to a deck they were not about. Mixing two projects' asks is the failure this step exists to prevent, and a segment column is the whole cost of preventing it.

Discarding happens at extraction, and it is what keeps one engagement per session intact. The other segments are counted and named so the consultant knows they were heard, and nothing else from them goes anywhere: not into the register, not into the ledger, not into the deck, not into a later session. The recording is read once in one session and does not travel; the register is the handoff artifact, already filtered to one deck and already stripped of what should not be extracted. A second engagement passing through the read is transient, and it is the only exposure the rule cannot remove.

Where a segment boundary is genuinely unclear, say so and put the ambiguous stretch to the consultant rather than assigning it.

## The register

One table, shown in chat, not written to a file. Columns:

**segment · speaker role · verbatim anchor · target · ask · class**

- **Speaker role**, not name: "CEO", "client marketing lead", "the analyst". A name appears only where the authority behind the ask changes how it resolves.
- **Verbatim anchor**: the short line that produced the ask, quoted. **No quote, no row.** An ask that cannot be anchored to a sentence someone actually said does not exist and is not recorded.
- **Target**: the slide and element the ask lands on, or `unassigned` where the room did not say. An unassigned ask is put to the consultant, never placed by inference.
- **Class**: the five existing classes — mechanical, judgment, ambiguous, scope, label. No new vocabulary, and `references/comment-shorthand.md` governs spoken shorthand exactly as it governs written shorthand.

**Last word wins.** When the room revisits an element and changes its mind ("actually, leave it"), one row survives and records that it superseded an earlier ask, so the consultant can see the reversal rather than both instructions.

**The register is confirmed in text before anything is applied.** The consultant reads it, strikes what is wrong and fills in what is unassigned. This is the same confirmation step the storyline and the titles get, and it is the check that catches a misheard or misattributed ask before it reaches a slide.

## Reconciling with comments already on the deck

Where a deck carries in-file comments too, extract those first (`deck-qc/scripts/pptx_comments.py`), then match each register row to an open comment that plainly names the same slide and element.

- A matched pair keeps the comment as the anchor and its single ledger row; the transcript supplies the intent. This is where the recording earns its keep: an *ambiguous* written comment with a spoken explanation beside it is usually a *judgment* or *mechanical* one, and resolves without a pop-up.
- An unmatched register row becomes its own ledger row, sourced `transcript`.
- Where the two conflict, the recording is later and governs; the log says so in the resolution column.

## What is not extracted

The register holds asks and their anchors. It does not hold the rest of the meeting. Nothing about a named person's performance, standing or relationships; no pricing, margins, fees or staffing; no personal information; no client gossip or legal exposure. Where an ask is entangled with that material, the ask is recorded stripped of it and the anchor quote is trimmed to the instruction.

A meeting transcript is client engagement data or Telesto internal data, or both at once. It lives in the session and the engagement folder and nowhere else: not a skill file, not the house register, not the client brief, not memory. `GOVERNANCE.md` governs.
