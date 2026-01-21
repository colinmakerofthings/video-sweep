import os
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
