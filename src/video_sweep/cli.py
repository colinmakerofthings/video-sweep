import argparse
import sys
import os
from rich.console import Console
from rich.table import Table
import tomli
from .finder import find_files
from .classifier import classify_video
from .renamer import rename_and_move, validate_movie_name

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

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show the version number and exit",
        default=argparse.SUPPRESS,
    )
    args = parser.parse_args()
    # Handle --version
    if getattr(args, "version", False):
        from . import __version__

        print(f"video-sweep version {__version__}")
        sys.exit(0)

    # Handle --init-config
    if args.init_config:
        sample = (
            "# Sample video-sweep config file\n"
            'source = "C:/Downloads"\n'
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
        # Print a plain text table if in test/subprocess environment
        if os.environ.get("VIDEO_SWEEP_PLAIN") or not sys.stdout.isatty():
            print("Files to move | Type | Destination | Valid | Suggested Name")
            print("-" * 60)
            # No rows, just header
        else:
            import io

            rich_buffer = io.StringIO()
            console = Console(file=rich_buffer, force_terminal=True, color_system=None)
            table = Table()
            table.add_column("Files to move", style="cyan", no_wrap=True)
            table.add_column("Type")
            table.add_column("Destination", style="green")
            table.add_column("Valid", style="magenta")
            table.add_column("Suggested Name", style="yellow")
            # No rows, just header
            console.print(table)
            rich_buffer.flush()
            print(rich_buffer.getvalue(), flush=True)
            sys.stdout.flush()
        sys.exit(0)

    try:
        use_plain = os.environ.get("VIDEO_SWEEP_PLAIN") or not sys.stdout.isatty()
        if use_plain:
            console = None
        else:
            import io

            rich_buffer = io.StringIO()
            console = Console(file=rich_buffer, force_terminal=True, color_system=None)
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
                # Extract title and year from new_filename for validation
                import re

                title_year_match = re.match(
                    r"(.+?) \[(\d{4})\]", os.path.splitext(new_filename or filename)[0]
                )
                if title_year_match:
                    extracted_title = title_year_match.group(1)
                    extracted_year = title_year_match.group(2)
                else:
                    extracted_title = None
                    extracted_year = None
                # Validate movie name using OMDb
                valid = None
                suggested = None
                if extracted_title and extracted_year:
                    valid, suggested = validate_movie_name(
                        extracted_title,
                        extracted_year,
                        f"{extracted_title} [{extracted_year}]",
                    )
                    # If OMDb suggested name uses (YEAR), convert to [YEAR]
                    if suggested:
                        import re

                        # Replace ' (YEAR)' at end with ' [YEAR]'
                        suggested = re.sub(r" \((\d{4})\)$", r" [\1]", suggested)
                # Use suggested name for move if available
                ext = os.path.splitext(filename)[1]
                if suggested:
                    target_filename = f"{suggested}{ext}"
                elif new_filename:
                    target_filename = new_filename
                else:
                    target_filename = filename
                target_path = os.path.join(output_dir, target_filename)
                # Store validation info
                validation = {
                    "valid": "Yes" if valid else "No" if valid is not None else "-",
                    "suggested": suggested or "",
                }
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
                validation = {"valid": "-", "suggested": ""}
            else:
                target_path = os.path.join(output_dir, filename)
                validation = {"valid": "-", "suggested": ""}
            results.append(
                {
                    "file": video,
                    "type": kind,
                    "target": target_path,
                    "output_dir": output_dir,
                    "valid": validation["valid"],
                    "suggested": validation["suggested"],
                }
            )

        # Prepare deleted files
        if clean_up:
            for file in non_videos:
                deleted_results.append({"file": file})
        # Print table summary using rich
        if use_plain:
            print("Files to move | Type | Destination | Valid | Suggested Name")
            print("-" * 60)
            for r in results:
                print(
                    f"{os.path.basename(os.path.normpath(r['file']))} | {r['type']} | {os.path.normpath(r['target'])} | {r['valid']} | {r['suggested']}"
                )
        else:
            table = Table()
            table.add_column("Files to move", style="cyan", no_wrap=True)
            table.add_column("Type")
            table.add_column("Destination", style="green")
            table.add_column("Valid", style="magenta")
            table.add_column("Suggested Name", style="yellow")
            for r in results:
                type_str = r["type"]
                if type_str == "movie":
                    type_str = f"[yellow]{type_str}[/yellow]"
                elif type_str == "series":
                    type_str = f"[blue]{type_str}[/blue]"
                valid_str = r["valid"]
                if valid_str == "No":
                    valid_str = f"[red]{valid_str}[/red]"
                table.add_row(
                    os.path.basename(os.path.normpath(r["file"])),
                    type_str,
                    os.path.normpath(r["target"]),
                    valid_str,
                    r["suggested"],
                )
            console.print(table)
            rich_buffer.flush()
            print(rich_buffer.getvalue(), flush=True)
            sys.stdout.flush()

        # Only show deleted table if --clean-up is specified
        if clean_up and deleted_results:
            if use_plain:
                print("Files to delete")
                print("-" * 20)
                for r in deleted_results:
                    print(os.path.basename(os.path.normpath(r["file"])))
            else:
                deleted_table = Table()
                deleted_table.add_column("Files to delete", style="red", no_wrap=True)
                for r in deleted_results:
                    deleted_table.add_row(os.path.basename(os.path.normpath(r["file"])))
                console.print(deleted_table)
                rich_buffer.flush()
                print(rich_buffer.getvalue(), flush=True)
                sys.stdout.flush()

        # Prompt for confirmation if not dry-run
        if not dry_run and (results or (clean_up and deleted_results)):
            proceed = input("Proceed with file moves? [y/N] ").strip().lower()
            if proceed != "y":
                print("Aborted. No files were moved.")
                sys.exit(0)

            # Move video files
            for r in results:
                # Pass OMDb-suggested name if available and kind is movie
                if r["type"] == "movie" and r.get("suggested"):
                    rename_and_move(
                        r["file"],
                        r["type"],
                        r["output_dir"],
                        dry_run=False,
                        omdb_suggested_name=r["suggested"],
                    )
                else:
                    rename_and_move(
                        r["file"], r["type"], r["output_dir"], dry_run=False
                    )

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

                # After all deletions, remove any empty folders in the source directory tree (silently)
                def remove_all_empty_dirs(root_dir):
                    for dirpath, dirnames, filenames in os.walk(
                        root_dir, topdown=False
                    ):
                        # Skip the root itself
                        if dirpath == root_dir:
                            continue
                        if not dirnames and not filenames:
                            try:
                                os.rmdir(dirpath)
                            except Exception:
                                pass

                remove_all_empty_dirs(source)

        # Validation table for movie names
        def print_validation_table(files):
            print(f"{'Current Name':40} | {'Valid':5} | {'Suggested Name':40}")
            print("-" * 90)
            for f in files:
                extracted_title, extracted_year = extract_title_year(
                    f
                )  # Assume this exists
                correct, suggested = validate_movie_name(
                    extracted_title, extracted_year, f
                )
                valid_str = "Yes" if correct else "No"
                suggested_str = suggested if suggested else ""
                print(f"{f:40} | {valid_str:5} | {suggested_str:40}")

        if results:
            print_validation_table([r["file"] for r in results])

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def extract_title_year(filename):
    """
    Extract title and year from a filename using the same logic as movie_new_filename.
    Returns (title, year) or (None, None) if not found.
    """
    import re

    name = os.path.splitext(os.path.basename(filename))[0]
    name = name.replace("[", "").replace("]", "")
    match = re.search(r"(\d{4})", name)
    if not match:
        return None, None
    year = match.group(1)
    title = name[: match.start()].replace(".", " ").strip()
    title = title.strip(" .")
    title = re.sub(r"\s+", " ", title)
    return title, year
