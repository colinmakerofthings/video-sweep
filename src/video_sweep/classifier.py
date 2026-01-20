import os


def classify_video(filepath: str) -> str:
    """Classify video as 'movie' or 'series' based on filename heuristics."""
    filename = os.path.basename(filepath)
    # Simple heuristic: if filename contains S01E01 or similar, it's a series
    if any(
        part in filename.upper() for part in ["S01E", "S02E", "S03E", "S04E", "S05E"]
    ):
        return "series"
    return "movie"
