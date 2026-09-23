# BUILD SPEC: The Telesto Standard 2.0 (the manual)

Prepared 2026-09-13 from the Cowork session that designed the workflow and the skills. Written for a Claude Code session to build. Everything here is settled unless marked OPEN.

## 0. What this is

One manual. It replaces the CFM, which is the older consulting manual written before AI work and far longer. There is no second manual.

- **PPT is internal**, the working file. **PDF is what ships** to the CEO and the team.
- **21 pages.** Ceiling is 25.
- Built on the dark Telesto v2 template, in the grammar already established on the P3-P5 pages.
- Built through the workflow it documents: use `draft-deck` to build it and `deck-qc` to score it, so the artifact is its own proof. Say so on the closing handoff to the CEO.

## 1. Deadlines

- **Fri 9/25** updated standard to the CEO. Deliver Thu 9/24 so the 25th has slack.
- **Wed 10/7** standard live, CFM retired.
- **Tue 10/20** full team trained and certified.

A gate at risk is raised the week before, not discovered after. That is a standing instruction from the CEO and it applies to this build.

## 2. The bar (CEO, 9/9). Use as acceptance criteria for every page

- Work starts in AI, with our role as direction and QC, rather than AI accelerating a draft we would have written anyway.
- Quality is scored against a published scorecard before anything ships, rather than settled by the reviewer's judgment.
- Anyone on the team can run it, rather than it living with whoever is best at it.
- Every deliverable adds to Telesto IP that the next engagement reuses.
- We are setting a novel way of working and need to be at least 4 months ahead of clients and competition.
- A gate at risk is raised the week before.

Her calibration on 9/9 was that what she had seen in the field was "1.0 practice executed well in a newer format." Every page should be checkable against that sentence: does this page describe the new way of working, or the old way in a new template?

## 3. Decisions settled 9/13

- The skill replaces most of what the old storyline taught. The manual becomes a guide on how to use the skill, with consultant judgment as the layer on top. Do not re-teach MECE, 80/20, storyline pyramids, title rules or page archetypes: those live in `draft-deck` and its references, and duplicating them guarantees drift.
- Front matter stays short: cover, what this manual does, the three types, the AI page.
- Services is dictated by the workflow chart: inputs, gates, iteration, the diff, plus the judgment layer.
- Services + Product is the product type list, a demonstration of each, and how a product becomes live and deployed.
- Product is held. It lists what is in development and ends there, until at least one product is commercially tested.
- **No margin, pricing or staffing content** until the CEO supplies it. Do not invent or estimate it.
- Product types: survey explorer, data dashboard, benchmark tool, internal tool. Dropped: scorecard, client portal. A fifth may be added; if it is, add one demo page and the total becomes 22.
- Demonstration pages are built blank, to a fixed layout, awaiting screenshots the user supplies.
- The sample QC page is a placeholder. The EDR AI deck produced a real report; the user will drop it in.

## 4. Assets

In this bundle or already on disk:

- `vs2.pptx` — the dark Telesto v2 template. 49 layouts. Every page inherits from the layout named `Blank (Contrast - Corner Image Ready)`, which carries the dark ground, the logo, the copyright line and the page number.
- `Telesto_Standard_v2_P3-P5.pptx` — three pages already built in the target grammar. Use as the visual reference and the source of reusable archetypes. Note the numbering is from the old storyline: its P3 (continuum) maps to the new P3, its P4 (pipeline) is superseded by the workflow chart, its P5 (tools and skills table) is OPEN, see section 7.
- `mk.py` — the python-pptx builder used for those pages. Carries the helpers: `new(title, active)` which adds a slide from the DARK layout, strips non-title placeholders, sets the title TOP-anchored at 22pt and draws the eyebrow tracker; `box()`, `text()`, and the raw-XML `shadow()` and `gradient()` helpers. Start from this rather than rewriting the scaffolding.
- `docs/telesto_deck_chain.html` / `.png` (repo root) — the workflow chart, already in the dark Telesto style and approved. It is P6. Port the SVG to native PowerPoint shapes rather than pasting the image, so the page stays editable.
- Project docs: `claude/vanguard-standard-v2-storyline.md` (the 9/10 storyline, superseded in structure but still the source for design grammar and the CEO meeting takeaways), `claude/workflow-and-skills.md`, `claude/qc-scorecard-design.md`, `claude/deck-types.md`, `claude/handoff-claude-code.md`.

## 5. Page spec, 21 pages

Titles below state intent, not final wording. Write each as a full-sentence action title in the build, then check the title chain end to end.

### Front matter (4)

| # | Eyebrow | Page | Visual | Notes |
|---|---|---|---|---|
| 1 | none | Cover | Title, date, version | Logo from the layout |
| 2 | 00 ORIENTATION | What this manual does, and what it retires | Two-lane comparison: the CFM way against the 2.0 way | Name the CFM explicitly. This page answers "1.0 in a newer format" head on |
| 3 | 00 ORIENTATION | The three types | Chevron continuum, three segments, markers placed | Reuse the built P3. Dashboards sit in the middle segment unless sophisticated enough to stand alone (CEO, 9/9). No margin or pricing rows |
| 4 | 00 ORIENTATION | For the AI reading this | Text page, the one dense page in the document | Write last, after every other page is final |

### Services (8)

| # | Eyebrow | Page | Visual | Notes |
|---|---|---|---|---|
| 5 | 01 SERVICES | Divider | Section mark | |
| 6 | 01 SERVICES | The workflow, end to end | The agentic workflow chart, ported to native shapes | Source: `docs/telesto_deck_chain.html`. Keep the pattern brackets and the legend |
| 7 | 01 SERVICES | What you supply | Input cards down the left, what each decides on the right | Prompt, data files, example deck (mandatory), stakeholder context when a roster exists, Build Brief only when the package includes a product or engineer time |
| 8 | 01 SERVICES | What the gate checks so you do not | Checklist panel drawn from `qc_rules.json` | Fonts 10pt floor, word budget, totals, footnotes, placeholders, notes, metadata, overflow, overlap. State that appendix and crosstab pages sit outside the style checks |
| 9 | 01 SERVICES | What a scored deck looks like | Sample QC report, placeholder frame | PLACEHOLDER. User supplies the real EDR AI output. Build the frame to hold a report of roughly one page |
| 10 | 01 SERVICES | How comments come back | The Revise loop: comment in the PPTX, mechanical done, judgment gets 2-3 options, ambiguous asked, a data-label rename asked with the footnote decision, a request for research nobody has done held and scoped | Reviewer comments in the file rather than describing fixes in prompts. Both comment stores are read |
| 11 | 01 SERVICES | What each engagement leaves behind | The Learn loop: shipped deck against last draft, proposed rule changes, human approves each | This is the IP bullet. Evidence available: three Learn passes on the EDR AI minipack between 9/12 and 9/13, each adding rules to `language-rules.md`. Show it as a before and after, not a description |
| 12 | 01 SERVICES | The judgment layer | The calls the chain cannot make | Title and message, exhibit choice, recommendation and claim sizing, what the data does not support. Closes the section on the human. This page is the clearest statement of the CEO's bar in the document |

### Services + product (7)

| # | Eyebrow | Page | Visual | Notes |
|---|---|---|---|---|
| 13 | 02 SERVICES + PRODUCT | Divider | Section mark | |
| 14 | 02 SERVICES + PRODUCT | Four product types | Four numbered cards, Palantir 01-04 system | Survey explorer, data dashboard, benchmark tool, internal tool. Leave the grid able to take a fifth |
| 15 | 02 | Demonstration: survey explorer | Screenshot frame plus a caption block | BLANK. Fixed layout, user supplies the screenshot |
| 16 | 02 | Demonstration: data dashboard | As above | BLANK |
| 17 | 02 | Demonstration: benchmark tool | As above | BLANK |
| 18 | 02 | Demonstration: internal tool | As above | BLANK. Colleagues are building this one |
| 19 | 02 | From analysis to a live, deployed product | Sequence with the decision points and the tier rule | Who moves the data decides the tier: consultant with Claude Code, consultant with Replit and real auth, or data engineering on Google Cloud. Include the five checks that decide whether analysis becomes a product |

### Product (2)

| # | Eyebrow | Page | Visual | Notes |
|---|---|---|---|---|
| 20 | 03 PRODUCT | Divider, marked in development | Section mark with the in-development treatment | |
| 21 | 03 PRODUCT | What is in development | Three items with their stage | Marketing intelligence bot, the most MVP-like. HALO, being built. ARIA, scoped only. End the document here. No roadmap, no dates, no commercial claims until at least one product is commercially tested |

## 6. Build rules

Inherit from the template, do not rebuild it. Add slides from `Blank (Contrast - Corner Image Ready)` and delete every placeholder except the title.

- Palette from the theme: ground 282828, card 333333, teal 009999, cyan 0BD0D9, deep teal 005366, navy 003366, white body, 8A8F92 muted for inactive navigation only. Arial throughout.
- Title TOP-anchored, 22pt bold white, left edge 0.61in, width 12.12in. No sub-headline under the title.
- Eyebrow tracker across the top: 00 ORIENTATION, 01 SERVICES, 02 SERVICES + PRODUCT, 03 PRODUCT. Active segment teal with a 0.025in underline, inactive 8A8F92. Keep all four segments on every page; 03 stays visible even though the section is held.
- Typography floor: nothing below 10pt except a footnote, 8pt floor there. No italics anywhere.
- Depth by role: spine elements take a gradient plus a soft shadow, content cards take a subtle gradient only with no border and no shadow, borders are reserved for status and selection.
- Concept pages get real visual grammar: chevrons for a progression, arrows between nodes, gate marks where approval happens, loop-back arrows where work returns. A row of cards standing in for a diagram is the thing to avoid.
- Tables are built from shapes and text boxes, never the native PowerPoint table. Bucket labels sit in feature boxes to the left of the rows, never as header bands.
- One idea per page. Visual first, minimal text.
- Author and core-properties author field empty on every saved file.
- Look at the render before handing off. Convert to PDF, rasterise, view every page, fix overlaps, overflow and hanging words, re-render.

## 7. OPEN items

- **The tools and skills inventory.** The CEO asked for this on 9/10: a table by path showing the skills and the build tools, with Gamma, portals and GitHub named. It was built as the old P5. The new structure has no home for it. Decide whether it folds into P3, becomes a page in Services, or is dropped with the CEO told why. Do not drop it silently.
- **The fifth product type**, if the user adds one. Adds one demo page and makes the document 22 pages.
- **Certification.** The 10/20 gate needs a definition. Proposed to the CEO but not agreed: a consultant runs one deck end to end unassisted, the QC score clears a stated threshold, and the edit log shows no mechanical fixes. If she agrees, it belongs on a page; if not, it stays out of the manual and lives in the training material.
- **`deck-qc` scripts in Cowork.** As of 9/13 the account copy of `deck-qc` shows no `scripts/` folder. If the scripts do not survive upload to account skill storage, the code gate is a Claude Code feature only, and P8 must say that plainly rather than implying the team gets it in Cowork. Resolve before the manual describes the gate as universal.

## 8. Pending inputs from the user

- Screenshots for pages 15 to 18.
- The real QC report output for page 9.
- A fifth product type, if any.
- CEO input on margin, pricing and staffing, which stays out of the document until it arrives.

## 9. Build order

1. Scaffold from `mk.py`: all 21 pages with eyebrow, title and page furniture, no content. Render and check the tracker and the title chain read correctly.
2. Page 6, the workflow chart, ported to native shapes. It is the largest single build and the spine of the document.
3. Services content, pages 7 to 12.
4. Front matter, pages 2 and 3, reusing the built P3.
5. Services + product, pages 13, 14 and 19, plus the four blank demo frames.
6. Product, pages 20 and 21.
7. Page 4, the AI page, written last.
8. Run `deck-qc` on the file. Fix what the gate blocks. Record the score, it goes to the CEO as evidence.
9. Export the PDF. Keep the PPT internal.

## 10. First prompt for the Claude Code session

> Read MANUAL-SPEC.md in this folder. Build step 1 of section 9: scaffold all 21 pages from `mk.py` into the v2 template, with the eyebrow tracker, the page titles as working full-sentence titles, and no body content. Render to PNG and show me every page before we add content. Do not invent margin, pricing, staffing or product claims anywhere in this document.
