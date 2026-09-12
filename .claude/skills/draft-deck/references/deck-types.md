# Deck types — routing and build spec for draft-deck v2 (2026-09-12, rev 3)

Reference files cannot be added through the skill proposal card, so a compact version goes inline in SKILL.md and this is the full spec. Copy into the skill folder as `references/deck-types.md`.

Rev 3: minipack given a fixed shape (summary of four points, four matching detail pages, conclusion and open discussion, next steps); typography floor noted; audience brief added as an optional input.

## The invariant, before any routing
Every Telesto deck produces a call to action or a discussion, supported by statistics, quotes or data visualization, and it works at two reading speeds: the title chain alone delivers the message on a phone in 20 seconds; the charts, tables and footnotes hold up to a 30-minute read. Both tests apply to every type. Density is not a style choice; it is set by the deck type and by each page's job.

## Typography floor, every type and paper
Nothing below 10pt except a footnote. Italics and grey detail text only as rare exceptions (the gate blocks above four per deck); quotes are set roman in quotation marks. If text must shrink below 10pt to fit, the page carries too much: cut, split, or footnote.

## Routing order
1. **Package** (from the Build Brief, or inferred from the prompt): 1 Services · 2 Services + product · 3 Product.
2. **Deck type** (seven). Under Package 1 all seven apply. Under Package 2 all seven apply; proposal, findings report and update change shape (below). Under Package 3 the deck explains or sells the product: proposal, explainer and update apply; the rest rarely do.
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
| **Minipack** | Answer one question between milestones | Cover with takeaway → exec summary, four numbered points (bold finding sentence, key number inline, one supporting sentence) → four detail pages, one per point, same order and number → conclusion and open discussion (what the points add up to; one prompt per question the room should settle) → next steps with owners and dates | One exhibit per detail page: bar chart, stat rail of percentages, shape-built table or heatmap; source and n; recommendation band where the point supports one | 7 by default; 3-5 summary points with detail pages one for one, never more than five | As findings, tighter |
| **Presentation** | Live narrative that still stands alone when forwarded | As findings or proposal, fewer words, larger exhibits, closing decision page | Visual-leaning; exhibits sized for a room | 8-15 | As the parent type |
| **Update** | Status to the sponsor | Where we are against plan → what we learned → decisions needed → next period | Medium: progress strip, status table from shapes | 3-6 | Plain, dated, owner-named |
| **Workshop** | Run a session | Agenda and objectives → framing pages → exercise or discussion pages with prompts → capture templates → close | Frameworks, 2x2s, deliberately empty capture grids | 6-12 | Questions and prompts, not conclusions |

## Package variants
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
