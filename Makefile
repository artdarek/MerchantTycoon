.PHONY: help venv install install-dev sync upgrade run clean test lint format

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36mmake %-15s\033[0m %s\n", $$1, $$2}'

venv:  ## Create a virtual environment using uv
	uv venv
	@echo "Virtual environment created. Activate it with: source .venv/bin/activate"

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
