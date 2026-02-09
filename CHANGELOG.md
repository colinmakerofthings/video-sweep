# Changelog

## [v0.3.0] - 2026-02-09

- feat: add workflow_call trigger to CI configuration (7d15740)
- fix: update Python version badge in README (fad7eae)
- feat: add badges for Python versions, license, CI, coverage, and code style in README (735ab36)
- refactor: clean up whitespace in test_main_module_execution and test_main_module_direct_call (0c38fc2)
- feat: implement automated release workflow and update changelog for version 0.3.0 (#29) (ac8450d)
- [WIP] Fix formatting for tests/test_cli.py with Black (#31) (9ab6272)
- Refactor classify_video function to use regex for series detection (#28) (bd6886c)
- Release v0.2.0: Add macOS metadata file filtering (973e2d0)
- Fix: Skip files starting with "._" in find_files and find_videos functions (#26) (8606250)
- Enhance CLI error handling and output for missing arguments; update tests to accept usage error codes (#25) (9f8cb53)
- Fix black formatting violations in cli.py (#24) (3a3ec19)
- Refactor test job to use matrix strategy for cross-platform and multi Python version testing (#21) (efcce7e)
- Add missing rich dependency to pyproject.toml (#20) (3aae0f4)
- Add tests for get_api_key_from_config and query_omdb functions (#17) (48f6795)
- Add validate_movie_name import to CLI and remove redundant import (52b626e)
- Add name validation feature using OMDb API to README (ab0fc45)
- Update README.md (42818a3)
- Update README.md (41fdbd0)
- Update README.md (d5bcd76)
- Add coverage tests for CLI and finder functionalities (#15) (f7cf168)
- Refactor main entry point and enhance renaming logic with OMDb suggestions (#14) (e381b4f)
- Add CI configuration, coverage reporting, and CLI tests (#13) (8d16065)
- Remove egg-info metadata files from the repository (fd05f99)
- Add OMDb API integration for movie name validation and suggestions (#11) (4e3aa6a)
- Refactor directory traversal for empty folder removal in CLI (71ccfaa)
- Folder cleanup linting (#10) (ef0ff39)
- Add functionality to remove empty directories after cleanup (#9) (6f17e7b)
- Add version display functionality to CLI (#8) (40ada3d)

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Automated release workflow with GitHub Actions
- Single-source versioning from pyproject.toml
- Auto-generated changelog from git commits

### Changed

- Improved series classification regex to support all season numbers (not just S01-S05)

### Fixed

- Series episodes now correctly classified (e.g., s08e01 recognized as series, not movie)

## [0.2.0] - 2024-01-15

### Features

- OMDb API integration for movie validation
- Rich console output with colored tables
- Cross-platform support (Windows, macOS, Linux)
- Series renaming with season folders
- Dry run mode
- Config file support

## [0.1.0] - 2023-12-01

### Initial Release

- Basic video file finding and classification
- Movie and series detection
- File renaming and moving
- Clean-up functionality for non-video files
