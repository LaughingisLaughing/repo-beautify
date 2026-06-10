#!/usr/bin/env bash
# scan_repo.sh — collect verified storefront facts for a repository as JSON.
# Usage: bash scan_repo.sh /path/to/repo
# Every fact downstream steps use MUST come from here (the "fact ledger"), not from memory.
# Designed for macOS bash 3.2; JSON emission via python3 (no here-docs, read-only-sandbox safe).

set -euo pipefail

PROJECT_DIR="${1:-.}"
[[ -d "$PROJECT_DIR" ]] || { echo "Error: '$PROJECT_DIR' is not a directory" >&2; exit 1; }
cd "$PROJECT_DIR"

# ---------- manifest ----------
NAME="" DESC="" VERSION="" MANIFEST="" MISSING_FIELDS=""
if [[ -f package.json ]]; then
  MANIFEST="package.json"
  NAME=$(python3 -c "import json;print(json.load(open('package.json')).get('name',''))" 2>/dev/null || true)
  DESC=$(python3 -c "import json;print(json.load(open('package.json')).get('description',''))" 2>/dev/null || true)
  VERSION=$(python3 -c "import json;print(json.load(open('package.json')).get('version',''))" 2>/dev/null || true)
  MISSING_FIELDS=$(python3 -c "
import json
d=json.load(open('package.json'))
print(','.join(k for k in ('description','author','repository','homepage','bugs','keywords','license') if not d.get(k)))" 2>/dev/null || true)
elif [[ -f pyproject.toml ]]; then
  MANIFEST="pyproject.toml"
  NAME=$(python3 -c "
import tomllib
d=tomllib.load(open('pyproject.toml','rb'))
p=d.get('project') or d.get('tool',{}).get('poetry',{})
print(p.get('name',''))" 2>/dev/null || true)
  DESC=$(python3 -c "
import tomllib
d=tomllib.load(open('pyproject.toml','rb'))
p=d.get('project') or d.get('tool',{}).get('poetry',{})
print(p.get('description',''))" 2>/dev/null || true)
  VERSION=$(python3 -c "
import tomllib
d=tomllib.load(open('pyproject.toml','rb'))
p=d.get('project') or d.get('tool',{}).get('poetry',{})
print(p.get('version',''))" 2>/dev/null || true)
elif [[ -f Cargo.toml ]]; then
  MANIFEST="Cargo.toml"
  NAME=$(grep -m1 '^name' Cargo.toml 2>/dev/null | sed 's/name[[:space:]]*=[[:space:]]*"//;s/".*$//' || true)
  VERSION=$(grep -m1 '^version' Cargo.toml 2>/dev/null | sed 's/version[[:space:]]*=[[:space:]]*"//;s/".*$//' || true)
fi
[[ -z "$NAME" ]] && NAME=$(basename "$PWD")

# ---------- license ----------
LICENSE=""
for f in LICENSE LICENSE.md LICENSE.txt; do
  if [[ -f "$f" ]]; then
    if head -5 "$f" | grep -qi "MIT"; then LICENSE="MIT"
    elif head -5 "$f" | grep -qi "Apache"; then LICENSE="Apache-2.0"
    elif head -5 "$f" | grep -qi "GPL"; then LICENSE="GPL"
    else LICENSE="present ($f)"; fi
    break
  fi
done

# ---------- git remote / branches / tags ----------
OWNER="" REPO="" CURRENT_BRANCH="" DEFAULT_BRANCH="" LATEST_TAG=""
if git rev-parse --git-dir >/dev/null 2>&1; then
  REMOTE=$(git remote get-url origin 2>/dev/null || true)
  if [[ "$REMOTE" == git@* ]]; then OWNER_REPO=$(echo "$REMOTE" | sed 's/.*://;s/\.git$//')
  else OWNER_REPO=$(echo "$REMOTE" | sed -E 's|https?://[^/]+/||;s/\.git$//'); fi
  OWNER=$(echo "${OWNER_REPO:-}" | cut -d'/' -f1)
  REPO=$(echo "${OWNER_REPO:-}" | cut -d'/' -f2)
  CURRENT_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || true)
  DEFAULT_BRANCH=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||' || true)
  LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || true)
fi

# ---------- package manager / CI ----------
PM=""
[[ -f pnpm-lock.yaml ]] && PM="pnpm"; [[ -z "$PM" && -f yarn.lock ]] && PM="yarn"
[[ -z "$PM" && -f package.json ]] && PM="npm"
[[ -z "$PM" && -f poetry.lock ]] && PM="poetry"; [[ -z "$PM" && -f requirements.txt ]] && PM="pip"
[[ -z "$PM" && -f pyproject.toml ]] && PM="pip"
[[ -z "$PM" && -f Cargo.toml ]] && PM="cargo"; [[ -z "$PM" && -f go.mod ]] && PM="go"
CI=""
[[ -d .github/workflows ]] && CI="github-actions"
[[ -z "$CI" && -f .gitlab-ci.yml ]] && CI="gitlab"

# ---------- community / docs files (link only what exists) ----------
HAS_CHANGELOG="false"; [[ -f CHANGELOG.md ]] && HAS_CHANGELOG="true"
HAS_CONTRIBUTING="false"; { [[ -f CONTRIBUTING.md ]] || [[ -f .github/CONTRIBUTING.md ]]; } && HAS_CONTRIBUTING="true"
HAS_COC="false"; { [[ -f CODE_OF_CONDUCT.md ]] || [[ -f .github/CODE_OF_CONDUCT.md ]]; } && HAS_COC="true"
HAS_SECURITY="false"; { [[ -f SECURITY.md ]] || [[ -f .github/SECURITY.md ]]; } && HAS_SECURITY="true"
HAS_FUNDING="false"; [[ -f .github/FUNDING.yml ]] && HAS_FUNDING="true"
DEMO_ASSETS=$(find . -maxdepth 3 \( -path ./node_modules -o -path ./.git \) -prune -o \
  -type f \( -iname "*.gif" -o -iname "demo*.png" -o -iname "screenshot*.png" -o -iname "*.cast" \) -print 2>/dev/null | head -5 | tr '\n' ',' || true)

# ---------- registry publish status (CRITICAL: drives install instructions) ----------
# States: published_npm | published_pypi | unpublished | unknown_tool_missing | unknown_network | not_applicable
PUBLISHED="not_applicable"
if [[ "$MANIFEST" == "package.json" && -n "$NAME" ]]; then
  if ! command -v npm >/dev/null 2>&1; then PUBLISHED="unknown_tool_missing"
  else
    set +e; NPM_OUT=$(npm view "$NAME" version 2>&1); NPM_RC=$?; set -e
    if [[ $NPM_RC -eq 0 ]]; then PUBLISHED="published_npm"
    elif echo "$NPM_OUT" | grep -q "E404"; then PUBLISHED="unpublished"
    else PUBLISHED="unknown_network"; fi
  fi
elif [[ "$MANIFEST" == "pyproject.toml" && -n "$NAME" ]]; then
  if ! command -v curl >/dev/null 2>&1; then PUBLISHED="unknown_tool_missing"
  else
    HTTP=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "https://pypi.org/pypi/$NAME/json" 2>/dev/null || echo "000")
    case "$HTTP" in
      200) PUBLISHED="published_pypi" ;;
      404) PUBLISHED="unpublished" ;;
      *)   PUBLISHED="unknown_network" ;;
    esac
  fi
fi

# ---------- GitHub-side metadata ----------
GH_API_STATUS="skipped" GH_JSON=""
if [[ -n "$OWNER" && -n "$REPO" ]]; then
  if command -v curl >/dev/null 2>&1; then
    HTTP=$(curl -s -o /tmp/repo_beautify_gh.$$ -w "%{http_code}" --max-time 10 "https://api.github.com/repos/$OWNER/$REPO" 2>/dev/null || echo "000")
    case "$HTTP" in
      200) GH_API_STATUS="ok"; GH_JSON=$(cat /tmp/repo_beautify_gh.$$) ;;
      404) GH_API_STATUS="not_found_or_private" ;;
      403|429) GH_API_STATUS="rate_limited" ;;
      *)   GH_API_STATUS="network_error" ;;
    esac
    rm -f /tmp/repo_beautify_gh.$$
  else
    GH_API_STATUS="curl_missing"
  fi
fi

# ---------- emit JSON via python3 (robust escaping, no here-doc) ----------
export RB_NAME="$NAME" RB_DESC="$DESC" RB_VERSION="$VERSION" RB_MANIFEST="$MANIFEST" \
  RB_MISSING="$MISSING_FIELDS" RB_LICENSE="$LICENSE" RB_OWNER="$OWNER" RB_REPO="$REPO" \
  RB_CURRENT_BRANCH="$CURRENT_BRANCH" RB_DEFAULT_BRANCH="$DEFAULT_BRANCH" RB_TAG="$LATEST_TAG" \
  RB_PM="$PM" RB_CI="$CI" RB_PUBLISHED="$PUBLISHED" RB_GH_STATUS="$GH_API_STATUS" \
  RB_GH_JSON="$GH_JSON" RB_HAS_CHANGELOG="$HAS_CHANGELOG" RB_HAS_CONTRIBUTING="$HAS_CONTRIBUTING" \
  RB_HAS_COC="$HAS_COC" RB_HAS_SECURITY="$HAS_SECURITY" RB_HAS_FUNDING="$HAS_FUNDING" \
  RB_DEMO_ASSETS="$DEMO_ASSETS"

python3 -c "
import json, os
e = os.environ
gh = {}
if e.get('RB_GH_JSON'):
    try: gh = json.loads(e['RB_GH_JSON'])
    except Exception: gh = {}
out = {
  'name': e.get('RB_NAME',''), 'description': e.get('RB_DESC',''), 'version': e.get('RB_VERSION',''),
  'manifest': e.get('RB_MANIFEST',''), 'manifest_missing_fields': e.get('RB_MISSING',''),
  'license': e.get('RB_LICENSE',''), 'owner': e.get('RB_OWNER',''), 'repo': e.get('RB_REPO',''),
  'current_branch': e.get('RB_CURRENT_BRANCH',''),
  'default_branch': gh.get('default_branch') or e.get('RB_DEFAULT_BRANCH','') or e.get('RB_CURRENT_BRANCH',''),
  'latest_tag': e.get('RB_TAG',''), 'package_manager': e.get('RB_PM',''), 'ci': e.get('RB_CI',''),
  'registry_published': e.get('RB_PUBLISHED',''),
  'github_api_status': e.get('RB_GH_STATUS',''),
  'github_description': gh.get('description') or '', 'github_topics': gh.get('topics', []),
  'github_private': gh.get('private'), 'github_homepage': gh.get('homepage') or '',
  'github_has_issues': gh.get('has_issues'),
  'has_changelog': e.get('RB_HAS_CHANGELOG')=='true', 'has_contributing': e.get('RB_HAS_CONTRIBUTING')=='true',
  'has_code_of_conduct': e.get('RB_HAS_COC')=='true', 'has_security_policy': e.get('RB_HAS_SECURITY')=='true',
  'has_funding': e.get('RB_HAS_FUNDING')=='true', 'demo_assets': [a for a in e.get('RB_DEMO_ASSETS','').split(',') if a],
}
print(json.dumps(out, indent=2, ensure_ascii=False))
"
