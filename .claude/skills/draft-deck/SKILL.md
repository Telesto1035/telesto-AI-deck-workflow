---
name: draft-deck
description: "Build first-draft consulting decks in Telesto house style from a prompt or files (survey data, crosstabs, transcripts, notes, prior decks), on Telesto or client paper, across eight deck types with findings reports and proposals as the priority types. Also resolves partner comments on an existing deck and rewrites titles, exec summaries or slide text. Triggers include \"draft the deck\", \"build the deck from this brief\", \"build the findings report\", \"survey report\", \"draft a proposal\", \"BD deck\", \"resolve these comments\", \"rewrite this title\", \"kickoff deck\", \"minipack\", \"update deck\", \"workshop materials\", \"user guide\", \"manual\". Synthesis and executive writing first, aesthetics second."
---

# Draft Deck (Telesto) v3

You produce the first draft that a trained consultant screens. The team is small and the draft has to arrive fast and close to finished, so you build directly from what you are given and ask only for what is missing. You still state your reasoning as you work, so the reviewer can challenge a call without re-deriving it.

Content and layout outrank styling. Never spend effort on lines, icons, or decoration at the expense of the storyline, the titles, or the evidence.

## The invariant

The chain exists so that a deck, human- or AI-written, reaches the partner mistake-free, up to the firm's conventions, and informed by the client's responsibility. This skill owns the writing and the client context; deck-qc owns the checks. A human applies the finishing touches, so the skill carries principles and a capped register, not a rule for every edit.


Every Telesto deck produces a call to action or a discussion, supported by statistics, quotes or data visualization, and it works at two reading speeds. Read only the titles on a phone and the message lands in 20 seconds. Read every chart and footnote for 30 minutes and nothing is ambiguous, unexplained or unsourced. Both tests apply to every type and every page. Density is not a style choice; it is set by the deck type and by each page's job.

## Division of labour: the AI phase builds the core three, a human adds the polish

Every slide has three things at its core, and they are what this skill spends its effort on:

1. **The title and message.** Is this the right claim for this room, given what the stakeholders need to hear and what Telesto can realistically recommend? The title is the takeaway; if it could move to another client's deck, it is not finished.
2. **The exhibit.** The one chart, table or quote set that shows the data behind the claim, native and editable, sourced and denominated.
3. **The recommendation.** What this changes or informs: the band that closes the page, in the recommendation register.

Everything else this skill knows about a finished page still applies (the edit patterns, the construction conventions, the paper), and callouts or highlights that carry data belong in the AI phase too: a highlighted bar, a delta called out beside a chart, a bolded number in a band. What waits for a human is the styling preference layer: decorative colour, icons, badges, spacing polish. The order of effort matters because the consultant should be thinking like a partner about what the page says in the larger story, not like an executor placing elements; placing elements is the cheap part.

**Confirm the storyline in text before building anything.** For a first draft, and whenever a comment or a new input changes the storyline (which pages exist, in what order, with which exhibit), write the page plan as text first: one line per page with the title, the exhibit it carries and the recommendation it closes on. Wait for the consultant's confirmation, then build. This holds even when a written brief is attached: the brief settles the takeaway and the storyline lines, and the page plan is still shown before the file exists. It saves time and tokens on both sides.

## Inputs and routing

There is no dot-dash step. The storyline comes from the inputs and you produce the page plan from them.

**Inputs, any combination:**
- A **written brief** (optional): a few lines from the consultant on takeaway, audience, value at stake and storyline. When none exists, draft those lines from the prompt, state them, and proceed.
- A **prompt**, the usual starting point.
- **Files**: survey data or crosstabs, quote repositories or transcripts, prior analysis, notes, a prior deck, a dashboard export. Files are the evidence; every number and quote in the deck traces to one of them.
- An **audience brief** (optional): a short list of who will be in the room, their titles and responsibilities, and the questions each needs answered, produced from the meeting roster by the `stakeholder-context` skill. When a roster, invite or attendee list is among the inputs and no audience brief is attached, run `stakeholder-context` first and build from its output; client context with a named audience is what sharpens the message and sets the storyline order, so it is not optional when the roster is known. When attached, its remit column sets how specific each recommendation gets (a person who places media gets channel mix and named conferences; a practice leader gets service implications), and it shapes the executive summary order (the sponsor's question first), the open-discussion page (one prompt per unanswered audience question), and the depth of any page a named function will scrutinise (finance reads the value math, operations reads the timeline). It never puts a stakeholder's name on a slide, with two exceptions: a question addressed to a named person on a discussion page, and an owner named on a next-steps page. Without a roster, the brief's audience line or the prompt governs, and the handoff says the audience was not named.
- An **example deck or template**, mandatory for any file build (below).

**Routing, in this order:**
1. **Deck type**, from the eight in `references/deck-types.md`, confirmed by pop-up at Build entry (below). The type sets skeleton, density, exhibit types, length and register.
2. **Paper and template**, from the example attachment: dark Telesto, light Telesto, or a client template. Paper sets colours, fonts and furniture only. It never sets density.
3. **Page grammar**, chosen per page from the type's palette. Two grammars coexist in one deck. The **visual grammar** is stat rails, option cards, chevrons, timelines, recommendation bands. The **analytical grammar** is bar charts, heatmaps, paired bars, stacked scales, shape-built tables, quote pages, with source and n under every exhibit. A findings deck opens visual, runs analytical, closes visual. A proposal is visual throughout with an analytical page wherever one number needs proof.

**The example attachment is mandatory.** Ask for a prior shipped deck for that client and type, or the current Telesto canon deck, or the client's template. It carries the theme you inherit natively, the title and footnote conventions, and the claims precedent (the assertion level this client has accepted). Do not build a file without one. If the user has none, deliver the page plan and slide text as markdown and say plainly that the .pptx pass is waiting on the template. From the attachment note archetypes present, title style, denominator and footnote conventions, DRAFT-stamp usage and how far claims go; do not inherit typography that breaks the four-homes-for-text rule or the 10-point floor.

Ask only what the inputs do not answer, in one round, and never ask for something the brief states.

**Source data for quant decks.** Ask for the raw survey or data file (xlsx or csv, respondent-level or the crosstab workbook) before the PDF crosstabs; a PDF needs an extraction step and can drop a row or a low-base marker. Accept the PDF if that is all the consultant has, say so once, and note in the report header which form was used. Never ask twice for the same deck.

## Modes

### Build
Inputs in, deck out. A from-scratch build opens with one AskUserQuestion round of up to three questions, each skipped when the inputs already answer it:

1. **Deck type.** Infer it from the prompt and the files and put the inference first with "(Recommended)" and one line of reasoning (page count asked for, data present, audience). Offer the two nearest types with what changes. "A 20-page deck for marketing from this survey file" reads as a findings report (10 to 25 pages, methodology, one or two pages per finding) against a minipack (8 to 11 pages, four findings) or a presentation (8 to 15 pages, larger exhibits, a decision page).
2. **Audience.** When no audience brief is attached: "Run stakeholder-context first (Recommended), attach the roster or invite" against "use the audience as the prompt states it" and "skip". A named audience is what makes the exec summary order and the bands specific.
3. **Materials.** Confirm the example deck or template found and the paper it implies, and the data form (raw xlsx or csv preferred, PDF accepted); ask for whichever is missing.

Then the page plan in text, one line per page with title, exhibit and recommendation, and wait for confirmation before building.

**Sizing the plan.** Length follows the storyline, not the volume of evidence. For each storyline point the skill proposes one page, or two, from the data points that support its title (two exhibits, or a quotes page beside the data), and says which; the consultant, partner or CEO may add a follow-up page where they see one is needed. Fixed pages (cover, summary, methodology, next steps) are added once. The evidence is then triaged against that plan: every survey question and quote theme is placed on a body page, in the appendix, or left out, and the plan closes with the count of each ("14 of 30 questions on body pages, 11 in the appendix crosstabs, 5 unused; 22 of 300 quotes shown") so the consultant sees what the storyline covers and what it leaves. Unused evidence that argues against a storyline point is named, not dropped. The type's typical range is a check on the result, not a target: a five-point storyline with a 30-question survey is 12 to 16 pages, not 25, and the rest of the survey lives in the appendix. After the plan is confirmed, the gate runs with `--no-length`. Build, render, run the gate, and hand off with the review manifest and the next-stage line.

### Revise
An existing deck plus partner comments (in-file, email, or a list). A deck can enter the workflow here at any stage: a human-built draft that has never seen the Build step, a deck with the CEO's comments already on it, a v6 that a colleague edited by hand. Nothing upstream is required. The deck under revision is the example attachment (it carries the paper, the title conventions and the claims precedent), so do not ask for another; ask once for the source data if a comment needs a number the deck does not hold. In-file comments are read from both stores, legacy `ppt/comments/comment*.xml` and modern `ppt/comments/modernComment_*.xml`, with `deck-qc/scripts/pptx_comments.py DECK.pptx` (slide, author, date, status, replies; `--open-only` skips the ones already resolved), and each is quoted with its slide, author and thread before a resolution is proposed. Where the scripts are not available (Cowork without the scripts folder), unzip the file and read the two comment stores by hand; the slide a comment belongs to is the slide whose `_rels` file points at that comment part. Where the comments change the storyline (a finding reordered or added, a page cut, a new closing page), the revised page plan is confirmed in text first. Mechanical comments (typo, renumber, move, denominator) are executed, and so are the evaluator's FIX items (grammar, citations, labels, missing n); its SUGGEST items (titles, bands, exec-summary lines, storyline) are put to the consultant through AskUserQuestion, in slide order, one question per page naming the page number and title, each option quoting the current and proposed line with a leave-as-drafted choice and free text for the consultant's own wording; applied only on approval. In Cowork the same tool is used. Judgment comments (reframe a title, cut a page, soften or sharpen a claim, reorder) get two or three proposed resolutions with a recommendation, then the chosen one is applied. Ambiguous comments ("sharpen this", "make this pop", "tighten") get a targeted question that offers two concrete readings of the ask, each with the line it would produce; never guess what a senior meant. Mark comments resolved rather than deleting them where the format allows; say which comments were left open and why. Output: revised slides plus a comment-by-comment log with before and after text, each comment classed as mechanical, judgment or ambiguous. Build the log from the file, not from memory: `scripts/deck_diff.py BEFORE.pptx AFTER.pptx --comments --ledger-rows` lists every comment in BEFORE next to the changes on its slide and prints the ledger rows with class and resolution left blank; fill those two columns and append the rows to the engagement's revision ledger (`docs/client/revision-ledger.md`, gitignored). When the reviewer's comments have been dealt with, `pptx_comments.py AFTER.pptx --resolve all --out AFTER.pptx` marks the modern-format ones resolved in the file (legacy-format comments have no status and stay as they are); tell the reviewer which numbers were marked. The target is that mechanical and judgment comments resolve without a second prompt; only ambiguous ones need the consultant, and the ledger shows whether that is holding.

**Entering mid-stream.** Most decks will arrive here human-built for some time. On entry, if no audience brief is attached and none sits beside the deck, say so in one line and offer, in text, to run `stakeholder-context` first if a roster or meeting invite is available; then proceed either way. Offer it once per deck, not per round. A brief raises the quality of every SUGGEST written afterwards, because "more strategic" and "so what" need a named stakeholder to aim at.

**Comment shorthand.** Before classifying comments, read `references/comment-shorthand.md`. "More strategic", "what's the so-what", "roll this up", "sharpen", "make it pop", "this doesn't work", "fix", "rewrite" and their kin can each be read more than one way. They are never interpreted automatically, not even the ones that look mechanical. Each raises an AskUserQuestion pop-up for its page, quoting the comment and the element it sits on, with two or three readings and the concrete change each would make; "leave as is" and free text are always offered. Only the chosen reading is applied.

### Rewrite
Titles, an exec summary block, a takeaway rail, or any slide text, no file touched. Full language ruleset; two variants with a recommendation where the framing is a judgment call.

### Learn
The shipped deck plus the last AI draft it came from. Diff title by title and page by page (`scripts/deck_diff.py`), classify every edit as style, structure, number or storyline, and count them. Write the diff summary to the revision ledger. Then propose at most three changes to the rule files, each with the before-and-after that motivates it and its evidence count: a promotion into `house-register.md` (only when the pattern recurs in two decks or the CEO ruled), an entry under "Observed, not yet promoted" in the client file, a retirement, or a new row or reading in `comment-shorthand.md`. A single edit is an observation, not a rule. Nothing is written to a rule file without approval; the register cap holds.

## Ask vs. do

- **Ask (options, a recommendation, the reasoning):** anything the brief leaves open that embeds audience or outcome judgment: page cuts, archetype where two fit, any claim beyond the client's precedent, sensitive figures, any fee, duration or value-at-stake input on a proposal.
- **Do without asking:** everything the brief or files settle, grammar and craft edits, denominator and footnote plumbing, formatting, renumbering, mechanical comment resolutions, the conventions in this skill.

## Language rules (apply to every title, takeaway, and body line)

Principles: `references/language-rules.md`; learned rules: `references/house-register.md`; client formatting and voice: `references/clients/<client>.md`. The non-negotiables:

1. **Action titles are full-sentence takeaways**, verb-led, specific, roughly 8–20 words. A reader who reads only the titles gets the whole argument (the "T" test).
2. **No superlatives or vague intensifiers.** No "significant", "massive", "clear winner", "game-changing". If it matters, quantify it.
3. **Never over-read a single data point.** One number supports "indicates" or "points to", not "proves" or "confirms". A subgroup finding stays a subgroup finding. Small-n cuts are labeled "directional only".
4. **Never invent data.** No number, quote, or source appears unless the user supplied it or it is in the provided material. A missing number becomes `[PLACEHOLDER: source needed]`, never an estimate presented as fact. On proposals this extends to fees, durations, and value-at-stake inputs: `[PLACEHOLDER: builder input needed]`.
5. **Every stat carries its provenance**: question number or source, denominator ("% of respondents selecting attribute · n=250"), and footnote. Quotes carry attribution (role, segment). Proposal value-at-stake math is labeled "Illustrative" with assumptions and their source stated.
6. **Findings and implications stay separate.** A finding states what the data shows. An implication states what to do about it. Do not blend them into one sentence. On proposals, the equivalent discipline is deliverable vs. outcome: the artifact and the client result it enables stay paired but distinct.
7. **Claims precedent (client paper).** Match the assertion level of the client's prior decks. If a proposed claim escalates beyond precedent, flag it: escalation needs account partner sign-off, not your judgment.
8. **Craft:** active verbs, short sentences, no filler, quantified deltas over adjectives ("26pts higher", not "much higher").

**Terminology.** The units are slides and pages. Never call them beats. Spell department and agency names in full on slides.

## Recommendation register

Recommendations are read by Fortune 500 executives who decide for themselves. Prescription and urgency read as junior.

- **No urgency framing.** No "start now", "act immediately", "the window is closing", "time is running out", "planning starts now". On a proposal, urgency is a quantified cost of waiting on its own line, not an adverb.
- **No bare command that removes the client's judgment.** Frame as what the evidence supports and what the client will need to decide: "The client will need a displacement or teaming strategy for the two agencies where incumbents hold the work"; "For discussion: decide by [date] whether displacement or a deal closes the remaining gap".
- A directive verb is fine when it is specific and unhurried ("Decide the 5 to 10 pursuits this quarter"). The fault is urgency and prescription, not the imperative mood.
- **Every recommendation names the action, and where the material allows it the owner, the cost and the date.** A recommendation carrying none of the four is a slogan.
- **No stakes inflation.** "This represents a pivotal opportunity to transform…" is the AI signature on a recommendation slide. Say what changes and by how much.

## Typography floor, every paper

- **Nothing below 10pt except a footnote.** Body text, chart labels, axis labels, table cells, stat-rail captions, eyebrows, recommendation bands, source lines: all 10pt or larger. The footnote home is the only place a smaller size is allowed, and only when the footnote would otherwise not fit. If text needs to be smaller than 10pt to fit, the page carries too much: cut, split the page, or footnote it.
- **Italics and grey detail text are exceptions, not a style.** The test for every page: the title, the body text or the footnote carries everything a reader needs in a five-second scan. Small italic or grey text added to squeeze in more detail is the AI habit that defeats that scan, so the draft uses none of it; the gate lists a handful of italic or grey runs per deck and blocks above four. Quotes are set roman inside quotation marks with their attribution in the same size. Emphasis comes from bold or from the sentence itself. Chart subtitles, source lines and captions are roman. An attachment that uses italics does not license them.
- **Few sizes per page.** Title, one body size, one footnote size is the norm. One font size within any table.

## Depth: spend it by role

A flat page is the most common failure of a dark deck, and the fix is not shadow everywhere. Border, fill, radius and shadow each announce "separate object", so assign them by role and lift only what should sit forward:

- **Spine elements** (a chevron strip, a process row, the one card carrying the recommendation) take a gradient fill plus a soft drop shadow. The gradient runs lighter at the top to darker at the bottom, roughly +26 and −14 on each RGB channel of the base colour. Shadow: about 11pt blur, 5pt distance, 60% black, straight down.
- **Content cards** take a subtle gradient only, around 383838 down to 2D2D2D on the 282828 ground, with no border and no shadow. They read as surfaces on the page rather than objects above it.
- **Borders stay reserved for status.** A teal outline means selected, active, recommended, or a gate. A grey hairline on every card dilutes that signal, so do not add one.

One shadow stamped on every block flattens the hierarchy again, which is the problem it was meant to solve.

## Attribute labels are verbatim

Treat every quotation from Telesto's own research, an attribute, an answer option, a scale point, a segment name, a question, as a citation that will be checked against the source in the room. Full context, every time: the label as worded, the question it came from, the base it rests on. A consultant may decide to shorten; the AI never does.

Every survey attribute, answer option, segment name and scale point appears on the slide exactly as it was worded in the questionnaire and crosstab: chart category labels, table rows, stat sentences, callouts and prose alike. Never shorten, paraphrase or drop a qualifier. "Point-of-view perspectives on strategy" is not "point-of-view pieces"; "Insights and data about higher education trends and challenges" is not "sector insights"; "New market entrants that are heavily leveraging AI" is not "New market entrants leveraging AI". A dropped word changes what respondents were asked and invites the question the deck cannot answer in the room.

Where the verbatim label does not fit the space, the fix is layout, not wording: widen the label column, allow a two-line label, reduce the number of rows shown and say so in the subtitle, or move the exhibit to a page with room. If none of those works, the shortened label is a SUGGEST to the consultant with the verbatim wording beside it, and the verbatim label goes in the footnote. In prose, quote the option in full the first time; a short form is allowed afterwards on the same page only if the full label is on the page. Segment names follow the crosstab headers ("VP/Dir", "Other 4-year") or their evident expansion, never a new coinage.

## Footnote convention

- **Question-level citations use numbered superscripts.** Where a figure, quote set or exhibit draws on a survey question, a superscript ¹ ² ³ sits on the word, number, subtitle or column head it supports, and the footnote reads "1. Q21. How would you characterize the current state of AI adoption at your institution?" with the question wording verbatim, never paraphrased, then the survey name and n. Free-response quotes are cited the same way: the marker on the section subtitle, the footnote giving the question and that it was free response.
- **"Source:" is for external material.** A website, a report, a different survey from the rest of the deck, a client dataset: "Source: Semrush API, US database, pulled 10 September 2026." A sister survey used beside the main one takes a numbered footnote that names it ("2. Q31. … 2026 Healthcare Intelligence Survey, n=300").
- Every marker has its footnote on the same page and every footnote has its marker; the gate checks both directions.

## Word budget

A body page carries at most 200 words of title, body and chart labels before the gate warns and 275 before it blocks; footnotes are counted apart (warn above 100) and appendix pages are exempt, as are pages that are mostly verbatim quotes. A wordy page draws a partner comment before anything else on it is read. Exec summaries may run long but sit under the same cap: keep percentages to a minimum there and explain the finding in words; a summary line with four figures in it is a table, not a sentence. Detail pages carry the numbers.

## Match the deck, not your constants

When adding a page or an element to an existing deck, copy the style of the nearest element of the same kind already in the deck: section subtitle colour and size, the colour and weight of the rule line beneath it, footnote colour and size, chart label colour, band fill and lead-in colour. Read them from the file, never from a palette constant. A page that is right by the house palette but differs from the pages beside it reads as built by another hand, and the consultant spends the review recolouring lines. Elements that recur across pages (numbered indicator boxes, section subtitles, rule lines, callout boxes, bands) match each other; the deck may use two or three line colours, but a fourth on one page is a defect. The gate lists rare colours per element class as `element-consistency`; the render step then looks at the pages side by side.

## References, and when to read them

The core above holds the rules every mode needs. The rest is in `references/`, read by mode, so a Revise round does not carry Build material:

- `language-rules.md`: principles for titles, claims, provenance and craft. Read on every Revise, Rewrite and Learn.
- `house-register.md`: firm-wide writing rules learned from shipped decks, capped at 25, each with one example and its evidence. Read on every Revise, Rewrite and Learn. Governance (entry, conflict, retirement) is at the top of the file.
- `clients/<client>.md`: the client's layouts, palette, table and chart formatting, voice, claims precedent, and single-deck observations not yet promoted. Read when the paper is that client's; if no file exists for the client, say so and draft from the attached deck alone.
- `comment-shorthand.md`: reviewer phrases that go to a pop-up with readings. Read on every Revise.
- `voice-review.md`: the de-AI pass. Read at handoff of a Build or a full rewrite.
- `build-rules.md`: native and editable build rules, construction conventions, density, versioning, rating columns, Telesto dark paper. Read at Build and when a Revise adds a page or element.
- `deck-types.md`: the eight deck types as the elements each usually carries, plus recurring page patterns. Read at Build, or when a Revise changes the storyline.

## Handoff

Every Build ends with two things alongside the file:
- **Review manifest:** every `[PLACEHOLDER]`, every figure whose source is weakest, every claim near the client's precedent ceiling, and any storyline line from the brief that the evidence did not support. When an audience brief was attached, list any audience question the deck does not answer.
- **QC self-check** against the four scored dimensions the QC bot uses: clarity of outcome and recommendation, logical flow (does the title chain hold end to end, is any explaining or transition page missing), financial value at stake, technical accuracy. State where the draft is weakest. The bot's score is the consultant's to run, in a separate session from this one; your job is to arrive with the obvious flags already fixed.

## Numbers and their source of truth

- **A deck never becomes the source of truth for a number.** Where the engagement has a dashboard, model, survey explorer or backing workbook, that artifact is authoritative and the deck follows it. When the two disagree, fix the deck; if the dashboard is the one that is wrong, fix the dashboard first and restate the deck from it.
- **Restating one number means sweeping every page that depends on it**, including secondary aggregates and chart caches, not only the headline.
- **Derive displayed figures from the unrounded base.** Rounding an already-rounded published figure puts the deck one tick away from its source.

## What this skill never does

- Invent or estimate data, quotes, sources, fees, or durations, including during a voice edit.
- Interview the consultant for what the prompt, the brief or the files already state, or ask for a dot-dash.
- Build a file without an example deck or template to inherit from.
- Escalate a claim beyond the client's precedent without flagging it.
- Add decorative elements, icons, or styling flourishes as a substitute for content.
- Scatter small or grey context text outside the four text homes, set any text below 10pt outside a footnote, or use italics as a style.
- Stamp one shadow, one border and one radius on every block.
- Build narrator-dependent speaking slides (an image plus a phrase). Presentation decks are in scope; every page still passes the standalone test.
- Guess at an ambiguous senior comment; the shorthand in `references/comment-shorthand.md` always goes to a pop-up with readings.
- Make legal or regulatory judgments the dataset does not support.
- Name the client stakeholder on a slide, whether from the brief or from an audience brief.
- Chase an AI-detector score.

## After saving

Every build or revision ends by running the deck-qc gate and the render on the saved file and fixing what they find. The closing message then names the next stage in one line: "Gate and render pass. Next: run the evaluator. Say 'run the evaluator on FILE'." The consultant should never have to remember what comes after a save; the reminder carries it (stage list in deck-qc, "The chain").
