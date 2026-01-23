from video_sweep.finder import find_files


def test_find_files_basic(tmp_path):
    # Create video and non-video files
    v1 = tmp_path / "a.mp4"
    v2 = tmp_path / "b.mkv"
    n1 = tmp_path / "note.txt"
    v1.write_text("")
    v2.write_text("")
    n1.write_text("")
    videos, non_videos = find_files(str(tmp_path))
    assert any(f.endswith(".mp4") for f in videos)
    assert any(f.endswith(".mkv") for f in videos)
    assert any(f.endswith(".txt") for f in non_videos)


def test_find_files_nested(tmp_path):
    # Nested structure
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "movie.avi").write_text("")
    (sub / "readme.md").write_text("")
    videos, non_videos = find_files(str(tmp_path))
    assert any(f.endswith(".avi") for f in videos)
    assert any(f.endswith(".md") for f in non_videos)


def test_find_files_no_videos(tmp_path):
    (tmp_path / "foo.txt").write_text("")
    videos, non_videos = find_files(str(tmp_path))
    assert videos == []
    assert len(non_videos) == 1


def test_find_files_empty(tmp_path):
    videos, non_videos = find_files(str(tmp_path))
    assert videos == []
    assert non_videos == []
