# Research note: how others run AI co-creation workflows (2026-09-12)

Question: are there best practices for co-creating content with AI, and how agentic do others go? Compared against the Telesto chain (stakeholder-context -> draft-deck -> deck-qc -> comment-based Revise -> Learn).

## What the sources say
- Anthropic, Building Effective Agents: five workflow patterns. The Telesto chain is prompt chaining with gates plus an evaluator-optimizer loop (draft-deck generates, deck-qc evaluates). Autonomous agents need "maximum number of iterations" and "checkpoints ... where agents pause for human feedback."
- Claude Code best practices: give the agent a check it can run so the loop closes without the human; Writer/Reviewer in separate sessions so the grader is not the author; adversarial review subagent; log rules into CLAUDE.md or skills and prune them. Stop hooks and /goal turn a check into a hard gate.
- Ralph loop (LogRocket, GitHub): loop = prompt -> plan -> execute -> evaluate -> exit or continue; succeeds only on bounded, verifiable tasks with completion criteria defined upfront; vague objectives cause scope creep. Humans do not intervene mid-loop.
- n8n human-in-the-loop: gate only at irreversible points; approve / reject / edit in the tool people already use; timeouts and defaults; log every decision and reduce gates as accuracy improves; high escalation rate means fix the AI, not add gates.
- Glean content review: draft -> voice edit -> fact check -> compliance -> approve; gates set by risk tier; machines do mechanical checks and routing, humans own tone, accuracy nuance and approval; ground drafts in approved knowledge upfront rather than over-edit afterward.
- McKinsey Lilli: 72% of firm active, 500k+ prompts a month, ~30% time saved on search and synthesis; quality measured by blind 5-point scoring of outputs; slide-building agents the most anticipated next feature. Human review is post hoc.
- Anthropic's Claude Explains blog: Claude drafts, subject-matter experts and editors add insight through iterations. Even the model maker keeps human editorial.
- Open-source consulting skill repos (e.g. strategy-skills-for-claude, 21 skills): standalone text outputs, no chaining, no review step, no deck output.

## Where Telesto stands
Ahead of public repos: chained skills, deck output, a separate QC evaluator, in-file comment review, a learn loop. Matches Anthropic's patterns. Not yet done: Layer 1 QC as a machine-runnable check the builder loops on until pass; explicit risk tiers written into the skills; iteration caps.

## Implications
1. Make deck-qc Layer 1 a check draft-deck runs in a loop (cap 3 passes) before handoff; humans then see only Layer 2 and storyline.
2. Write the risk tiers down: short deck = no brief, one partner pass; product or engineer time = brief plus staging review; client-facing send = the only irreversible gate.
3. Fully unattended content pipelines exist mainly in creator and marketing contexts where the quality bar is lower. For MD-audience decks the realistic target is unattended mechanical polish and attended judgment.
