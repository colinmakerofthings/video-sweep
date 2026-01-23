try:
    from .cli import main
except ImportError:
    # If run as 'python -m video_sweep' from outside src, import from video_sweep.cli
    from video_sweep.cli import main

if __name__ == "__main__":
    main()
