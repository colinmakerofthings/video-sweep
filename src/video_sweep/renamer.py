import os
import shutil

def rename_and_move(filepath: str, kind: str, target_dir: str, dry_run: bool = False) -> None:
    """Rename and move the video file to the target directory. If dry_run, only print the action."""
    filename = os.path.basename(filepath)
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, filename)
    if dry_run:
        print(f"Would move: {filepath} -> {target_path}")
        return
    try:
        shutil.move(filepath, target_path)
        print(f"Moved: {filepath} -> {target_path}")
    except Exception as e:
        print(f"Failed to move {filepath}: {e}")
