# Deck types — routing and build spec for draft-deck v2 (2026-09-12, rev 3)

Reference files cannot be added through the skill proposal card, so a compact version goes inline in SKILL.md and this is the full spec. Copy into the skill folder as `references/deck-types.md`.

Rev 3: minipack given a fixed shape (summary of four points, four matching detail pages, conclusion and open discussion, next steps); typography floor noted; audience brief added as an optional input.

## The invariant, before any routing
Every Telesto deck produces a call to action or a discussion, supported by statistics, quotes or data visualization, and it works at two reading speeds: the title chain alone delivers the message on a phone in 20 seconds; the charts, tables and footnotes hold up to a 30-minute read. Both tests apply to every type. Density is not a style choice; it is set by the deck type and by each page's job.

## Typography floor, every type and paper
Nothing below 10pt except a footnote. Italics and grey detail text only as rare exceptions (the gate blocks above four per deck); quotes are set roman in quotation marks. If text must shrink below 10pt to fit, the page carries too much: cut, split, or footnote.

## Routing order
1. **Package** (from the Build Brief, or inferred from the prompt): 1 Services · 2 Services + product · 3 Product.
2. **Deck type** (eight). Under Package 1 the first seven apply. Under Package 2 the first seven apply; proposal, findings report and update change shape (below). Under Package 3 the deck explains, sells or teaches the product: proposal, explainer, update and manual apply; the rest rarely do.
3. **Paper and template** from the mandatory example attachment: dark Telesto, light Telesto, or a client template. Paper sets colours, fonts and furniture only. It does not set density.
4. **Page grammar** chosen per page from the type's archetype palette. Two grammars coexist in one deck: the visual grammar (stat rails, option cards, chevrons, timelines, bands) and the analytical grammar (bar charts, heatmaps, paired bars, stacked scales, shape-built tables, quote pages, sources under every exhibit). A findings deck opens visual and runs analytical; a proposal is visual throughout with an analytical page where a number needs proof.

## Optional input: audience brief
A short list of who is in the room, their titles and responsibilities, and the questions each needs answered, built from the meeting roster by a separate skill. It orders the executive summary (sponsor's question first), writes the open-discussion prompts, and sets the depth of pages a named function will scrutinise. It never puts a stakeholder's name on a slide.

## How each type builds

| Type | Job | Skeleton | Page grammar and density | Length | Register |
|---|---|---|---|---|---|
| **Findings / survey report** | Deliver evidence and what to do about it | Cover with takeaway → exec summary (numbered findings + implications, or a numbered fix list) → methodology → one page per finding: eyebrow number, action title, exhibit(s), recommendation band, source and n → recommendations → appendix pointer | Analytical body: up to two exhibits a page; charts, heatmaps, paired bars, stacked scales, quote pages, matrices; question footnotes and denominators. Visual open and close. Highest density of the seven | 10-25 (services); 6-12 when a product holds the detail | Findings declarative and data-anchored; implications labelled; recommendation band closes each finding page |
| **Proposal / BD** | Obtain the decision to buy | Cover with takeaway as title → stakes (stat rail, value at stake in dollars) → options, three tiers, recommended tier marked visually, outcome line each → path and first 30 days → optional team and terms | Visual throughout: stat callouts, option cards, timeline; a chart only where one number needs proof. Lowest density | 4-7 | Outcome-led; every option priced; value at stake labelled illustrative with assumptions; the brief's SCARF choice honoured on the opening page |
| **Kickoff** | Align on scope, plan and roles | Objectives and success → scope and workstreams → approach and timeline → roles, governance, cadence → first two weeks | Medium: timeline strip, workstream cards, shape-built roles table | 5-8 | Operational; dates and owners on every commitment |
| **Minipack** | Answer one question between milestones | Cover (topic and stake) → callout page with the one-sentence takeaway → exec summary, four numbered findings written as the client's opportunity, each with a one-line implication → detail pages in the same order, one or two per finding sharing the eyebrow number, each closing on a recommendation band → next steps with owners and dates → appendix (backup, headlines, crosstabs; not counted toward length) | One exhibit per detail page: bar chart, stat rail of percentages, shape-built table or heatmap; source and n; recommendation band where the point supports one | 8-11 body pages before the appendix; four findings, one or two pages each | As findings, tighter |
| **Presentation** | Live narrative that still stands alone when forwarded | As findings or proposal, fewer words, larger exhibits, closing decision page | Visual-leaning; exhibits sized for a room | 8-15 | As the parent type |
| **Update** | Status to the sponsor | Where we are against plan → what we learned → decisions needed → next period | Medium: progress strip, status table from shapes | 3-6 | Plain, dated, owner-named |
| **Workshop** | Run a session | Agenda and objectives → framing pages → exercise or discussion pages with prompts → capture templates → close | Frameworks, 2x2s, deliberately empty capture grids | 6-12 | Questions and prompts, not conclusions |
| **Manual / user guide** | Teach a reader to operate a product or a workflow, so that anyone on the team, or at the client, can run it unassisted | Cover → what this replaces and why → orientation (the parts and how they relate) → section divider per part → one page per operation: what you do, what comes back, what you decide → demonstration pages (fixed screenshot frame plus caption) → what is next or in development | Visual first: flow charts ported to native shapes, chevrons for sequence, gate and loop marks, numbered cards; a takeaway band closes every page except cover, dividers, demonstrations and placeholders. One dense reference page allowed, written last | 15-25 | Plain instruction to the operator. No pitch, no recommendation chain. The storyline test is coverage: every operation the reader performs has a page. Client manuals state the gain (time, iterations, cost) with the measure that proves it; internal manuals state the measure and whether it has been counted, never a number that has not been |

## Package variants
- **Manual.** P3 (product) is its home: a client user guide shipped with a live product, or the internal standard that teaches the team the workflow (the Vanguard Standard, Sep 2026). P2 uses the manual as the one "how to use the product" page or a short appendix, not a separate deck.
- **Proposal.** P1: services scope and fees. P2: options include the product component (what it holds, who refreshes it, access); the path shows product launch beside deck milestones. P3: product-led: problem → what the product does → how the client uses it → value → price and pilot terms.
- **Findings report.** P2: cut backup pages, the product answers follow-up cuts; add one page on how to use the product.
- **Update.** P2 and P3: add product usage, refresh status, open access issues.
- **Presentation.** P3 explainer variant, 3-5 pages: problem → what it does → how the client uses it → value → what happens next.
- **Kickoff.** P2 and P3: data access, environments and refresh ownership become a workstream.

## Gaps this spec closed in v1.5
1. Deck type was asked for in setup but changed nothing downstream. Every type inherited one skeleton, so a proposal drew a TOC and a methodology page it should never have.
2. Chart and table rules existed only for Huron client paper. Dark Telesto analytical pages now have their own rules.
3. Density was implied to follow paper (dark = sparse). It follows type and page job.
4. Modes were dot-dash-centric. The Build Brief, or the prompt where no brief exists, is the storyline input.
5. No package routing.
6. The example attachment was treated as optional in text mode; it is mandatory for any file build.

---

# Deck type rules moved from SKILL.md (2026-09-13, text unchanged)

This block and the sections above cover the same ground with small differences in wording. Both are kept until the consultant chooses which wording stands; where they disagree, the SKILL.md wording below was the later-edited one.

## Deck types

Full spec with skeletons and package variants: `references/deck-types.md`. Two types take most of the firm's hours and scrutiny and are specified in detail here; the minipack has a fixed shape; the manual teaches rather than argues; the other four are compact.

### Priority 1: Findings / survey report
The deck that a room of MDs, team leads and directors reads for an hour. It allows no ambiguity, no AI-speak, no unexplained number.

- **Skeleton:** cover with the takeaway as title → executive summary (numbered findings, each a bold finding sentence with the key numbers inline, one to three supporting sentences, and a labelled implication line; or a numbered fix list as in the Re-rebrand deck) → methodology (who, n, how sampled, when, margin of error, which cuts are directional) → one page per finding → recommendations or next steps → appendix pointer.
- **Finding page anatomy:** numbered eyebrow (the finding's number; two pages supporting one finding share it), full-sentence action title, one or two exhibits, a recommendation band closing the page, source and n under every exhibit, question wording verbatim in the footnote.
- **Exhibits:** built from the data files as native charts with editable data. Bar charts and heatmaps wherever many percentages are involved; paired bars for two respondent groups; stacked scales for rating batteries; quote pages with verbatim attributed quotes; shape-built tables with bucket labels in feature boxes on the left. Up to two exhibits a page. No numeric labels inside bar segments. Two questions on one page are each labelled; a second question is never introduced as an unlabelled caveat.
- **Length:** 10 to 25 pages for services; 6 to 12 when a product holds the detail (Package 2). Appendix pages (crosstabs, methodology detail, backup) sit after an Appendix divider and do not count toward length; they are opened only when asked.
- **Register:** findings declarative and data-anchored; implications labelled and separate; the recommendation register below governs every band.
- **Exemplars:** Re-rebrand (dark Telesto), EDR Institution Priorities and Competitive Intelligence (client paper), Diligence Squared for the analytical density a research buyer expects.

### Priority 2: Proposal / BD
New or existing client. It speaks the buyer's language: why now, what problem this solves, what dollars are involved, and what the buyer decides. Urgency is shown as a quantified cost of waiting, never as an imperative.

- **Skeleton:** cover with the takeaway as title and "Prepared for" → where we left off or the stakes (stat rail; value at stake in dollars, labelled illustrative with assumptions) → the problem and why now → options, three tiers, each priced with an outcome line, the recommended tier marked visually → the path (timeline, first 30 days) → optional team and terms.
- **Page grammar:** visual throughout. Stat callouts, option cards, chevrons, timeline, closing band. A chart only where one number needs proof.
- **Length:** 4 to 7 pages.
- **Register:** outcome-led; the brief's SCARF choice honoured on the opening page (credit the client's own direction, let their criteria select the answer). Fees, durations and value-at-stake inputs come from the user or become `[PLACEHOLDER: builder input needed]`.
- **Package variants:** P1 services scope and fees. P2 options include the product component (what it holds, who refreshes it, access) and the path shows product launch beside deck milestones. P3 the proposal is product-led: problem → what the product does → how the client uses it → value → price and pilot terms.
- **Exemplars:** ULSE/TRIP (Aug 2026, 7 pages) and Rotary (Aug 2026, 4 pages), both CEO-approved and the style guide for how a proposal recommends.
- **Exemplar grammar, taken from those two decks.** Cover: a one-sentence takeaway as title, a one-line subtitle naming the engagement, "Prepared for" with name and title, CONFIDENTIAL and the month. Numbered eyebrows carry the spine: 01 THE STAKES (or WHERE WE LEFT OFF when there is prior work) · 02 THE RESPONSE · 03 THE PATH, with WHERE X COULD GO NEXT and THE PROGRAM inserted when the proposal sits inside a longer roadmap. Stakes page: a stat rail of three to four figures per side (the engine vs the leak), each figure with its source in the caption, uncertain ones tagged "(to validate in week 1)", and the value at stake as a range labelled Illustrative with the arithmetic stated. Response page: three options in ascending depth, each as NAME · price · duration, three to five bullets, and a closing line that starts "Outcome:"; the middle option carries the RECOMMENDED marker and a line that sizes the fee against the stakes ("roughly 0.3% of one year's scenario risk"); each option "builds on the last". Path page: dated steps (THIS WEEK, NEXT TWO WEEKS, BY [date]) with named working sessions, THE COST OF WAITING as a quantified panel, and THE FIRST 30 DAYS identical on every option. Urgency appears only as the cost of waiting, never as an imperative.

### Manual / user guide
The deck that teaches a reader to operate a product or a workflow unassisted. It is a Package 3 type: a client user guide shipped with a live product, or the internal standard that teaches the team the workflow. It does not pitch and it does not build a recommendation chain.

- **Skeleton:** cover → what this replaces and why → orientation (the parts and how they relate) → one divider per part → one page per operation, each stating what the reader does, what comes back and what the reader decides → demonstration pages on a fixed screenshot frame with a caption → what is next or in development.
- **Storyline test:** coverage, not argument. List every operation the reader performs and check that each has a page. The title chain still reads top to bottom.
- **Page grammar:** visual first. Flow charts ported to native shapes, chevrons for sequence, gate and loop-back marks, numbered cards. A one-sentence takeaway band closes every page except the cover, dividers, demonstration pages and placeholders. One dense reference page is allowed and is written last.
- **Length:** 15 to 25 pages.
- **Register:** plain instruction to the operator. A client manual states the gain (time, iterations, cost) with the measure that proves it. An internal manual states the measure and whether it has been counted; it never carries a number that has not been.
- **Exemplar:** the Vanguard Standard (Sep 2026, dark Telesto), built with this skill and scored with deck-qc.

### Minipack: fixed shape
The between-milestones deck that answers one question with evidence. Its shape is fixed so a reader who has seen one can read the next without orientation. Revised 2026-09-12 after the EDR AI minipack shipped.

- **Skeleton:** cover with the topic and the stake as title → callout page carrying the one-sentence takeaway in large type → executive summary with four numbered findings, each a bold finding sentence written as the client's opportunity ("Leaders need help with…") with its key numbers and a one-line implication → detail pages in the same order carrying the same eyebrow number, one or two pages per finding, each closing on a recommendation band → next steps with owners and dates → appendix divider, then backup pages, usable headlines and crosstabs, which do not count toward length.
- **Page patterns:** a stat column beside quote cards; two ranked bar charts side by side; a small-multiple matrix of attributes by segment; a quotes page in two themed groups on the side-panel layout; a readiness table with a key-takeaways panel. The side-panel layout is for low-text pages (exec summary, quotes, next steps); exhibit pages stay on the white layout.
- **Length:** 8 to 11 body pages before the appendix.
- **Register:** findings as the client's opportunity; recommendation bands bold the action phrases and carry the client proof the consultant supplies; no conclusion page, the bands and the next steps close the argument.

### The other four, compact
- **Kickoff:** objectives and success → scope and workstreams → approach and timeline → roles, governance, cadence → first two weeks. Medium density; timeline strip, workstream cards, shape-built roles table. 5 to 8 pages. Operational register with dates and owners. P2 and P3 add data access, environments and refresh ownership as a workstream.
- **Presentation:** as findings or proposal with fewer words and larger exhibits, closing on a decision page. 8 to 15 pages. P3 explainer variant, 3 to 5 pages: problem → what it does → how the client uses it → value → what happens next.
- **Update:** against plan → what we learned → decisions needed → next period. Progress strip, shape-built status table. 3 to 6 pages. P2 and P3 add product usage and refresh status.
- **Workshop:** agenda and objectives → framing pages → exercise pages with prompts → empty capture grids → close. 6 to 12 pages. Questions and prompts, not conclusions.

