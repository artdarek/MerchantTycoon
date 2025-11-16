#!/usr/bin/env bash
# Purpose: Create an unversioned DMG in dist/ from the built .app bundle.
#
# Env (optional):
#   APP_NAME     Display name (default: "Merchant Tycoon")
#   DIST_DIR     Source directory (default: dist)
#   VOLNAME      Mounted volume name (default: APP_NAME)
#   DMG_NAME     Output filename (default: "${APP_NAME}.dmg")
#   OUT_DIR      Output directory (default: dist)
#   WINDOW_POS   create-dmg --window-pos (default: "200 120")
#   WINDOW_SIZE  create-dmg --window-size (default: "800 400")
#   ICON_SIZE    create-dmg --icon-size (default: 100)
#   APP_LINK_POS create-dmg --app-drop-link (default: "600 185")

set -euo pipefail

APP_NAME=${APP_NAME:-"Merchant Tycoon"}
DIST_DIR=${DIST_DIR:-dist}
VOLNAME=${VOLNAME:-"${APP_NAME}"}
WINDOW_POS=${WINDOW_POS:-"200 120"}
WINDOW_SIZE=${WINDOW_SIZE:-"800 400"}
ICON_SIZE=${ICON_SIZE:-100}
APP_LINK_POS=${APP_LINK_POS:-"600 185"}

APP_BUNDLE="${DIST_DIR}/${APP_NAME}.app"
OUT_DIR=${OUT_DIR:-dist}

if ! command -v create-dmg >/dev/null 2>&1; then
  echo "create-dmg not found. Install with: brew install create-dmg" >&2
  exit 1
fi

if [[ ! -d "${APP_BUNDLE}" ]]; then
  echo "App bundle not found at: ${APP_BUNDLE}" >&2
  echo "Build app bundle first." >&2
  exit 1
fi

# Default DMG name matches app artifact name (no version)
DMG_BASE="${APP_NAME}.dmg"
DMG_NAME=${DMG_NAME:-"${DMG_BASE}"}
mkdir -p "${OUT_DIR}"
DMG_PATH="${OUT_DIR}/${DMG_NAME}"

echo "Creating DMG: ${DMG_PATH} from ${APP_BUNDLE}"
rm -f "${DMG_PATH}" || true

# Split pairs like "200 120"
set -- ${WINDOW_POS}
WIN_X=$1; WIN_Y=$2
set -- ${WINDOW_SIZE}
WIN_W=$1; WIN_H=$2
set -- ${APP_LINK_POS}
LINK_X=$1; LINK_Y=$2

create-dmg \
  --volname "${VOLNAME}" \
  --window-pos ${WIN_X} ${WIN_Y} \
  --window-size ${WIN_W} ${WIN_H} \
  --icon-size ${ICON_SIZE} \
  --app-drop-link ${LINK_X} ${LINK_Y} \
  "${DMG_PATH}" \
  "${APP_BUNDLE}"

echo "✅ Created DMG: ${DMG_PATH}"
