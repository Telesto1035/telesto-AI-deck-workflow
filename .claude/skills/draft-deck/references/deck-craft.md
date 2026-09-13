# Deck craft conventions

Formatting conventions learned from shipped work, most recently the EDR board deck (Aug 2026). Entries labeled **Huron/EDR** are client-paper specifics; the rest applies on any paper. Where this file conflicts with a freshly attached shipped deck, the attachment wins.

## Slide density

- Executive summary: at most 5 rows, 3 columns (findings / implications / recommendations). Six rows or a fourth column taxes the eye; move the overflow to a discussion page or appendix.
- 2-3 exhibits maximum per slide; one idea per page. Anything more goes to appendix.
- Each exec-summary point double-clicks into 1 body slide (rarely 2) that expands the point with data.
- Certain pages can be text-heavy (methodology, discussion), but never a wall of text for executive audiences.

## Titles (Huron/EDR)

- Aptos Display, 24pt, on every content page. Cover page excluded.
- Hold titles to two lines (roughly 105 characters). Shorten the sentence; do not shrink the font.
- Number chips (the 1/2/3 squares on double-click pages) top-align with the first line of the title.
- Titles sit ~0.4" from the top edge, not flush against it (template default is too high).

## Tables (Huron/EDR)

- Tahoma throughout. One font size within any table; never mix sizes inside a grid. 11pt is comfortable for an 8-10 row table.
- Header row: aubergine fill (theme accent 2, 5D013A), white bold text.
- Percentage columns centered; attribute/name column left-aligned.
- Huron's row highlighted with the theme tint (F5E6EF), bold aubergine text. Bold the max value per column.
- Exec-summary grid: uniform size across all three columns (9.5pt at 5 rows), every cell top-aligned.

## Charts (Huron/EDR)

- Native bar charts only; never rendered images. Leave think-cell data objects untouched ("do not delete").
- Single color: all bars theme accent 2 aubergine. No two-color highlight schemes; they confuse the read.
- Data labels: percentages centered inside the bars, white, Tahoma 10, regular weight (not bold), '0%' format.
- Category labels ("attributes"): hide the native axis labels and render a column of left-aligned Tahoma 10pt text boxes instead (never 9pt: the 10pt floor applies to chart labels on every paper, decided 2026-09-12) (the shipped slide-18 archetype), so every label shares one left edge. Native axis labels self-size and produce inconsistent alignment.
- Pin the chart's plot area with a manual layout so the label boxes stay registered to the bars. Note in handoff: resizing the chart in PowerPoint will not move the label boxes.
- Value axis deleted; no gridlines, no tick marks, no legend, no chart title.
- Subtitle line above each chart carries metric and denominator: "% of respondents selecting · n=302 · top 6 of 10 shown". State trimming explicitly (no silent top-N).

## Callouts and takeaways (Huron/EDR)

- Takeaway, discussion, and context lines sit on a band-fill rectangle (EBE9E4, the exec-summary column-band color), no outline, text inset ~0.12" from the box edges, box edges aligned to the column grid.
- Label the register: "Takeaway:", "For discussion:", "Context:". On board/advisor decks, takeaway rails may be phrased as open discussion questions.

## Footnotes

- Write the whole question text verbatim, numbered; never paraphrase. Replace survey piping tokens (e.g., $HQ14_text) with the actual piped value, following the shipped deck's precedent.
- End the footnote with source and base: "; Competitive Intelligence survey, n=302."

## Versioning

- The version number _vN moves up only after a CEO or client revision, or when the storyline or page order changes. Everything else is an iteration of the same version: gate fixes, evaluator FIX items, resolved SUGGEST items, render fixes. Iterations are saved as _vN_1, _vN_2 and so on, never as a new N. When the consultant hands back an edited file, that edit is the new version and the AI iterations on it start again at _1. Never bump the version on your own; a build script that writes a new file writes the next iteration.


## Tables and text boxes (all papers)

- Consulting tables (about four columns, three to five rows) are text boxes on a grid with thin horizontal divider lines between rows; the header row is bold; no vertical rules or cell fills. Native tables only for large tables and heatmaps. The Public Sector deck (Sep 2026) carries both constructions; the lines-and-text-boxes one is the preferred form.
- Section subtitles inside a page: bold, 14 or 16pt, with a thin horizontal line directly beneath.
- Every text box: zero insets on all four sides, top-anchored, so the grid aligns and boxes of different lengths share a top edge.
- Charts: think-cell was used before and is still acceptable; a native chart is fine when its data stays editable and its format matches the think-cell look described above (left-aligned label column, labels outside bars, one colour, no gridlines).


## Huron layouts, as used on the shipped EDR minipack (2026-09-12)

- Cover Option 1 for the cover; Callout Option 1 for the one-sentence takeaway page (image background, ~30 words, 36pt).
- Content Header Only (white) for every page with an exhibit.
- 1_Content Header Only (aubergine side panel, title in the panel) for low-text pages only, to vary the rhythm: exec summary, quote pages, next steps. Never for a chart page.
- Divider Option 1 for the appendix divider.
- Competitor rows in charts carry logos; the client row is boxed with a dashed outline. Stat callouts at 26pt with the sentence at 10pt beside them; key phrase and number bold in aubergine.

- An analyst rating column (readiness, maturity, fit) carries a footnote marker and a footnote that says whose estimate it is and what it rests on: "Readiness is Telesto's estimate from the survey results shown beside each area." The data beside it justifies the call; the footnote says so.
