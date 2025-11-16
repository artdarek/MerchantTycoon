#!/usr/bin/env bash
# Purpose: Convert a .iconset to .icns and apply it to the macOS .app bundle.
#
# Env (optional):
#   ICONSET_DIR  Path to .iconset dir (default: build/icon.iconset)
#   ICON_ICNS    Output .icns path (default: build/icon.icns)
#   APP_BUNDLE   Path to .app bundle (default: dist/"Merchant Tycoon".app)

set -euo pipefail

ICONSET_DIR=${ICONSET_DIR:-build/icon.iconset}
ICON_ICNS=${ICON_ICNS:-build/icon.icns}
APP_NAME="Merchant Tycoon"
APP_BUNDLE=${APP_BUNDLE:-"dist/${APP_NAME}.app"}

if ! command -v iconutil >/dev/null 2>&1; then
  echo "iconutil not found. This command requires macOS." >&2
  exit 1
fi

if [[ ! -d "${ICONSET_DIR}" ]]; then
  echo "${ICONSET_DIR} not found. Run: make build-iconset" >&2
  exit 1
fi

echo "Converting ${ICONSET_DIR} -> ${ICON_ICNS}..."
iconutil -c icns "${ICONSET_DIR}" -o "${ICON_ICNS}"

RES_DIR="${APP_BUNDLE}/Contents/Resources"
PLIST="${APP_BUNDLE}/Contents/Info.plist"

if [[ ! -d "${RES_DIR}" ]]; then
  echo "App bundle not found. Build it first with dedicated script" >&2
  exit 1
fi

echo "Copying icon.icns into app bundle..."
cp "${ICON_ICNS}" "${RES_DIR}/AppIcon.icns"

echo "Setting CFBundleIconFile in Info.plist..."
/usr/libexec/PlistBuddy -c "Set :CFBundleIconFile AppIcon" "${PLIST}" 2>/dev/null \
  || /usr/libexec/PlistBuddy -c "Add :CFBundleIconFile string AppIcon" "${PLIST}"

echo "✅ Applied AppIcon.icns to ${APP_BUNDLE}"
