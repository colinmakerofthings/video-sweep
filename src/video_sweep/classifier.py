import os
import re


def classify_video(filepath: str) -> str:
    """Classify video as 'movie' or 'series' based on filename heuristics."""
    filename = os.path.basename(filepath)
    # Simple heuristic: if filename contains S01E01 or similar, it's a series
    if re.search(r"[Ss]\d+[Ee]\d+", filename):
        return "series"
    return "movie"
