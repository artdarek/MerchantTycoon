#!/usr/bin/env bash
# Purpose: Create a versioned ZIP in bin/ from artifacts in dist/.
#
# Output: bin/merchant-tycoon-macos-{version}.zip
# Includes: .app bundle, terminal executable, and the DMG if present.

set -euo pipefail

APP_NAME="Merchant Tycoon"
DIST_DIR="dist"
BIN_DIR="bin"


require_zip() {
  if ! command -v zip >/dev/null 2>&1; then
    echo "zip not found. Please install zip." >&2
    exit 1
  fi
}

refresh_tags() {
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git fetch --tags --quiet || true
  fi
}

detect_version() {
  # Prefer explicit override, otherwise delegate to shared detector
  if [[ -n "${VERSION_OVERRIDE:-}" ]]; then
    echo "${VERSION_OVERRIDE}"
    return
  fi
  bash scripts/build/detect_version.sh
}

collect_artifacts() {
  # Build list of artifacts to include; error if none present
  local items=()
  [[ -d "${DIST_DIR}/${APP_NAME}.app" ]] && items+=("${APP_NAME}.app")
  [[ -f "${DIST_DIR}/${APP_NAME}" ]] && items+=("${APP_NAME}")
  # Include DMG if present
  [[ -f "${DIST_DIR}/${APP_NAME}.dmg" ]] && items+=("${APP_NAME}.dmg")
  if [[ ${#items[@]} -eq 0 ]]; then
    echo "No build artifacts found in '${DIST_DIR}/'." >&2
    echo "Please build them first, for example:" >&2
    echo "  make build-artifacts    # builds executable + .app" >&2
    echo "  or: make build-macos" >&2
    echo "Directory contents of '${DIST_DIR}/' (if any):" >&2
    ls -la "${DIST_DIR}" || true
    return 1
  fi
  printf '%s\n' "${items[@]}"
}

VERSION_OVERRIDE="${VERSION:-}"

main() {
  require_zip
  refresh_tags

  local ver
  ver=$(detect_version)
  [[ -n "${ver}" ]] || ver="0.0.0"

  # Collect artifacts (separate function) – compatible with older bash (no mapfile)
  local inclu=()
  while IFS= read -r line; do
    inclu+=("$line")
  done < <(collect_artifacts) || exit 1
  mkdir -p "${BIN_DIR}"
  local out="${BIN_DIR}/merchant-tycoon-macos-${ver}.zip"
  echo "Version: ${ver}"
  echo -n "Including:"; for x in "${inclu[@]}"; do echo -n " ${x}"; done; echo
  echo "Zipping ${DIST_DIR}/ -> ${out}"
  (
    cd "${DIST_DIR}"
    zip -yr "../${out}" "${inclu[@]}" >/dev/null
  )
  echo "✅ Created ${out}"
}

main "$@"
