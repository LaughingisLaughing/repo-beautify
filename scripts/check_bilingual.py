#!/usr/bin/env python3
"""Parity checker for bilingual READMEs.

Usage: python3 check_bilingual.py README.md README.zh-CN.md

Enforces the rules in references/bilingual-readme.md:
- non-`text` fenced code blocks (bash/json/mermaid/...) must be an identical sequence
- `text` fenced blocks (localizable prompts) must match in count
- external URLs and image sources must match as sets (switcher self-links exempt)
- heading counts must match; both files must carry a language switcher line

Exit 0 when in sync, 1 with a report when drifted.
"""
import re
import sys
from pathlib import Path

FENCE = re.compile(r"^```(\w*)\n(.*?)^```\s*$", re.M | re.S)
URL = re.compile(r"https?://[^\s)\"'<>\]]+")
IMG = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
HTML_IMG = re.compile(r"<img[^>]+src=\"([^\"]+)\"")
HEADING = re.compile(r"^#{1,6}\s+\S", re.M)
SWITCHER_EXEMPT = {"README.md", "README.zh-CN.md", "README.zh-TW.md"}


def parse(path: Path):
    src = path.read_text(encoding="utf-8")
    blocks = [(lang or "", body) for lang, body in FENCE.findall(src)]
    prose = FENCE.sub("", src)
    urls = {u.rstrip(".,;:") for u in URL.findall(prose)}
    imgs = set(IMG.findall(prose)) | set(HTML_IMG.findall(prose))
    return {
        "blocks": blocks,
        "urls": urls,
        "imgs": {i for i in imgs if i not in SWITCHER_EXEMPT},
        "headings": len(HEADING.findall(prose)),
        "has_switcher": ("README.zh-CN.md" in src or "README.zh-TW.md" in src or "README.md" in src),
    }


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    a_path, b_path = Path(sys.argv[1]), Path(sys.argv[2])
    a, b = parse(a_path), parse(b_path)
    problems = []

    a_code = [(l, c) for l, c in a["blocks"] if l != "text"]
    b_code = [(l, c) for l, c in b["blocks"] if l != "text"]
    if len(a_code) != len(b_code):
        problems.append(f"non-text code blocks: {len(a_code)} vs {len(b_code)}")
    else:
        for i, ((la, ca), (lb, cb)) in enumerate(zip(a_code, b_code)):
            if la != lb or ca != cb:
                problems.append(f"code block #{i+1} differs (lang {la!r} vs {lb!r})")

    a_text = sum(1 for l, _ in a["blocks"] if l == "text")
    b_text = sum(1 for l, _ in b["blocks"] if l == "text")
    if a_text != b_text:
        problems.append(f"`text` prompt blocks: {a_text} vs {b_text}")

    for key in ("urls", "imgs"):
        only_a, only_b = a[key] - b[key], b[key] - a[key]
        if only_a:
            problems.append(f"{key} only in {a_path.name}: {sorted(only_a)[:5]}")
        if only_b:
            problems.append(f"{key} only in {b_path.name}: {sorted(only_b)[:5]}")

    if a["headings"] != b["headings"]:
        problems.append(f"heading count: {a['headings']} vs {b['headings']}")
    for p, d in ((a_path, a), (b_path, b)):
        if not d["has_switcher"]:
            problems.append(f"{p.name} missing language switcher line")

    if problems:
        print(f"DRIFT between {a_path.name} and {b_path.name}:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    print(f"OK: {a_path.name} and {b_path.name} are in parity "
          f"({len(a_code)} code blocks, {a['headings']} headings, {len(a['urls'])} urls)")


if __name__ == "__main__":
    main()
