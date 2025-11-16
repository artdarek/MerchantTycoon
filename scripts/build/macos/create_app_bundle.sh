#!/bin/bash
# Purpose: Create a macOS .app bundle wrapper around the terminal executable.
#
# Inputs/Assumptions:
# - Requires `dist/Merchant Tycoon` executable to exist (built by PyInstaller)
#
# Effects:
# - Creates `dist/Merchant Tycoon.app` with a launcher that opens Terminal
# - Installs executable into the bundle's Resources and generates Info.plist

set -e

APP_NAME="Merchant Tycoon"
BUNDLE_DIR="dist/${APP_NAME}.app"
CONTENTS_DIR="${BUNDLE_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"
EXECUTABLE="dist/Merchant Tycoon"

if [[ ! -f "${EXECUTABLE}" ]]; then
  echo "Executable not found: ${EXECUTABLE}" >&2
  echo "Please build the terminal executable first, for example:" >&2
  echo "  make build-artifacts    # builds executable + .app" >&2
  echo "  or: make build-macos" >&2
  exit 1
fi

echo "Creating .app bundle structure..."

# Clean up existing bundle if it exists
rm -rf "${BUNDLE_DIR}"

# Create directory structure
mkdir -p "${MACOS_DIR}"
mkdir -p "${RESOURCES_DIR}"

# Copy the executable to Resources (we'll launch it from there)
echo "Copying executable..."
cp "${EXECUTABLE}" "${RESOURCES_DIR}/merchant-tycoon-bin"
chmod +x "${RESOURCES_DIR}/merchant-tycoon-bin"

# Create the launcher script that opens Terminal
echo "Creating launcher script..."
cat > "${MACOS_DIR}/${APP_NAME}" << 'LAUNCHER_EOF'
#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESOURCES_DIR="${SCRIPT_DIR}/../Resources"
EXECUTABLE="${RESOURCES_DIR}/merchant-tycoon-bin"

# Launch the game in a new Terminal window with comfortable size
osascript <<EOF
tell application "Terminal"
    activate
    set newWindow to do script "cd '${RESOURCES_DIR}' && ./merchant-tycoon-bin ; echo '' ; echo 'Press any key to close this window...' ; read -n 1 ; exit"
    tell window 1
        set bounds to {50, 50, 1250, 750}
    end tell
end tell
EOF
LAUNCHER_EOF

chmod +x "${MACOS_DIR}/${APP_NAME}"

# Create Info.plist
echo "Creating Info.plist..."
cat > "${CONTENTS_DIR}/Info.plist" << 'PLIST_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Merchant Tycoon</string>
    <key>CFBundleDisplayName</key>
    <string>Merchant Tycoon</string>
    <key>CFBundleIdentifier</key>
    <string>com.artdarek.merchanttycoon</string>
    <key>CFBundleVersion</key>
    <string>1.1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.1.0</string>
    <key>CFBundleExecutable</key>
    <string>Merchant Tycoon</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2025 artdarek. MIT License.</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST_EOF

echo ""
echo "✅ .app bundle created successfully!"
echo ""
echo "Bundle location: ${BUNDLE_DIR}"
echo ""
echo "To test:"
echo "  open \"${BUNDLE_DIR}\""
echo ""
echo "To install:"
echo "  cp -r \"${BUNDLE_DIR}\" /Applications/"
echo ""
