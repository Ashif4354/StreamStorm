.PHONY: help run run-dev run-api run-api-dev pytest run-ui run-site build-ui build-site deb artifacts update-versions executable firebase-deploy dgupdater-commit-publish generate-setup-windows trigger-cross-os-build build-and-release

# Set shell to bash for Unix systems (Linux/macOS)
# Windows uses cmd.exe by default which is handled via ifeq
ifneq ($(OS),Windows_NT)
	SHELL := /bin/bash
endif

# Variables
PY_SCRIPTS_DIR := build/scripts

# Detect OS
ifeq ($(OS),Windows_NT)
	PYTHON := python
	DETECTED_OS := Windows
	ACTIVATE_VENV := call venv\Scripts\activate.bat &&
	ACTIVATE_FUNCTIONS_VENV := call src\functions\venv\Scripts\activate.bat &&
else
	PYTHON := python3
	DETECTED_OS := $(shell uname -s)
	ifeq ($(DETECTED_OS),Darwin)
		DETECTED_OS := Darwin
	endif
	ACTIVATE_VENV := source venv/bin/activate &&
	ACTIVATE_FUNCTIONS_VENV := source src/functions/venv/bin/activate &&
endif

help:
	@echo "StreamStorm Build System"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make deps                     Install all dependencies (npm for UI/Site, uv sync for Engine)"
	@echo ""
	@echo "Core Commands:"
	@echo "  make run                      Start the Engine app (uv run main.py in src/Engine)"
	@echo "  make run-dev                  Start Engine in development mode"
	@echo "  make run-api                  Start API only"
	@echo "  make run-api-dev              Start API only in development mode"
	@echo "  make pytest                   Run tests with STREAMSTORM_ENV=test"
	@echo "  make ui                       Start the UI (npm start in src/UI)"
	@echo "  make site                     Start the Site (npm run dev in src/Site)"
	@echo ""
	@echo "Build Commands:"
	@echo "  make build-ui                 Build the UI (npm build in src/UI)"
	@echo "  make build-site               Build the Site (npm build in src/Site)"
	@echo "  make deb                      Build DEB installer (Linux only)"
	@echo ""
	@echo "Release Commands:"
	@echo "  make artifacts                Download release artifacts"
	@echo "  make update-versions          Update versions across all config files"
	@echo "  make executable               Generate executable using PyInstaller"
	@echo "  make firebase-deploy          Deploy to Firebase"
	@echo "  make dgupdater-commit-publish Commit and publish with dgupdater"
	@echo "  make generate-setup-windows   Generate Windows setup file (Windows only)"
	@echo "  make trigger-cross-os-build   Trigger cross-OS build workflow on GitHub"
	@echo "  make build-and-release        Run full build and release process"
	@echo ""
	@echo "Detected OS: $(DETECTED_OS)"

# ============================================================================
# CORE COMMANDS
# ============================================================================

deps:
	@echo "Installing dependencies..."
	cd src/UI && npm install
	cd src/Site && npm install
	cd src/Engine && uv sync

run:
	@echo "Starting Engine..."
	cd src/Engine && uv run main.py

run-dev:
	@echo "Starting Engine in development mode..."
ifeq ($(OS),Windows_NT)
	cd src/Engine && set STREAMSTORM_ENV=development&& uv run main.py
else
	cd src/Engine && STREAMSTORM_ENV=development uv run main.py
endif

run-api:
	@echo "Starting API only..."
ifeq ($(OS),Windows_NT)
	cd src/Engine && set STREAMSTORM_RUN_ONLY_API=true&& uv run main.py
else
	cd src/Engine && STREAMSTORM_RUN_ONLY_API=true uv run main.py
endif

run-api-dev:
	@echo "Starting API only in development mode..."
ifeq ($(OS),Windows_NT)
	cd src/Engine && set STREAMSTORM_ENV=development&& set STREAMSTORM_RUN_ONLY_API=true&& uv run main.py
else
	cd src/Engine && STREAMSTORM_ENV=development STREAMSTORM_RUN_ONLY_API=true uv run main.py
endif

pytest:
	@echo "Running tests..."
ifeq ($(OS),Windows_NT)
	cd src/Engine && set STREAMSTORM_ENV=test&& uv run pytest
else
	cd src/Engine && STREAMSTORM_ENV=test uv run pytest
endif

ui:
	@echo "Starting UI..."
	cd src/UI && npm start

site:
	@echo "Starting Site..."
	cd src/Site && npm run dev

# ============================================================================
# BUILD COMMANDS
# ============================================================================

build-ui:
	@echo "Building UI..."
	cd src/UI && npm run build

build-site:
	@echo "Building Site..."
	cd src/Site && npm run build

# Platform-specific DEB command
deb:
ifeq ($(DETECTED_OS),Linux)
	@echo "Building DEB package..."
	chmod +x ./export/linux/DEBIAN/postinst
	dpkg-deb --build ./export/linux ./export/streamstorm.deb
	@if [ -f ./export/streamstorm.deb ]; then \
		mv ./export/streamstorm.deb ./export/installers/streamstorm.deb; \
		echo "DEB package created successfully at ./export/installers/streamstorm.deb"; \
	else \
		echo "Error: Failed to create DEB package"; \
		exit 1; \
	fi
else
	@echo "Error: 'make deb' is only available on Linux"
	exit 1
endif



# ============================================================================
# RELEASE COMMANDS
# ============================================================================

artifacts:
	@echo "Downloading release artifacts..."
	cd src/Engine && uv sync
	$(ACTIVATE_VENV) $(PYTHON) $(PY_SCRIPTS_DIR)/download_linux_artifacts.py

update-versions:
	@echo "Running update versions script..."
	cd src/Engine && uv sync
	$(ACTIVATE_VENV) $(PYTHON) $(PY_SCRIPTS_DIR)/update_versions.py

executable:
	@echo "Running generate executable script..."
	cd src/Engine && uv sync
	$(ACTIVATE_VENV) $(PYTHON) $(PY_SCRIPTS_DIR)/generate_executable.py

firebase-deploy:
	@echo "Setting up functions venv..."
	$(PYTHON) -m venv src/functions/venv
	$(ACTIVATE_FUNCTIONS_VENV) pip install -q -r src/functions/requirements.txt
	@echo "Running Firebase deploy script..."
	$(ACTIVATE_FUNCTIONS_VENV) $(PYTHON) $(PY_SCRIPTS_DIR)/firebase_deploy.py

dgupdater-commit-publish:
	@echo "Running dgupdater commit and publish script..."
	cd src/Engine && uv sync
	$(ACTIVATE_VENV) $(PYTHON) $(PY_SCRIPTS_DIR)/dgupdater_commit_and_publish.py

generate-setup-windows:
ifeq ($(DETECTED_OS),Windows)
	@echo "Running generate setup file script..."
	cd src/Engine && uv sync
	$(ACTIVATE_VENV) $(PYTHON) $(PY_SCRIPTS_DIR)/generate_setup_file_windows.py
else
	@echo "Error: 'make generate-setup-windows' is only available on Windows"
	@exit 1
endif

trigger-cross-os-build:
	@echo "Triggering cross-os-build GitHub Actions workflow..."
	cd src/Engine && uv sync
	$(ACTIVATE_VENV) $(PYTHON) $(PY_SCRIPTS_DIR)/trigger_cross_os_build.py

build-and-release:
	@echo "Running full build and release process..."
	cd src/Engine && uv sync
	$(ACTIVATE_VENV) $(PYTHON) $(PY_SCRIPTS_DIR)/build_and_release.py

# ============================================================================
# COMBINED TARGETS
# ============================================================================

.DEFAULT_GOAL := help
