# video-sweep 🧹

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://pypi.org/project/video-sweep/)
[![License](https://img.shields.io/github/license/colinmakerofthings/video-sweep)](LICENSE)
[![CI](https://github.com/colinmakerofthings/video-sweep/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/colinmakerofthings/video-sweep/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/colinmakerofthings/video-sweep/branch/main/graph/badge.svg)](https://codecov.io/gh/colinmakerofthings/video-sweep)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-d7ff64.svg)](https://docs.astral.sh/ruff/)

CLI tool to find, classify, intelligently rename, and move video files to user-specified locations. Optionally, clean up non-video files.

## Features

- Finds video files (.mp4, .mkv, .avi)
- Classifies as movie or series
- Name validation using OMDb API for accurate title and year matching
- Renames and moves files
  - Movies: `Title [Year].ext` to the movie output folder
  - Series: `SeriesName SxxEyy.ext` to `series_output/SeriesName/Season N/`
    - Example: `SeriesName (2014) - S04E01 -EpisodeTitle.mkv` → `SeriesName S04E01.mkv` in `series_output/SeriesName/Season 4/`
- Cleans up non-video files (optional)
- All paths provided via CLI arguments or config
- Basic error handling and console warnings for skipped files
- Dry run mode for safe preview
- Console table output with color-coded type column
- Cross-platform support (Windows, macOS, Linux)
- Python 3.8 - 3.11 compatible

## Installation

```bash
pip install video-sweep
```

## Usage

```bash
video-sweep --source <source_folder> --series-output <series_folder> --movie-output <movie_folder> [--clean-up] [--dry-run] [--config <file>] [--init-config <file>]
```

- `--clean-up`: Permanently delete non-video files in the source folder (shows a table of files to be deleted).
- `--dry-run`: Preview all actions without moving or deleting any files (safe to use with or without --clean-up).
- `--config <file>`: Load options from a TOML config file. If not specified, config.toml in the current directory is used if present.
- `--init-config <file>`: Generate a sample TOML config file at the given path and exit.

### Example config.toml

```toml
source = "C:/Downloads"
series_output = "D:/Media/Series"
movie_output = "D:/Media/Movies"
clean_up = true
dry_run = false

[omdb]
api_key = "your_api_key_here"
```

## Examples

```bash
video-sweep --source "C:/Downloads" --series-output "D:/Media/Series" --movie-output "D:/Media/Movies"

# Use a config file
video-sweep --config config.toml

# Generate a sample config file
video-sweep --init-config config.toml

# Preview all actions (no files moved or deleted)
video-sweep --source "C:/Downloads" --series-output "D:/Media/Series" --movie-output "D:/Media/Movies" --dry-run

# Move/rename video files and permanently delete non-video files
video-sweep --source "C:/Downloads" --series-output "D:/Media/Series" --movie-output "D:/Media/Movies" --clean-up

# Preview all actions, including cleanup (no files moved or deleted)
video-sweep --source "C:/Downloads" --series-output "D:/Media/Series" --movie-output "D:/Media/Movies" --clean-up --dry-run
```

## Movie Name Validation

After renaming, the tool automatically validates movie names using the OMDb API. If a suggested name is found, the file will be moved/renamed to match the OMDb format. Invalid names are highlighted in red in the results table.

**OMDb API Key:**
Set the OMDB_API_KEY environment variable to enable validation.

| Current Name         | Valid | Suggested Name          |
|--------------------- |-------|-------------------------|
| Example (2020)       | Yes   |                         |
| WrongName (2019)     | No    | Correct Title (2019)    |

## OMDb API Key Setup

To enable movie name validation, add your OMDb API key to the `[omdb]` section of `config.toml`:

```toml
[omdb]
api_key = "your_api_key_here"
```

If the API key is not set, validation will be skipped automatically.

## License

MIT

