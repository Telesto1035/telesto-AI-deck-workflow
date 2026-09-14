# Resolving the list: ask by slide, do not make them review every line

Read when a FIX and SUGGEST list is ready to be resolved with the consultant.

The report is for reading. The resolution is a set of choices, collected with the AskUserQuestion tool, never as a prose "reply apply all, apply selected, or skip". Reviewing thirty items one by one is the slow path this skill exists to avoid.

## Sort every finding into a bucket first

- **Settled.** A mechanical error with exactly one correct answer, a number the attached source decides, or anything in the hygiene pass. Apply it. Do not ask. List what you applied afterwards.
- **Decided by the consultant's own message.** Anything they already ruled on in this conversation. Apply it as stated.
- **Not a defect.** Anything under "What is not a defect". Drop it silently.
- **Judgment.** Everything else. This goes to AskUserQuestion.

## Titles, recommendations and exec-summary lines are always SUGGEST

By this stage those lines are human-written. Rewriting them pulls the deck back toward AI tone. So never apply a change to a title, a recommendation band, an exec-summary line or a takeaway as a settled fix, even when it is plainly wrong. Put it in a question, quote the current line and the proposed line in full, and let the consultant choose, edit or decline. The only exception is a factual error inside one of those lines that the source settles, such as a wrong figure or a misspelled agency: change that and nothing else, and say which words you touched.

## One question per slide, not one per finding

Slide order by default; worst slide first only when the consultant asks. Each question header is the page number and title ("Page 14, Next steps"). Each option quotes the exact line, cell or label before and after, so the consultant never has to open the file to decide. Where a slide has two unrelated judgment calls, make them two options under one question with `multiSelect: true`. Ask in batches of up to four slides per call. Between batches, apply what has been decided so the consultant sees progress.

Reviewer shorthand ("more strategic", "so what", "fix", "this doesn't work") is never read one way: draft-deck `references/comment-shorthand.md` gives the readings to offer, each with its concrete change.

## The bulk route, only for a sweeping mechanical change

Group across slides only when the same fault appears in several places and the fix is identical in kind: harmonising one source line across six pages, replacing straight quote marks, spelling out an agency everywhere, removing the same title prefix from five pages, resizing sibling exhibits to one geometry. Say how many slides the option touches and list them. Anything that changes the meaning of one page's argument is not a bulk item.

## Option rules

- Put the option you would choose first and append "(Suggested)" to its label.
- Write the full proposed replacement text in the option's `description`; use `preview` for a before-and-after.
- Offer a real "do less" option in every question: leave as drafted, or flag only.
- Set `multiSelect: true` where the items are independent.
- The tool supplies the free-text "Other" path; do not add an option for it, and honour whatever the consultant writes in.
- A QUESTION-class item never gets a suggested default. Two disagreeing numbers with no source is a question asked straight, with the candidate values and their pages. You do not pick.

Apply everything in one pass once the answers come back, then validate, re-render the touched pages, re-run the number ledger and report the delta. Ask a second round only for a new problem the first pass created.
