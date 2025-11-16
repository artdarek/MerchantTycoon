# Packaging macOS Binary with `make bin`

This document outlines the plan and flow used by the `make bin` target to create a portable ZIP of the game for macOS.

## Goals

- Always produce `bin/merchant-tycoon-macos-{version}.zip`.
- Work even if the current commit isn’t tagged.
- Auto-build artifacts if missing.
- Include both the `.app` bundle and the terminal binary when present.

## Inputs and Overrides

- `VERSION=...` — override auto-detected version (useful for CI or ad‑hoc builds).
- `FORCE_BUILD=1` — force a rebuild before packaging.

## Step‑by‑Step Flow

1) Preflight
- Verify required tools exist:
  - `zip` — used to create the archive.

2) Refresh Git Tags (best‑effort)
- If inside a git repository, fetch tags quietly:
  - `git fetch --tags --quiet || true`

3) Determine Version
- Use the first non‑empty of:
  - `VERSION` variable provided to `make bin`.
  - Latest tag by version (independent of reachability):
    - `git tag --list --sort=-v:refname | head -1 | sed -E 's/^v//'`
  - Version from `pyproject.toml` (BSD/macOS compatible):
    - `awk -F '"' '/^[[:space:]]*version[[:space:]]*=/{print $2; exit}' pyproject.toml`
  - Fallback: `0.0.0`

4) Ensure Artifacts Exist
- Build if necessary or if `FORCE_BUILD=1`:
  - Missing `dist/` or both of the following absent triggers a build:
    - `dist/Merchant Tycoon.app`
    - `dist/Merchant Tycoon`
  - Build command: `make build-macos`

5) Select Artifacts to Package
- Include if present:
  - `dist/Merchant Tycoon.app`
  - `dist/Merchant Tycoon`
- Exit with a clear message if neither is present.

6) Create ZIP in `bin/`
- Output filename: `bin/merchant-tycoon-macos-{version}.zip`.
- Run from within `dist/` to maintain clean top‑level names in the archive:
  - `cd dist && zip -yr "../bin/merchant-tycoon-macos-{version}.zip" ...`

7) Summary Output
- Print the effective version and the included artifacts.
- Print the final output path.

## Examples

Package existing build:

```bash
make bin
```

Force a rebuild, override the version:

```bash
make bin FORCE_BUILD=1 VERSION=1.5.1

## Scripts

Orchestrated release packaging script:

- `scripts/build/macos/release.sh package`
  - Accepts `VERSION` and `FORCE_BUILD` as environment variables
  - Ensures artifacts exist (builds if needed) and then zips via `build_macos_bin.sh`

Lower-level helpers:
- `scripts/build/macos/build_artifacts.sh` — builds terminal executable and .app bundle; applies iconset if available (or attempts to generate)
- `scripts/build/macos/release_as_zip.sh` — zips dist artifacts into a versioned zip (no building)
- `scripts/build/detect_version.sh` — prints detected version
```

## Notes

- The `.zip` may include both the terminal executable and the `.app` bundle if both are present.
- The target is designed to be resilient across macOS/BSD environments (uses `awk` instead of GNU‑specific sed escapes).
