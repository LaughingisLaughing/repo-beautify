# README Structure and Style Catalog

## The two built-in styles

| | classic | visual |
|---|---|---|
| Lineage | othneildrew/Best-README-Template (16k+ stars) | capsule-render + typing-svg + socialify + mermaid + star-history composition |
| First impression | "serious, maintained OSS project" | "polished launch page" |
| Maintenance cost | low (all static markdown) | medium (third-party image services) |
| Best for | libraries courting contributors, long-lived tools | personal brand, launch-phase, portfolio repos |
| Template | `assets/template-classic.md` | `assets/template-visual.md` |

When the user has not picked, either ask with the one-line tradeoff above, or generate both and let them choose visually via `scripts/build_compare.py`.

## Section order (both styles)

1. Hero (banner / title + tagline + badges)
2. The problem, in 2-3 concrete sentences (show the pain, e.g. a "before" snippet)
3. The fix / how it works (mermaid diagram if the project has real topology)
4. Quick Start (verified install + 2-3 commands max)
5. Full usage / commands reference (collapsibles for anything long)
6. Configuration / formats
7. Notes and caveats
8. Star history + footer (visual style only)
9. License + author

## Content-merge rules (re-skinning an existing README)

1. Inventory the old README's H2/H3 sections first.
2. Map every old section into the new structure; long reference material goes into `<details>` blocks rather than being cut.
3. After writing, diff the two section inventories. Anything dropped must be a deliberate, stated decision, not an accident.
4. Factual upgrades found during the scan (wrong install command, dead links) are fixed inline and called out to the user.

## Adaptation by project type

- **CLI tool**: lead with a terminal-style code block of the 3 core commands; commands table (emoji keys optional, skip for conservative repos)
- **Library**: lead with minimal import → use → result example; API table links
- **App / service**: lead with screenshot or demo GIF; setup → configure → run
- **Skill / prompt collection**: lead with the natural-language prompts users will actually paste; collapsibles per scenario
- **Tiny utility**: hero + what it does + usage; skip diagrams, skip star history

## Bilingual READMEs (optional, not a default)

Only when the project's audience justifies it: keep `README.md` (English) as canonical, add `README.zh-CN.md`, and put a one-line language switcher at the top of both (`English | [简体中文](README.zh-CN.md)`). Mirror section anchors so cross-links work. Treat this as a storefront add-on, not part of every makeover.

## Writing tone

- Concise, direct, active voice. "Run this" not "you might want to consider running this".
- Describe what it does, never how amazing it is.
- The first 10 lines decide whether anyone scrolls; spend your effort there.
- Avoid em dashes; use commas, colons, or parentheses.
