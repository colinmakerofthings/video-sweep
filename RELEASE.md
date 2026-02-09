# Release Procedure

This document is for maintainers. Do not include secrets here.

## Prerequisites

- You have push access to the repo.
- PyPI trusted publishing is configured for this repository.
- Your working tree is clean.

## Local Test (Recommended)

1. Create or activate a virtual environment.
2. Reinstall the package from local source:

   - pip uninstall video-sweep -y
   - pip install -e .

3. Run code quality checks:

   - ruff check .
   - black --check .
   - If ruff/black complain, fix it: black . then resolve ruff issues

4. Run a quick smoke test:

   - video-sweep --version
   - python -m video_sweep --help

5. Run tests:

   - python -m pytest

## Release Steps

1. Bump version in pyproject.toml.
2. Update CHANGELOG.md (optional, if you want to note the release manually).
3. Commit and push changes:

   - git add .
   - git commit -m "chore: bump version to X.Y.Z"
   - git push origin main

4. Create and push the tag:

   - git tag vX.Y.Z
   - git push origin vX.Y.Z

5. GitHub Actions will:

   - Run tests
   - Build the package
   - Publish to PyPI
   - Create a GitHub Release
   - Update CHANGELOG.md

## Verify Release

- Confirm the GitHub Actions workflow succeeded.
- Confirm PyPI shows the new version.
- Verify the CLI:

  - pip install --upgrade video-sweep
  - video-sweep --version

## Rollback (If Needed)

- Do not delete a published PyPI version.
- Publish a new patch release that fixes the issue.
- If a bad tag was pushed, create a new tag with the next version.
