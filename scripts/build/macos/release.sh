#!/usr/bin/env bash
# Purpose: Orchestrate macOS release packaging.
#
# Flow:
# - Ensure artifacts exist (build executable + .app, apply iconset, create DMG if possible)
# - Create versioned ZIP in bin/
# - If dist/Merchant Tycoon.dmg exists, create versioned DMG in bin/

set -euo pipefail

APP_NAME="Merchant Tycoon"
DIST_DIR="dist"
BIN_DIR="bin"

usage() {
  cat <<USAGE
Usage: $0 [command] [options]

Commands:
  package           Build (if needed) and zip dist artifacts to bin/merchant-tycoon-macos-{version}.zip

Environment variables (or options):
  VERSION           Override version used in output name (default: detect)
  FORCE_BUILD=1     Force running build before packaging

Options:
  --version X       Same as VERSION=X (override detected version)
  --force-build     Same as FORCE_BUILD=1
  -h, --help        Show this help

Examples:
  $0 package
  VERSION=1.5.1 $0 package
  FORCE_BUILD=1 $0 package
USAGE
}

# --- args/env ---
CMD="package"
VERSION_OVERRIDE="${VERSION:-}"
FORCE_BUILD_FLAG="${FORCE_BUILD:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    package) CMD="package" ; shift ;;
    --version) VERSION_OVERRIDE="$2" ; shift 2 ;;
    --force-build) FORCE_BUILD_FLAG="1" ; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

require_zip() {
  if ! command -v zip >/dev/null 2>&1; then
    echo "zip not found. Please install zip." >&2
    exit 1
  fi
}

build_artifacts_if_needed() {
  local need_build=0
  [[ -d "${DIST_DIR}" ]] || need_build=1
  [[ -d "${DIST_DIR}/${APP_NAME}.app" || -f "${DIST_DIR}/${APP_NAME}" ]] || need_build=1
  [[ "${FORCE_BUILD_FLAG}" == "1" ]] && need_build=1 || true
  if [[ ${need_build} -eq 1 ]]; then
    bash scripts/build/macos/build_artifacts.sh
  fi
}

release_dmg_if_present() {
  # If a DMG artifact exists, also create versioned DMG in bin/
  local dmg_src="${DIST_DIR}/${APP_NAME}.dmg"
  if [[ -f "${dmg_src}" ]]; then
    VERSION="${VERSION_OVERRIDE}" bash scripts/build/macos/release_as_dmg.sh
  else
    echo "[release] No DMG artifact found at ${dmg_src}; skipping DMG release"
  fi
}

do_package() {
  require_zip
  build_artifacts_if_needed
  VERSION="${VERSION_OVERRIDE}" bash scripts/build/macos/release_as_zip.sh
  release_dmg_if_present
}

case "${CMD}" in
  package) do_package ;;
  *) usage; exit 2 ;;
esac
