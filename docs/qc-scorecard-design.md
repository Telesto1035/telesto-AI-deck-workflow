# QC bot (deck-qc) — design spec (rev 3, 2026-09-11)

Status: design agreed 9/11; skill `deck-qc` v1 proposed the same day. Consultant-run self-check, not a gate. No engineering build required; it runs as a Claude skill on the PPTX.

Rev 3 changes: hanging-word check added to Layer 1; Layer 2 now applies proposed changes on approval and flags (rather than guesses) where the right change depends on data or client context the bot does not have.

## What it is for
The equivalent of a grammar checker for decks. A deck goes through three or four revisions, often written by different AI models. The bot catches the mechanical and logical errors early so the partner read is about narrative, storyline and client context only, and the deck arrives with numbers, footnotes and terms she can take straight into the room. Target: 80% or more of errors caught before partner review.

What AI catches well: missing referents, undefined terms, numbers that do not reconcile across pages or to source, footnotes missing or misnumbered, placeholders left in, text that overflows or hangs, pages arguing two different things, conclusions that do not follow from the exhibit on the page, title chains that break. What it does not judge: visual excellence, client context, whether the storyline is the right one.

The bot is a separate skill from draft-deck on purpose. A generator grading its own output defeats the check; running QC in a different session or model from the one that drafted is preferred.

## Inputs
- **The PPTX** (required). The bot reads the file; it does not care which model wrote it.
- **The Build Brief** (optional, strongly preferred). Supplies deck type, package, audience, the one-line takeaway, value at stake, storyline lines. Enables the brief-to-deck check: does the deck deliver the takeaway, are the storyline lines present, is the value at stake on the page.
- **Source files** (optional): crosstabs, survey export, model workbook, quote repository. Enables number tracing to source rather than only cross-page consistency.
- **Prior version** (optional). Enables a diff: what changed, whether earlier flags were fixed, whether a fix regressed something.
- **Prior shipped deck for the client** (optional). Enables the claims-precedent check.

## Mode awareness, so a proposal is not faulted for lacking charts
The bot loads a profile from the deck type (from the brief, or inferred from the file and stated in the header). The profile sets what is required, what is not applicable, and the expected length.

| Type | Required | Not applicable | Length |
|---|---|---|---|
| Findings / survey report | Exec summary linked to body pages; methodology with n and margin of error; source and n under every exhibit; question wording in footnotes; recommendation on each finding page | Priced options | 10-25 |
| Proposal / BD | Takeaway on cover; value at stake in dollars, labelled illustrative with assumptions; priced options with outcome lines; recommended option marked; path with dates; cost of waiting quantified | Methodology page; footnote density; chart count | 4-7 |
| Kickoff | Scope, timeline with dates, roles with owners, first two weeks | Financial value at stake; exhibits | 5-8 |
| Minipack | Takeaway; evidence sourced; what changes | Exec summary; methodology | 3-6 |
| Presentation | As parent type; closing decision page | Footnote density on the page (may sit in appendix) | 8-15 |
| Update | Against-plan status; decisions needed; dates and owners | Financial value at stake; exhibits | 3-6 |
| Workshop | Agenda; prompts on exercise pages; capture pages present | Recommendations; value at stake; sourced exhibits | 6-12 |

Package 2 shortens the findings profile and adds a product hand-off page check. Package 3 uses the proposal profile in product-led form. Financial value at stake is scored only where the profile requires it; elsewhere it reports N/A and the overall reflects three dimensions.

## How the bot inspects
Extract every string with page and shape (python-pptx: runs, table cells, chart caches, notes, comments, author field). Render every page (soffice to PDF, pdftoppm to images) because overflow, cut-off text, hanging words, overlaps and palette drift are visible in the image and invisible in the XML. Build a number ledger and a term ledger. Read the title chain as one text before reading any body.

## Two layers of checks

### Layer 1: mechanical, deterministic, offered as FIX
Each finding names the page, quotes the offending text, and states the fix. The consultant approves in batch or by item; the bot applies and re-runs.
- **Numbers reconcile.** The same metric with different values across pages; exec summary figure vs body page figure; chart data vs its label or title; components that do not sum to the total (rounding of one point allowed and noted); a percentage inconsistent with its stated n; a figure absent from the attached source file.
- **Sources and footnotes.** An exhibit with no source line or no n; footnote numbers out of sequence, duplicated or orphaned; a survey question cited without its wording where the type requires it; a second question used as a caveat without a citation; two questions on one page not each labelled.
- **Referents and terms.** "This", "these", "the above", or a pronoun with no antecedent on the page; an acronym used before it is defined; the same thing named two ways (AMC vs academic medical center, the two 2026 surveys by their agreed names); a department or agency abbreviated on a slide; the client stakeholder named on a slide.
- **Leftovers.** [PLACEHOLDER], TBD, XX, template text, lorem, unresolved comments, hidden slides, DRAFT stamp state inconsistent with the version, author field populated.
- **Text and shape mechanics.** Text overflowing its box or cut off; empty text boxes; orphan shapes off-canvas; more than one font size inside a table; numeric labels inside bar segments.
- **Hanging words** (added rev 3). A text box whose last line carries one or two short words with empty space beside them, spotted in the render. Fix in order: widen or nudge the text box where the layout has room; else rewrite a few words to pull the orphan up without changing meaning. Both offered where both are possible; the rewrite waits for approval because it touches wording.
- **Style drift between pages**, the signature of multi-model drafting: title font or size changing mid-deck, eyebrow numbering skipping or restarting, footer or page number missing on some pages, colour palette departing from the template, a different recommendation-band treatment on one page.

### Layer 2: logic and language, judgment, offered as SUGGEST, then applied on approval
Each finding names the page, states the problem, and proposes the change. On approval the bot applies it. Where the right change depends on data or context the bot does not have (which of two figures is correct, what the source says, what the client cares about), it marks the item QUESTION with the question stated and does not guess (rev 3).
- **Title chain.** Read every action title in sequence. Does the argument hold end to end? Is a page missing that explains a concept, carries a transition, or breaks down a framework the next page assumes? Do two titles say different things about the same fact?
- **Exec summary to body.** Every summary point has a body page; every body page traces to a summary point; the numbers agree.
- **Conclusion follows exhibit.** Does the recommendation band on a page follow from the exhibit on that page? Does the title claim more than the exhibit shows?
- **Claim sizing.** A single data point with "proves" or "confirms"; a subgroup finding promoted to the whole; a totalizing word ("every", "never") on single-survey data; a claim beyond the client's precedent where a prior deck is attached.
- **Outcome clarity.** Can a reader state the one takeaway and the decision after the titles alone? Is there a closing decision or next-step page where the profile requires one?
- **Value at stake.** Present, in dollars, with assumptions and source, where the profile requires it; labelled illustrative where projected.
- **Voice.** The draft-deck word list and Tier 1 patterns: negative parallelism, participle riders, urgency framing, importance puffery, label-colon titles, abstract-noun subjects, prescriptive titles, sharp verbs about named firms. Proposed rewrite supplied and applied on approval. A voice fix never alters a number.
- **Portability test.** A title that could move to another client's deck unchanged is flagged as not yet a finding, with a specific version proposed where the exhibit supports one.

## Scoring: four dimensions, 1 to 5, per deck
The score is the summary; the flag lists are the product.

| Score | Clarity of outcome and recommendation | Logical flow | Financial value at stake | Technical accuracy |
|---|---|---|---|---|
| 5 | One takeaway on the cover; every title asserts; a closing decision page; the reader knows what to decide | Title chain reads as one argument; no gaps; exec summary and body map one to one | Dollar impact stated, sourced, assumptions shown, and tied to the recommendation | Every figure traced to a source; all totals reconcile; footnotes complete; no leftovers |
| 4 | Takeaway clear; one or two titles are labels; decision page present | One soft transition or one page out of order | Dollar impact stated and sourced; assumptions partly shown | One unsourced figure or one footnote gap |
| 3 | Takeaway present but must be inferred from several pages; no decision page | One missing page or one contradiction between pages | Dollar impact stated without source or assumptions | Two to four unsourced figures or one reconciliation failure |
| 2 | Several label titles; the reader cannot say what to decide | Two or more contradictions or two missing pages | Value at stake implied but never quantified | Multiple reconciliation failures; placeholders present |
| 1 | No discernible takeaway | Pages do not connect | Absent where required | Figures cannot be traced; the deck cannot go to a partner |

Technical accuracy below 3 is flagged in the report header regardless of the overall, since a single wrong number in front of MDs is the failure the bot exists to prevent.

## Report format
1. **Header:** deck type and package (from the brief, or inferred and said so), pages, version, and the one line the reader should act on first. Technical accuracy warning here if below 3.
2. **Scorecard:** four dimensions with the score and a one-line reason each; N/A where the profile says so.
3. **Fix list:** numbered, page-referenced, quoted text, stated fix. Ends with apply all, apply selected, or skip.
4. **Suggest list:** numbered, page-referenced, problem, proposed change. Items needing data or client context marked QUESTION.
5. **Brief check** (when the brief is attached): takeaway delivered or not; storyline lines present or missing; value at stake on the page or not.
6. **Diff** (when a prior version is attached): what changed, which earlier flags closed, any regressions.
7. **Not checked:** visual excellence, client context, whether the storyline is the right one. Stated every time so no one mistakes a 5 for a finished deck.

## Actions
- **Fix** applies mechanical changes the consultant approved, then re-scores and shows the delta.
- **Suggest** hands the consultant the proposed text; on approval the bot applies it. Where the change depends on data or context the bot does not have, it asks instead of applying.
- A number changes only when the source says what it should be. Two disagreeing pages and no source: the bot asks which is right.
- Edits at run level so mixed formatting survives; chart caches patched in XML, never via replace_data; validate against the original, re-render, save as a new version with the author field empty.
- Re-run is expected between revisions; the diff makes the cycle visible.

## Out of scope by design
Visual judgment, storyline judgment, client context, blocking. The partner supplies the first three; nothing blocks.

## Next
Cold test on a live Huron deliverable: run deck-qc on a draft before partner review, count flags the partner would have raised versus flags she raised anyway, and measure the rewrite rate against the 80% target. Anchors may need tightening after the first three runs.
