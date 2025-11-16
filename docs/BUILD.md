# Building Merchant Tycoon macOS App

This guide explains how to build a standalone macOS application bundle (.app) for Merchant Tycoon.

## Quick Start

The easiest way to build and package on macOS is to use the interactive build menu:

```bash
make build
```

You’ll see options like:

- [m] Build artifacts (executable + .app)
- [i] Create iconset (build/icon.iconset)
- [a] Apply iconset to .app (set AppIcon.icns)
- [b] Package bin zip (bin/merchant-tycoon-macos-{version}.zip)
- [d] Create DMG (dist/Merchant Tycoon.dmg)
- [v] Versionize macOS app (dist/version/MerchantTycoon-{version}-{n} + zip)
- [x] Delete old build (clean)

Common flows:

1) Build the app:
```bash
make build   # then press m (or: make build-macos-artifacts)
```

2) Generate and apply an app icon (optional):
```bash
make build   # then press i (provide ICON=... if needed)
make build   # then press a
```

3) Create a versioned bundle and a matching zip archive:
```bash
make build   # then press v
```

4) Package a release zip (bin/merchant-tycoon-macos-{version}.zip):
```bash
make build   # then press b (or: make build-bin)
```

5) Create a DMG installer (dist/Merchant Tycoon.dmg):
```bash
make build   # then press d (or: make build-dmg)
```

After (1), you’ll have:
- `dist/Merchant Tycoon` (standalone executable)
- `dist/Merchant Tycoon.app` (double‑clickable app)

After (3), you’ll also get:
- `dist/version/MerchantTycoon-{version}-{n}/` (copied from dist)
- `dist/version/MerchantTycoon-{version}-{n}.zip` (archive of that folder)

## Prerequisites

- macOS 10.13 (High Sierra) or later
- Python 3.13+ (with Textual installed)
- pip or uv package manager
- PyInstaller (install with dev dependencies: `uv pip install -e '.[dev]'`)

## Understanding TUI Applications

Merchant Tycoon is a **Terminal User Interface (TUI)** application built with the Textual framework. Unlike GUI apps, TUI apps run inside a terminal window and use text-based rendering. This requires special handling when creating a .app bundle.

## Detailed Build Process

### Method 1: Using Make (Recommended)

Simply run:

```bash
make build-macos
```

To clean build artifacts:

```bash
make build-clean
```

### Method 2: Manual Build Steps

If you prefer to build manually:

#### Step 1: Install PyInstaller

**Option A: Install dev dependencies (recommended)**

```bash
uv pip install -e .[dev]
```

This installs PyInstaller along with other development tools defined in `pyproject.toml`.

**Option B: Install PyInstaller directly**

```bash
pip install pyinstaller
```

#### Step 2: Build the Terminal Executable

Build the standalone executable:

```bash
python3 -m PyInstaller \
  --name="Merchant Tycoon" \
  --onefile \
  --collect-all textual \
  --collect-all rich \
  --add-data="src/merchant_tycoon/template/style.tcss:merchant_tycoon/template" \
  src/merchant_tycoon/__main__.py
```

**Important flags explained:**
- `--name="Merchant Tycoon"` - Name of the application
- `--onefile` - Bundle everything into a single executable
- `--collect-all textual` - Recursively include all Textual modules (required for TUI)
- `--collect-all rich` - Recursively include all Rich modules (required by Textual)
- `--add-data` - Include non-Python files (CSS stylesheet)
- **No `--windowed` flag** - TUI apps need terminal access, not GUI mode

This creates: `dist/Merchant Tycoon` (~13.5 MB standalone executable)

#### Step 3: Create .app Bundle Wrapper

Since this is a TUI app, we need a wrapper that opens Terminal and runs the executable:

```bash
./scripts/build/macos/create_app_bundle.sh
```

This creates a proper macOS .app bundle at `dist/Merchant Tycoon.app` that:
- Opens Terminal automatically when double-clicked
- Runs the game inside the terminal
- Can be moved to /Applications like any Mac app
- Closes terminal after game exits

### Build Output

After building, you'll have:
- **Terminal Executable**: `dist/Merchant Tycoon` - Can be run from command line
- **.app Bundle**: `dist/Merchant Tycoon.app` - Double-clickable application

If you versionize (recommended for releases):
- **Versioned Folder**: `dist/version/MerchantTycoon-{version}-{n}`
- **Zip Archive**: `dist/version/MerchantTycoon-{version}-{n}.zip`

Where `{version}` is read from `pyproject.toml` and `{n}` auto‑increments.

### Method 3: Using py2app (Alternative, Not Recommended)

py2app is macOS-specific but has proven unreliable for TUI applications. A setup script is provided for reference:

```bash
pip install py2app
rm -rf build dist
python3 setup_py2app.py py2app
```

**Note:** This method is not recommended and may not work correctly.

## Running the App

### Option 1: Double-click the .app bundle (Recommended)

For end users, simply double-click `Merchant Tycoon.app` in Finder, or:

```bash
open "dist/Merchant Tycoon.app"
```

### Option 2: Run the executable directly

For developers and terminal users:

```bash
./dist/Merchant\ Tycoon
```

Or:

```bash
cd dist
./Merchant\ Tycoon
```

## Distribution

### For Personal Use

Simply copy the app to your Applications folder:

```bash
cp -r "dist/Merchant Tycoon.app" /Applications/
```

### For Public Distribution

If you want to distribute the app to others:

#### 1. Code Signing (Optional but recommended)

```bash
codesign --deep --force --sign - "dist/Merchant Tycoon.app"
```

#### 2. Create DMG (Recommended)

```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
  --volname "Merchant Tycoon" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --app-drop-link 600 185 \
  "MerchantTycoon.dmg" \
  "dist/Merchant Tycoon.app"
```

#### 3. Create ZIP

You can use the versioned zip generated by the build menu:

```bash
make build   # then press v
ls dist/version/MerchantTycoon-*.zip
```

Or zip manually (simple single‑bundle zip):

```bash
cd dist
zip -r "../MerchantTycoon-macOS.zip" "Merchant Tycoon.app"
cd ..
```

The versioned zip includes both the terminal executable and the .app bundle.

### Packaging Releases (ZIP + DMG)

You can produce versioned release artifacts under `bin/` using the Make targets and scripts:

- `make build-bin` — creates `bin/merchant-tycoon-macos-{version}.zip`
  - Detects version (override with `VERSION=...`).
  - Ensures artifacts exist (builds if missing when using `make build-release`).
  - Includes `dist/Merchant Tycoon.app`, the terminal executable, and the DMG if present.

- `make build-dmg` — creates `dist/Merchant Tycoon.dmg` (unversioned, matches artifacts)
  - Uses `create-dmg` (install with `brew install create-dmg`).
  - DMG is also created automatically during `build-artifacts` if `create-dmg` is available.

- `make build-release` — orchestrates build + package
  - Builds artifacts if needed, creates the versioned ZIP in `bin/`, and if a DMG exists in `dist/`, also creates a versioned DMG in `bin/`.

Version detection order (for release zip/DMG names):
- `VERSION` env override
- Latest git tag by version (leading `v` stripped)
- `pyproject.toml` version
- Fallback `0.0.0`

Related scripts:
- `scripts/build/macos/build_artifacts.sh`
- `scripts/build/macos/release_as_zip.sh`
- `scripts/build/macos/create_app_dmg.sh`
- `scripts/build/macos/release_as_dmg.sh`
- `scripts/build/macos/release.sh`
- `scripts/build/detect_version.sh`

## App Icon (Optional)

To create and apply an application icon:

1) Generate an `.iconset` from a PNG (1024×1024 recommended):

```bash
make build-iconset ICON=docs/icon/icon.png
```

This creates `build/icon.iconset/` with all required sizes using macOS `sips`.

2) Convert and apply to the .app bundle:

```bash
make build-iconset-apply
```

This converts to `build/icon.icns` with `iconutil`, copies it as `AppIcon.icns` into `dist/Merchant Tycoon.app/Contents/Resources`, and updates `Info.plist` accordingly.

## Troubleshooting

### "Merchant Tycoon.app is damaged and can't be opened"

This is macOS Gatekeeper preventing unsigned apps. Users can bypass this:

```bash
xattr -cr "/Applications/Merchant Tycoon.app"
```

Or: System Settings → Privacy & Security → Click "Open Anyway"

### Missing Textual Modules Error

If you get `ModuleNotFoundError: No module named 'textual'` or similar:

1. Make sure you're using Python 3.13+:
   ```bash
   python3 --version  # Should show 3.13+
   python3 -m PyInstaller ...
   ```

2. Ensure you're using `--collect-all textual --collect-all rich` flags (not just `--hidden-import`)

### Missing style.tcss

If the app runs but looks wrong, the stylesheet wasn't included. Make sure to use the `--add-data` flag.

### App doesn't start or crashes

Check the system logs for errors:

```bash
log show --predicate 'process == "Merchant Tycoon"' --last 1m
```

## Clean Build

To clean all build artifacts:

```bash
make build-clean
```

Or manually:

```bash
rm -rf build dist __pycache__
find . -type d -name "*.egg-info" -exec rm -rf {} +
find . -type d -name "__pycache__" -exec rm -rf {} +
```

## Advanced Options

### Custom Icon

To add a custom icon:

1. Create an `.icns` file from your icon image
2. Add to PyInstaller command:
   ```bash
   --icon=path/to/icon.icns
   ```

### Universal Binary (Intel + Apple Silicon)

To create a universal binary that works on both architectures:

1. Build on an Intel Mac: `dist/Merchant Tycoon-x86_64`
2. Build on an Apple Silicon Mac: `dist/Merchant Tycoon-arm64`
3. Combine with lipo:
   ```bash
   lipo -create -output "Merchant Tycoon" \
     "Merchant Tycoon-x86_64" \
     "Merchant Tycoon-arm64"
   ```

## Technical Details

### File Size

- **Terminal Executable**: ~13.5 MB
- **.app Bundle**: ~13.5 MB (same, just wrapped)

The bundle includes:
- Python interpreter
- Textual framework and all dependencies
- Rich library for terminal rendering
- All game code and data files
- No external dependencies required

### Architecture

- The app is architecture-specific (arm64 for Apple Silicon, x86_64 for Intel)
- Built app runs on the architecture it was built on
- Use universal binary approach for cross-architecture support

### Save Files

- Save files are stored in `~/.config/merchant_tycoon/`
- Same location whether running from source or built app
- User data is preserved across updates

## Version Information

- Built with: PyInstaller 6.x+
- Python: 3.13+
- Textual Framework: 0.47.0+
- Target: macOS 10.13+ (High Sierra and later)
- Architecture: Native (arm64 or x86_64)

## Build System Files

- Make targets:
  - `build` — interactive menu
  - `build-macos-artifacts` — build executable + .app (applies iconset if available; attempts to generate if missing)
  - `build-macos` — same as above, explicit two-step build
  - `build-iconset` / `build-iconset-apply` — icon generation and application
  - `build-bin` — package dist/ into `bin/merchant-tycoon-macos-{version}.zip`
  - `build-clean` — clean build artifacts
- Scripts (macOS):
  - `scripts/build/macos/create_app_executable.sh`
  - `scripts/build/macos/create_app_bundle.sh`
  - `scripts/build/macos/build_artifacts.sh`
  - `scripts/build/macos/iconset_generate.sh`
  - `scripts/build/macos/iconset_apply.sh`
  - `scripts/build/macos/release_as_zip.sh`
  - `scripts/build/macos/release.sh`
- Generic helper:
  - `scripts/build/detect_version.sh` — shared version detector
- Alternative (not recommended):
  - `setup_py2app.py` — legacy py2app script
