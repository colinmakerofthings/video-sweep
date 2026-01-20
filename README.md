# video-sweep

Minimal CLI tool to find, classify (movie/series), rename, and move video files to a user-specified location.

## Features

- Finds video files (.mp4, .mkv, .avi)
- Classifies as movie or series
- Renames and moves files
- All paths provided via CLI arguments
- Basic error handling

## Installation

```bash
pip install video-sweep
```

## Usage

```bash
video-sweep --source <source_folder> --series-output <series_folder> --movie-output <movie_folder> [--dry-run]
```

## Example

```bash
# Move files
video-sweep --source "D:/Downloads" --series-output "D:/Media/Series" --movie-output "D:/Media/Movies"

# Dry run (no files moved)
video-sweep --source "D:/Downloads" --series-output "D:/Media/Series" --movie-output "D:/Media/Movies" --dry-run
```

## License

MIT
