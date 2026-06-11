# Changelog

## [0.4.1] - 2026-06-11
### Changed
- Chinese edition typography rules hardened in `references/bilingual-readme.md`: corner brackets 「」 for quotes, full-width punctuation throughout Chinese prose (with the bold-marker colon pitfall called out), a residual-punctuation lint command, and stronger anti-translationese guidance.
- `README.zh-CN.md` reworked accordingly: full-width punctuation, corner-bracket quotes, and more natural phrasing (reviewed jointly with DeepSeek).

## [0.4.0] - 2026-06-11
### Added
- Chinese edition workflow (SKILL.md step 6): generate a parity-checked `README.zh-CN.md` in the same repo, with `references/bilingual-readme.md` covering translation boundaries (commands/code byte-identical, prose localized), tone rules, anchor handling, and maintenance.
- `scripts/check_bilingual.py`: bilingual parity checker enforcing identical command/mermaid blocks, matching URL/image sets, equal heading counts, and language switchers in both files.
- Dogfood: this repo now ships `README.zh-CN.md` with a language switcher on both editions.

### Changed
- Skill trigger description now fires on 中文 README / 双语 README / bilingual README / README.zh-CN.

## [0.3.0] - 2026-06-11
### Added
- Hero style catalog: ten self-hosted animated SVG hero templates in `assets/heroes/` (swiss, aurora, vignelli, orbit, blueprint, brutalist, dotwave, editorial, outline, bauhaus), each with a branded preview in `assets/heroes/previews/` and a live gallery in the README.
- Cookbook style-catalog table mapping each hero style to the project temperament it fits.

### Changed
- SKILL.md step 3 now points to the catalog and instructs letting the user pick a hero style by name.

### Removed
- `assets/hero-swiss-template.svg`, superseded by `assets/heroes/swiss.svg`.

## [0.2.0] - 2026-06-11
### Added
- Self-hosted animated hero SVG guidance: new "Self-hosted hero SVG" cookbook section and `assets/hero-swiss-template.svg` (Swiss Grid style, HyperFrames design-guide lineage; ~2KB, zero third-party requests, readable at frame 0).

### Changed
- Own README hero switched from capsule-render + readme-typing-svg (two external services) to the self-hosted Swiss Grid SVG; footer simplified to match.

## [0.1.0] - 2026-06-10
### Added
- Initial `repo-beautify` Agent Skill: verified-facts scan, two README style templates (classic / visual), visual services cookbook, structure and content-merge rules.
- `scripts/scan_repo.sh`: storefront fact scanner (manifest, license, remote, registry publish status, GitHub description/topics/visibility).
- `scripts/build_compare.py`: side-by-side README variant comparison page with GitHub CSS, mermaid rendering, and dark mode toggle.
- Anti-fabrication hard rules: fact ledger (every claim cites scan JSON, a file path, a command output, or an API result), badge evidence requirements, content-merge inventory diff.
- Hardened per multi-model review (Claude + GPT-5.5): registry status split into published/unpublished/unknown states, default-branch detection via GitHub API, `github_api_status` field, DOMPurify sanitization in the comparison page, URL-encoding requirements for all service URLs, conditional Roadmap/Contributing sections, mermaid-cli validation step, alt-text and GitHub HTML sanitization guidance.
