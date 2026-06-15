# Visual Services Cookbook

URL recipes for the battle-tested services this skill composes. All render natively in GitHub READMEs as plain `<img>` / markdown images. Only use a service when the fact it visualizes is real (see Hard Rules in SKILL.md).

## Self-hosted hero SVG (preferred for the top banner)

A hand-crafted animated SVG committed to the repo beats third-party banner services on every axis: ~2KB vs an external request, unique design vs a template look, and no uptime dependency.

**Style catalog** (templates in `assets/heroes/<style>.svg`, branded previews in `assets/heroes/previews/`). Let the user pick by name; if they have not chosen, suggest 2-3 that fit the project's temperament:

| style | look | best for |
| --- | --- | --- |
| `swiss` | paper grid, weight contrast, hopping accent square | editorial restraint, long-lived tools |
| `aurora` | dark drifting gradient blobs | dark-mode-first, product-brand repos |
| `vignelli` | oversized cropped type, red rule | bold statements, design-adjacent projects |
| `orbit` | terminal prompt, orbiting satellites | CLIs and dev tools |
| `blueprint` | engineering drawing, marching dashes | infra, build systems, specs |
| `brutalist` | thick frame, hard shadow, ticker strip | opinionated tools, manifestos |
| `dotwave` | LED matrix pulse wave | data, signals, monitoring |
| `editorial` | serif masthead, small caps | docs, writing, knowledge bases |
| `outline` | stroke-only type, flowing gradient | modern type-driven landing vibes |
| `bauhaus` | geometric primaries in motion | playful-but-disciplined projects |

Rules for filling a template (and for designing new ones):

- **Self-contained**: CSS keyframes / SMIL only, no JS, no external fonts or images. SVG loaded via `<img>` (GitHub camo) cannot fetch ANY external resource; use system font stacks (`system-ui`, `ui-monospace`) and accept minor cross-platform variance.
- **Readable at t=0**: text fully visible on the first frame; animation is ambient decoration (a traveling accent, a drawing line), never a fade-in reveal. Headless screenshots freeze SVG-in-img at frame 0, and so do some RSS readers.
- **Facts in the artwork**: station labels, versions, commands in the hero must come from the ledger like any other claim.
- **Namespace your classes** (e.g. `.hero-*`): if the SVG is ever inlined into an HTML page next to other SVGs, bare class names collide.
- Reference it with a relative path: `<img src="assets/hero.svg" width="100%" alt="..."/>`. Keep an honest `alt`.
- Extreme weight contrast (200 vs 800) per the HyperFrames design guide; one accent color; 880x220 viewBox renders crisply at GitHub's content width.

## capsule-render (gradient banner) — github.com/kyechan99/capsule-render

```text
https://capsule-render.vercel.app/api?type=waving&color=0:8B5CF6,50:6366F1,100:3B82F6&height=200&section=header&text=PROJECT_NAME&fontSize=52&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=TAGLINE&descSize=18&descAlignY=55
```

- `type`: waving | rect | egg | shark | slice | venom (waving reads best as header + footer pair)
- Footer variant: `&section=footer&height=120`, drop text params
- Pitfall: `animation=fadeIn` starts at opacity 0; headless screenshots freeze it at t=0 so text looks missing in automated checks. Real browsers are fine. Verify via `curl | grep '<text'`.

## readme-typing-svg (typing animation) — github.com/DenverCoder1/readme-typing-svg

```text
https://readme-typing-svg.demolab.com/?font=Fira+Code&weight=600&size=22&duration=3000&pause=800&color=6366F1&center=true&vCenter=true&width=600&lines=Line+one;Line+two;Line+three
```

- Lines are URL-encoded, `+` for spaces, `;` separates lines, `%E2%80%A2` for bullet dot
- Keep to 2-4 short lines; this is a tagline, not a paragraph

## shields.io badges — github.com/badges/shields + github.com/Ileriayo/markdown-badges

- Static tech badge: `https://img.shields.io/badge/LABEL-COLOR?style=for-the-badge&logo=LOGO&logoColor=white` (logos from simple-icons slugs)
- Dynamic GitHub badges: `https://img.shields.io/github/{stars|forks|issues|license|contributors}/OWNER/REPO?style=for-the-badge`
- Use ONE style (`for-the-badge` recommended) across the whole README
- 3-6 badges in the hero; group status and tech separately
- Golden rule: a badge for a nonexistent CI/package is a lie; skip it
- Known transient failure: dynamic badges sometimes render "unable to select next GitHub token from pool"; ignore, it self-heals

## socialify (social card) — github.com/wei/socialify

```text
https://socialify.git.ci/OWNER/REPO/image?description=1&font=Inter&language=1&name=1&owner=1&pattern=Circuit%20Board&theme=Dark
```

- Public repos only. Pulls live repo description: fix the GitHub description BEFORE embedding, or the card shows blank
- Patterns: Circuit Board | Plus | Brick Wall | Overlapping Hexagons | Floating Cogs
- Also ideal as the repo's actual social preview image (Settings → Social preview, manual upload)

## star-history — github.com/star-history/star-history

```text
https://api.star-history.com/svg?repos=OWNER/REPO&type=Date&theme=dark
```

- Wrap in a link to `https://star-history.com/#OWNER/REPO&Date`
- **Skip this section entirely for repos under ~50 stars.** Two compounding reasons: (1) the chart is near-empty and reads as "no traction"; (2) star-history embeds the repo owner's avatar inside the SVG, and for new/low-star repos its server often leaves that avatar as an EXTERNAL `<image href="https://avatars.githubusercontent.com/...">` instead of inlining it as base64. GitHub renders README SVGs via `<img>` in "secure static mode", which blocks all external resource loads, so the avatar shows as a broken-image icon next to the "Star History" title. Verified failure mode, not transient.
- **Use the lowercase `owner/repo`** in the URL. star-history 301-redirects mixed-case names to lowercase, and GitHub's camo image proxy does not follow redirects (whole chart breaks).
- Before shipping it, confirm the chart is self-contained: `curl -sL "<svg-url>" | grep -c 'href="http'` must be `0`. Any external `href` inside means a guaranteed broken icon under `<img>`.

## mermaid (architecture diagram) — built into GitHub

GitHub natively renders fenced ```mermaid blocks since 2022. Prefer `flowchart LR` for sync/pipeline topologies. Style the hub node with the accent color:

```text
flowchart LR
    S[("source of truth")] -->|symlink| A["target A"]
    style S fill:#6366F1,color:#fff
```

Derive nodes from the project's REAL structure (scan output), never a generic diagram.

## github-readme-stats (repo pin) — github.com/anuraghazra/github-readme-stats

```text
https://github-readme-stats.vercel.app/api/pin/?username=OWNER&repo=REPO&theme=transparent
```

Optional; mostly useful when cross-linking sibling repos.

## Rendering caveats (all services)

- **URL-encode every substituted query value** (project names, taglines): spaces, `&`, `#`, and CJK characters silently break the image.
- GitHub proxies images through camo with aggressive caching; URL changes can take hours to propagate. Cache-bust by changing any query param.
- GitHub sanitizes raw HTML in READMEs: `<script>`/`<style>` stripped, many attributes dropped; `<details>` works but markdown nested inside usually needs blank lines around it.
- **Alt text**: decorative images (banners, footers) get `alt=""` or a short label; informative images (charts, social cards) get an alt that states what they show. Never encode load-bearing information ONLY in a generated image.
- All of these are third-party uptime dependencies, acceptable for storefront flair only.
