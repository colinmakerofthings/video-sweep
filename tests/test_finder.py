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


def test_find_videos_empty(tmp_path):
    found = find_videos(str(tmp_path))
    assert found == []


def test_find_videos_non_video(tmp_path):
    (tmp_path / "file.txt").write_text("")
    (tmp_path / "image.jpg").write_text("")
    found = find_videos(str(tmp_path))
    assert found == []


def test_find_videos_mixed_case(tmp_path):
    (tmp_path / "movie.MP4").write_text("")
    (tmp_path / "show.MkV").write_text("")
    found = find_videos(str(tmp_path))
    assert any(f.endswith(".MP4") or f.endswith(".MkV") for f in found)
