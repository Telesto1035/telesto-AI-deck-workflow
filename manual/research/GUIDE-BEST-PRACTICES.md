# How Anthropic and OpenAI write public-facing guides, and what the Vanguard Standard takes from them

Research pass 2026-09-13, for the first Telesto manual. Four PDFs reviewed page by page (copies in this folder), plus two web resources. Technical documentation excluded on purpose.

## The examples

| Guide | Publisher | Pages | Reader | What it is for |
|---|---|---|---|---|
| How Anthropic teams use Claude Code | Anthropic, 2025 | 23 | Teams considering adoption, technical and not | Ten internal teams, two pages each: use cases, impact, tips |
| A practical guide to building agents | OpenAI, 2025 | 34 | Product and engineering leads building a first agent | Definitions, when to build, design foundations, guardrails |
| AI in the Enterprise | OpenAI, 2025 | 25 | Executives sponsoring adoption | Seven lessons, one customer story each |
| Identifying and scaling AI use cases | OpenAI, 2025 | 34 | Team leads finding where AI helps | Three-step method, six use-case primitives, prioritisation |
| ChatGPT for any role | OpenAI Academy, web | ~2,000 words | Non-technical workers | Four task categories, a templated prompt per task, click-to-try |
| Claude 101 | Anthropic Academy, web course | 11 lessons | Professionals new to Claude | Meet Claude, organise work, expand reach, use cases by role |

Sources: [Anthropic PDF](https://www-cdn.anthropic.com/58284b19e702b49db9302d5b6f135ad8871e7658.pdf), [OpenAI agents guide](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf), [AI in the Enterprise](https://cdn.openai.com/business-guides-and-resources/ai-in-the-enterprise.pdf), [Identifying and scaling AI use cases](https://cdn.openai.com/business-guides-and-resources/identifying-and-scaling-ai-use-cases.pdf), [ChatGPT for any role](https://academy.openai.com/public/clubs/work-users-ynjqu/resources/chatgpt-for-any-role), [Claude 101](https://anthropic.skilljar.com/claude-101), [Building effective agents](https://www.anthropic.com/research/building-effective-agents).

## What they have in common

1. **A contents page with fewer than ten lines.** Every PDF opens with a one-page contents list. The reader sees the whole argument before page 3. Sections are named as actions or questions ("When should you build an agent?", "Start with evals"), not as nouns.

2. **One repeating page template per section.** Anthropic gives every team the same two-page pair: left column a grey box saying who the team is, right column "Main use cases" as bold-lead paragraphs; then a second page "Team impact" and "Top tips". OpenAI's Enterprise guide gives every lesson the same sequence: lesson title, "How it started", "How it's going", a quote with name and title, a link. Once the reader has read one section, the rest read at twice the speed.

3. **Numbered 01, 02, 03 lists as the main exhibit.** Three or four numbered items with a bold label and one sentence each. This is the dominant visual across all four PDFs. It replaces bullet lists and paragraphs alike.

4. **Definitions set in a tinted callout, one sentence.** "Agents are systems that independently accomplish tasks on your behalf." Pink box, page 4. The Anthropic essay does the same with workflow versus agent. The definition arrives before any argument that depends on it.

5. **Proof is a number with a name attached.** "98% of Morgan Stanley advisors use OpenAI every day." "Vim mode with 70% of code written autonomously." "39% of U.S. adults in two years, the internet reached 20%." Every number sits next to who reported it. Quotes carry name, title and company. There are no unattributed claims of speed or savings.

6. **The register is plain instruction.** Short sentences, active verbs, second person ("Ask your teams to list scenarios where they..."). No jargon that a first-year employee would need to look up. The agents guide says "you should consider adding complexity only when it demonstrably improves outcomes", which is as close as any of them gets to a slogan.

7. **A "when not to" section.** Both agent guides devote a page to when the approach does not apply. The Enterprise guide says what it does not cover. This is what makes the guidance credible rather than promotional.

8. **The close moves the reader toward action.** "Start today" with three numbered steps. "Action items" pages with a prompt the reader can paste. "More resources" as the last page. A summary is fine when it is paired with what to do next; a summary alone is what these guides avoid.

9. **Whitespace is a feature.** Every PDF runs a single column at roughly 60 characters per line, leaves a third of most pages empty, and uses one accent colour on a white ground. Section openers are a full page with the title alone. Photos and illustrations are rare and never decorative: the Klarna phones show the product.

10. **Tips come from practitioners, not the author.** Anthropic's "Top tips" are written as the team's own advice ("Write detailed Claude.md files", "Treat it like a slot machine"). The reader is persuaded by peers, not by the publisher.

## How they sell without pitching

- The capability is shown by what someone did with it, in past tense, with the result. Not by describing features.
- The measure is always stated before the number: what was counted, over what period, by whom.
- The reader is told what to do in the first hour, not what the product will become.
- The "when not to" page does the selling. A guide that names its limits is believed on its claims.

## What the Vanguard Standard should take

| Practice | How it lands in the manual |
|---|---|
| Contents page with action-phrased sections | Not a separate page (page budget), but the eyebrow tracker plays this role. The four segment names should read as what the reader does, not what the section is about. Revisit "ORIENTATION / SERVICES / SERVICES + PRODUCT / PRODUCT" once the CEO has reacted. |
| One repeating template per section | Every Services operation page (5 to 10) uses the same three-column anatomy: what you do, what comes back, what you decide. Every demo page uses the same frame plus caption. The reader learns the shape once. |
| Numbered 01-04 lists as the main exhibit | Already the Palantir-numbered card system on page 12. Use it on page 6 (five inputs) and page 10 (four decisions) too. |
| One-sentence definition in a callout | Page 5 needs one: what the workflow is, in one sentence, before the chart. Candidate: the workflow versus agent line already in the chart's footnote. |
| Proof is a number with a name | Page 9 (Learn) shows three real Learn passes on the EDR minipack with the rule each added, dated. Page 7 shows this deck's own QC score. No efficiency number until prompts-per-deck has been counted on two decks; until then state the measure and that counting has started. |
| Plain instruction, second person | Titles already use "you supply", "comments go in the PPTX". Keep the body in the same voice. This is also the fix for the AI-flavoured phrasing flagged on 9/13. |
| A "when not to" page | Page 10 (four decisions the consultant keeps) is this page. It should say plainly what the workflow does not do: judge the storyline, pick between two disagreeing numbers, rewrite a title without approval. |
| Close by moving the reader to action | Decided 2026-09-13: getting consultants to run the workflow belongs in the Services section, which is why that section exists. It is not a separate closing page. The Services pages carry the "do this first" instruction in their takeaway bands; the document still ends on the Product section as planned. |
| Tips from practitioners | The takeaway bands can carry the consultant's own lesson from the EDR and Huron decks ("render before you hand off", "comment in the file, not the prompt") rather than a restatement of the title. |
| Whitespace | The dark template already runs sparse. The word budget (200 warn, 275 block) enforces it. Demo pages stay screenshot plus one caption. |

## What not to copy

- Full-page photographs and gradients: decorative in the OpenAI guides, and the dark Telesto template has no place for them.
- 25 to 34 pages: the manual's ceiling is 25 and the current plan is 19. The OpenAI guides repeat themselves; the Anthropic guide does not, and it is the shortest.
- Vendor "More resources" pages: the manual's equivalent is one line on page 6 pointing to the Claude account, GitHub and the data engineer's repository.
- Marketing statistics from third parties (McKinsey, BCG). The manual's proof is internal and dated.

## Consultant decisions on this research (2026-09-13)

- The Anthropic pattern of simple tables, diagrams, screenshots and shaded takeaway or to-do boxes matches what Telesto already builds. The learning is confirmation, not a new style.
- "Identifying use cases" and "teaching your team" (the OpenAI use-cases guide) are the two structures directly relevant to this manual: the product-types page and the Services operation pages respectively.
- Do not copy Anthropic or OpenAI page style. The Telesto dark template is built and works. Take structure and register only.
- The manual may summarise, as long as it moves the reader toward action. Action on the workflow lives in Services, not on a separate page.
