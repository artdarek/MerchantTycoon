# Repository Guidelines

## Project Structure & Module Organization
- Source lives under `src/merchant_tycoon` (engine, model, ui, events). Entry points: `src/merchant_tycoon/__main__.py` (module run) and `src/merchant_tycoon/game.py`.
- Assets: `src/merchant_tycoon/template/style.tcss` is packaged data.
- Top-level files: `pyproject.toml` (build/metadata), `Makefile` (common tasks), `docs/images` (screenshots), `dist/` (artifacts).

## Build, Test, and Development Commands
- `make venv` — create/manage a `.venv` using `uv`.
- `make install-dev` — editable install for local development.
- `make run` — run the game (`python -m merchant_tycoon`).
- `make bin` — build a standalone binary with PyInstaller to `dist/merchant-tycoon`.
- `make clean` / `make bin-clean` — remove build artifacts.
- Dependency workflow: `uv sync` (resolve/install), `uv lock --upgrade` then `uv sync` (upgrade).
- After install: run via `merchant-tycoon` (console script) or `python -m merchant_tycoon`.

## Coding Style & Naming Conventions
- Python 3.8+; 4-space indentation; limit lines to ~100–120 chars.
- Names: `snake_case` for modules/functions, `PascalCase` for classes, `UPPER_SNAKE` for constants.
- Keep domain boundaries: engine logic in `engine/`, data classes in `model/`, TUI in `ui/`, events in `events/`.
- Use absolute imports within the package avoind relative imports;
- Avoid circular deps by isolating services.
- Lint/format: ruff recommended (not enforced yet). Examples: `ruff check src/`, `ruff format src/`.
- Use English language in comments and docstrings.

## Testing Guidelines
- No tests configured yet. If adding tests, use `pytest` with files `tests/test_*.py` mirroring package structure.
- Write fast, unit-level tests for services and models; avoid TUI snapshot flakiness.
- Run locally with `pytest` (consider wiring `make test` once tests exist).

## Commit & Pull Request Guidelines
- Commits: concise, imperative mood (e.g., "Refactor engine service", "Fix savegame path").
- PRs: include clear description, linked issues, and manual test notes; add screenshots/GIFs for UI changes (place raw assets under `docs/images`).
- Keep changes focused; update docs when behavior or commands change.

## Security & Configuration Tips
- Do not commit secrets or local env artifacts (`.venv/`, `dist/`).
- When running without install, ensure `PYTHONPATH=src` (handled by `make run`).
