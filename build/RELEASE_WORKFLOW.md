# StreamStorm Release Workflow

The version bump and release build are separate workflows. Update and push the version first, then publish a GitHub Release with a matching `vX.X.X` tag.

## 1. Update and push the version

After merging the release changes into `master`, run the **Update Version** workflow from the Actions tab. Enter `X.X.X` or `vX.X.X`. It updates the version files and commits the changes to `master`.

You can also update the version locally:

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
- **Windows (`windows-latest`)**: `StreamStorm.exe`, publishes updater data through `make dgupdater-commit-publish`, then creates both setup installer filenames.
- Uploads all build artifacts to the same GitHub Release that triggered the workflow.

## Required repository secrets

| Secret | Purpose | Required? |
|---|---|---|
| `STREAMSTORM_SENTRY_DSN` | Injected into release executables for Sentry monitoring. | Optional |
| `DGUPDATER_CONFIG` or `DGUPDATER_MONGODB_URI` | Credentials for publishing updater data. | Required for updater publishing |
| `RELEASE_PAT` | Allows the **Update Version** workflow to push when repository rules block `GITHUB_TOKEN`. | Optional unless branch protection requires it |

## Manual build fallback

After updating the version and pushing the release commit, the existing build commands can still be run locally:

```bash
make executable
make dgupdater-commit-publish VERSION=X.X.X
make generate-setup-windows
make trigger-cross-os-build
make artifacts
```
