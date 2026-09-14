---
name: onepagebrief-builder
description: "Build the one-slide Telesto Deliverable Brief (PPT) that precedes any AI build: selects the package type (service only / service + product / product only), interviews the consultant block by block, renders the approved-format slide for partner review, and hands the approved brief to draft-deck as build input. Triggers: \"one page brief\", \"deliverable brief\", \"build the brief\", \"brief for review\", or starting any client deliverable before drafting."
---

# One-Page Brief Builder (Telesto) — v1.2

You produce ONE PowerPoint slide: the Deliverable Brief. It is the upstream gate of Telesto's 2.0 workflow: the consultant answers your questions, you render the slide, a partner approves it, and the approved brief becomes the verbatim build input for the deliverable. Quality control works like product development: spec approval upstream, QC gate downstream, not layered review in the middle.

This skill is distinct from `onepagerbrief` (the HTML team-update one-pager). This skill's output is always the pre-build PPT brief.

Rules of the artifact:
- One slide, always. A block that will not fit means the thinking is not done: help the user condense, never spill to slide 2.
- Terminology: "slide" and "page," never "beat."
- White background, Telesto teal, Arial. No em dashes anywhere in slide text; use colons or commas.
- The brief precedes the build. If scope changes mid-build, the brief is amended and re-approved first.
- One brief per client package, not per component. A bundled product gets its lines in FORM; it earns a separate build spec only if it has an independent lifecycle (keeps operating after delivery, different audience, or an engineered build).

## Step 1 — Interview, one block at a time

Interview interactively. Where the AskUserQuestion tool is available, use it for every selection question below; otherwise ask in plain text. Ask in this order, ONE block per turn; skip anything the user already supplied. If the user attaches a prior deck, dot-dash, or notes, pre-fill every block you can and confirm rather than re-ask.

1. **Package type (ALWAYS the first question, a selection):**
   1. **Service only** — consulting slides; closest to what Telesto currently makes for clients; denser pages are acceptable
   2. **Service + product** — consulting accompanied by a data product; more strategic; the product or dashboard replaces some appendix and supporting elements of the deck
   3. **Product only** — a live tech product is the deliverable; the PPT exists to explain it (what it does, how to use it, the value)
2. **Deck type (types 1 and 2 only, a selection)** — branches into the draft-deck skill's types: Proposal/BD · Findings/research report · Update · Kickoff · Workshop · Minipack · Presentation. For type 3, skip this: the deck is a short product explainer by definition.
3. **Setup:** paper (Telesto or client, name the client); client; SOW/engagement; land date/occasion; approving partner.
4. **Goal** (3 lines): What decision or action does this enable for the client? Which SOW commitment does it fulfill? What does it set up for the account?
5. **Audience**: Who reads or uses it, by name and role? What should the primary reader DO within a week? Who will it be forwarded to? (Type 3: also, who are the recurring USERS of the product, if different from the reader of the explainer?)
6. **Takeaway**: "What is the one takeaway, in one sentence?" Push back on two-sentence answers and on labels ("Q3 findings" is not a takeaway). This sentence becomes the slide title.
7. **Client needs, three lenses** (one line each):
   - Technical: what must be accurate, complete, and defensible for this reader to trust it?
   - Financial: what is the value at stake, quantified? What economics does the reader weigh?
   - Psychological — SCARF (selection): which ONE or TWO elements should this deliverable deliberately serve?
     - Status: the reader's standing is recognized; open by crediting their wins or direction
     - Certainty: the reader needs confidence; validation flags, methodology, and sourcing up front
     - Autonomy: the decision must feel like THEIRS; present criteria and options, let their weighting select the answer
     - Relatedness: partnership register; "we," shared history, continuity
     - Fairness: transparent criteria, balanced findings, tensions stated not hidden
     Then the fill-in: "State the choice as a design move: e.g. 'autonomy: the criteria page lets his own weighting select rail.'"
8. **Storyline**: 5-8 numbered lines, one line = one page (or one product section). Ask which line carries the recommendation; star it. By package type:
   - Type 1: pages only; density per current client conventions.
   - Type 2: mark any line whose supporting detail LIVES IN THE PRODUCT rather than in deck pages (these replace appendix/backup pages); the deck keeps the storyline, the product carries the depth.
   - Type 3: the storyline is the explainer arc: the problem → what the product does → how the client uses it → the value and what happens next. The product itself is the centerpiece; the deck stays short.
   If the user has no storyline, elicit one: what proves the takeaway, in what order, and what should the reader feel page by page?
9. **Form**: by package type —
   - Type 1: page-count target and grammar (Telesto dark tech grammar for Telesto-paper proposals/BD/updates; survey/findings grammar for findings reports; client conventions on client paper).
   - Type 2: deck page target PLUS one line per product component (what it is, what deck content it replaces, who refreshes it and how often).
   - Type 3: the product (what it is, platform, who operates it) plus the explainer deck's page target (typically 3-5 pages).
10. **Open items for review** (max 4, merged): judgment calls only a partner can make (pricing posture, claim escalation, client politics) AND missing data or sources, including any figure the AI could plausibly invent (name the source required before build). If the user offers more than 4, make them rank; keep the top 4.

Never invent content for any block. A blank the user cannot fill becomes an open item, not your guess.

## Step 2 — Render the slide

Build with pptxgenjs (Node). Ask once for the Telesto logo PNG if not already attached this session; if unavailable, use a text wordmark "TELESTO" (Arial bold 11pt, teal, top-right) instead and say so.

Design constants: LAYOUT_WIDE (13.33x7.5). Typography floor: nothing below 10pt except the footer line, no italics anywhere; the same floor qc_check.py enforces on decks. If a card does not fit at 10pt, cut words, never the size: the brief is a summary, and a block that needs 9pt is saying too much. Colors (no # prefix): teal 009999, ink 1B1D1F, body 3A4045, grey 6A7075, card fill F4F6F7, review-card fill F0FAFA. Arial throughout. White background.

Layout (inches):
- Kicker "DELIVERABLE BRIEF": x0.45 y0.32, 10pt bold teal, charSpacing 1.2
- Logo: x11.78 y0.13 w1.13 h0.45 (or wordmark)
- Takeaway = title: x0.45 y0.62 w12.45, 19pt bold ink (shrink to 17pt if it wraps past 2 lines)
- Header strip: x0.45 y1.5, 10pt; teal bold labels CLIENT/TYPE/PAPER/LANDS/PARTNER, grey values. TYPE shows package type plus deck type, e.g. "Service + product · Proposal".
- Card grid from y1.90, three columns: A x0.45 w3.98 (GOAL h1.55; AUDIENCE y+1.67 h1.40; CLIENT NEEDS y+3.19 h1.95) · B x4.57 w4.16 (STORYLINE h5.10; caption "★ recommended page · one line = one page" 10pt roman grey at bottom) · C x8.87 w3.98 (FORM h1.25; OPEN ITEMS FOR REVIEW y+1.39 h3.70)
- Cards: roundRect rectRadius 0.07, label 10pt bold teal charSpacing 1 at top, body 10pt lineSpacingMultiple 1.12, bold ink lead-ins (Client:/SOW:/Technical: etc.)
- Storyline: teal bold 01-06 numbers, paraSpaceAfter 11; star on the recommendation line; in type 2, suffix "→ product" in teal on lines whose depth lives in the product
- OPEN ITEMS card is the ONLY bordered card: teal 1.5pt border, fill F0FAFA, teal bold numerals
- Footer line x0.45 y7.14, 8pt grey roman (the only text below 10pt; it sits in the footnote band): "The approved brief precedes the build and becomes the AI build input; scope changes amend the brief first."

pptxgenjs gotchas: set layout before adding slides; every addText needs isTextBox:true and margin:0; hex colors without #; breakLine:true between runs that end a line; never a literal bullet character.

QA before delivering: render to image (soffice → pdftoppm), view it, and check: no text overflow or card overlap, footer clear of cards, takeaway fits, exactly one bordered card. Then run `qc_check.py` on the file (it must pass: empty author field, no PptxGenJS fingerprint in docProps, no run below 10pt outside the footer, no italics). Fix and re-render until clean. Deliver the .pptx.

## Step 3 — Hand off to the build

After partner approval, the brief drives the build. Routing by package type:
- **Type 1 (service only)** → draft-deck, Mode 1, with the selected deck type.
- **Type 2 (service + product)** → draft-deck for the deck (Mode 1, selected deck type); the "→ product" storyline lines and the FORM product lines define the product's content. The product gets its own build spec ONLY if it has an independent lifecycle or needs an engineered build; that spec is reviewed by whoever owns the build risk, not a second exec review.
- **Type 3 (product only)** → the product build comes first (from FORM and the storyline arc); the 3-5 page explainer deck is drafted last, from the same brief, in Telesto dark tech grammar.

Mapping into draft-deck:
- Storyline lines = the dot-dash, one line per page; the starred line is the recommendation page
- Deck type + paper = draft-deck's mode flags and grammar choice
- TONE from the SCARF choice: status → open by crediting the client's direction or wins before presenting; certainty → sourcing, validation flags, and methodology visible early; autonomy → criteria-and-options pages where the reader's weighting selects the answer, recommendation marked visually not verbally; relatedness → "we" register, continuity with prior work; fairness → transparent criteria, countervailing data kept next to headline numbers
- Client-needs Technical line = the sourcing bar; Financial line = the value-at-stake framing for titles
- Open items: any UNRESOLVED open item ships as a [PLACEHOLDER] or flag in the draft, never silently resolved by the AI

If the user amends the brief after the build starts, update the slide first, note what changed, then apply the change to the build.

## Next stage

The approved brief is `draft-deck`'s storyline input. Close with one line: "Brief approved and saved as FILE. Next: run stakeholder-context if a roster exists, then build the deck. Say 'build the deck from BRIEF'."
