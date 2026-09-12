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

- Keep the deck's _vN in the filename across working iterations. Save iterations as "…_vN (1)", "(2)", and so on. Bump to _vN+1 only on a material change or when the user signals.
