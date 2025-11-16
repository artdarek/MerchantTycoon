#!/usr/bin/env bash
# Commit only the version bump in pyproject.toml
#
# Steps:
# - Read current version from pyproject.toml
# - Unstage all files
# - Stage pyproject.toml only
# - Commit with message: "chore(): Version bump to vX.X.X"

set -euo pipefail

PYPROJECT="pyproject.toml"

if [[ ! -f "$PYPROJECT" ]]; then
  echo "File not found: $PYPROJECT" >&2
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not a git repository. Aborting." >&2
  exit 1
fi

# Read version (prefer Python tomllib, fallback to awk)
read_version() {
  local ver
  ver=$(python3 - <<'PY' 2>/dev/null || true
import tomllib
with open('pyproject.toml','rb') as f:
    data = tomllib.load(f)
print(data.get('project', {}).get('version', ''))
PY
)
  if [[ -z "$ver" ]]; then
    ver=$(awk -F '"' '/^[[:space:]]*version[[:space:]]*=/{print $2; exit}' "$PYPROJECT" 2>/dev/null || true)
  fi
  echo "$ver"
}

VERSION=$(read_version)
if [[ -z "$VERSION" ]]; then
  echo "Could not detect version in $PYPROJECT" >&2
  exit 1
fi

# Check if pyproject has changes; if not, nothing to commit
if git diff --quiet -- "$PYPROJECT" && git diff --cached --quiet -- "$PYPROJECT"; then
  echo "No changes detected in $PYPROJECT; nothing to commit."
  exit 0
fi

echo "Unstaging all files..."
git reset

echo "Staging $PYPROJECT..."
git add "$PYPROJECT"

MSG="chore(): Version bump to v$VERSION"
echo "Committing: $MSG"
git commit -m "$MSG"

echo "✅ Committed version bump: v$VERSION"

# Push the commit to the upstream (or set upstream to origin/<branch>)
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1; then
  echo "Pushing to upstream..."
  git push
else
  echo "No upstream set for branch '$BRANCH'. Pushing to origin and setting upstream..."
  git push -u origin "$BRANCH"
fi

echo "✅ Pushed commit on branch: $BRANCH"
