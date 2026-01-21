import os
import shutil
import re


def movie_new_filename(filename: str) -> str:
    """Generate new filename for a movie: title [year].ext. If no year, return None."""
    name, ext = os.path.splitext(filename)
    # Remove all [ and ] from the original name
    name = name.replace("[", "").replace("]", "")
    match = re.search(r"(\d{4})", name)
    if not match:
        return None
    year = match.group(1)
    title = name[: match.start()].replace(".", " ").strip()
    # Remove trailing/leading spaces and periods
    title = title.strip(" .")
    # Replace multiple spaces with a single space
    title = re.sub(r"\s+", " ", title)
    return f"{title} [{year}]{ext}"


def rename_and_move(
    filepath: str, kind: str, target_dir: str, dry_run: bool = False
) -> None:
    """Rename and move the video file to the target directory. If dry_run, only print the action."""
    filename = os.path.basename(filepath)
    # All types: move directly to target_dir, no subfolder
    os.makedirs(target_dir, exist_ok=True)

    if kind == "movie":
        new_filename = movie_new_filename(filename)
        if not new_filename:
            print(f"Warning: No year found in '{filename}'. Skipping rename/move.")
            return
        target_path = os.path.join(target_dir, new_filename)
        if os.path.exists(target_path):
            print(
                f"Warning: Target file '{target_path}' already exists. Skipping move."
            )
            return
    elif kind == "series":
        result = series_new_filename(filename)
        if not result:
            print(
                f"Warning: No episode code found in '{filename}'. Skipping rename/move."
            )
            return
        series_name, season_num, episode_code, new_filename = result
        season_folder = f"Season {season_num}"
        target_path = os.path.join(target_dir, series_name, season_folder, new_filename)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        if os.path.exists(target_path):
            print(
                f"Warning: Target file '{target_path}' already exists. Skipping move."
            )
            return
    else:
        target_path = os.path.join(target_dir, filename)
        if os.path.exists(target_path):
            print(
                f"Warning: Target file '{target_path}' already exists. Skipping move."
            )
            return

    if dry_run:
        print(f"Would move: {filepath} -> {target_path}")
        return
    try:
        shutil.move(filepath, target_path)
        print(f"Moved: {filepath} -> {target_path}")
    except Exception as e:
        print(f"Failed to move {filepath}: {e}")


def series_new_filename(filename: str) -> tuple:
    """
    Generate new filename and output path for a series episode.
    Returns (series_name, season_num, episode_code, new_filename) or None if not matched.
    """
    name, ext = os.path.splitext(filename)
    # Remove year in brackets, e.g. (2014)
    name = re.sub(r"\(\d{4}\)", "", name)
    # Find episode code SxxEyy
    ep_match = re.search(r"S(\d{2})E(\d{2})", name, re.IGNORECASE)
    if not ep_match:
        return None
    season_num = int(ep_match.group(1))
    episode_code = ep_match.group(0).upper()
    # Series name: everything before episode code
    series_name = name[: ep_match.start()].replace(".", " ").replace("-", " ").strip()
    # Remove extra spaces
    series_name = re.sub(r"\s+", " ", series_name)
    # Remove trailing/leading spaces and periods
    series_name = series_name.strip(" .")
    new_filename = f"{series_name} {episode_code}{ext}"
    return series_name, season_num, episode_code, new_filename
