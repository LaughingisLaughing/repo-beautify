#!/usr/bin/env python3
"""Publish-safety audit: is this repo safe to open-source?

Usage:
  python3 publish_audit.py /path/to/repo [--history]

Checks (working tree = tracked files only):
  BLOCKER  well-known secret formats (AWS, GitHub, Slack, OpenAI/Anthropic/
           OpenRouter, Google, Stripe, JWT, private key blocks)
  BLOCKER  risky tracked filenames (.env*, *.pem, *.key, id_rsa*, credentials*)
  WARN     absolute home paths (/Users/<u>, /home/<u>, C:\\Users\\<u>)
  WARN     private/internal network addresses and hostnames
  WARN     personal author emails in git history (vs GitHub noreply)

--history additionally scans every line ever ADDED in git history with the
secret patterns: a secret deleted from the tip still lives in history.

Delegates to `gitleaks` for deep secret detection when it is installed;
the builtin patterns still run (they cover dimensions gitleaks does not).

Exit codes: 0 clean (warnings allowed), 1 blockers found.
Triage guidance: references/publish-safety.md.
"""
import re
import subprocess
import sys
from pathlib import Path

SECRET_PATTERNS = [
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("Slack token", re.compile(r"\bxox[bpars]-[A-Za-z0-9-]{10,}\b")),
    ("OpenAI/Anthropic/OpenRouter key", re.compile(r"\bsk-(?:ant-|or-v1-|proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Stripe key", re.compile(r"\b[sr]k_(?:live|test)_[A-Za-z0-9]{20,}\b")),
    ("Private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("Generic secret assignment", re.compile(
        r"(?i)\b(?:api[_-]?key|secret|token|passwd|password)\b\s*[:=]\s*['\"][A-Za-z0-9+/_-]{16,}['\"]")),
]
RISKY_FILES = re.compile(
    r"(^|/)(\.env(\..+)?|.+\.pem|.+\.p12|.+\.pfx|.+\.keystore|id_rsa.*|id_ed25519.*|"
    r".+\.key|credentials(\..+)?|\.netrc|\.npmrc|\.pypirc|service[-_]?account.*\.json)$", re.I)
HOME_PATH = re.compile(r"(?:/Users/|/home/|C:\\Users\\)[A-Za-z0-9_.-]+[/\\]")
PRIVATE_NET = re.compile(
    r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b"
    r"|\b[a-z0-9.-]+\.(?:internal|corp|lan|local)\b")
NOREPLY = re.compile(r"(users\.noreply\.github\.com|noreply|\[bot\])")
# 跳过明显的占位值,降低误报
PLACEHOLDER = re.compile(r"(?i)(example|placeholder|your[_-]?|xxx|<.*>|\{\{.*\}\}|\bdummy\b|\bsample\b)")


def sh(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True).stdout


def tracked_files(repo):
    return [f for f in sh(["git", "ls-files"], repo).splitlines() if f]


def scan_text(name, text, findings, where):
    for line_no, line in enumerate(text.splitlines(), 1):
        if PLACEHOLDER.search(line):
            continue
        for label, pat in SECRET_PATTERNS:
            if pat.search(line):
                findings.append(("BLOCKER", f"{label} @ {where}:{name}:{line_no}: {line.strip()[:90]}"))
        if HOME_PATH.search(line):
            findings.append(("WARN", f"absolute home path @ {where}:{name}:{line_no}: {line.strip()[:90]}"))
        if PRIVATE_NET.search(line):
            findings.append(("WARN", f"private network ref @ {where}:{name}:{line_no}: {line.strip()[:90]}"))


def main():
    args = [a for a in sys.argv[1:]]
    history = "--history" in args
    args = [a for a in args if a != "--history"]
    repo = Path(args[0] if args else ".").resolve()
    if not (repo / ".git").exists():
        sys.exit(f"not a git repo: {repo}")
    findings = []

    # 1) tracked filenames
    files = tracked_files(repo)
    for f in files:
        if RISKY_FILES.search(f):
            findings.append(("BLOCKER", f"risky tracked file: {f}"))

    # 2) tracked file contents
    for f in files:
        p = repo / f
        try:
            raw = p.read_bytes()
        except OSError:
            continue
        if len(raw) > 1_000_000 or b"\x00" in raw[:4096]:
            continue
        scan_text(f, raw.decode("utf-8", errors="replace"), findings, "tree")

    # 3) git history (added lines only)
    if history:
        log = sh(["git", "log", "-p", "--all", "--no-color"], repo)
        added = "\n".join(l[1:] for l in log.splitlines() if l.startswith("+") and not l.startswith("+++"))
        scan_text("(history)", added, findings, "history")

    # 4) author emails
    emails = sorted({e for e in sh(["git", "log", "--format=%ae%n%ce"], repo).splitlines() if e})
    personal = [e for e in emails if not NOREPLY.search(e)]
    if personal:
        findings.append(("WARN", f"author emails in history (deliberate is fine, else use GitHub noreply): {', '.join(personal)}"))

    # 5) delegate to gitleaks when available
    gitleaks = subprocess.run(["which", "gitleaks"], capture_output=True).returncode == 0
    if gitleaks:
        r = subprocess.run(["gitleaks", "detect", "--source", str(repo), "--no-banner", "--exit-code", "9"],
                           capture_output=True, text=True)
        if r.returncode == 9:
            findings.append(("BLOCKER", "gitleaks found leaks in git history (run `gitleaks detect -v` for details)"))
        elif r.returncode != 0:
            findings.append(("WARN", f"gitleaks errored (code {r.returncode}); builtin patterns still applied"))

    blockers = [f for s, f in findings if s == "BLOCKER"]
    warns = [f for s, f in findings if s == "WARN"]
    print(f"publish audit: {repo.name} | {len(files)} tracked files | history={'yes' if history else 'no'} | gitleaks={'yes' if gitleaks else 'no'}")
    for f in blockers:
        print(f"  BLOCKER  {f}")
    for f in warns:
        print(f"  WARN     {f}")
    if blockers:
        print("\nNOT safe to publish. A secret anywhere in history requires rotation AND a history purge;")
        print("deleting it from the tip is not enough. See references/publish-safety.md.")
        sys.exit(1)
    print("OK: no blockers." + (f" {len(warns)} warning(s) to review." if warns else ""))


if __name__ == "__main__":
    main()
