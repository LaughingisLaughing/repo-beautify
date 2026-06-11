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

## Tone and punctuation rules for the Chinese edition

写作语气:
- 技术中文,简洁、直接、主动语态。落笔前先想「中国工程师会怎么说这句话」,再写,而不是对着英文直译。读起来像翻译的句子(被动语态堆叠、"进行""作出"类壳动词、定语从句直搬)必须重写。
- 不要营销腔。原文克制,译文也克制。

标点(硬性规定,逐条检查):
- 引号一律用直角引号「」,嵌套用『』。不用 "" '' 也不用 "" 。
- 中文语境内的逗号、句号、冒号、分号、括号、顿号全部用全角:,。:;()、。**特别注意两个高频漏网处**:加粗标记后的冒号(`**规则**:` 的冒号两侧是星号和数字,容易漏)和列表项内的短句逗号。
- 半角标点只允许出现在:代码块、行内代码、URL、文件路径、markdown 语法本身(链接括号、徽章)。
- 范围用半角连字符(如 1-10);中英文之间留一个空格(如「在 GitHub 上」)。

生成后用这条命令找残留半角标点(命中即修,markdown 链接路径的括号除外):

```bash
python3 -c "
import re,sys
src=open('README.zh-CN.md',encoding='utf-8').read()
src=re.sub(r'\`\`\`(?!text)\w*\n.*?\`\`\`','',src,flags=re.S)
src=re.sub(r'\`[^\`]*\`|!?\[[^\]]*\]\([^)]*\)|https?://\S+|<[^>]+>','',src)
print([m.group() for m in re.finditer(r'[一-鿿][,;:()\"]|[,;:()\"][一-鿿]',src)] or '清洁')"
```

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
