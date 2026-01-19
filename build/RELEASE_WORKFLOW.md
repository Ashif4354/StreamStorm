# StreamStorm Release Workflow

This document outlines the steps to release a new version of StreamStorm.

## Prerequisites

- Ensure all code changes are complete and tested
- Update the version number in `src/Engine/lib/settings/Settings.py`

---

## Release Steps

### 1. Update Versions
```bash
make update-versions
```

### 2. Commit and Push
Commit and push the new version to the `master` branch. This is required for the Linux build to pick up the new version.

```bash
git add .
git commit -m "Release vX.X.X"
git push origin master
```

### 3. Build Windows Executable
```bash
make executable
```

### 4. Deploy Firebase Functions
```bash
make firebase-deploy
```

### 5. Trigger Cross-OS Build
Triggers GitHub Actions to build for Linux/macOS.
```bash
make trigger-cross-os-build
```

### 6. Generate Artifacts
This should be executed only after the cross-os build is completed.
```bash
make artifacts
```

### 7. Publish Auto-Updater
Commits and publishes the new version to the auto-updater database.
```bash
make dgupdater-commit-publish
```

### 8. Generate Windows Setup
```bash
make generate-setup-windows
```

---

## GitHub Release

1. **Create a new GitHub release** at [Releases](https://github.com/Ashif4354/StreamStorm/releases/new)
2. **Tag**: `vX.X.X` (match the version in Settings.py)
3. **Title**: `StreamStorm vX.X.X`
4. **Add changelog** describing the changes in this release
5. **Upload files** from `export/` directory:
   - `windows/StreamStorm_Setup.exe`
   - `windows/StreamStorm.exe`
   - Linux/macOS artifacts (from GitHub Actions)
6. **Publish** the release
