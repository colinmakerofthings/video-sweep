import os
from unittest.mock import patch
from video_sweep.renamer import rename_and_move


def test_rename_and_move_movie(tmp_path):
    src = tmp_path / "source"
    tgt = tmp_path / "target"
    src.mkdir()
    tgt.mkdir()
    video = src / "movie.2023.mp4"
    video.write_text("")
    rename_and_move(str(video), "movie", str(tgt))
    assert os.path.exists(os.path.join(str(tgt), "movie [2023].mp4"))


def test_rename_and_move_series(tmp_path):
    src = tmp_path / "source"
    tgt = tmp_path / "target"
    src.mkdir()
    tgt.mkdir()
    video = src / "SeriesName (2014) - S04E01 - Other text.mkv"
    video.write_text("")
    rename_and_move(str(video), "series", str(tgt))
    expected_path = os.path.join(
        str(tgt), "SeriesName", "Season 4", "SeriesName S04E01.mkv"
    )
    assert os.path.exists(expected_path)


def test_rename_and_move_series_missing_episode(tmp_path, capsys):
    src = tmp_path / "source"
    tgt = tmp_path / "target"
    src.mkdir()
    tgt.mkdir()
    video = src / "SeriesName (2014) - Other text.mkv"
    video.write_text("")
    rename_and_move(str(video), "series", str(tgt))
    # Should not move file, should print warning
    out = capsys.readouterr().out
    assert "Warning: No episode code found" in out
    assert not os.path.exists(
        os.path.join(str(tgt), "SeriesName", "Season 4", "SeriesName S04E01.mkv")
    )


def test_rename_and_move_movie_no_year(tmp_path, capsys):
    src = tmp_path / "source"
    tgt = tmp_path / "target"
    src.mkdir()
    tgt.mkdir()
    video = src / "moviefile.mp4"
    video.write_text("")
    rename_and_move(str(video), "movie", str(tgt))
    out = capsys.readouterr().out
    assert "Warning: No year found" in out
    assert not any(f.name.startswith("moviefile") for f in tgt.iterdir())


def test_rename_and_move_target_exists(tmp_path, capsys):
    src = tmp_path / "source"
    tgt = tmp_path / "target"
    src.mkdir()
    tgt.mkdir()
    video = src / "movie.2023.mp4"
    video.write_text("")
    # Create target file first
    target = tgt / "movie [2023].mp4"
    target.write_text("already here")
    rename_and_move(str(video), "movie", str(tgt))
    out = capsys.readouterr().out
    assert "already exists" in out


def test_rename_and_move_dry_run(tmp_path, capsys):
    src = tmp_path / "source"
    tgt = tmp_path / "target"
    src.mkdir()
    tgt.mkdir()
    video = src / "movie.2023.mp4"
    video.write_text("")
    rename_and_move(str(video), "movie", str(tgt), dry_run=True)
    out = capsys.readouterr().out
    assert "Would move" in out
    assert not any(f.name.startswith("movie") for f in tgt.iterdir())


def test_rename_and_move_series_invalid(tmp_path, capsys):
    src = tmp_path / "source"
    tgt = tmp_path / "target"
    src.mkdir()
    tgt.mkdir()
    video = src / "Show SXXEYY.mkv"
    video.write_text("")
    rename_and_move(str(video), "series", str(tgt))
    out = capsys.readouterr().out
    assert "No episode code found" in out
    assert not any(f.is_file() for f in tgt.rglob("*"))


def test_rename_and_move_makedirs_failure(tmp_path, capsys):
    """Test rename_and_move when os.makedirs fails."""
    src = tmp_path / "source"
    src.mkdir()
    video = src / "movie.2023.mp4"
    video.write_text("")

    # Mock the entire rename_and_move flow to avoid directory creation
    with patch(
        "video_sweep.renamer.shutil.move", side_effect=OSError("Permission denied")
    ):
        rename_and_move(str(video), "movie", str(tmp_path))
        out = capsys.readouterr().out
        assert "Failed to move" in out


def test_rename_and_move_shutil_move_failure(tmp_path, capsys):
    """Test rename_and_move when shutil.move fails."""
    src = tmp_path / "source"
    tgt = tmp_path / "target"
    src.mkdir()
    tgt.mkdir()
    video = src / "movie.2023.mp4"
    video.write_text("")

    with patch(
        "video_sweep.renamer.shutil.move", side_effect=OSError("File is locked")
    ):
        rename_and_move(str(video), "movie", str(tgt))
        out = capsys.readouterr().out
        assert "Failed to move" in out


def test_rename_and_move_movie_with_omdb_suggestion(tmp_path):
    """Test rename_and_move movie with OMDb-suggested name."""
    src = tmp_path / "source"
    tgt = tmp_path / "target"
    src.mkdir()
    tgt.mkdir()
    video = src / "movie.2023.mp4"
    video.write_text("")

    rename_and_move(str(video), "movie", str(tgt), omdb_suggested_name="Inception")
    assert os.path.exists(os.path.join(str(tgt), "Inception.mp4"))


def test_rename_and_move_movie_omdb_suggestion_exists(tmp_path, capsys):
    """Test rename_and_move movie with OMDb suggestion when target exists."""
    src = tmp_path / "source"
    tgt = tmp_path / "target"
    src.mkdir()
    tgt.mkdir()
    video = src / "movie.2023.mp4"
    video.write_text("")

    # Create target file
    target = tgt / "Inception.mp4"
    target.write_text("existing")

    rename_and_move(str(video), "movie", str(tgt), omdb_suggested_name="Inception")
    out = capsys.readouterr().out
    assert "already exists" in out


def test_rename_and_move_unknown_kind(tmp_path):
    """Test rename_and_move with unknown file kind."""
    src = tmp_path / "source"
    tgt = tmp_path / "target"
    src.mkdir()
    tgt.mkdir()
    video = src / "file.mp4"
    video.write_text("")

    rename_and_move(str(video), "unknown", str(tgt))
    # Should move file as-is for unknown kind
    assert os.path.exists(os.path.join(str(tgt), "file.mp4"))


def test_rename_and_move_series_with_lowercase_episode(tmp_path):
    """Test rename_and_move series with lowercase episode code."""
    src = tmp_path / "source"
    tgt = tmp_path / "target"
    src.mkdir()
    tgt.mkdir()
    video = src / "SeriesName (2014) - s04e01 - Other text.mkv"
    video.write_text("")
    rename_and_move(str(video), "series", str(tgt))
    # Should still find and convert to uppercase
    expected_path = os.path.join(
        str(tgt), "SeriesName", "Season 4", "SeriesName S04E01.mkv"
    )
    assert os.path.exists(expected_path)


def test_rename_and_move_series_creates_directories(tmp_path):
    """Test that rename_and_move creates nested directories for series."""
    src = tmp_path / "source"
    tgt = tmp_path / "target"
    src.mkdir()
    # Don't create tgt, let rename_and_move create it
    video = src / "MyShow - S02E05.mkv"
    video.write_text("")
    rename_and_move(str(video), "series", str(tgt))
    expected_path = os.path.join(str(tgt), "MyShow", "Season 2", "MyShow S02E05.mkv")
    assert os.path.exists(expected_path)
