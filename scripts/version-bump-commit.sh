#!/usr/bin/env bash
# Commit only the version bump in pyproject.toml
#
# Usage:
#   scripts/version-bump-commit.sh [--push]
#
# Steps:
# - Read current version from pyproject.toml
# - Unstage all files
# - Stage pyproject.toml only
# - Commit with message: "chore(): Version bump to vX.X.X"
# - If --push is provided, push the commit to remote

set -euo pipefail

PYPROJECT="pyproject.toml"

DO_PUSH="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --push) DO_PUSH="1"; shift ;;
    -h|--help)
      echo "Usage: $0 [--push]"; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; echo "Usage: $0 [--push]"; exit 2 ;;
  esac
done

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

if [[ "$DO_PUSH" == "1" ]]; then
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
else
  echo "(Skipping push; run with --push to push automatically)"
fi
