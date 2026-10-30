# Template contract

**Version 1 (Oct 2026).** The version lives in `deck-qc/scripts/qc_rules.json` as `template_contract_version`; bump both together.

What draft-deck and deck-qc assume of any Telesto AI-readable template, house or client. The skills hold no client template, palette or page; a template holds no skill rule. This page is where the two meet, and `qc_check.py TEMPLATE.pptx --template` checks a template against it.

## Contents
- What a template carries
- Where templates live
- Keeping the two in step

## What a template carries

1. **Three kinds of page.** Starter pages are the layouts a deck is built from. Exemplar pages show a finished page in the paper's style and carry real or dummy client content. Readme pages explain the template to the drafter. A deck duplicates starter pages only (build-rules rule 1).
2. **Sections named Starter, Exemplar and Readme**, each name containing that word (a section called "Exemplar · Scaling TC" counts). Recommended: without them an exemplar page whose stamp was deleted cannot be told from a starter page, and `--template` says so as INFO.
3. **The exemplar stamp** on every exemplar page, the section's divider page included: text beginning `EXEMPLAR ·`, such as `EXEMPLAR · DUMMY DATA` or `EXEMPLAR · <deck> (<month year>) · DO NOT REUSE CONTENT`.
4. **The readme eyebrow** on every readme page, wherever the readme sits in the file: `TEMPLATE README · NOT A DECK PAGE`. Starter pages carry neither string. Both strings block at hand-back on a deck, so a page that keeps one cannot ship.
5. **A readme that states:** `Template contract v<n>`, the version the template meets; which pages to delete before a deck leaves (exemplar and readme sections, unused starters); the slide master or layout a deck inherits; the palette roles (which color marks what); and any page-design exception (a page type that departs from the paper's title size, for instance).
6. **Footnote homes named for what they hold.** A source or note line on a starter page sits in a shape named `Source`, `Note` or `Footnote`; the gate finds footnote homes by name (`footnote_name_regex`).
7. **Colors from the theme**, or applied by hand on at least `palette_recurrence_slides` slides, so the gate reads them as the deck's palette for fills and text alike.
8. **Type at the floor.** 10pt or larger outside footnotes, 8pt floor in them, on starter pages; the paper's convention never lowers it.
9. **"template" anywhere in the file name**, so the Stop hook skips it as a template rather than gating it as a deck. Client papers use `Telesto_<Client>_PPT_Template_<year>_v<n>.pptx`.

## Where templates live

The template library is the SharePoint folder **TelestoStrategyTeam > Shared Documents > Client Projects > Telesto AI templates**, synced to the template owner's machine through the OneDrive client. One subfolder per paper:

```
Telesto AI templates/
  Telesto/     house templates
  <Client>/    that client's template, one current version plus superseded ones in an Archive folder
```

SharePoint keeps each file's version history. Give a team member access to the `Telesto/` folder and to their own clients' folders only.

- **A client folder is attached only to that client's Cowork project.** Exemplar pages carry client content, so a project that sees two clients' folders breaks one engagement per session (GOVERNANCE rule 3). The `Telesto/` folder may be attached to any project.
- **The client brief's Deck style section names the template file and the contract version it meets.** The template carries the paper; the brief carries the conventions the template cannot show (title form, voice, claims precedent).
- **Never in the repo.** A client template carries client content in its exemplar pages. The Telesto template may sit in `tests/fixtures/` while the repo is private (CLAUDE.md).

## Keeping the two in step

- **The local registry** lists the templates to check: `tests/fixtures/client/templates.json` (gitignored), as `{"templates": [{"client": "<Client>", "path": "<full path>", "contract": 1}]}`. `pytest tests/` runs `--template` on every listed template present on the machine and skips the rest.
- **When a template changes:** update its readme and the client brief's Deck style section, then run `qc_check.py TEMPLATE.pptx --template` until it exits 0.
- **When this contract changes:** bump the version here and in `qc_rules.json`, bump `VERSION`, and run `pytest tests/` with the registry in place. A template on an older version warns and still works; update it, or record it as behind in its client brief.
