#!/usr/bin/env bash
# Purpose: Build the standalone macOS terminal executable with PyInstaller.
#
# Inputs:
# - None (reads project sources and assets)
#
# Effects:
# - Produces `dist/Merchant Tycoon` (no .app bundle)
# - Exits if PyInstaller is not installed

set -euo pipefail

APP_NAME="Merchant Tycoon"

echo "Step 1/2: Checking PyInstaller..."
if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "PyInstaller not found. Install dev dependencies with: uv pip install -e '.[dev]'" >&2
  exit 1
fi

echo "Step 2/2: Building executable with PyInstaller..."
python3 -m PyInstaller \
  --name="${APP_NAME}" \
  --onefile \
  --collect-all textual \
  --collect-all rich \
  --add-data="src/merchant_tycoon/template/style.tcss:merchant_tycoon/template" \
  src/merchant_tycoon/__main__.py

echo ""
echo "✅ Executable build complete!"
echo "   Terminal executable: dist/${APP_NAME}"
