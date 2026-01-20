import os
from typing import List

VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi'}

def find_videos(source_dir: str) -> List[str]:
    """Recursively find video files in the source directory."""
    videos = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:
                videos.append(os.path.join(root, file))
    return videos
