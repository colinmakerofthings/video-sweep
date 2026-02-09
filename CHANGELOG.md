# Changelog

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

## [0.2.0] - Previous release

### Added
- OMDb API integration for movie validation
- Rich console output with colored tables
- Cross-platform support (Windows, macOS, Linux)
- Series renaming with season folders
- Dry run mode
- Config file support

## [0.1.0] - Initial release

### Added
- Basic video file finding and classification
- Movie and series detection
- File renaming and moving
- Clean-up functionality for non-video files
