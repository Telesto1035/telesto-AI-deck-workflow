# HANDOFF: Telesto's Agentic PPT Workflow, build in Claude Code

Prepared 2026-09-12 from the Cowork session that designed the workflow. This file is the spec. A fresh Claude Code session should be able to read it and build the repository without the conversation that produced it.

## 0. What is in this bundle

```
HANDOFF.md                     this file
skills/
  draft-deck/                  SKILL.md v2.1 (saved) + references/ (deck-craft, language-rules, page-archetypes, deck-types)
  deck-qc/                     SKILL.md v4 (saved)
  onepagebrief-builder/        SKILL.md v1.1 (saved)
docs/
  workflow-and-skills.md       the chain, versions, decisions
  qc-scorecard-design.md       QC design rev 3 (the basis for qc_check.py)
  research-ai-content-workflows.md
  telesto_deck_chain.html/.png the workflow chart (Anthropic pattern vocabulary, Telesto dark paper)
fixtures/
  telesto_v2_template.pptx     the dark Telesto template every Telesto-paper deck inherits from
  Telesto_Standard_v2_P3-P5.pptx  three manual pages built with python-pptx (clean fixture)
  Telesto_Deliverable_Brief_Example.pptx  white Build Brief (pptxgenjs)
  Telesto_Package_Types.pptx   one-page explainer
```

Two skill versions were proposed in Cowork but not yet saved when this bundle was cut: `draft-deck` v2.2 (stakeholder-context input, brief optional, Revise reads legacy and modern PPTX comments, Learn mode) and `stakeholder-context` v1 (new). If they have been saved since, export them from the account and replace the copies here; if not, treat this bundle's `docs/workflow-and-skills.md` as the description of what they add and rebuild them in the repo.

Shipped client decks (public sector, ULSE/TRIP proposal, Re-rebrand, EDR) are not in this bundle. Add them to `fixtures/` locally; they are the real test set.

## 1. The chain, in one paragraph

stakeholder-context (agent) → draft-deck (agent: router, then generator) → **qc_check.py (code gate, loops back to the generator until clean, cap 3)** → deck-qc Layer 2 (evaluator agent, fresh context) → human comments in the PPTX → draft-deck Revise → ship → draft-deck Learn (diff shipped vs draft, propose skill patterns). The Build Brief (onepagebrief-builder) is a branch taken only when the package includes a product or engineer time. Terms follow Anthropic, "Building Effective Agents": workflow = predefined path; agent = the LLM directs its own tool use. See `docs/telesto_deck_chain.png`.

## 2. Repository layout to create

```
telesto-deck-skills/
  CLAUDE.md
  README.md
  .claude/
    settings.json              hooks (Stop hook runs qc_check.py)
    skills/
      draft-deck/              from skills/ (SKILL.md + references/)
      deck-qc/
        SKILL.md
        scripts/qc_check.py    NEW, section 3
        scripts/qc_rules.json  NEW, thresholds and word lists
      onepagebrief-builder/
      stakeholder-context/     from the v1 proposal, or rebuild per docs/workflow-and-skills.md
    agents/
      deck-evaluator.md        NEW, section 5
  scripts/
    publish_skills.py          NEW, section 7 (diff repo skills vs account copies)
    run_chain.sh               LATER, section 8
  tests/
    fixtures/                  the decks above plus broken variants (section 6)
    test_qc_check.py
```

Do not put the Telesto template or client decks in a public repository. The repo is private or local.

## 3. qc_check.py, the gate

Purpose: the deterministic subset of deck-qc Layer 1 plus the hygiene pass, as a script the generator can loop on without a model in the loop. Everything a model has to judge (numbers vs source, referents, title chain, voice) stays in the deck-qc skill.

**CLI**

```
python qc_check.py DECK.pptx [--rules qc_rules.json] [--json out.json] [--fix-safe] [--profile findings|proposal|kickoff|minipack|presentation|update|workshop]
```

Exit 0 = pass (no blocking findings). Exit 1 = blocking findings present. Exit 2 = file could not be opened. Print a human-readable table to stdout and, with `--json`, write findings to a file.

**Finding schema**

```json
{"id":"font-size-floor","severity":"block|warn|info","slide":7,"shape":"TextBox 12","shape_id":34,
 "text":"Source: Institution Priorities survey, n=250","detail":"9.0pt outside a footnote home",
 "fix":"resize|reword|clear|delete|none","auto_fixable":true}
```

**Checks, with the XML they read** (python-pptx for slides; lxml for parts python-pptx does not expose)

| id | rule | severity | source |
|---|---|---|---|
| font-size-floor | any run with `sz` < 1000 (10pt) whose shape is not a footnote home. Footnote home = shape whose top edge is in the bottom 12% of the slide, or whose name matches `/foot|source|note/i`. Footnotes may go below 10pt but never below 8pt. | block | `a:rPr/@sz`, `a:endParaRPr/@sz`, `a:defRPr`; inherit from layout/master when absent |
| italics | any run with `i="1"` | block | `a:rPr/@i` |
| table-one-size | more than one font size inside one shape-built table group or one native `a:tbl` | warn | group children / `a:tbl` cells |
| author-empty | `dc:creator` or `cp:lastModifiedBy` non-empty | block | `docProps/core.xml` |
| metadata-scrub | title, subject, keywords, description, category, contentStatus set; `TotalTime` > 0; `Template` non-empty; `docProps/custom.xml` present; generator fingerprints (`PptxGenJS`, `python-pptx`, `Aspose`, `Spire`, `OpenXML SDK`, `Generated by`, `Created with`) anywhere in XML parts | block | `docProps/core.xml`, `docProps/app.xml`, `docProps/custom.xml`, all `*.xml` |
| speaker-notes | any `notesSlide` part with text | block (report the text in full before it is stripped) | `ppt/notesSlides/*.xml` |
| hidden-slides | `p:sld/@show="0"` | warn (list, ask) | slide XML |
| comments-open | any comment part with unresolved threads; legacy `ppt/comments/*.xml` and modern `ppt/comments/modernComment_*.xml` | warn (list, ask) | comment parts |
| placeholders | text matching `\[PLACEHOLDER[^\]]*\]`, `\bTBD\b`, `\bXX+\b`, `lorem ipsum`, `Click to add`, `\{\{.*\}\}` | block | runs |
| empty-textbox | text shape with no visible characters | warn | runs |
| off-canvas | shape bbox outside slide bounds by more than 1pt | warn | `a:off`, `a:ext` vs `p:sldSz` |
| overflow-estimate | estimated text height > frame height when `a:bodyPr` has no autofit; estimate = lines × size × 1.2 using a per-font average char width (Arial 0.5em). Report as `warn`, `auto_fixable=false`; the render check confirms | warn | `a:bodyPr`, runs |
| footnote-sequence | superscript or bracketed markers `¹²³` / `[1]` on a slide not matching the footnote list on the same slide; duplicates; gaps | block | runs |
| totals-sum | a row or column of numbers followed by a total that differs by more than 1 point (percent) or 1 unit; parse numbers from shape-built tables by y-alignment and from native tables | block | runs, `a:tbl` |
| chart-cache-label | chart cached value differs from a data label or title figure on the same slide | block | `ppt/charts/chartN.xml` `c:numCache`, runs |
| label-in-bar | data labels positioned inside bar segments (`c:dLblPos` = `ctr`, `inBase`, `inEnd`) | warn | chart XML |
| semicolon-runs | table cell text with 2+ semicolons | warn | cells |
| abbreviation-list | tokens in `qc_rules.json["expand"]` (e.g. `State` for Department of State, `Acad Med`, `academic medical centers` → AMC) | warn | runs |
| stakeholder-name | any name in `qc_rules.json["client_names"]` (populated per engagement) on a slide | block | runs |
| style-drift | title font size or face differs across slides; footer or slide number missing on some content slides; fill colours outside the theme palette plus the allowlist in rules | warn | title placeholders, `a:srgbClr` |
| draft-stamp | `DRAFT` present on some content slides but not others | warn | runs |

**Hanging words** are not in the script. They need the render. The skill does that step; the script stays fast and deterministic.

**`--fix-safe`** applies only findings with `auto_fixable=true` and exactly one correct answer: clear author and metadata, strip notes (after printing them), delete `custom.xml` and its relationship, remove generator strings, italic → roman, replace semicolon runs with paragraph breaks. It never changes a number, a size, or wording, and it writes `DECK.qc.pptx` beside the input rather than overwriting. Validate the saved file opens (re-load with python-pptx) before exiting.

**Renderer note**: overflow and hanging words are confirmed visually by the skill (soffice → PDF → pdftoppm). A wrapped footer or clipped label can be a LibreOffice artifact; compare against the unmodified original before flagging (deck-qc v4 rule).

**qc_rules.json** holds: size floor (10), footnote floor (8), footnote home band (0.12), palette (282828, 333333, 009999, 0BD0D9, 005366, 003366, FFFFFF, 8A8F92 plus client palettes by name), word list from draft-deck's dated list (voice checks are `info` only here; the skill does the judgment), `expand` map, `client_names` (empty by default; filled per engagement, never committed with real names).

## 4. Hook: make the gate deterministic

`.claude/settings.json`

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "python3 .claude/skills/deck-qc/scripts/qc_gate_hook.py"
      }]
    }]
  }
}
```

`qc_gate_hook.py`: find any `.pptx` written or modified during the session (compare mtimes against session start, or read the transcript path the hook receives), run `qc_check.py --json` on each, and if any `block` finding exists, print the findings and exit 2 so the turn cannot end. Keep a counter in a temp file; after 3 blocked stops, exit 0 and print "gate cap reached, handing off with findings attached" so the loop terminates. Ignore files under `tests/fixtures/`.

Amended 2026-09-14 after a live Cowork run: gate what changed since the **last Stop**, not since session start (a session that runs for days otherwise gates the whole workspace). The state file records the mtime of every file that gated clean and skips it until it is written again; a file that blocked is never skipped. Exclusions moved out of the code into `qc_rules.json` `gate_exclude`, which also carries `.qc.pptx` so the `--fix-safe` output does not cascade into a second block. Templates (`*template*.pptx`, `*.potx`, or a file with no `ppt/slides/slideN.xml` part) are skipped and logged: a template is specimen layouts, not a deck.

The hook is what Cowork cannot do. In Cowork the skill text asks for the render check; here it is enforced.

## 5. Subagent: the evaluator in a fresh context

`.claude/agents/deck-evaluator.md`

```markdown
---
name: deck-evaluator
description: Runs deck-qc Layer 2 on a PPTX in a fresh context, separate from the session that built it. Use after qc_check.py passes.
tools: Read, Bash, Grep, Glob
---
You are the deck-qc evaluator. Load .claude/skills/deck-qc/SKILL.md and apply Layer 2 only (title chain, exec summary to body, conclusion follows exhibit, claim sizing, quotes as evidence, outcome clarity, value at stake, voice, portability). Layer 1 has already passed the code gate; do not repeat it. Score the four dimensions 1-5 with the anchors in the skill. Return the report in the skill's format. You never edit the file. You never guess a number; mark it QUESTION.
```

Invoke from the build session: "Use the deck-evaluator subagent on OUT.pptx." Its output comes back into the build session, where the consultant approves Layer 2 suggestions and draft-deck applies them.

## 6. Fixtures and tests

Fixtures come in pairs: a clean deck and a broken copy with known faults, so `test_qc_check.py` asserts that each fault is found and nothing else is.

Broken variants to generate with a small script (`tests/make_broken.py`) from each clean deck:
- one body run at 9pt, one footnote at 7pt
- one italic quote
- author field "Reviewer One", `TotalTime` 214, a `custom.xml` with SharePoint fields
- a speaker note containing "Build sequence: ..."
- a `[PLACEHOLDER: source needed]`
- a table row whose components sum to 98 against a stated 100
- a chart cache value 34 with a label "36%"
- footnote markers ¹ ² ⁴ with footnotes 1, 2, 3
- a `State` abbreviation for Department of State
- a hidden slide

Acceptance for `qc_check.py`: every planted fault found on every fixture; zero `block` findings on the clean fixtures (warn allowed and listed); runtime under 5 seconds on a 25-page deck; `--fix-safe` output re-opens in python-pptx and in PowerPoint.

Then the real test: run on the shipped public sector deck and the ULSE proposal *as they were before the partner's edits*, and compare flags against the edits actually made. That is the first measurement of the 80% target.

## 7. Skills: source of truth and publishing

The repo is the source of truth. Cowork loads skills from the account's skill storage, which has no git connection. Flow: edit in repo → commit → publish the changed SKILL.md to the account (proposal card or skills settings upload) → the team's Cowork picks it up. Never edit in Cowork and forget the repo; if a card is saved in Cowork, copy the file back the same day.

`scripts/publish_skills.py`: given the path to the synced skills folder on this machine, diff each repo `SKILL.md` and `references/*` against the account copy, print which are stale in which direction. It cannot write to account storage; the publish is a click.

A pre-commit hook may refuse a commit that changes a `SKILL.md` unless `tests/` ran since (touch a marker file).

## 8. Later: run the chain unattended

`scripts/run_chain.sh INPUTS_DIR OUT_DIR` using `claude -p`: stakeholder-context on the roster → draft-deck Build with the brief or prompt → (gate loops inside via the hook) → deck-evaluator → write the report beside the deck. Defer until prompts-per-deck says manual invocation is the bottleneck.

## 9. CLAUDE.md for the repo (keep it short)

```markdown
# telesto-deck-skills
- Skills live in .claude/skills/. The repo is the source of truth; account copies are published from here.
- Never commit client decks, the Telesto template, or real client names in qc_rules.json.
- Run `pytest tests/` before committing a SKILL.md change.
- Generated PPTX files must have an empty author field; qc_check.py enforces it.
- Fonts 10pt or larger except footnotes (8pt floor); no italics anywhere. Tables from shapes, not native tables.
- Units are slides and pages, never beats.
```

## 10. Build order and acceptance

1. `qc_check.py` + `qc_rules.json` + tests on the four bundled fixtures. Done when section 6 acceptance passes.
2. Repo scaffold, skills copied in, `CLAUDE.md`, private remote if one exists.
3. Stop hook + cap. Done when a deliberately broken build cannot end its turn until fixed or capped.
4. `deck-evaluator` subagent. Done when it returns a scored report on a fixture without touching the file.
5. Run on the two shipped decks; record flags vs partner edits; adjust rules.
6. `publish_skills.py`; publish draft-deck v2.2 and stakeholder-context v1 if not already saved.
7. Measure: prompts per deck and edit type (style / structure / number / storyline) on the next two live decks.

## 11. First prompt for the Claude Code session

> Read HANDOFF.md in this folder. Build step 1 of section 10: `qc_check.py` and `qc_rules.json` per section 3, with `tests/test_qc_check.py` and `tests/make_broken.py` per section 6, using the fixtures in `fixtures/`. Use python-pptx for slides and lxml for docProps and chart parts. Do not modify the fixtures in place. Show me the test run and the findings table for `Telesto_Standard_v2_P3-P5.pptx` before moving to step 2.
