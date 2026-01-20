

import argparse
import sys
import os
from rich.console import Console
from rich.table import Table
from .finder import find_videos
from .classifier import classify_video
from .renamer import rename_and_move

def main():
    parser = argparse.ArgumentParser(description="Find, classify, rename, and move video files.")
    parser.add_argument('--source', required=True, help='Source directory to scan for videos')
    parser.add_argument('--series-output', required=True, help='Output directory for series')
    parser.add_argument('--movie-output', required=True, help='Output directory for movies')
    parser.add_argument('--dry-run', action='store_true', help='If set, only print actions without moving files')
    args = parser.parse_args()

    try:
        videos = find_videos(args.source)
        results = []
        from .renamer import movie_new_filename
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

        # Print table summary using rich
        console = Console()
        table = Table()
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Type", style="magenta")
        table.add_column("Target", style="green")
        for r in results:
            table.add_row(os.path.basename(r['file']), r['type'], r['target'])
        console.print(table)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
