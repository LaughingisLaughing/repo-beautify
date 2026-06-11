# Bilingual README (Chinese Edition)

How to generate a `README.zh-CN.md` in the same repo, localized rather than word-for-word translated, that cannot silently drift into lies.

## File layout and switcher

- `README.md` stays canonical (usually English). The Chinese edition lives at `README.zh-CN.md` (GitHub language-suffix convention; use `README.zh-TW.md` for Traditional Chinese only when asked).
- Both files carry a language switcher line directly under the hero/badges block, centered:
  - in `README.md`: `<p align="center">English | <a href="README.zh-CN.md">简体中文</a></p>`
  - in `README.zh-CN.md`: `<p align="center"><a href="README.md">English</a> | 简体中文</p>`
- The hero SVG is brand artwork: reuse the same file, do not fork a translated hero unless the user asks.

## What gets translated, what never does

**Translate** (localize, do not transliterate): prose paragraphs, section headings (keep the emoji), table cells that contain descriptions, blockquote prompts aimed at humans, image alt texts.

**Never translate**:
- fenced code blocks for commands/config/diagrams (`bash`, `json`, `yaml`, `mermaid`...): keep byte-identical to the English edition
- project names, command names, CLI flags, file paths, URLs, badge markup
- established dev terms where the English is the term (`symlink`, `frontmatter`, `fork`, `Pull Request`, `commit`); on first occurrence you may add a Chinese gloss in parentheses
- license names, version numbers

**Exception**: fenced blocks tagged `text` that contain natural-language prompts MAY be localized (agents accept Chinese prompts), but keep the same number of blocks in the same order.

## Tone rules for the Chinese edition

- 技术中文:简洁、直接、主动语态,避免翻译腔("运行这条命令"而不是"这条命令可以被运行")。
- 不要营销腔;原文克制,译文也克制。
- 标点使用中文全角标点;范围用半角连字符(如 1-10)。
- 中英文之间留一个空格(如 "在 GitHub 上")。

## Anchors and internal links

GitHub generates heading anchors from the heading text, so Chinese headings produce different anchors than English ones. Internal `#anchor` links inside `README.zh-CN.md` must point at the Chinese anchors of the same file, never at the English ones. Cross-file links (to docs, code, issues) stay unchanged.

## Validation (mandatory before finishing)

Run the parity checker:

```bash
python3 scripts/check_bilingual.py README.md README.zh-CN.md
```

It enforces:
- identical sequence of non-`text` code blocks (commands, json, mermaid)
- same count of `text` blocks
- same set of external URLs and image sources (the two switcher self-links are exempt)
- same heading count, and both files carry a switcher line

A parity failure usually means a translated command, a dropped section, or a stale edition after the English README changed. Fix the file, not the checker.

## Maintenance

The Chinese edition drifts when the English one changes. After any `README.md` edit, re-run the parity checker; if it fails, re-sync the affected sections. Mention this in the PR/commit that touches `README.md`.
