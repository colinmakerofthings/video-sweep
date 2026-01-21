import os

"""
utils.py: Utility functions for video-sweep project.
Includes remove_empty_parents for cleaning up empty directories after file operations.
"""


def remove_empty_parents(path, stop_dir):
    """
    Recursively remove empty parent directories up to stop_dir (not including stop_dir).
    Args:
        path (str): Path to start checking from (usually the file's parent directory).
        stop_dir (str): Directory at which to stop (do not remove this directory).
    """
    path = os.path.abspath(path)
    stop_dir = os.path.abspath(stop_dir)
    while True:
        parent = os.path.dirname(path)
        if parent == path or path == stop_dir:
            break
        try:
            if not os.listdir(path):
                os.rmdir(path)
            else:
                break
        except Exception:
            break
        path = parent
