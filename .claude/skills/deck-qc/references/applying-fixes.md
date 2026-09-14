# Applying fixes: editing craft

Read when applying decided fixes to the file.

- **A qualifier in a label is data until the source says otherwise.** "Program management" and "program management, health" may be two different rows with different sizes and incumbents; harmonizing them into one wording destroys the distinction the deck is built on. Look both up in the source first. If they are two rows, every page carries the fuller name. Same for "revenue" against "net revenue", or a segment name that gains a region.
- **Edit with python-pptx at the run level.** Edit only the runs a fix touches so bold lead-ins and mixed formatting survive. Never replace a whole paragraph's text to change one word. After a multi-run splice, check the bold or color boundary landed where the original had it.
- **A reused run resets its formatting.** A first run inherited from an old paragraph can carry a hyperlink, an underline or a color; strip them and set color, size and weight explicitly.
- **New elements copy a sibling, not a constant.** Color, size and line style come from the nearest element of the same kind already in the deck.
- **Never touch chart data through `chart.replace_data()`.** Patch `ppt/charts/chartN.xml` inside the zip and say so. Changing a value updates an auto label, but a custom `c:rich` label does not and must be edited too. Growing a bar can push its label past the plot edge, so set the value axis max when a value grows.
- **Hand-built scatter and quadrant exhibits carry no data model.** Recover one before moving anything: read the axis tick positions, fit the scale, group the marks into bands, match them to the source rows by size order, and verify against the marks the slide already labels.
- **To make sibling exhibits match**, derive one linear transform from the reference page's axis geometry and apply it to every shape in the plot region, marks and labels together. Check it reproduces the reference page's own ticks before applying it anywhere.
- **Check the fill of what you are marking before choosing a marker color.** A dark marker on a dark mark is invisible; the render is the only way to know.
- **A number changes only when the source says what it should be.** If two pages disagree and no source is attached, ask which is right.
- **Shortening to fix an overflow is a wording change.** Cut the least load-bearing clause, prefer one stated elsewhere in the deck, and name every cut in the summary so the author can put it back. Never shorten an attribute label, an option name or a question wording; widen the box or split the line instead.
- **Leave embedded chart workbooks and think-cell OLE objects alone.** Deleting them breaks the charts' editability. Say you found them and left them.
- **Save as a new iteration, never over the input.** Validate against the original, re-render every page touched, re-score, show the delta, and run the gate on what you save.
