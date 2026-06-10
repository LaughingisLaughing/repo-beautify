---
name: repo-beautify
description: "Use when the user asks to beautify, redesign, polish, or professionalize a GitHub repo storefront/README; compare README styles; improve repo metadata, topics, social preview, or package manifest; or says README 美化, 美化仓库, 仓库门面, repo 门面, 项目主页包装, 徽章, badges, social card, star history. Covers README visual redesign (hero banner, badges, mermaid diagrams, collapsible docs), GitHub description/topics, and manifest enrichment, all fact-verified. Do NOT use for GitHub profile READMEs, full API docs, CONTRIBUTING generation, or GitHub Pages sites."
---

# Repo Beautify

Turn a repository's storefront (README + GitHub metadata + package manifest) into something that looks professional AND stays truthful. Beautification has three layers, in order: facts, content, visuals.

## Hard Rules (apply to every step)

1. **Fact ledger.** Every claim in the output must cite one of: the scan JSON, an existing file path in the repo, a command output you ran, or a live API result. If a claim has no ledger entry, it does not go in. This covers badges, install commands, roadmap items, architecture diagrams, screenshots, and feature lists alike.
2. **Never fabricate.** No badge, install command, or section for anything that does not exist. A fake badge is worse than no badge. "Probably published to npm" is not a fact; the scan's `registry_published` field is.
3. **Re-skinning must not lose docs.** Inventory the old README's sections first; map every substantive section (CLI flags, config, formats, caveats) into the new structure (collapsibles are fine, deletion is not). Diff the two inventories before finishing; any drop must be deliberate and stated.
4. **Scale to the project.** A 50-line script does not need a 300-line README or a star-history chart.

## Workflow

### 1. Scan and verify facts

Run `scripts/scan_repo.sh <repo-dir>`. It emits the fact ledger JSON: manifest data and missing fields, license, owner/repo, current AND default branch, latest tag, package manager, CI, registry publish status, GitHub description/topics/visibility, community files (CHANGELOG / CONTRIBUTING / CODE_OF_CONDUCT / SECURITY / FUNDING), demo assets.

Interpretation rules:
- `registry_published`: `unpublished` → install instructions MUST use the Git URL form (`npm install -g github:owner/repo`). `unknown_network` / `unknown_tool_missing` → STOP and confirm with the user before writing any install command; do not guess.
- `github_api_status` != `ok` → do not infer public/private or description/topics from blanks; say the check was inconclusive.
- Empty `github_description` / `github_topics` are storefront bugs to fix in step 5.
- socialify, star-history, github-readme-stats render only for public repos (`github_private: false`, verified, not assumed).

### 2. Pick a style (with the user, not for them)

Read `references/readme-structure.md` for the catalog and tradeoffs. Built-in templates:
- `assets/template-classic.md`: Best-README-Template lineage; conservative, contributor-oriented.
- `assets/template-visual.md`: gradient hero, typing animation, badges, social card, mermaid, star history; launch/brand-oriented.

If the user has not chosen, EITHER ask with a one-line tradeoff summary, OR generate both and build a comparison page with `scripts/build_compare.py --repo OWNER/REPO --manifest variants.json --out compare.html` so they pick in the browser.

### 3. Generate the README

Read `references/visual-services.md` for exact URL recipes and pitfalls. For the top banner, prefer a self-hosted animated hero SVG over banner services: ten styles ship in `assets/heroes/` (previews in `assets/heroes/previews/`); let the user pick by name or suggest 2-3 matching the project's temperament. The cookbook's "Self-hosted hero SVG" section has the catalog and the filling rules. Content rules:
- Lead with the problem the project solves, concretely (a "before" snippet beats adjectives).
- Quick Start uses the verified install command from the ledger, nothing else.
- Mermaid diagram only when the project has real topology; derive nodes from the actual structure. GitHub renders ```mermaid natively.
- Long prompt collections / CLI references go into `<details>` collapsibles.
- ALL values substituted into service URLs (project name, taglines, colors) must be URL-encoded; CJK, spaces, `&`, `#` in a query param break the image.
- Link CHANGELOG / CONTRIBUTING / SECURITY only if the ledger says they exist; a Roadmap section requires an actual roadmap source (issues enabled + open issues, or a roadmap doc).

### 4. Validate before showing the user

- No leftover placeholders (`{{...}}`, `TODO`, template repo names).
- Badge evidence check: HTTP 200 is NOT enough (static badges always return 200). Each badge needs a ledger entry: CI badge → workflow file exists; version badge → registry says published; license badge → license file present.
- Mermaid: validate with `npx -y @mermaid-js/mermaid-cli -i diagram.mmd -o /tmp/out.svg` when npx is available; otherwise trace node IDs and arrows manually and say so.
- Install commands are copy-paste runnable against the verified registry state.
- Optional render check (serve locally + screenshot). Known artifact: headless screenshots freeze SVG-in-img CSS animations at t=0, so capsule-render/typing-svg text can look missing in screenshots while fine in real browsers. Verify via `curl <svg-url> | grep '<text'` instead.

### 5. Fix the rest of the storefront (often forgotten)

- **GitHub description + topics**: `gh repo edit owner/repo --description "..." --add-topic a --add-topic b` (5-8 topics, lowercase, hyphenated).
- **Manifest enrichment**: ensure `description`, `author`, `repository`, `homepage`, `bugs`, `keywords` exist (package.json or pyproject/Cargo equivalents). The scan's `manifest_missing_fields` lists what to add.
- **Releases**: if the ledger shows no tags, suggest tagging the current version; a Releases page is part of the storefront.
- **Social preview**: suggest the socialify image for Settings → Social preview. This is a manual upload; do not claim an API can set it.
- **Community files**: link existing CONTRIBUTING / CODE_OF_CONDUCT / SECURITY; if absent, suggest (do not generate, out of scope).
- **Bilingual README** (optional, only when the audience justifies it): `README.zh-CN.md` plus a language switcher line at the top of both files.

### 6. Versioning

README-only changes are docs-only (no version bump). If the manifest was touched (step 5), bump PATCH and add a Keep-a-Changelog entry.

## Failure modes seen in the wild

- shields.io dynamic GitHub badges occasionally render "unable to select next GitHub token from pool"; transient, ignore.
- star-history is nearly empty for 0-star repos; keep it as a footer element, never present it as traction.
- GitHub proxies all README images through camo and caches aggressively; URL changes can take hours to appear. Cache-bust with any new query param.
- GitHub sanitizes raw HTML: scripts/styles stripped, many attributes dropped; `<details>` works but nested markdown inside often needs surrounding blank lines.
- Accessibility: decorative images get `alt=""`; informative images get an alt that states what they show. Never encode load-bearing information only in a generated image.
- Two heavy instruction sets injected at once dilute each other; when another large design skill is active, load only one.
