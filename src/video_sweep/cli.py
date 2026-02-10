import argparse
import sys
import os
import logging
from rich.console import Console
from rich.table import Table
import tomli
from .finder import find_files
from .classifier import classify_video
from .renamer import rename_and_move, validate_movie_name

# For removing empty parent folders
from .utils import remove_empty_parents


def main():
    # Check if OMDb API key is present
    from .omdb import get_api_key_from_config

    omdb_api_key = get_api_key_from_config()
    show_omdb_columns = bool(omdb_api_key)
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
        from importlib.metadata import version

        print(f"video-sweep version {version('video-sweep')}")
        sys.exit(0)

    # Handle --init-config
    if args.init_config:
        # Ensure .toml extension
        config_path = args.init_config
        if not config_path.endswith(".toml"):
            config_path = f"{config_path}.toml"

        sample = (
            "# Sample video-sweep config file\n"
            'source = "/Users/YOUR_USERNAME/Downloads"\n'
            'series_output = "/Users/YOUR_USERNAME/Movies/TV Shows"\n'
            'movie_output = "/Users/YOUR_USERNAME/Movies"\n'
            "clean_up = false\n"
            "dry_run = false\n"
        )
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(sample)
        print(f"Sample config written to {config_path}")
        sys.exit(0)

    # Load config file if specified, or auto-load only when no CLI options are set
    config = {}
    has_cli_values = any(
        getattr(args, opt) is not None
        for opt in ("source", "series_output", "movie_output")
    ) or any(hasattr(args, opt) for opt in ("dry_run", "clean_up"))
    config_path = args.config
    if not config_path and not has_cli_values and os.path.exists("config.toml"):
        config_path = os.path.join(os.getcwd(), "config.toml")
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

    source = get_opt("source")
    series_output = get_opt("series_output")
    movie_output = get_opt("movie_output")
    dry_run = get_opt("dry_run", False)
    clean_up = get_opt("clean_up", False)

    if not source or not series_output or not movie_output:
        print(
            "Error: --source, --series-output, and --movie-output are required.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Normalize paths after validation
    source = os.path.normpath(source)
    series_output = os.path.normpath(series_output)
    movie_output = os.path.normpath(movie_output)

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
                if show_omdb_columns:
                    # Extract title and year from new_filename for validation
                    import re

                    title_year_match = re.match(
                        r"(.+?) \[(\d{4})\]",
                        os.path.splitext(new_filename or filename)[0],
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
                else:
                    # No OMDb columns, skip validation
                    target_path = os.path.join(output_dir, new_filename or filename)
                    validation = {}

            if kind == "series":
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
            elif kind not in ("movie", "series"):
                target_path = os.path.join(output_dir, filename)
                validation = {"valid": "-", "suggested": ""}
            result_entry = {
                "file": video,
                "type": kind,
                "target": target_path,
                "output_dir": output_dir,
            }
            if show_omdb_columns:
                result_entry["valid"] = validation.get("valid", "")
                result_entry["suggested"] = validation.get("suggested", "")
            results.append(result_entry)

        # Prepare deleted files
        if clean_up:
            for file in non_videos:
                deleted_results.append({"file": file})
        # Print table summary using rich
        if use_plain:
            header = "Files to move | Type | Destination"
            if show_omdb_columns:
                header += " | Valid | Suggested Name"
            print(header)
            print("-" * len(header))
            for r in results:
                file_name = os.path.basename(os.path.normpath(r["file"]))
                target = os.path.normpath(r["target"])
                row = f"{file_name} | {r['type']} | {target}"
                if show_omdb_columns:
                    row += f" | {r.get('valid', '')} | {r.get('suggested', '')}"
                print(row)
        else:
            table = Table()
            table.add_column("Files to move", style="cyan", no_wrap=True)
            table.add_column("Type")
            table.add_column("Destination", style="green")
            if show_omdb_columns:
                table.add_column("Valid", style="magenta")
                table.add_column("Suggested Name", style="yellow")
            for r in results:
                type_str = r["type"]
                if type_str == "movie":
                    type_str = f"[yellow]{type_str}[/yellow]"
                elif type_str == "series":
                    type_str = f"[blue]{type_str}[/blue]"
                row_args = [
                    os.path.basename(os.path.normpath(r["file"])),
                    type_str,
                    os.path.normpath(r["target"]),
                ]
                if show_omdb_columns:
                    valid_str = r.get("valid", "")
                    if valid_str == "No":
                        valid_str = f"[red]{valid_str}[/red]"
                    row_args.append(valid_str)
                    row_args.append(r.get("suggested", ""))
                table.add_row(*row_args)
            console.print(table)
            rich_buffer.flush()
            print(rich_buffer.getvalue(), flush=True)
            sys.stdout.flush()
            # Clear buffer after printing
            rich_buffer.truncate(0)
            rich_buffer.seek(0)

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
                # Clear buffer after printing
                rich_buffer.truncate(0)
                rich_buffer.seek(0)

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

                # After all deletions, remove any empty folders in the
                # source directory tree (silently)
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
                            except Exception as e:
                                logging.debug(
                                    f"Could not remove empty directory {dirpath}: {e}"
                                )

                remove_all_empty_dirs(source)

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
