# Voice review pass (moved from SKILL.md 2026-09-13, text unchanged)

Read at the handoff of a Build or a full rewrite, and whenever a Revise rewrites more than a title or a band. Not needed on gate-fix iterations.

This pass hunts classes of pattern that instruction-tuned models produce at above-human rates, with the research that identified them. It is not a register of house preferences: a single reviewer edit never becomes a rule here. House and client wording preferences live in the house register and the client files (see SKILL.md, References), and reach this pass only as the word list below, which is reviewed annually and capped.

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

- **Business-register tells:** leverage (verb), utilize, facilitate, empower, streamline, harness, navigate (challenges), unpack, lean into, double down, robust, comprehensive, crucial, pivotal, key (adjective), landscape (abstract), realm, testament, underscore (verb), delve, showcase, seamless, ecosystem, transformative, game-changer, paradigm shift, ever-evolving, multifaceted, at its core, in today's [X], it's worth noting, when it comes to, going forward.
- **Consulting hollow-speak:** force multiplier, boil the ocean, synergies, move the needle, low-hanging fruit, north star, at pace.
- **Empty intensifiers:** just, really, literally, genuinely, honestly, simply, actually, truly, deeply, fundamentally, inevitably, remarkably, arguably.
- **Em dashes in original prose:** replace with commas, full stops, or restructure. Claude over-uses them relative to professional human writers (The Economist, July 2026, 55,940-sentence corpus study), so the rule is worth keeping for this stack even though the popular version of it is now wrong for other models. Verbatim quoted material keeps its own punctuation.


**Portability test, the single highest-yield check.** Read each action title and each recommendation line and ask whether it could move unchanged to another client's deck. If it could, it is not a finding. A title that passes makes a claim someone could disagree with, is specific to this client, and carries a number.

### What is NOT a tell, and must not be "fixed"

General anti-AI advice will damage a consulting deck if applied literally. These stay:

- **Formal register.** Formality is not a tell; specific words are. Do not colloquialize a findings deck.
- **Bold-lead bullets** (`**Label:** text`) in slide bodies and recommendation boxes. A tell in continuous prose only.
- **Title case in deck headers and column headings.**
- **Three-item structures** where the content genuinely has three parts. The test is whether you could defend dropping the weakest item: if yes it was padding, if no it is MECE.
- **Named frameworks and coined labels** that the deck defines and evidences. Naming a construct is half of what the client is buying. The fault is a coined label deployed as shorthand for an argument never made.
- **Passive voice in itself.** The real fault is nominalization and missing actors; instruction-tuned models use agentless passive at roughly half the human rate.

