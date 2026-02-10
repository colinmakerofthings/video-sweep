import os
import shutil
import re
from .omdb import query_omdb, get_suggested_name


def sanitize_filename(name: str) -> str:
    """
    Remove or replace characters not allowed in Windows filenames.
    Periods (.) and dashes (-) are allowed and preserved.
    """
    # Windows forbidden chars: < > : " / \ | ? *
    # Do NOT remove . or -
    return re.sub(r'[<>:"/\\|?*]', "", name)


def movie_new_filename(filename: str) -> str:
    """Generate new filename for a movie: title [year].ext. If no year, return None."""
    name, ext = os.path.splitext(filename)
    # Remove all [ and ] from the original name
    name_clean = name.replace("[", "").replace("]", "")
    # If filename starts with a 4-digit number, treat as title, look for year elsewhere
    m_start = re.match(r"^(\d{4})(.*)", name_clean)
    if m_start:
        title = m_start.group(1).strip()
        # Look for year in brackets/parentheses after title
        m_year = re.search(r"[\[(](\d{4})[\])]", name)
        if m_year:
            year = m_year.group(1)
            return sanitize_filename(f"{title} [{year}]{ext}")
        # Fallback: if no year found, just use the title
        return sanitize_filename(f"{title}{ext}")
    # Otherwise, use the first 4-digit number as year
    match = re.search(r"(\d{4})", name_clean)
    if not match:
        return None
    year = match.group(1)
    title = name_clean[: match.start()].replace(".", " ").strip()
    # Remove trailing/leading spaces and periods
    title = title.strip(" .")
    # Replace multiple spaces with a single space
    title = re.sub(r"\s+", " ", title)
    return sanitize_filename(f"{title} [{year}]{ext}")


def rename_and_move(
    filepath: str,
    kind: str,
    target_dir: str,
    dry_run: bool = False,
    omdb_suggested_name: str = None,
) -> None:
    """Rename and move the video file to the target directory.
    If dry_run, only print the action.
    If omdb_suggested_name is provided (and kind==movie), use it as the new filename."""
    filename = os.path.basename(filepath)
    # All types: move directly to target_dir, no subfolder
    os.makedirs(target_dir, exist_ok=True)

    if kind == "movie":
        # Use OMDb-suggested name if provided
        if omdb_suggested_name:
            ext = os.path.splitext(filename)[1]
            new_filename = sanitize_filename(f"{omdb_suggested_name}{ext}")
        else:
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
    Returns (series_name, season_num, episode_code, new_filename) or None if
    not matched.
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


def validate_movie_name(extracted_title, extracted_year, current_name):
    omdb_data = query_omdb(extracted_title, extracted_year)
    if not omdb_data:
        return False, None
    suggested = get_suggested_name(omdb_data)
    # Normalize OMDb suggested name to [YEAR] format for comparison
    import re

    if suggested:
        # Sanitize for filesystem before proposing/validating
        suggested = sanitize_filename(suggested)
        suggested_normalized = re.sub(r" \((\d{4})\)$", r" [\1]", suggested)
    else:
        suggested_normalized = None
    # Compare normalized names
    correct = (
        suggested_normalized and suggested_normalized.lower() == current_name.lower()
    )
    return correct, suggested_normalized if not correct else None
