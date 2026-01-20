import os


VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi"}


def find_files(source_dir: str):
    """Recursively find all files in the source directory, returning (videos, non_videos)."""
    videos = []
    non_videos = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            full_path = os.path.join(root, file)
            if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:
                videos.append(full_path)
            else:
                non_videos.append(full_path)
    return videos, non_videos


def find_videos(source_dir: str):
    """Recursively find all video files in the source directory."""
    videos = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:
                videos.append(os.path.join(root, file))
    return videos
