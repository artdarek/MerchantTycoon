#!/usr/bin/env bash
# Purpose: Create a versioned DMG in bin/ from the unversioned DMG artifact in dist/.
#
# Output: bin/merchant-tycoon-macos-{version}.dmg
# Env (optional):
#   VERSION   Override detected version
#   DIST_DIR  Source directory (default: dist)
#   BIN_DIR   Output directory (default: bin)
#   APP_NAME  App display name (default: "Merchant Tycoon")

set -euo pipefail

APP_NAME=${APP_NAME:-"Merchant Tycoon"}
DIST_DIR=${DIST_DIR:-dist}
BIN_DIR=${BIN_DIR:-bin}

DMG_SRC="${DIST_DIR}/${APP_NAME}.dmg"

refresh_tags() {
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git fetch --tags --quiet || true
  fi
}

detect_version() {
  VERSION="${VERSION:-}"
  if [[ -n "${VERSION}" ]]; then
    echo "${VERSION}"
    return
  fi
  bash scripts/build/detect_version.sh
}

main() {
  if [[ ! -f "${DMG_SRC}" ]]; then
    echo "DMG artifact not found: ${DMG_SRC}" >&2
    echo "Please create it first, for example:" >&2
    echo "  make build-dmg            # or part of build-artifacts if create-dmg is available" >&2
    exit 1
  fi

  refresh_tags
  local ver
  ver=$(detect_version)
  ver=${ver:-0.0.0}

  mkdir -p "${BIN_DIR}"
  local out="${BIN_DIR}/merchant-tycoon-macos-${ver}.dmg"
  echo "Version: ${ver}"
  echo "Copying ${DMG_SRC} -> ${out}"
  cp -f "${DMG_SRC}" "${out}"
  echo "✅ Created ${out}"
}

main "$@"
