---
name: draft-deck
description: "Build first-draft consulting decks in Telesto house style from a Build Brief, a prompt, or files (survey data, crosstabs, transcripts, notes, prior decks), on Telesto or client paper, across seven deck types with findings reports and proposals as the priority types. Also resolves partner comments on an existing deck and rewrites titles, exec summaries or slide text. Triggers include \"draft the deck\", \"build the deck from this brief\", \"build the findings report\", \"survey report\", \"draft a proposal\", \"BD deck\", \"resolve these comments\", \"rewrite this title\", \"kickoff deck\", \"minipack\", \"update deck\", \"workshop materials\". Synthesis and executive writing first, aesthetics second."
---

# Draft Deck (Telesto) — v2.2

You produce the first draft that a trained consultant screens. The team is small and the draft has to arrive fast and close to finished, so you build directly from what you are given and ask only for what is missing. You still state your reasoning as you work, so the reviewer can challenge a call without re-deriving it.

Content and layout outrank styling. Never spend effort on lines, icons, or decoration at the expense of the storyline, the titles, or the evidence.

## The invariant

Every Telesto deck produces a call to action or a discussion, supported by statistics, quotes or data visualization, and it works at two reading speeds. Read only the titles on a phone and the message lands in 20 seconds. Read every chart and footnote for 30 minutes and nothing is ambiguous, unexplained or unsourced. Both tests apply to every type and every page. Density is not a style choice; it is set by the deck type and by each page's job.

## Division of labour: the AI phase builds the core three, a human adds the polish

Every slide has three things at its core, and they are what this skill spends its effort on:

1. **The title and message.** Is this the right claim for this room, given what the stakeholders need to hear and what Telesto can realistically recommend? The title is the takeaway; if it could move to another client's deck, it is not finished.
2. **The exhibit.** The one chart, table or quote set that shows the data behind the claim, native and editable, sourced and denominated.
3. **The recommendation.** What this changes or informs: the band that closes the page, in the recommendation register.

Everything else this skill knows about a finished page still applies (the edit patterns, the construction conventions, the paper), and callouts or highlights that carry data belong in the AI phase too: a highlighted bar, a delta called out beside a chart, a bolded number in a band. What waits for a human is the styling preference layer: decorative colour, icons, badges, spacing polish. The order of effort matters because the consultant should be thinking like a partner about what the page says in the larger story, not like an executor placing elements; placing elements is the cheap part.

**Confirm the storyline in text before building anything.** For a first draft, and whenever a comment or a new input changes the storyline (which pages exist, in what order, with which exhibit), write the page plan as text first: one line per page with the title, the exhibit it carries and the recommendation it closes on. Wait for the consultant's confirmation, then build. This holds even when a Build Brief is attached: the brief settles the takeaway and the storyline lines, and the page plan is still shown before the file exists. It saves time and tokens on both sides.

## Inputs and routing

There is no dot-dash step. The storyline comes from the inputs and you produce the page plan from them.

**Inputs, any combination:**
- The approved **Build Brief** slide, optional and produced only on request. The consultant's prompt and the client context (prior decks, the audience brief, the files) are the main inputs to a v1 draft; a brief is worth the round trip when the package includes a product or engineer time. When attached, it holds the takeaway, goal, audience, value at stake, client needs, storyline lines, format and open items. When it is attached, the storyline is settled and you build without re-asking.
- A **prompt**. When no brief exists, draft the brief blocks from the prompt in a few lines, state them, and proceed.
- **Files**: survey data or crosstabs, quote repositories or transcripts, prior analysis, notes, a prior deck, a dashboard export. Files are the evidence; every number and quote in the deck traces to one of them.
- An **audience brief** (optional): a short list of who will be in the room, their titles and responsibilities, and the questions each needs answered, produced from the meeting roster by the `stakeholder-context` skill. When a roster, invite or attendee list is among the inputs and no audience brief is attached, run `stakeholder-context` first and build from its output; client context with a named audience is what sharpens the message and sets the storyline order, so it is not optional when the roster is known. When attached, it shapes the executive summary order (the sponsor's question first), the open-discussion page (one prompt per unanswered audience question), and the depth of any page a named function will scrutinise (finance reads the value math, operations reads the timeline). It never puts a stakeholder's name on a slide. Without a roster, the Build Brief's audience block or the prompt governs, and the handoff says the audience was not named.
- An **example deck or template**, mandatory for any file build (below).

**Routing, in this order:**
1. **Package**, from the brief or inferred: 1 Services · 2 Services + product · 3 Product. Under 1 all seven deck types apply. Under 2 all seven apply and the proposal, findings report and update change shape. Under 3 the deck explains or sells the product: proposal, explainer and update apply; the rest rarely do.
2. **Deck type**, from the seven below. The type sets skeleton, density, exhibit types, length and register.
3. **Paper and template**, from the example attachment: dark Telesto, light Telesto, or a client template. Paper sets colours, fonts and furniture only. It never sets density.
4. **Page grammar**, chosen per page from the type's palette. Two grammars coexist in one deck. The **visual grammar** is stat rails, option cards, chevrons, timelines, recommendation bands. The **analytical grammar** is bar charts, heatmaps, paired bars, stacked scales, shape-built tables, quote pages, with source and n under every exhibit. A findings deck opens visual, runs analytical, closes visual. A proposal is visual throughout with an analytical page wherever one number needs proof.

**The example attachment is mandatory.** Ask for a prior shipped deck for that client and type, or the current Telesto canon deck, or the client's template. It carries the theme you inherit natively, the title and footnote conventions, and the claims precedent (the assertion level this client has accepted). Do not build a file without one. If the user has none, deliver the page plan and slide text as markdown and say plainly that the .pptx pass is waiting on the template. From the attachment note archetypes present, title style, denominator and footnote conventions, DRAFT-stamp usage and how far claims go; do not inherit typography that breaks the four-homes-for-text rule or the 10-point floor.

Ask only what the inputs do not answer, in one round, and never ask for something the brief states.

## Modes

### Build
Inputs in, deck out. Infer package, type and paper; ask once for anything missing. Produce the page plan as text, one line per page with title, exhibit and recommendation, and wait for confirmation before building; a Build Brief settles the storyline but the plan is still confirmed. Build, render, self-check, then hand off with the review manifest (below).

### Revise
An existing deck plus partner comments (in-file, email, or a list). In-file comments are read from both stores, legacy `ppt/comments/comment*.xml` and modern `ppt/comments/modernComment_*.xml`, and each is quoted with its slide, author and thread before a resolution is proposed. Where the comments change the storyline (a finding reordered or added, a page cut, a new closing page), the revised page plan is confirmed in text first. Mechanical comments (typo, renumber, move, denominator) are executed. Judgment comments (reframe a title, cut a page, soften or sharpen a claim, reorder) get two or three proposed resolutions with a recommendation, then the chosen one is applied. Ambiguous comments ("sharpen this", "make this pop", "tighten") get a targeted question that offers two concrete readings of the ask, each with the line it would produce; never guess what a senior meant. Mark comments resolved rather than deleting them where the format allows; say which comments were left open and why. Output: revised slides plus a comment-by-comment log with before and after text, each comment classed as mechanical, judgment or ambiguous. Append the log to the engagement's revision ledger (`docs/client/revision-ledger.md`, gitignored) with deck, version and date. The target is that mechanical and judgment comments resolve without a second prompt; only ambiguous ones need the consultant, and the ledger shows whether that is holding.

### Rewrite
Titles, an exec summary block, a takeaway rail, or any slide text, no file touched. Full language ruleset; two variants with a recommendation where the framing is a judgment call.

### Learn
The shipped deck plus the last AI draft it came from. Diff title by title and page by page, classify every edit as style, structure, number or storyline, and count them. From the style and structure edits, propose patterns for the title rewrite table and the word list, each with the before and after that motivates it. Read the revision ledgers and the gate's findings for the same decks alongside the diff: a class of comment or flag that recurs across decks is a rule the draft should already follow, and is proposed as one. Nothing is added to this skill without approval; the output is a proposal list and the counts, which feed the prompts-per-deck measure. Rules change when people change their minds: a proposal may also retire or loosen an existing rule when the ledger shows partners now accept what it forbids.

## Ask vs. do

- **Ask (options, a recommendation, the reasoning):** anything the brief leaves open that embeds audience or outcome judgment: page cuts, archetype where two fit, any claim beyond the client's precedent, sensitive figures, any fee, duration or value-at-stake input on a proposal.
- **Do without asking:** everything the brief or files settle, grammar and craft edits, denominator and footnote plumbing, formatting, renumbering, mechanical comment resolutions, the conventions in this skill.

## Deck types

Full spec with skeletons and package variants: `references/deck-types.md`. Two types take most of the firm's hours and scrutiny and are specified in detail here; the minipack has a fixed shape; the other four are compact.

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

## Language rules (apply to every title, takeaway, and body line)

Full rules and examples: `references/language-rules.md`. Formatting conventions by paper: `references/deck-craft.md`. The non-negotiables:

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
- **No bare command that removes the client's judgment.** Frame as what the evidence supports and what the client will need to decide: "Huron will need a displacement or teaming strategy for VA and DHA"; "For discussion: decide by mid-2027 whether displacement or a deal closes the last $45M".
- A directive verb is fine when it is specific and unhurried ("Decide the 5 to 10 pursuits this quarter"). The fault is urgency and prescription, not the imperative mood.
- **Every recommendation names the action, and where the material allows it the owner, the cost and the date.** A recommendation carrying none of the four is a slogan.
- **No stakes inflation.** "This represents a pivotal opportunity to transform…" is the AI signature on a recommendation slide. Say what changes and by how much.

## Voice review pass — run before handoff, as a separate pass

Draft first, then review against the named patterns below. A single up-front instruction to "not sound like AI" does not hold: these patterns are optimised into the model and regenerate under pressure, so they have to be hunted deliberately. (Juzek and Ward, COLING 2025, traced them to instruction tuning rather than training data.)

Report what you changed. Never invent or alter a fact while de-slopping; a voice edit that moves a number is worse than the slop it replaced. Do not score the draft for "how AI it sounds", and never target an AI-detector result: detectors have real error rates, and the objective is that an experienced partner reads the page as competent human work.

### Tier 1 — fix on a single sighting

- **Negative parallelism.** "It's not X, it's Y", "not just X but Y", "Y rather than X", and the split forms ("This does not mean X. It means Y." / "The question isn't X. The question is Y."). Keep the contrast only when the negated half is a belief the reader actually holds.
- **Participle riders.** A trailing `-ing` clause that attaches hollow significance to a plain fact: "…, highlighting the need for continued investment", "…, underscoring the shift", "…, reflecting a broader trend". Also *emphasizing, showcasing, ensuring, fostering, contributing to*. Instruction-tuned models produce these at 2 to 5 times human rates (Reinhart et al., PNAS 2025). Cut the clause, or make it a sentence with a subject.
- **Nominalized, verbless titles.** "Operational efficiency improvement opportunities across the supply chain footprint." Force a finite verb and a number. Prefer Saxon words to Latinate ones: *use* not *utilize*, *help* not *facilitate*, *build* not *establish*.
- **Importance puffery.** "marks a pivotal moment", "stands as a testament to", "plays a key role in", "underscores its significance", "solidifies its position", "sets the stage for", "reflects a broader shift".
- **Vague attribution.** "experts agree", "studies show", "industry reports suggest", "many argue", "widely regarded as". In a client deliverable this is a liability as well as a tell. No source, no claim.
- **Throat-clearing and self-answered questions.** "Here's the thing", "Let me be clear", "What nobody tells you", "Let's unpack", "The result? Devastating."
- **Arguing with no one.** "I'm not saying…", "Don't get me wrong…", "Some might say… but". Residue from an earlier draft; delete it.
- **Copula avoidance.** *serves as, stands as, functions as, represents a, boasts, features* where *is* or *has* is the word.
- **Summary-restating closers.** A "Key takeaways" page that repeats the action titles verbatim; a "Path forward" that names no owner and no date; "In conclusion", "Ultimately", "Overall".
- **The "Despite these challenges…" formula** and the stock risks-then-reassurance page.
- **False agency.** "the decision emerges", "the culture shifts", "the data tells us". Name who did it.
- **Chatbot residue.** "Great question", "Certainly", "I hope this helps", "Would you like me to".

### Tier 2 — fix only when they cluster on a page

Em dashes; three-item lists; stacked hedges ("could potentially", "might arguably"); three or more consecutive sentences opening the same way; curly quotes and unicode arrows; long sentences chained by "and" with no internal punctuation. Any one of these alone is ordinary writing.

### Word list, dated

Recheck annually. The vocabulary drifts by model generation, and a word that was a tell in 2024 may not be one now. Never extend a flagged word to its synonyms; that only flattens the prose.

- **Doyoung edits these out on sight:** earned, already, carry / carries, load-bearing, recast, hypothesis, "this confirms [client]".
- **Business-register tells:** leverage (verb), utilize, facilitate, empower, streamline, harness, navigate (challenges), unpack, lean into, double down, robust, comprehensive, crucial, pivotal, key (adjective), landscape (abstract), realm, testament, underscore (verb), delve, showcase, seamless, ecosystem, transformative, game-changer, paradigm shift, ever-evolving, multifaceted, at its core, in today's [X], it's worth noting, when it comes to, going forward.
- **Consulting hollow-speak:** force multiplier, boil the ocean, synergies, move the needle, low-hanging fruit, north star, at pace.
- **Empty intensifiers:** just, really, literally, genuinely, honestly, simply, actually, truly, deeply, fundamentally, inevitably, remarkably, arguably.
- **Em dashes in original prose:** replace with commas, full stops, or restructure. Claude over-uses them relative to professional human writers (The Economist, July 2026, 55,940-sentence corpus study), so the rule is worth keeping for this stack even though the popular version of it is now wrong for other models. Verbatim quoted material keeps its own punctuation.

### Titles: patterns Telesto rewrites out

| Rewrite this | Into this | Rule |
|---|---|---|
| "Adjacency quadrant: 35 federal markets" | "We ranked 35 federal service markets by size and closeness to Huron's core" | No label-colon opener |
| "Entrenchment is agency-specific" | "Booz Allen, Deloitte, Accenture and Leidos hold established positions" | No abstract-noun subject |
| "VA, DoD and HHS rank must-win" | "VA, DoD and HHS are must-win agencies" | No compressed verb-noun |
| "Each agency needs its own version" | "Most common topics leaders cited as challenge or priority include EHR, workforce and AI" | No prescription in a title |
| "Each draws criticism from the leaders who used them" | "Some leaders commented on uneven quality of work" | Softer verb when a named firm is the subject |

**Portability test, the single highest-yield check.** Read each action title and each recommendation line and ask whether it could move unchanged to another client's deck. If it could, it is not a finding. A title that passes makes a claim someone could disagree with, is specific to this client, and carries a number.

### What is NOT a tell, and must not be "fixed"

General anti-AI advice will damage a consulting deck if applied literally. These stay:

- **Formal register.** Formality is not a tell; specific words are. Do not colloquialize a findings deck.
- **Bold-lead bullets** (`**Label:** text`) in slide bodies and recommendation boxes. A tell in continuous prose only.
- **Title case in deck headers and column headings.**
- **Three-item structures** where the content genuinely has three parts. The test is whether you could defend dropping the weakest item: if yes it was padding, if no it is MECE.
- **Named frameworks and coined labels** that the deck defines and evidences. Naming a construct is half of what the client is buying. The fault is a coined label deployed as shorthand for an argument never made.
- **Passive voice in itself.** The real fault is nominalization and missing actors; instruction-tuned models use agentless passive at roughly half the human rate.

## Typography floor, every paper

- **Nothing below 10pt except a footnote.** Body text, chart labels, axis labels, table cells, stat-rail captions, eyebrows, recommendation bands, source lines: all 10pt or larger. The footnote home is the only place a smaller size is allowed, and only when the footnote would otherwise not fit. If text needs to be smaller than 10pt to fit, the page carries too much: cut, split the page, or footnote it.
- **Italics and grey detail text are exceptions, not a style.** The test for every page: the title, the body text or the footnote carries everything a reader needs in a five-second scan. Small italic or grey text added to squeeze in more detail is the AI habit that defeats that scan, so the draft uses none of it; the gate lists a handful of italic or grey runs per deck and blocks above four. Quotes are set roman inside quotation marks with their attribution in the same size. Emphasis comes from bold or from the sentence itself. Chart subtitles, source lines and captions are roman. An attachment that uses italics does not license them.
- **Few sizes per page.** Title, one body size, one footnote size is the norm. One font size within any table.

## Telesto dark paper (2.0)

The 2.0 house paper is dark and built for screen. It is the default for Telesto-paper work unless the user asks for the light template; client paper is unaffected. Dark does not mean sparse: a survey report on dark paper is as chart-heavy as the type demands. Reference artifacts: ULSE/TRIP and Rotary (proposals), Re-rebrand (findings), the Vanguard Standard v2 deck (the manual).

**Inherit the template, do not rebuild it.** Open the current Telesto deck or template and add slides from the layout named `Blank (Contrast - Corner Image Ready)`. That layout carries the dark ground, the logo, the copyright line and the page number, so none of those get drawn by hand. Delete every placeholder except the title on each new slide.

**Palette, from the theme:** ground 282828 · card 333333 · teal 009999 (accent5) · bright cyan 0BD0D9 (accent3) · deep teal 005366 · navy 003366 · body white · muted 8A8F92 for inactive navigation and non-focus chart series only. Arial throughout.

**Title.** Anchor the title text frame to the TOP, so one-line and two-line titles both sit directly under the eyebrow. 22pt bold white, left edge 0.61 in, width 12.12 in. No smaller sub-headline under the title; a category label slot is fine.

**Eyebrow.** A numbered eyebrow above the title is the storyline spine: `01 THE STAKES`, `02 THE RESPONSE`, or `01`, `02` on finding pages. The manual's variant is a multi-segment tracker with the active segment lit in teal and the rest muted; client decks use the single numbered eyebrow.

**Analytical pages on dark paper.** Bars single-hue teal, with muted grey for non-focus series and a lighter teal for the highlighted item. Data labels white, outside the segment. Heatmaps in teal tints from ground to full teal, values white. Tables built from shapes, bucket labels in teal-tinted feature boxes to the left of the rows, one font size within a table. Source line and n under every exhibit, full size, white or muted; never small grey.

## Depth: spend it by role

A flat page is the most common failure of a dark deck, and the fix is not shadow everywhere. Border, fill, radius and shadow each announce "separate object", so assign them by role and lift only what should sit forward:

- **Spine elements** (a chevron strip, a process row, the one card carrying the recommendation) take a gradient fill plus a soft drop shadow. The gradient runs lighter at the top to darker at the bottom, roughly +26 and −14 on each RGB channel of the base colour. Shadow: about 11pt blur, 5pt distance, 60% black, straight down.
- **Content cards** take a subtle gradient only, around 383838 down to 2D2D2D on the 282828 ground, with no border and no shadow. They read as surfaces on the page rather than objects above it.
- **Borders stay reserved for status.** A teal outline means selected, active, recommended, or a gate. A grey hairline on every card dilutes that signal, so do not add one.

One shadow stamped on every block flattens the hierarchy again, which is the problem it was meant to solve.

## Concept pages get real visual grammar

A page explaining a continuum, a process, a set of gates or a sequence is drawn in the grammar of that idea: chevrons for a progression, arrows between nodes, an explicit gate mark where approval happens, a loop-back arrow where work returns to be fixed, a timeline where dates matter. A row of cards standing in for a diagram is the thing to avoid. Let the shape carry the meaning: where a step is advisory rather than blocking, draw it as a loop, not a gate.

Icons earn their place where a set of items is scanned rather than read, such as scored dimensions or archetype tiles, and in front of each statement on an implication or recommendation page in place of accent bars. Render them from one icon family to teal PNGs at 256px and place them at about 0.34 in. Never scatter icons as decoration.

## Build rules — native and human-editable, nothing hardcoded

1. **Inherit, don't invent.** Duplicate slides from the attached shipped deck that match the target archetype, then replace text. This carries theme colors, fonts, footers, and page furniture natively. Build a slide from scratch only when no archetype in the attachment fits.
2. **Native elements only.** Text boxes, shape-built tables, native charts with editable data. Never render text or charts as images. Never use SmartArt or grouped decorative constructions the user can't easily pull apart.
3. **Charts come from the data files.** Read the crosstab, survey export or workbook, compute the displayed figures from the unrounded base, and bind them into native charts. State metric and denominator in the chart subtitle. State trimming explicitly (no silent top-N). Where a chart's data lives in a think-cell object, patch the cache in `ppt/charts/chartN.xml`; never `chart.replace_data()` on it.
4. **No hardcoded styling.** Colors and fonts come from the deck theme (scheme colors), not pasted hex values, wherever the format allows. A human opening the file must be able to edit any element the ordinary way.
5. **Keep the deck's evidence furniture**: DRAFT stamp on working pages, copyright footer, page numbers, question-number footnotes, denominator lines.
6. **One idea per page.** If a storyline line needs two ideas, it needs two pages.
7. **Four homes for text** (`references/deck-craft.md`): action title, chart/table title, content text box, footnote. No small or grey text outside a footnote; few font treatments per page; one font size within any table. The typography floor above applies: 10pt minimum outside footnotes, italics and grey text only as rare exceptions. This rule overrides habits found in the attachment.
8. **Tables hold data, not prose pairs.** Deliverables→outcomes and similar paired lists are built as individual text boxes with drawn rules and numbered ovals. Multi-item cells become bullets, never semicolon runs. Where a column is headed Quotes, the cells hold verbatim quotes.
9. **Preserve bold-lead runs when replacing text.** A find-and-replace spanning both runs collapses the paragraph into the bold run. Edit only the runs the match touches.
10. **File integrity.** python-pptx API for slide content. Raw XML is permitted in exactly two places: the chart-cache patch, and `a:effectLst` (shadows) or `a:gradFill` (gradients) on shapes you created yourself. Never let two slides share an embedded OLE object: when duplicating a slide carrying hidden think-cell data, strip the object from the duplicate. Validate against the original file before handing off.
11. **Leave the author / core-properties author field empty** on every generated file.
12. Work with the pptx skill's mechanics for unpacking, duplicating (`add_slide.py`), editing slide XML, and validating. Content QA: no leftover placeholder text from the source slides, no orphaned visuals after text replacement.
13. Apply `references/deck-craft.md` for client-paper specifics (Huron/EDR titles, tables, charts, callouts, footnotes, versioning). A freshly attached shipped deck beats it, except where the four-homes rule or the typography floor says otherwise.
14. **Look at the render before handing off.** Convert to PDF with the pptx skill's soffice wrapper, rasterise with pdftoppm, and view every page. Overlaps, overflow, stranded titles and hanging single words on a last line are invisible in the XML and obvious in the image. Fix (widen the box, or reword a few words), re-render, then send.

## Word budget (set 2026-09-12)

A body page carries at most 200 words of title, body and chart labels before the gate warns and 275 before it blocks; footnotes are counted apart (warn above 100) and appendix pages are exempt, as are pages that are mostly verbatim quotes. A wordy page draws a partner comment before anything else on it is read. Exec summaries may run long but sit under the same cap: keep percentages to a minimum there and explain the finding in words; a summary line with four figures in it is a table, not a sentence. Detail pages carry the numbers.

## Construction conventions (house, every paper)

Stated by the CEO 2026-09-12. They override habits found in an attachment.

- **Text boxes are zero-margin and top-anchored.** Every text box you create has all four insets at 0 and its text anchored to the top, so edges align to the grid and a one-line and a three-line box start at the same height. python-pptx: `tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0` and `tf.vertical_anchor = MSO_ANCHOR.TOP`. The gate lists departures as information.
- **Section subtitles are a bold line with a rule beneath.** A section or panel inside a page is announced by a bold subtitle at 14 or 16pt and a thin horizontal line directly below it, not by a filled band or a box. One subtitle size per page.
- **Tables are lines and text boxes, not the native table feature.** The consulting table of roughly four columns and three to five rows is built from one text box per cell, aligned on a grid, with thin horizontal divider lines between rows and a bold header row; no vertical rules, no cell fills. Multi-item cells are bullets. The native PowerPoint table is reserved for large tables (more rows or columns than fit that construction) and for heatmaps, where cell fills carry the data. The gate warns on a small native table.
- **Bar charts keep the Y axis line.** The category axis is drawn as a thin ink line with no tick marks and no native labels; the label column to its left carries the attributes. Data labels sit outside the bar end.
- **Chart subtitles fit on one line under the section rule.** The metric-and-denominator line ("% of buyers · Q2 and Q23 · n=302") must not spill below the rule. When it does, either give the box two lines and make sure the second line holds more than one word, or rephrase to fit one line. Never leave a single orphan word on a second line anywhere.
- **Conclusion and discussion pages read left against right.** "What the findings add up to" on the left, "For discussion" (or "Implications", "Next") on the right, each under its own bold subtitle and rule, not stacked.
- **Charts are native and editable, and match the think-cell look.** think-cell was the house tool and remains available but is not required. A native chart must keep its data editable (never a picture) and match the established format: category labels as a column of left-aligned text boxes sharing one left edge, data labels outside the bars, one series colour with a muted colour for non-focus series, no gridlines, no legend where one series is shown, source and denominator line beneath. Where a chart's data lives in an existing think-cell object, patch its cache; do not rebuild it.

## Lessons from the first live Revise (EDR AI minipack, 2026-09-12)

- **Use the client's plain layouts.** On Huron paper the team uses two or three: the cover ("Cover Option 1"), the white content page ("Content Header Only", title across the top, footer and page number placeholders), and the divider ("Divider Option 1"). Layouts whose name starts with a number ("1_Content Header Only", "3_…", "4_…") carry a coloured side panel and are for select pages only; a finding page never goes on one. Take footer and page-number placeholders from the layout, never by copying them from another slide.
- **Look at the page before handing it over.** Estimates of overflow and overlap from the XML are not enough. On Windows, `deck-qc/scripts/render_check.py` exports each body page to PNG through PowerPoint and lists every text frame whose text is taller than its box; look at the PNGs. Elsewhere, soffice and pdftoppm. A page is not built until it has been seen.
- **The eyebrow number is a finding number, not a page number.** Two pages that both support finding 1 both carry "1". Never renumber to make pages consecutive.
- **Chart attribute labels are black.** The category label column, the data labels and the segment headers are ink; aubergine and the client accent are for the highlighted bar and for bold lead-ins only.
- **Do not write "the good news" or "the bad news".** State the positive fact under a neutral head ("Where Huron already stands") and let the number carry it.
- **Appendix and data pages stay as they are.** Crosstabs, backup exhibits and methodology pages are not restyled, resized or re-fonted by the AI phase or by the gate; smaller type is allowed there. Only hygiene (author, notes, metadata) applies to the whole file.
- **When a text run is reused, reset its formatting.** A first run inherited from an old paragraph can carry a hyperlink, an underline or a colour; strip them and set colour, size and weight explicitly, or the new text comes out pink and underlined.

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
- Interview the user for what the brief or the files already state, or ask for a dot-dash.
- Build a file without an example deck or template to inherit from.
- Escalate a claim beyond the client's precedent without flagging it.
- Add decorative elements, icons, or styling flourishes as a substitute for content.
- Scatter small or grey context text outside the four text homes, set any text below 10pt outside a footnote, or use italics as a style.
- Stamp one shadow, one border and one radius on every block.
- Build narrator-dependent speaking slides (an image plus a phrase). Presentation decks are in scope; every page still passes the standalone test.
- Guess at an ambiguous senior comment.
- Make legal or regulatory judgments the dataset does not support.
- Name the client stakeholder on a slide, whether from the brief or from an audience brief.
- Chase an AI-detector score.