from video_sweep.finder import find_videos


def test_find_videos(tmp_path):
    # Create dummy video files
    video1 = tmp_path / "movie.mp4"
    video2 = tmp_path / "show.mkv"
    video3 = tmp_path / "clip.avi"
    video1.write_text("")
    video2.write_text("")
    video3.write_text("")
    # Create a non-video file
    (tmp_path / "doc.txt").write_text("")
    found = find_videos(str(tmp_path))
    assert len(found) == 3
    assert all(f.endswith((".mp4", ".mkv", ".avi")) for f in found)
