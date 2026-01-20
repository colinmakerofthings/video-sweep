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
video-sweep --source <source_folder> --series-output <series_folder> --movie-output <movie_folder> [--clean-up] [--dry-run] [--config <file>] [--init-config <file>]
```

- `--clean-up`: Move non-video files in the source folder to a 'Deleted' folder (shows a table of files to be deleted).
- `--dry-run`: Preview all actions without moving or deleting any files (safe to use with or without --clean-up).
- `--config <file>`: Load options from a TOML config file. If not specified, config.toml in the current directory is used if present.
- `--init-config <file>`: Generate a sample TOML config file at the given path and exit.

### Example config.toml

```toml
source = "D:/Downloads"
series_output = "D:/Media/Series"
movie_output = "D:/Media/Movies"
clean_up = true
dry_run = false
```

## Examples

```bash
video-sweep --source "D:/Downloads" --series-output "D:/Media/Series" --movie-output "D:/Media/Movies"

# Use a config file
video-sweep --config config.toml

# Generate a sample config file
video-sweep --init-config config.toml

# Preview all actions (no files moved or deleted)
video-sweep --source "D:/Downloads" --series-output "D:/Media/Series" --movie-output "D:/Media/Movies" --dry-run

# Move/rename video files and clean up non-video files
video-sweep --source "D:/Downloads" --series-output "D:/Media/Series" --movie-output "D:/Media/Movies" --clean-up

# Preview all actions, including cleanup (no files moved or deleted)
video-sweep --source "D:/Downloads" --series-output "D:/Media/Series" --movie-output "D:/Media/Movies" --clean-up --dry-run
```

## License

MIT
