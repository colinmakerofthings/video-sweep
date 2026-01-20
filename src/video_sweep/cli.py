

import argparse
import sys
import os
from rich.console import Console
from rich.table import Table
from .finder import find_files
from .classifier import classify_video
from .renamer import rename_and_move

def main():
    parser = argparse.ArgumentParser(description="Find, classify, rename, and move video files.")
    parser.add_argument('--source', required=True, help='Source directory to scan for videos')
    parser.add_argument('--series-output', required=True, help='Output directory for series')
    parser.add_argument('--movie-output', required=True, help='Output directory for movies')
    parser.add_argument('--dry-run', action='store_true', help='If set, only print actions without moving files')
    parser.add_argument('--clean-up', action='store_true', help='If set, move non-video files to Deleted folder')
    args = parser.parse_args()

    try:
        console = Console()
        videos, non_videos = find_files(args.source)
        results = []
        deleted_results = []
        from .renamer import movie_new_filename
        # Handle video files
        for video in videos:
            kind = classify_video(video)
            output_dir = args.series_output if kind == 'series' else args.movie_output
            filename = os.path.basename(video)
            if kind == 'movie':
                new_filename = movie_new_filename(filename)
                if new_filename:
                    target_path = os.path.join(output_dir, new_filename)
                else:
                    target_path = os.path.join(output_dir, filename)
            else:
                target_path = os.path.join(output_dir, filename)
            results.append({
                'file': video,
                'type': kind,
                'target': target_path
            })
            rename_and_move(video, kind, output_dir, dry_run=args.dry_run)

        # Handle non-video files (cleanup)
        if args.clean_up:
            deleted_dir = os.path.join(args.source, "Deleted")
            if non_videos:
                os.makedirs(deleted_dir, exist_ok=True)
            for file in non_videos:
                target_path = os.path.join(deleted_dir, os.path.basename(file))
                deleted_results.append({'file': file, 'target': target_path})
                if args.dry_run:
                    print(f"Would move (delete): {file} -> {target_path}")
                else:
                    try:
                        if os.path.exists(target_path):
                            print(f"Warning: Deleted file '{target_path}' already exists. Skipping move.")
                            continue
                        os.rename(file, target_path)
                        print(f"Moved (deleted): {file} -> {target_path}")
                    except Exception as e:
                        print(f"Failed to move (delete) {file}: {e}")
        # Only show deleted table if --clean-up is specified
        if args.clean_up and deleted_results:
            deleted_table = Table(title="Files to be deleted...")
            deleted_table.add_column("File", style="red", no_wrap=True)
            deleted_table.add_column("Target", style="yellow")
            for r in deleted_results:
                deleted_table.add_row(os.path.basename(r['file']), r['target'])
            console.print(deleted_table)

        # Print table summary using rich
        table = Table()
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Type", style="magenta")
        table.add_column("Target", style="green")
        for r in results:
            table.add_row(os.path.basename(r['file']), r['type'], r['target'])
        console.print(table)

        # Print deleted files table if any
        if deleted_results:
            deleted_table = Table(title="Files to be deleted...")
            deleted_table.add_column("File", style="red", no_wrap=True)
            deleted_table.add_column("Target", style="yellow")
            for r in deleted_results:
                deleted_table.add_row(os.path.basename(r['file']), r['target'])
            console.print(deleted_table)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
