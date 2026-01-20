from video_sweep.classifier import classify_video


def test_classify_movie():
    assert classify_video("/path/to/Inception.mp4") == "movie"


def test_classify_series():
    assert classify_video("/path/to/BreakingBad.S01E01.mkv") == "series"
