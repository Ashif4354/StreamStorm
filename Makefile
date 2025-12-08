.PHONY: help run run-ui run-site build-ui build-site deb artifacts update-versions executable firebase-deploy dgupdater-commit-publish generate-setup-windows build-and-release

# Variables
PY_SCRIPTS_DIR := build/scripts

# Detect OS
ifeq ($(OS),Windows_NT)
	PYTHON := python
	DETECTED_OS := Windows
	ACTIVATE_VENV := call venv\Scripts\activate.bat &&
else
	PYTHON := python3
	DETECTED_OS := $(shell uname -s)
	ifeq ($(DETECTED_OS),Darwin)
		DETECTED_OS := Darwin
	endif
	ACTIVATE_VENV := source venv/bin/activate &&
endif

help:
	@echo "StreamStorm Build System"
	@echo ""
	@echo "Core Commands:"
	@echo "  make run                      Start the Engine app (uv run main.py in src/Engine)"
	@echo "  make ui                   Start the UI (npm start in src/UI)"
	@echo "  make site                 Start the Site (npm run dev in src/Site)"
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
	@echo "  make build-and-release        Run full build and release process"
	@echo ""
	@echo "Detected OS: $(DETECTED_OS)"

# ============================================================================
# CORE COMMANDS
# ============================================================================

run:
	@echo "Starting Engine application..."
	cd src/Engine && uv run main.py

ui:
	@echo "Starting UI application..."
	cd src/UI && npm start

site:
	@echo "Starting Site application..."
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
	$(PYTHON) $(PY_SCRIPTS_DIR)/download_linux_artifacts.py

update-versions:
	@echo "Running update versions script..."
	$(PYTHON) $(PY_SCRIPTS_DIR)/update_versions.py

executable:
	@echo "Running generate executable script..."
	$(PYTHON) $(PY_SCRIPTS_DIR)/generate_executable.py

firebase-deploy:
	@echo "Running Firebase deploy script..."
	$(PYTHON) $(PY_SCRIPTS_DIR)/firebase_deploy.py

dgupdater-commit-publish:
	@echo "Running dgupdater commit and publish script..."
	$(PYTHON) $(PY_SCRIPTS_DIR)/dgupdater_commit_and_publish.py

generate-setup-windows:
ifeq ($(DETECTED_OS),Windows)
	@echo "Running generate setup file script..."
	$(PYTHON) $(PY_SCRIPTS_DIR)/generate_setup_file_windows.py
else
	@echo "Error: 'make generate-setup-windows' is only available on Windows"
	@exit 1
endif

build-and-release:
	@echo "Running full build and release process..."
	$(PYTHON) $(PY_SCRIPTS_DIR)/build_and_release.py

# ============================================================================
# COMBINED TARGETS
# ============================================================================

.DEFAULT_GOAL := help
