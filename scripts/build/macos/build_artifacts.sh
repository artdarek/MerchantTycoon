#!/usr/bin/env bash
# Purpose: Build macOS artifacts (terminal executable + .app) and polish them.
#
# Steps:
# - Build terminal executable (PyInstaller)
# - Create .app bundle if missing
# - Apply iconset if present (or attempt to generate then apply)
# - Create an unversioned DMG in `dist/` if `create-dmg` is available

set -euo pipefail

APP_NAME="Merchant Tycoon"
DIST_DIR="dist"
ICONSET_DIR_DEFAULT="build/icon.iconset"
ICON_ICNS_DEFAULT="build/icon.icns"

echo "[build] Building terminal executable..."
bash scripts/build/macos/create_app_executable.sh

if [[ ! -d "${DIST_DIR}/${APP_NAME}.app" ]]; then
  echo "[build] Creating .app bundle wrapper..."
  bash scripts/build/macos/create_app_bundle.sh
fi

if [[ ! -d "${DIST_DIR}/${APP_NAME}.app" || ! -f "${DIST_DIR}/${APP_NAME}" ]]; then
  echo "[build] Error: Missing artifacts in ${DIST_DIR}/" >&2
  ls -la "${DIST_DIR}" || true
  exit 1
fi

echo "[build] ✅ Artifacts present in ${DIST_DIR}/"

# Optionally apply iconset if present
ICONSET_DIR="${ICONSET_DIR:-$ICONSET_DIR_DEFAULT}"
ICON_ICNS="${ICON_ICNS:-$ICON_ICNS_DEFAULT}"
if [[ -d "${ICONSET_DIR}" ]]; then
  echo "[build] Applying iconset from ${ICONSET_DIR}..."
  ICONSET_DIR="${ICONSET_DIR}" ICON_ICNS="${ICON_ICNS}" bash scripts/build/macos/iconset_apply.sh || true
else
  echo "[build] No iconset found at ${ICONSET_DIR}; attempting to generate..."
  # Try to generate iconset (uses default ICON path if not provided)
  ICONSET_DIR="${ICONSET_DIR}" bash scripts/build/macos/iconset_generate.sh || true
  if [[ -d "${ICONSET_DIR}" ]]; then
    echo "[build] Generated iconset. Applying..."
    ICONSET_DIR="${ICONSET_DIR}" ICON_ICNS="${ICON_ICNS}" bash scripts/build/macos/iconset_apply.sh || true
  else
    echo "[build] Iconset generation failed; skipping icon apply."
  fi
fi

# Optionally create a DMG in dist/ if create-dmg is available
if command -v create-dmg >/dev/null 2>&1; then
  echo "[build] Creating DMG in ${DIST_DIR}/..."
  OUT_DIR="dist" bash scripts/build/macos/create_app_dmg.sh || true
else
  echo "[build] create-dmg not found; skipping DMG (install via: brew install create-dmg)"
fi
