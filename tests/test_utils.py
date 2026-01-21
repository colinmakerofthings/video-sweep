import os
import tempfile
from video_sweep.utils import remove_empty_parents


def test_remove_empty_parents():
    # Create nested directories
    with tempfile.TemporaryDirectory() as root:
        d1 = os.path.join(root, "a")
        d2 = os.path.join(d1, "b")
        d3 = os.path.join(d2, "c")
        os.makedirs(d3)
        # Place a file in the deepest dir
        f = os.path.join(d3, "file.txt")
        with open(f, "w") as fp:
            fp.write("test")
        # Remove the file
        os.remove(f)
        # Now remove empty parents up to root
        remove_empty_parents(d3, root)
        # d3, d2, d1 should all be removed, only root remains
        assert not os.path.exists(d3)
        assert not os.path.exists(d2)
        assert not os.path.exists(d1)
        assert os.path.exists(root)
