.PHONY: help venv install install-dev sync upgrade run clean test lint format build build-macos build-clean build-iconset build-iconset-apply build-version

# Default source icon (override with: make build-iconset ICON=path/to/icon.png)
ICON ?= icon.png
ICONSET_DIR ?= build/icon.iconset
ICON_ICNS ?= build/icon.icns

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
	@echo "  [i] Create iconset (build/icon.iconset)"
	@echo "  [a] Apply iconset to .app"
	@echo "  [v] Versionize macOS app (dist/version/MerchantTycoon-{version})"
	@echo "  [x] Delete old build"
	@echo "  [q] Quit (default)"
	@printf "Enter choice: "; read ans; \
	case "$$ans" in \
		[Mm]) \
			$(MAKE) build-macos; \
			;; \
		[Ii]) \
			$(MAKE) build-iconset; \
			;; \
		[Aa]) \
			$(MAKE) build-iconset-apply; \
			;; \
		[Vv]) \
			$(MAKE) build-version; \
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

build-iconset:  ## Generate macOS .iconset under build/ from icon (ICON=... or docs/icon/icon.png)
	@command -v sips >/dev/null 2>&1 || { echo "sips not found. This command requires macOS."; exit 1; }
	@SRC="$(ICON)"; \
	if [ ! -f "$$SRC" ] && [ -f docs/icon/icon.png ]; then SRC="docs/icon/icon.png"; fi; \
	if [ ! -f "$$SRC" ]; then echo "Source icon not found. Provide PNG via ICON=path/to/icon.png (recommended 1024x1024)."; exit 1; fi; \
	echo "Generating $(ICONSET_DIR) from $$SRC..."; \
	mkdir -p $(ICONSET_DIR); \
	sips -z 16 16     "$$SRC" --out $(ICONSET_DIR)/icon_16x16.png; \
	sips -z 32 32     "$$SRC" --out $(ICONSET_DIR)/icon_16x16@2x.png; \
	sips -z 32 32     "$$SRC" --out $(ICONSET_DIR)/icon_32x32.png; \
	sips -z 64 64     "$$SRC" --out $(ICONSET_DIR)/icon_32x32@2x.png; \
	sips -z 128 128   "$$SRC" --out $(ICONSET_DIR)/icon_128x128.png; \
	sips -z 256 256   "$$SRC" --out $(ICONSET_DIR)/icon_128x128@2x.png; \
	sips -z 256 256   "$$SRC" --out $(ICONSET_DIR)/icon_256x256.png; \
	sips -z 512 512   "$$SRC" --out $(ICONSET_DIR)/icon_256x256@2x.png; \
	sips -z 512 512   "$$SRC" --out $(ICONSET_DIR)/icon_512x512.png; \
	cp "$$SRC" $(ICONSET_DIR)/icon_512x512@2x.png; \
	echo "✅ Created $(ICONSET_DIR) (use iconutil to convert to .icns if needed)"

build-iconset-apply:  ## Convert build/icon.iconset to .icns and apply to macOS .app bundle
	@command -v iconutil >/dev/null 2>&1 || { echo "iconutil not found. This command requires macOS."; exit 1; }
	@[ -d "$(ICONSET_DIR)" ] || { echo "$(ICONSET_DIR) not found. Run: make build-iconset"; exit 1; }
	@echo "Converting $(ICONSET_DIR) -> $(ICON_ICNS)..."
	iconutil -c icns "$(ICONSET_DIR)" -o "$(ICON_ICNS)"
	@[ -d "dist/Merchant Tycoon.app/Contents/Resources" ] || { echo "App bundle not found. Build it first with: make build-macos"; exit 1; }
	@echo "Copying icon.icns into app bundle..."
	cp "$(ICON_ICNS)" "dist/Merchant Tycoon.app/Contents/Resources/AppIcon.icns"
	@echo "Setting CFBundleIconFile in Info.plist..."
	@/usr/libexec/PlistBuddy -c "Set :CFBundleIconFile AppIcon" "dist/Merchant Tycoon.app/Contents/Info.plist" 2>/dev/null \
		|| /usr/libexec/PlistBuddy -c "Add :CFBundleIconFile string AppIcon" "dist/Merchant Tycoon.app/Contents/Info.plist"
	@echo "✅ Applied AppIcon.icns to dist/Merchant Tycoon.app"

# Extract version from pyproject.toml and create versioned build folder
build-version:  ## Create dist/version/MerchantTycoon-{version}-{n} and copy app artifacts from dist/ (also zips it)
	@echo "Reading version from pyproject.toml..."
	@VER=$$(python3 -c "import tomllib,sys;print(tomllib.load(open('pyproject.toml','rb'))['project'].get('version',''))"); \
	if [ -z "$$VER" ]; then \
		echo "Could not determine version from pyproject.toml"; exit 1; \
	fi; \
	BASE="dist/version/MerchantTycoon-$$VER"; \
	LAST_N=$$(ls -1d "$$BASE"-* 2>/dev/null | sed -n 's/^.*-\([0-9][0-9]*\)$$/\1/p' | sort -n | tail -1); \
	if [ -z "$$LAST_N" ]; then BUILD_N=1; else BUILD_N=$$((LAST_N+1)); fi; \
	OUT="$$BASE-$$BUILD_N"; \
	echo "Creating $$OUT and copying dist artifacts (build #$$BUILD_N)..."; \
	mkdir -p "$$OUT"; \
	COPIED=0; \
	if [ -e "dist/Merchant Tycoon" ]; then \
		cp -R "dist/Merchant Tycoon" "$$OUT/" && COPIED=1; \
	fi; \
	if [ -e "dist/Merchant Tycoon.app" ]; then \
		cp -R "dist/Merchant Tycoon.app" "$$OUT/" && COPIED=1; \
	fi; \
	if [ "$$COPIED" -eq 0 ]; then \
		echo "No dist artifacts found. Run: make build-macos"; \
	fi; \
	echo "✅ Versionized at $$OUT"; \
	command -v zip >/dev/null 2>&1 || { echo "zip not found. Please install zip."; exit 1; }; \
	ZIP="$$OUT.zip"; \
	PARENT=$$(dirname "$$OUT"); BASE=$$(basename "$$OUT"); \
	echo "Zipping $$OUT -> $$ZIP ..."; \
	cd "$$PARENT" && zip -yr "$$BASE.zip" "$$BASE" >/dev/null 2>&1; \
	echo "✅ Created $$ZIP"
