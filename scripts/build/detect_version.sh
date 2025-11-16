#!/usr/bin/env bash
# Purpose: Detect the project version for packaging/build naming.
#
# Behavior (first non-empty wins):
# 1) VERSION env override
# 2) Latest git tag by version (leading "v" stripped)
# 3) Version from pyproject.toml via python tomllib
# 4) Version from pyproject.toml via awk (BSD/macOS compatible)
# 5) Fallback "0.0.0"

set -euo pipefail

OVERRIDE="${VERSION:-}"
if [[ -n "${OVERRIDE}" ]]; then
  echo "${OVERRIDE}"
  exit 0
fi

# Try latest tag (ignore errors)
TAG_VER=$(git tag --list --sort=-v:refname 2>/dev/null | head -1 | sed -E 's/^v//') || TAG_VER=""
if [[ -n "${TAG_VER}" ]]; then
  echo "${TAG_VER}"
  exit 0
fi

# Try pyproject via Python tomllib
PY_VER=$(python3 - <<'PY' 2>/dev/null || true
import tomllib
print(tomllib.load(open('pyproject.toml','rb'))['project'].get('version',''))
PY
)
if [[ -n "${PY_VER}" ]]; then
  echo "${PY_VER}"
  exit 0
fi

# Try pyproject via awk (BSD compatible)
AWK_VER=$(awk -F '"' '/^[[:space:]]*version[[:space:]]*=/{print $2; exit}' pyproject.toml 2>/dev/null || true)
if [[ -n "${AWK_VER}" ]]; then
  echo "${AWK_VER}"
  exit 0
fi

echo "0.0.0"
