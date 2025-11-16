#!/usr/bin/env bash
# Bump project version in pyproject.toml and optionally create a git tag.
#
# Usage:
#   scripts/version-bump.sh [--major|--minor|--patch] [--create-tag]
#
# Behavior:
# - Reads current version from pyproject.toml (project.version)
# - Increments selected section (default: --patch if none provided)
# - Updates pyproject.toml in-place
# - If --create-tag is passed and inside a git repo, creates an annotated tag: v<new-version>

set -euo pipefail

usage() {
  cat <<USAGE
Usage: $0 [--major|--minor|--patch] [--create-tag]

Options:
  --major        Increment MAJOR (X.0.0)
  --minor        Increment MINOR (X.Y.0)
  --patch        Increment PATCH (X.Y.Z+1) [default]
  --create-tag   Create annotated git tag 'v<new-version>'
  -h, --help     Show this help

Examples:
  $0 --patch
  $0 --minor --create-tag
USAGE
}

INCR="patch"
CREATE_TAG="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --major) INCR="major"; shift ;;
    --minor) INCR="minor"; shift ;;
    --patch) INCR="patch"; shift ;;
    --create-tag) CREATE_TAG="1"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

PYPROJECT="pyproject.toml"
[[ -f "$PYPROJECT" ]] || { echo "File not found: $PYPROJECT" >&2; exit 1; }

# Read current version (prefer Python tomllib, fallback to awk)
read_current_version() {
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

CURRENT_VER=$(read_current_version)
if [[ -z "$CURRENT_VER" ]]; then
  echo "Could not detect current version in $PYPROJECT" >&2
  exit 1
fi

if [[ ! "$CURRENT_VER" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
  echo "Unsupported version format: $CURRENT_VER (expected X.Y.Z)" >&2
  exit 1
fi

MAJOR=${BASH_REMATCH[1]}
MINOR=${BASH_REMATCH[2]}
PATCH=${BASH_REMATCH[3]}

case "$INCR" in
  major)
    ((MAJOR+=1)); MINOR=0; PATCH=0 ;;
  minor)
    ((MINOR+=1)); PATCH=0 ;;
  patch)
    ((PATCH+=1)) ;;
  *) echo "Invalid increment type: $INCR" >&2; exit 2 ;;
esac

NEW_VER="${MAJOR}.${MINOR}.${PATCH}"

# Update pyproject.toml (first version= line)
tmpfile=$(mktemp)
awk -v newver="$NEW_VER" 'BEGIN{done=0} {
  if (!done && $0 ~ /^[[:space:]]*version[[:space:]]*=/) {
    gsub(/"[0-9]+\.[0-9]+\.[0-9]+"/, "\"" newver "\"")
    done=1
  }
  print
}' "$PYPROJECT" > "$tmpfile"
mv "$tmpfile" "$PYPROJECT"

echo "Bumped version: $CURRENT_VER -> $NEW_VER"

if [[ "$CREATE_TAG" == "1" ]]; then
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    tag="v$NEW_VER"
    if git rev-parse "$tag" >/dev/null 2>&1; then
      echo "Git tag already exists: $tag" >&2
      exit 1
    fi
    git tag -a "$tag" -m "Release $tag"
    echo "Created git tag: $tag"
  else
    echo "Not a git repository; skipping tag creation" >&2
  fi
fi

echo "Done."

