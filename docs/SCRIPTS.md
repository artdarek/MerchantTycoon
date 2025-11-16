# Scripts Overview

This document describes the contents of the `scripts/` directory and serves as the central place to document all current and future build/release shell scripts.

## Structure

```
scripts/
└── build/
    ├── detect_version.sh
    └── macos/
        ├── build_artifacts.sh
        ├── create_app_bundle.sh
        ├── create_app_dmg.sh
        ├── create_app_executable.sh
        ├── iconset_apply.sh
        ├── iconset_generate.sh
        ├── release.sh
        ├── release_as_dmg.sh
        └── release_as_zip.sh
```

## Shared Utilities

- `scripts/build/detect_version.sh`
  - Purpose: Detect the project version for packaging/build naming.
  - Order (first non-empty wins):
    1) `VERSION` env override
    2) Latest git tag by version (leading `v` stripped)
    3) `pyproject.toml` via Python `tomllib`
    4) `pyproject.toml` via `awk` (BSD/macOS compatible)
    5) Fallback `0.0.0`

## macOS Build Scripts

- `scripts/build/macos/create_app_executable.sh`
  - Purpose: Build the standalone macOS terminal executable with PyInstaller.
  - Output: `dist/Merchant Tycoon` (no `.app` bundle). Exits if PyInstaller missing.

- `scripts/build/macos/create_app_bundle.sh`
  - Purpose: Create a macOS `.app` wrapper around the terminal binary.
  - Requires: `dist/Merchant Tycoon` to exist; otherwise exits with guidance.
  - Output: `dist/Merchant Tycoon.app` (launcher opens Terminal and runs the game).

- `scripts/build/macos/iconset_generate.sh`
  - Purpose: Generate a `.iconset` from a PNG (recommended 1024×1024).
  - Env: `ICON` (source PNG), `ICONSET_DIR` (default `build/icon.iconset`).

- `scripts/build/macos/iconset_apply.sh`
  - Purpose: Convert `.iconset` to `.icns` and apply to the `.app` bundle.
  - Env: `ICONSET_DIR` (default `build/icon.iconset`), `ICON_ICNS` (default `build/icon.icns`), `APP_BUNDLE` (default `dist/"Merchant Tycoon".app`).

- `scripts/build/macos/create_app_dmg.sh`
  - Purpose: Create an unversioned DMG from the `.app` bundle.
  - Output: `dist/Merchant Tycoon.dmg` (no version; matches artifact name).
  - Env: `VOLNAME`, `DMG_NAME`, `OUT_DIR` (default `dist`), Window/icon layout knobs for `create-dmg`.

- `scripts/build/macos/build_artifacts.sh`
  - Purpose: Build macOS artifacts (executable + `.app`) and polish them.
  - Steps: build executable → create `.app` if missing → apply iconset (or generate then apply) → create unversioned DMG in `dist/` if `create-dmg` is available.

## macOS Release Scripts

- `scripts/build/macos/release_as_zip.sh`
  - Purpose: Create a versioned ZIP from `dist/` artifacts.
  - Output: `bin/merchant-tycoon-macos-{version}.zip`.
  - Includes: `.app`, terminal executable, and DMG (if present).
  - Version detection: `VERSION` env override or shared detector.

- `scripts/build/macos/release_as_dmg.sh`
  - Purpose: Create a versioned DMG from the unversioned `dist` DMG.
  - Output: `bin/merchant-tycoon-macos-{version}.dmg`.
  - Version detection: `VERSION` env override or shared detector.

- `scripts/build/macos/release.sh`
  - Purpose: Orchestrate macOS release packaging.
  - Flow: ensure artifacts → create versioned ZIP → if `dist/Merchant Tycoon.dmg` exists, create versioned DMG.

## Conventions & Notes

- All scripts use `set -euo pipefail` for safety.
- macOS-only scripts may require system tools: `sips`, `iconutil`, and `create-dmg`.
- Paths with spaces are handled carefully; avoid unquoted globbing in new scripts.
- Prefer small, composable scripts with a single responsibility and a clear docblock.

## Adding New Scripts

When adding a new script:
- Place generic helpers under `scripts/build/` and platform-specific ones under a subfolder (e.g., `macos/`).
- Include a docblock with Purpose, Inputs/Env, Effects/Output.
- If the script is a public entry point, consider adding a Make target and documenting it in `docs/BUILD.md`.

