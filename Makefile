.PHONY: help venv install install-dev sync upgrade run clean test lint format bin bin-clean

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

install-dev:  ## Install the game in development mode (editable)
	uv pip install -e .

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
