#!/usr/bin/env bash
# Purpose: Generate a macOS .iconset directory from a source PNG (recommended 1024x1024).
#
# Env:
#   ICON         Source image path (default: docs/icon/icon.png or icon.png)
#   ICONSET_DIR  Output iconset dir (default: build/icon.iconset)

set -euo pipefail

ICONSET_DIR_DEFAULT="build/icon.iconset"
ICON_DEFAULT="docs/icon/icon.png"

SRC_ICON="${ICON:-}"
OUT_DIR="${ICONSET_DIR:-}"

if [[ -z "${SRC_ICON}" ]]; then
  if [[ -f "${ICON_DEFAULT}" ]]; then
    SRC_ICON="${ICON_DEFAULT}"
  elif [[ -f "icon.png" ]]; then
    SRC_ICON="icon.png"
  else
    echo "Source icon not found. Provide PNG via ICON=path/to/icon.png (recommended 1024x1024)." >&2
    exit 1
  fi
fi

OUT_DIR=${OUT_DIR:-$ICONSET_DIR_DEFAULT}

if ! command -v sips >/dev/null 2>&1; then
  echo "sips not found. This command requires macOS." >&2
  exit 1
fi

echo "Generating ${OUT_DIR} from ${SRC_ICON}..."
mkdir -p "${OUT_DIR}"

sips -z 16 16     "${SRC_ICON}" --out "${OUT_DIR}/icon_16x16.png" >/dev/null
sips -z 32 32     "${SRC_ICON}" --out "${OUT_DIR}/icon_16x16@2x.png" >/dev/null
sips -z 32 32     "${SRC_ICON}" --out "${OUT_DIR}/icon_32x32.png" >/dev/null
sips -z 64 64     "${SRC_ICON}" --out "${OUT_DIR}/icon_32x32@2x.png" >/dev/null
sips -z 128 128   "${SRC_ICON}" --out "${OUT_DIR}/icon_128x128.png" >/dev/null
sips -z 256 256   "${SRC_ICON}" --out "${OUT_DIR}/icon_128x128@2x.png" >/dev/null
sips -z 256 256   "${SRC_ICON}" --out "${OUT_DIR}/icon_256x256.png" >/dev/null
sips -z 512 512   "${SRC_ICON}" --out "${OUT_DIR}/icon_256x256@2x.png" >/dev/null
sips -z 512 512   "${SRC_ICON}" --out "${OUT_DIR}/icon_512x512.png" >/dev/null
cp "${SRC_ICON}" "${OUT_DIR}/icon_512x512@2x.png"

echo "✅ Created ${OUT_DIR} (use iconutil to convert to .icns if needed)"
