# Makefile Guide

This document explains how to use the project Makefile: what each target does, when to use it, and any options/variables that influence behavior.

The Makefile is designed to streamline local development, dependency management, packaging, and release tasks across platforms (primarily macOS, with a Windows build helper).

## Quick Start

- List available commands: `make help`
- Create or manage virtualenv: `make venv`
- Install for development: `make install-dev`
- Run the game: `make run`
- Build macOS artifacts: `make build-artifacts`
- Interactive build menu: `make build`
- Package macOS release: `make release`
- Clean build artifacts: `make build-clean` or `make clean`

## Requirements

- Python 3.8+
- uv (for venv and dependency management)
- macOS build scripts are under `scripts/build/macos` (bash)
- Windows build requires running on Windows with `pyinstaller` available

Tip: After a dev install, you can also run via the console script `merchant-tycoon`.

## Conventions

- All commands are phony targets (no file outputs with the same name).
- Help descriptions are the text after `##` in the Makefile; shown by `make help`.
- When running without install, the Makefile uses `PYTHONPATH=src` so module imports resolve.

---

## Targets

### 1) Help & Env

- `help`
  - Purpose: Show all available make commands with short descriptions.
  - Usage: `make help`

- `venv`
  - Purpose: Create/manage a local virtual environment using `uv`.
  - Behavior:
    - If `.venv` exists, shows an interactive menu to: show activation instructions, show deactivation instructions, recreate, or delete the environment.
    - If `.venv` does not exist, creates it with `uv venv` and shows activation instructions.
  - Notes: `make` cannot activate your shell; follow the printed `source .venv/bin/activate` instructions in your terminal.

### 2) Install & Dependencies

- `install`
  - Purpose: Install the app in production mode (no dev extras).
  - Command: `uv pip install .`
  - Use when: You want a clean, non-editable install of the package.

- `install-dev`
  - Purpose: Install in development mode (editable) with dev dependencies.
  - Command: `uv pip install -e '.[dev]'`
  - Use when: You are developing locally and want changes in `src/` to be reflected immediately.

- `sync`
  - Purpose: Sync dependencies from `pyproject.toml`. Creates/updates `uv.lock` as needed and installs packages.
  - Command: `uv sync`
  - Use when: You’ve changed dependencies or pulled updates.

- `upgrade`
  - Purpose: Upgrade all packages to their latest versions and refresh `uv.lock`.
  - Commands: `uv lock --upgrade` then `uv sync`
  - Use when: You want to update to the latest compatible versions across the board.

### 3) Run & Clean

- `run`
  - Purpose: Run the game from source.
  - Command: `PYTHONPATH=src python3 -m merchant_tycoon`
  - Notes: Mirrors `python -m merchant_tycoon`; `PYTHONPATH=src` ensures imports resolve without an install.

- `clean`
  - Purpose: Remove build artifacts, caches, and local venv.
  - Removes: `build/`, `dist/`, `*.egg-info`, `src/*.egg-info`, `.venv`, `__pycache__` dirs, `*.pyc`, `*.pyo`.
  - Use when: You want a completely clean workspace (including deleting `.venv`).

- `build-clean`
  - Purpose: Remove build artifacts produced by packaging steps.
  - Removes: `build/`, `dist/`, `*.spec`.
  - Use when: You want to rebuild packaging artifacts from scratch but keep your `.venv`.

- `test`
  - Purpose: Placeholder for running tests (none configured yet).
  - Current behavior: Prints a message.
  - Suggestion: Add `pytest` and tests under `tests/` in the future.

- `lint`
  - Purpose: Placeholder for linting.
  - Suggestion: Use `ruff check src/`.

- `format`
  - Purpose: Placeholder for formatting.
  - Suggestion: Use `ruff format src/`.

### 4) Build & Release (macOS)

- `build`
  - Purpose: Interactive build menu for macOS-related tasks.
  - Options shown:
    - `[a]` Build dist/ artifacts (executable + `.app` + `.dmg`)
    - `[b]` Build bin from artifacts (delegates to `release`)
    - `[r]` Build & release (artifacts then package)
    - `[x]` Delete old build (delegates to `build-clean`)
    - `[q]` Quit
  - Notes: Uses the scripted steps in `scripts/build/macos`.

- `build-artifacts`
  - Purpose: Build macOS artifacts (CLI executable and `.app` bundle). No packaging.
  - Command: `bash scripts/build/macos/build_artifacts.sh`
  - Output: Produces items under `dist/` and/or `build/` as per script.
  - Notes: Applies iconset if present (and will attempt to generate one); creates a DMG if `create-dmg` is available.

- `release`
  - Purpose: Build artifacts if needed, then package versioned archives for distribution.
  - Command: `VERSION="$(VERSION)" FORCE_BUILD="$(FORCE_BUILD)" bash scripts/build/macos/release.sh package`
  - Outputs: Versioned `.zip` and/or `.dmg` in `bin/`.
  - Options:
    - `VERSION`: Override the version (otherwise derived by the script).
    - `FORCE_BUILD=1`: Force rebuilding artifacts even if they already exist.

### 5) Windows Build

- `build-windows`
  - Purpose: Build a standalone Windows executable (`.exe`) with PyInstaller.
  - Preconditions: Run on Windows; `pyinstaller` available on PATH (install dev deps with `uv pip install -e .[dev]`).
  - Command (abbrev.):
    - `python -m PyInstaller --name="Merchant Tycoon" --onefile ... src/merchant_tycoon/__main__.py`
  - Output: `dist/Merchant Tycoon.exe`

### 6) Git Utilities

- `rebase`
  - Purpose: Interactive helper to rebase `main` onto `develop`, with an optional force-push.
  - Flow:
    1. Fetch latest refs: `git fetch`
    2. Checkout `main`
    3. `git rebase develop`
    4. Prompt to force-push: `git push -f origin main`
    5. Switch back to `develop`
  - Warning: Force-pushing rewrites the remote history for `origin/main`. Use with care.

---

## Variables & Options

- `PYTHONPATH=src` (used by `run`)
  - Ensures local imports resolve when running from the source tree without installing the package.

- `VERSION` (used by `release`)
  - Overrides the version embedded in packaged artifacts. Example: `make release VERSION=0.4.0`.

- `FORCE_BUILD` (used by `release`)
  - Forces rebuilding even if artifacts already exist. Example: `make release FORCE_BUILD=1`.

- Icon variables (honored by build scripts when passed via env/Make):
  - `ICON` — source PNG for iconset generation (ideally 1024×1024)
  - `ICONSET_DIR` — output `.iconset` directory (default `build/icon.iconset`)
  - `ICON_ICNS` — output `.icns` file (default `build/icon.icns`)
  - Example: `make build-artifacts ICON=docs/icon/my.png ICONSET_DIR=build/my.iconset ICON_ICNS=build/my.icns`
  - Note: `build_artifacts.sh` will try to generate and apply an iconset automatically if none is present.

---

## Examples

- Create venv, install dev, run the game:
  - `make venv`
  - `source .venv/bin/activate`
  - `make install-dev`
  - `make run`

- Upgrade all dependencies and sync:
  - `make upgrade`

- Build macOS artifacts then package a release with a custom version:
  - `make build-artifacts`
  - `make release VERSION=1.2.3`

- Clean packaging outputs only, then rebuild:
  - `make build-clean`
  - `make build-artifacts`

- Build Windows executable (on Windows):
  - `uv pip install -e '.[dev]'`
  - `make build-windows`

---

## Troubleshooting

- Missing uv: Install uv and ensure it is on your PATH.
- PyInstaller not found (Windows build): Install dev dependencies with `uv pip install -e '.[dev]'` on Windows.
- Import errors when running from source: Ensure you are using `make run` or have `PYTHONPATH=src` set, or install the package with `make install-dev`.

---

## Notes

- Scripts under `scripts/build/macos` control the macOS build and release details; see those scripts for advanced options.
- The Makefile help text lists only targets with a `##` description comment; keep descriptions up to date when adding new targets.
