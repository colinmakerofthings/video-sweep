import argparse
import sys
import os
from rich.console import Console
from rich.table import Table
import tomli
from .finder import find_files
from .classifier import classify_video
from .renamer import rename_and_move

# For removing empty parent folders
from .utils import remove_empty_parents


def main():
    parser = argparse.ArgumentParser(
        description="Find, classify, rename, and move video files."
    )
    parser.add_argument("--source", help="Source directory to scan for videos")
    parser.add_argument("--series-output", help="Output directory for series")
    parser.add_argument("--movie-output", help="Output directory for movies")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="If set, only print actions without moving files",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--clean-up",
        action="store_true",
        help="If set, move non-video files to Deleted folder",
        default=argparse.SUPPRESS,
    )
    parser.add_argument("--config", help="Path to TOML config file")
    parser.add_argument(
        "--init-config",
        help="Generate a sample config TOML file at the given path and exit",
    )
    args = parser.parse_args()

    # Handle --init-config
    if args.init_config:
        sample = (
            "# Sample video-sweep config file\n"
            'source = "D:/Downloads"\n'
            'series_output = "D:/Media/Series"\n'
            'movie_output = "D:/Media/Movies"\n'
            "clean_up = false\n"
            "dry_run = false\n"
        )
        with open(args.init_config, "w", encoding="utf-8") as f:
            f.write(sample)
        print(f"Sample config written to {args.init_config}")
        sys.exit(0)

    # Load config file if specified or present in current directory
    config = {}
    config_path = args.config or (
        os.path.join(os.getcwd(), "config.toml")
        if os.path.exists("config.toml")
        else None
    )
    if config_path:
        try:
            with open(config_path, "rb") as f:
                config = tomli.load(f)
        except Exception as e:
            print(f"Error loading config file: {e}", file=sys.stderr)
            sys.exit(1)

    # Merge config and CLI args (CLI takes precedence)
    def get_opt(opt, default=None):
        # For booleans, only use CLI if explicitly set
        if opt in ("dry_run", "clean_up"):
            if hasattr(args, opt):
                return getattr(args, opt)
            return config.get(opt, default)
        return (
            getattr(args, opt)
            if getattr(args, opt) is not None
            else config.get(opt, default)
        )

    source = os.path.normpath(get_opt("source"))
    series_output = os.path.normpath(get_opt("series_output"))
    movie_output = os.path.normpath(get_opt("movie_output"))
    dry_run = get_opt("dry_run", False)
    clean_up = get_opt("clean_up", False)

    if not source or not series_output or not movie_output:
        print(
            "Error: source, series-output, and movie-output must be specified (via CLI or config).",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        console = Console()
        videos, non_videos = find_files(source)
        results = []
        deleted_results = []
        from .renamer import movie_new_filename

        # Handle video files
        from .renamer import series_new_filename

        for video in videos:
            kind = classify_video(video)
            output_dir = series_output if kind == "series" else movie_output
            filename = os.path.basename(video)
            if kind == "movie":
                new_filename = movie_new_filename(filename)
                if new_filename:
                    target_path = os.path.join(output_dir, new_filename)
                else:
                    target_path = os.path.join(output_dir, filename)
            elif kind == "series":
                result = series_new_filename(filename)
                if result:
                    series_name, season_num, episode_code, new_filename = result
                    season_folder = f"Season {season_num}"
                    target_path = os.path.join(
                        output_dir, series_name, season_folder, new_filename
                    )
                else:
                    target_path = os.path.join(output_dir, filename)
            else:
                target_path = os.path.join(output_dir, filename)
            results.append(
                {
                    "file": video,
                    "type": kind,
                    "target": target_path,
                    "output_dir": output_dir,
                }
            )

        # Prepare deleted files
        if clean_up:
            for file in non_videos:
                deleted_results.append({"file": file})
        # Print table summary using rich
        table = Table()
        table.add_column("Files to move", style="cyan", no_wrap=True)
        table.add_column("Type")
        table.add_column("Destination", style="green")
        for r in results:
            type_str = r["type"]
            if type_str == "movie":
                type_str = f"[yellow]{type_str}[/yellow]"
            elif type_str == "series":
                type_str = f"[blue]{type_str}[/blue]"
            table.add_row(
                os.path.basename(os.path.normpath(r["file"])),
                type_str,
                os.path.normpath(r["target"]),
            )
        console.print(table)

        # Only show deleted table if --clean-up is specified
        if clean_up and deleted_results:
            deleted_table = Table()
            deleted_table.add_column("Files to delete", style="red", no_wrap=True)
            for r in deleted_results:
                deleted_table.add_row(os.path.basename(os.path.normpath(r["file"])))
            console.print(deleted_table)

        # Prompt for confirmation if not dry-run
        if not dry_run and (results or (clean_up and deleted_results)):
            proceed = input("Proceed with file moves? [y/N] ").strip().lower()
            if proceed != "y":
                print("Aborted. No files were moved.")
                sys.exit(0)

            # Move video files
            for r in results:
                rename_and_move(r["file"], r["type"], r["output_dir"], dry_run=False)

            # Delete files marked for deletion
            if clean_up:
                for r in deleted_results:
                    file = r["file"]
                    try:
                        os.remove(file)
                        print(f"Deleted: {file}")
                    except Exception as e:
                        print(f"Failed to delete {file}: {e}")
                    # Remove empty parent folders up to source dir
                    remove_empty_parents(os.path.dirname(file), source)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
