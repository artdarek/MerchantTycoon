# Build Guide

This guide consolidates the build process for macOS and Windows into a single reference. It covers prerequisites, recommended Makefile flows, script entry points, manual commands, artifacts, and versioning.

Related docs:
- Make targets: docs/MAKEFILE.md
- Build scripts overview: docs/SCRIPTS.md

## Overview

- Primary platform: macOS (PyInstaller-built terminal executable and .app bundle; optional DMG).
- Windows helper: standalone `.exe` via PyInstaller (run on Windows).
- Artifacts live under `dist/` (build outputs) and `bin/` (versioned release zips/DMGs).
- Versioning for packaged outputs is auto-detected; override with `VERSION=...`.

## Prerequisites

- Python 3.8+ (local dev); PyInstaller build scripts assume modern Python.
- uv (recommended for env/deps): `make venv`, `make install-dev`.
- macOS tools:
  - PyInstaller (via `uv pip install -e '.[dev]'`).
  - `sips` and `iconutil` (built-in on macOS) for icon workflows.
  - Optional: `create-dmg` (`brew install create-dmg`) to produce a DMG.
- Windows:
  - Run on Windows, PyInstaller available on PATH.

## Recommended Flows (Makefile)

Common commands (see docs/MAKEFILE.md for all targets and options):

- Build macOS artifacts (terminal executable + .app):
  - `make build-artifacts`
  - Output: `dist/Merchant Tycoon` and `dist/Merchant Tycoon.app`
  - Notes: If `create-dmg` is installed, a non-versioned `dist/Merchant Tycoon.dmg` may also be created automatically.

- Package a release zip (auto-detect version, or override):
  - `make release`
  - `make release VERSION=1.5.1`
  - `make release FORCE_BUILD=1` (forces rebuild before packaging)
  - Output: `bin/merchant-tycoon-macos-{version}.zip` (includes `.app`, terminal executable, and DMG if present)

- Clean build outputs:
  - Packaging-only clean: `make build-clean` (removes `build/`, `dist/`, `*.spec`)
  - Full clean: `make clean` (also removes `.venv`, caches)

- Windows executable (run on Windows):
  - `make build-windows`
  - Output: `dist/Merchant Tycoon.exe`

Tip: You can also use the interactive `make build` menu to chain steps (build artifacts, package release, or clean).

## Script Entry Points

Build scripts live under `scripts/build/macos/` and are orchestrated by Makefile targets. See docs/SCRIPTS.md for details. Key scripts:

- `build_artifacts.sh` — builds terminal executable and `.app`, applies iconset if available, creates DMG if `create-dmg` exists.
- `release.sh package` — ensures artifacts exist and creates `bin/merchant-tycoon-macos-{version}.zip`.
- `release_as_zip.sh` — zips existing `dist/` artifacts (no building).
- Icon helpers:
  - `iconset_generate.sh` — create `.iconset` directory from a source PNG (`ICON=...`, defaults to `docs/icon/icon.png` or `icon.png`).
  - `iconset_apply.sh` — convert `.iconset` to `.icns` and set as app icon (`ICONSET_DIR`, `ICON_ICNS`, `APP_BUNDLE`).

Version detection helper:
- `scripts/build/detect_version.sh` — chooses version using: `VERSION` env → latest git tag → `pyproject.toml` → fallback `0.0.0`.

## Manual Build (macOS)

If you prefer explicit steps or need to customize flags:

1) Install PyInstaller (recommended: dev install)

```
uv pip install -e '.[dev]'
```

2) Build terminal executable

```
python3 -m PyInstaller \
  --name="Merchant Tycoon" \
  --onefile \
  --collect-all textual \
  --collect-all rich \
  --add-data="src/merchant_tycoon/template/style.tcss:merchant_tycoon/template" \
  src/merchant_tycoon/__main__.py
```

Produces `dist/Merchant Tycoon`.

3) Create `.app` bundle (scripted)

```
bash scripts/build/macos/create_app_bundle.sh
```

4) (Optional) Generate and apply app icon

```
# Generate .iconset from a 1024x1024 PNG (defaults to docs/icon/icon.png)
ICON=path/to/icon.png bash scripts/build/macos/iconset_generate.sh

# Apply icon to the app bundle
ICONSET_DIR=build/icon.iconset bash scripts/build/macos/iconset_apply.sh
```

5) (Optional) Create a DMG

- Auto (if available): `build_artifacts.sh` will attempt DMG via `create-dmg`.
- Manual:
```
OUT_DIR=dist bash scripts/build/macos/create_app_dmg.sh
```

6) Package a versioned ZIP (no rebuild)

```
bash scripts/build/macos/release_as_zip.sh
```

## Manual Build (Windows)

Run on Windows with PyInstaller installed (via `uv pip install -e '.[dev]'`), then either use `make build-windows` or run a similar PyInstaller command targeting `src/merchant_tycoon/__main__.py`.

## Artifacts & Layout

- `dist/Merchant Tycoon` — standalone terminal executable (macOS).
- `dist/Merchant Tycoon.app` — macOS app bundle (double‑clickable).
- `dist/Merchant Tycoon.dmg` — non-versioned DMG (if `create-dmg` available).
- `bin/merchant-tycoon-macos-{version}.zip` — versioned release zip containing `.app`, executable, and DMG when present.
- `dist/Merchant Tycoon.exe` — standalone Windows executable.

## Versioning & Options

- `VERSION=...` — override detected version for release packaging.
- `FORCE_BUILD=1` — force rebuilding before packaging.
- Icon envs (used by icon scripts / build_artifacts):
  - `ICON` — source PNG (ideally 1024×1024).
  - `ICONSET_DIR` — output `.iconset` directory (default `build/icon.iconset`).
  - `ICON_ICNS` — output `.icns` file (default `build/icon.icns`).

## Troubleshooting

- `pyinstaller` not found — install dev deps: `uv pip install -e '.[dev]'`.
- DMG not created — install `create-dmg` (`brew install create-dmg`) or package only as ZIP.
- Imports fail when running locally — prefer `make run` or ensure `PYTHONPATH=src` or install with `make install-dev`.

## Maintenance Tips

- Prefer Makefile targets for predictable builds and packaging; they use the scripts above.
- Keep `docs/MAKEFILE.md` and `docs/SCRIPTS.md` in sync with changes to targets and scripts.
- When adding new build steps, wire them in `scripts/build/...` and expose via Makefile with clear help text.
