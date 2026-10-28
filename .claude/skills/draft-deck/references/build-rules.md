# Build rules

Read at the Build stage and whenever a Revise adds a page or a new element. Universal to every paper; client formatting is in the Deck style section of the client brief.

## Contents
- Build rules (native, editable, nothing hardcoded)
- Concept pages
- Telesto dark paper
- Slide density, footnotes, versioning, rating columns
- Construction lessons from live revisions

## Build rules — native and human-editable, nothing hardcoded

1. **Inherit, don't invent.** Duplicate slides from the attached shipped deck that match the target archetype, then replace text. This carries theme colors, fonts, footers, and page furniture natively. Build a slide from scratch only when no archetype in the attachment fits.
2. **Native elements only.** Text boxes, shape-built tables, native charts with editable data. Never render text or charts as images. Never use SmartArt or grouped decorative constructions the user can't easily pull apart.
3. **Charts come from the data files.** Read the crosstab, survey export or workbook, compute the displayed figures from the unrounded base, and bind them into native charts. State metric and denominator in the chart subtitle. State trimming explicitly (no silent top-N). Changing data in an existing chart follows deck-qc `references/applying-fixes.md` (patch the cache, never `chart.replace_data()`).
4. **No hardcoded styling.** Colors and fonts come from the deck theme (scheme colors), not pasted hex values, wherever the format allows. A human opening the file must be able to edit any element the ordinary way.
5. **Keep the deck's evidence furniture**: DRAFT stamp on working pages, copyright footer, page numbers, question-number footnotes, denominator lines.
6. **One idea per page.** If a storyline line needs two ideas, it needs two pages.
7. **Four homes for text** (client specifics in the Deck style section of the client brief): action title, chart/table title, content text box, footnote. No small or gray text outside a footnote; few font treatments per page; one font size within any table. The typography floor in SKILL.md applies: 10pt minimum outside footnotes, gray text only as a rare exception. This rule overrides habits found in the attachment.
8. **Tables hold data, not prose pairs.** Deliverables→outcomes and similar paired lists are built as individual text boxes with drawn rules and numbered ovals. Multi-item cells become bullets, never semicolon runs. Where a column is headed Quotes, the cells hold verbatim quotes.
9. **Bar charts keep the Y axis line.** The category axis is a thin line at the bars' origin with no tick marks and no numeric scale; data labels sit outside the bar end.
10. **Edit text at the run level**, and reset a reused run's formatting, as in deck-qc `references/applying-fixes.md`. A find-and-replace spanning a bold lead-in collapses the paragraph into the bold run.
11. **File integrity.** python-pptx API for slide content. Raw XML is permitted in exactly two places: the chart-cache patch, and `a:effectLst` (shadows) or `a:gradFill` (gradients) on shapes you created yourself. Never let two slides share an embedded OLE object: when duplicating a slide carrying hidden think-cell data, strip the object from the duplicate. Validate against the original file before handing off.
12. **Leave the author / core-properties author field empty** on every generated file.
13. Work with the pptx skill's mechanics for unpacking, duplicating (`add_slide.py`), editing slide XML, and validating. Content QA: no leftover placeholder text from the source slides, no orphaned visuals after text replacement.
14. Apply the Deck style section of the client brief for client-paper specifics (titles, tables, charts, callouts, footnotes). A freshly attached shipped deck beats it, except where the four-homes rule or the typography floor says otherwise.
15. **Look at the render before handing off.** Use deck-qc stage 2 (`render_check.py`: PowerPoint, contact sheets; soffice and pdftoppm where PowerPoint is absent). Overlaps, overflow, stranded titles and hanging single words on a last line are invisible in the XML and obvious in the image. Fix (widen the box, or reword a few words), re-render, then send.


## Concept pages get real visual grammar

A page explaining a continuum, a process, a set of gates or a sequence is drawn in the grammar of that idea: chevrons for a progression, arrows between nodes, an explicit gate mark where approval happens, a loop-back arrow where work returns to be fixed, a timeline where dates matter. A row of cards standing in for a diagram is the thing to avoid. Let the shape carry the meaning: where a step is advisory rather than blocking, draw it as a loop, not a gate.

Icons earn their place where a set of items is scanned rather than read, such as scored dimensions or archetype tiles, and in front of each statement on an implication or recommendation page in place of accent bars. Never scatter icons as decoration.


## Telesto dark paper (2.0)

The 2.0 house paper is dark and built for screen. It is the default for Telesto-paper work unless the user asks for the light template; client paper is unaffected. Dark does not mean sparse: a survey report on dark paper is as chart-heavy as the type demands. Reference artifacts: ULSE/TRIP and Rotary (proposals), Re-rebrand (findings), the Vanguard Standard v2 deck (the manual).

**Inherit the template, do not rebuild it.** Open the current Telesto deck or template and add slides from the layout named `Blank (Contrast - Corner Image Ready)`. That layout carries the dark ground, the logo, the copyright line and the page number, so none of those get drawn by hand. Delete every placeholder except the title on each new slide.

**Palette, from the theme:** ground 282828 · card 333333 · teal 009999 (accent5) · bright cyan 0BD0D9 (accent3) · deep teal 005366 · navy 003366 · body white · muted 8A8F92 for inactive navigation and non-focus chart series only. Arial throughout.

**Title.** Anchor the title text frame to the TOP, so one-line and two-line titles both sit directly under the eyebrow. 22pt bold white, left edge 0.61 in, width 12.12 in. No smaller sub-headline under the title; a category label slot is fine.

**Eyebrow.** A numbered eyebrow above the title is the storyline spine: `01 THE STAKES`, `02 THE RESPONSE`, or `01`, `02` on finding pages. The manual's variant is a multi-segment tracker with the active segment lit in teal and the rest muted; client decks use the single numbered eyebrow.

**Analytical pages on dark paper.** Bars single-hue teal, with muted gray for non-focus series and a lighter teal for the highlighted item. Data labels white, outside the segment. Heatmaps in teal tints from ground to full teal, values white. Tables built from shapes (a native table is fine for a large table or a heatmap), bucket labels in teal-tinted feature boxes to the left of the rows, one font size within a table. Source line and n under every exhibit, full size, white or muted; never small gray.

## Slide density

- 2-3 exhibits maximum per slide; one idea per page. Anything more goes to appendix.
- Each exec-summary point double-clicks into 1 body slide (rarely 2) that expands the point with data.
- Certain pages can be text-heavy (methodology, discussion), but never a wall of text for executive audiences.
## Footnotes

The convention (numbered superscripts, question wording verbatim, "Source:" for external material) is in SKILL.md. Two construction points: replace survey piping tokens (such as $HQ14_text) with the piped value, following the shipped deck; end a survey footnote with the survey name and base ("; Competitive Intelligence survey, n=200").
## Versioning

- The version number _vN moves up only after a CEO or client revision, or when the storyline or page order changes. Everything else is an iteration of the same version: gate fixes, evaluator FIX items, resolved SUGGEST items, render fixes. Iterations are saved as _vN_1, _vN_2 and so on, never as a new N. When the consultant hands back an edited file, that edit is the new version and the AI iterations on it start again at _1. Never bump the version on your own; a build script that writes a new file writes the next iteration.
## Rating columns

- An analyst rating column (readiness, maturity, fit) carries a footnote marker and a footnote that says whose estimate it is and what it rests on. The data beside it justifies the call; the footnote says so.

## Construction lessons from live revisions
- **The eyebrow number is a finding number, not a page number.** Two pages that support finding 1 both carry "1". Never renumber to make pages consecutive.
- **Appendix and data pages stay as they are.** Crosstabs, backup exhibits and methodology pages are not restyled, resized or re-fonted by the AI phase or by the gate; smaller type is allowed there. Only hygiene (author, notes, metadata) applies to the whole file.
- **Use the client's plain layouts by default.** Side-panel or numbered layout variants are for varying rhythm on low-text pages; the client brief's Deck style section says which.
