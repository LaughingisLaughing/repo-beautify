# Publish-Safety Triage Guide

What to do with each `scripts/publish_audit.py` finding before open-sourcing a repo.

## BLOCKER: a secret (token, key, private key block)

1. **Rotate it first.** The moment a repo goes public, assume every string in it has been read. Rotation is mandatory even if you purge history afterwards.
2. **Purge it from history** if it appears anywhere in `git log` (the audit's `--history` mode checks exactly this). Removing it from the current files is NOT enough:
   ```bash
   # preferred tool; rewrites history
   git filter-repo --replace-text <(echo 'THE_SECRET==>REDACTED')
   git push --force-with-lease
   ```
   History rewrites change every subsequent commit hash; coordinate with anyone who has clones, and re-tag releases.
3. Move the value to an environment variable or a vault, add the carrier file to `.gitignore`, and commit a `.env.example` with placeholder values instead.

## BLOCKER: risky tracked file (.env, *.pem, id_rsa, credentials.json...)

Even when the content looks harmless today: untrack it (`git rm --cached <file>`), add the pattern to `.gitignore`, and if it ever contained real credentials, treat it as a leaked secret (see above).

## WARN: absolute home paths (/Users/name, /home/name)

Leaks a username and machine layout, and breaks portability. Replace with relative paths, `~`, or environment variables. Common hiding spots: launch configs, log snippets pasted into docs, test fixtures.

## WARN: private network references (10.x.x.x, *.internal)

Usually fine in examples, but verify nothing maps your real internal topology (hostnames, service ports, dashboards). Replace real infra with `example.com` / documentation IPs (192.0.2.0/24).

## WARN: personal author emails in git history

A deliberate choice for many open-source authors; if not deliberate, set the GitHub noreply address for future commits:
```bash
git config user.email "<id>+<username>@users.noreply.github.com"
```
Rewriting past authorship needs `git filter-repo --mailmap`; only worth it before the repo has consumers.

## Not problems (do not "fix")

- Public GitHub usernames, repo URLs, MIT/Apache license texts
- `noreply` / `[bot]` commit emails
- Documentation placeholders (`YOUR_API_KEY`, `{{TOKEN}}`); the audit already skips obvious ones

## Pre-publish checklist (beyond secrets)

- [ ] `python3 scripts/publish_audit.py . --history` exits 0
- [ ] LICENSE file exists and matches the manifest's `license` field
- [ ] `.gitignore` covers `.env*`, key material, build output
- [ ] GitHub description + topics set (storefront step 5)
- [ ] README install instructions verified against registry state (the fact ledger)
