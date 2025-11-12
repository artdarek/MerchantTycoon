.PHONY: help venv install install-dev sync upgrade run clean test lint format build build-macos build-clean

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36mmake %-15s\033[0m %s\n", $$1, $$2}'

venv:  ## Create a virtual environment using uv (create if missing; show how to activate, deactivate, recreate, or delete)
	@if [ -d .venv ]; then \
		echo ".venv already exists."; \
		echo "What do you want to do?"; \
		echo "  [a] Activate (show instructions)"; \
		echo "  [d] Deactivate (show instructions)"; \
		echo "  [r] Recreate"; \
		echo "  [x] Delete"; \
		echo "  [q] Quit (default q)"; \
		printf "Enter choice: "; read ans; \
		case "$$ans" in \
			[Aa]) \
				if [ -f .venv/bin/activate ]; then \
					echo "To activate the virtual environment in your current shell, run:"; \
					echo ""; \
					echo "  source .venv/bin/activate"; \
					echo ""; \
					echo "(Note: make cannot activate your shell; you must run the command above yourself.)"; \
				else \
					echo "Activation script not found. Consider choosing 'recreate' to rebuild the venv."; \
				fi ;; \
			[Dd]) \
				echo "To deactivate the virtual environment in your current shell, run:"; \
				echo ""; \
				echo "  deactivate"; \
				echo ""; \
				echo "(Run this in the shell where the venv is currently active.)"; \
				;; \
			[Rr]) \
				echo "Recreating virtual environment..."; \
				rm -rf .venv && uv venv && echo "Virtual environment recreated. Activate it with: source .venv/bin/activate"; \
				;; \
			[Xx]) \
				echo "Deleting virtual environment..."; \
				rm -rf .venv && echo "Virtual environment deleted."; \
				;; \
			[Qq]) \
				echo "Quit."; \
				;; \
			*) \
				echo "Quit."; \
				;; \
			esac; \
	else \
		uv venv && echo "Virtual environment created. Activate it with: source .venv/bin/activate"; \
	fi

install:  ## Install the game in production mode
	uv pip install .

install-dev:  ## Install the game in development mode with dev dependencies (editable)
	uv pip install -e '.[dev]'

sync:  ## Sync dependencies from pyproject.toml (creates/updates uv.lock)
	uv sync

upgrade:  ## Upgrade all packages to latest versions and update uv.lock
	uv lock --upgrade
	uv sync

run:  ## Run the game
	PYTHONPATH=src python3 -m merchant_tycoon

clean:  ## Clean up build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	rm -rf .venv
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

test:  ## Run tests (placeholder for future tests)
	@echo "No tests configured yet"

lint:  ## Run code linting (placeholder)
	@echo "Linting not configured yet"
	@echo "Consider adding: ruff check src/"

format:  ## Format code (placeholder)
	@echo "Formatting not configured yet"
	@echo "Consider adding: ruff format src/"

build:  ## Interactive build menu (choose platform or clean)
	@echo "Build Options:"
	@echo "  [m] Build for macOS"
	@echo "  [x] Delete old build"
	@echo "  [q] Quit (default)"
	@printf "Enter choice: "; read ans; \
	case "$$ans" in \
		[Mm]) \
			$(MAKE) build-macos; \
			;; \
		[Xx]) \
			$(MAKE) build-clean; \
			;; \
		[Qq]) \
			echo "Quit."; \
			;; \
		*) \
			echo "Quit."; \
			;; \
	esac

build-macos:  ## Build standalone macOS executable and .app bundle
	@echo "Building macOS application..."
	@echo ""
	@echo "Step 1/3: Checking PyInstaller..."
	@command -v pyinstaller >/dev/null 2>&1 || { echo "PyInstaller not found. Install dev dependencies with: uv pip install -e .[dev]"; exit 1; }
	@echo "Step 2/3: Building executable with PyInstaller..."
	python3 -m PyInstaller \
		--name="Merchant Tycoon" \
		--onefile \
		--collect-all textual \
		--collect-all rich \
		--add-data="src/merchant_tycoon/template/style.tcss:merchant_tycoon/template" \
		src/merchant_tycoon/__main__.py
	@echo ""
	@echo "Step 3/3: Creating .app bundle wrapper..."
	./scripts/build/create_app_bundle.sh
	@echo ""
	@echo "✅ Build complete!"
	@echo "   Terminal executable: dist/Merchant Tycoon"
	@echo "   App bundle: dist/Merchant Tycoon.app"
	@echo ""
	@echo "To run:"
	@echo "  open \"dist/Merchant Tycoon.app\""
	@echo ""
	@echo "To install:"
	@echo "  cp -r \"dist/Merchant Tycoon.app\" /Applications/"

build-clean:  ## Clean build artifacts (build, dist, *.spec)
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.spec
	@echo "✅ Build artifacts cleaned"
