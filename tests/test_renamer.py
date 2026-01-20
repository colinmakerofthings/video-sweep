import os
import shutil
from video_sweep.renamer import rename_and_move

def test_rename_and_move(tmp_path):
    src = tmp_path / "source"
    tgt = tmp_path / "target"
    src.mkdir()
    tgt.mkdir()
    video = src / "movie.mp4"
    video.write_text("")
    rename_and_move(str(video), "movie", str(tgt))
    assert os.path.exists(os.path.join(str(tgt), "movie", "movie.mp4"))
