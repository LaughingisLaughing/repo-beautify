# Changelog

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
