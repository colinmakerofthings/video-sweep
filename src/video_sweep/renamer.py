import os
import shutil
import re

def movie_new_filename(filename: str) -> str:
    """Generate new filename for a movie: title [year].ext. If no year, return None."""
    name, ext = os.path.splitext(filename)
    match = re.search(r'(\d{4})', name)
    if not match:
        return None
    year = match.group(1)
    title = name[:match.start()].replace('.', ' ').strip()
    # Remove trailing/leading spaces and periods
    title = title.strip(' .')
    # Replace multiple spaces with a single space
    title = re.sub(r'\s+', ' ', title)
    return f"{title} [{year}]{ext}"

def rename_and_move(filepath: str, kind: str, target_dir: str, dry_run: bool = False) -> None:
    """Rename and move the video file to the target directory. If dry_run, only print the action."""
    filename = os.path.basename(filepath)
    os.makedirs(target_dir, exist_ok=True)

    # For movies, generate new filename
    if kind == 'movie':
        new_filename = movie_new_filename(filename)
        if not new_filename:
            print(f"Warning: No year found in '{filename}'. Skipping rename/move.")
            return
        target_path = os.path.join(target_dir, new_filename)
        if os.path.exists(target_path):
            print(f"Warning: Target file '{target_path}' already exists. Skipping move.")
            return
    else:
        target_path = os.path.join(target_dir, filename)
        if os.path.exists(target_path):
            print(f"Warning: Target file '{target_path}' already exists. Skipping move.")
            return

    if dry_run:
        print(f"Would move: {filepath} -> {target_path}")
        return
    try:
        shutil.move(filepath, target_path)
        print(f"Moved: {filepath} -> {target_path}")
    except Exception as e:
        print(f"Failed to move {filepath}: {e}")
