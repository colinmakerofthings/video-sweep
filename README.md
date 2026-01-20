# video-sweep

Minimal CLI tool to find, classify (movie/series), rename, and move video files to user-specified locations. Optionally, clean up non-video files.

## Features

- Finds video files (.mp4, .mkv, .avi)
- Classifies as movie or series
- Renames and moves files
- Cleans up non-video files (optional)
- All paths provided via CLI arguments
- Basic error handling
- Dry run mode for safe preview

## Installation

```bash
pip install video-sweep
```

## Usage

```bash
video-sweep --source <source_folder> --series-output <series_folder> --movie-output <movie_folder> [--clean-up] [--dry-run]
```

- `--clean-up`: Move non-video files in the source folder to a 'Deleted' folder (shows a table of files to be deleted).
- `--dry-run`: Preview all actions without moving or deleting any files (safe to use with or without --clean-up).

## Examples

```bash
# Move and rename video files only
video-sweep --source "D:/Downloads" --series-output "D:/Media/Series" --movie-output "D:/Media/Movies"

# Preview all actions (no files moved or deleted)
video-sweep --source "D:/Downloads" --series-output "D:/Media/Series" --movie-output "D:/Media/Movies" --dry-run

# Move/rename video files and clean up non-video files
video-sweep --source "D:/Downloads" --series-output "D:/Media/Series" --movie-output "D:/Media/Movies" --clean-up

# Preview all actions, including cleanup (no files moved or deleted)
video-sweep --source "D:/Downloads" --series-output "D:/Media/Series" --movie-output "D:/Media/Movies" --clean-up --dry-run
```

## License

MIT
