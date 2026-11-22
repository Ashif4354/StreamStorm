# StreamStorm Release Workflow

The version bump is done locally and the release build is a workflow. Update and push the version first, then publish a GitHub Release with a matching `vX.X.X` tag.

## 1. Update and push the version

After merging the release changes into `master`, update the version locally:

```bash
make update-versions VERSION=X.X.X
git add .
git commit -m "Release vX.X.X"
git push origin master
```

## 2. Publish the GitHub Release

1. Open [Create a new Release](https://github.com/Ashif4354/StreamStorm/releases/new).
2. Create or select a tag matching the version you pushed, such as `v4.2.1`, targeting the version-bump commit on `master`.
3. Set your release title and description.
4. Publish the release.

The **Release Workflow** runs only for a published release. It validates that the tag uses `vX.X.X` and matches `project.json`, then builds from the exact commit referenced by the tag. It does not bump versions, push to `master`, or move the tag.

## What the release workflow builds and uploads

- **Linux (`ubuntu-22.04`)**: executable, `.deb` package, and `StreamStorm.tar.gz`.
- **Windows (`windows-latest`)**: `StreamStorm.exe` and both setup installer filenames.
- Uploads all build artifacts to the same GitHub Release that triggered the workflow.
- **Windows job order**: build `StreamStorm.exe`, then publish the updater (`make dgupdater-commit-publish`), then generate the setup installer. The publish must come before the installer because it rewrites `dgupdaterconf.json` and `dgupdaterupdate/`, which the installer bundles; the installer would otherwise ship with a stale version.
- The Windows job waits for the Linux build, so a Linux failure stops the release before anything is published to the updater.

If the Windows job fails after the updater step (for example during Inno Setup), re-run the workflow. Republishing the same version is allowed.

### Pre-releases

Publishing a GitHub **pre-release** runs every build and uploads the assets, but skips the updater publish. Use a pre-release to dry-run the pipeline end to end before cutting the real release.

### Dry run (manual)

Run **Release Workflow** from the Actions tab (**Run workflow**, pick any branch) to rehearse the pipeline with no tag and no release. A manual run is always a dry run: it builds Linux, the Windows executable and the Windows installer from the selected commit, using the version in `project.json`, and keeps the results as downloadable run artifacts (`linux-artifacts`, `windows-artifacts`).

A dry run never publishes to the updater and never uploads to a GitHub Release, and it does not need the dgupdater secrets. It still requires `STREAMSTORM_SENTRY_DSN`. Because the updater publish is skipped, the Windows installer from a dry run bundles the unpublished `dgupdaterconf.json`, and the publish step itself is only exercised by a real release.

### Updater safety checks

Before anything is written, the publish step refuses to continue if the new version is lower than the version in `export/windows/dgupdaterconf.json` or lower than the version stored in the updater database, and it fails if the database version cannot be read. Publishing a lower tag fails instead of downgrading production; the same version as the database is republished with a warning.

### Concurrency

The release workflow runs one at a time (`release-workflow` group, never cancelled).

### Obscura

Obscura is not bundled with any installer. It is an experimental engine that users install themselves and switch to from Settings. The default engine is Chromium, so no release build step depends on Obscura.

## Required repository secrets

| Secret | Purpose | Required? |
|---|---|---|
| `STREAMSTORM_SENTRY_DSN` | Injected into release executables for Sentry monitoring. The release workflow fails if it is empty. | Required |
| `DGUPDATER_CONFIG` or `DGUPDATER_MONGODB_URI` | Credentials for publishing updater data. The release workflow fails early if neither is set (non-pre-releases). | Required for updater publishing |

## Manual build fallback

After updating the version and pushing the release commit, the existing build commands can still be run locally:

```bash
make executable
make dgupdater-commit-publish VERSION=X.X.X
make generate-setup-windows
make trigger-cross-os-build
make artifacts
```
