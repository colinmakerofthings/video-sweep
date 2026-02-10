import os
import tempfile
from unittest.mock import patch
import pytest
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


def test_remove_empty_parents_stops_at_non_empty():
    """Test that remove_empty_parents stops when it encounters a non-empty dir."""
    with tempfile.TemporaryDirectory() as root:
        d1 = os.path.join(root, "a")
        d2 = os.path.join(d1, "b")
        d3 = os.path.join(d2, "c")
        os.makedirs(d3)
        # Place a file in d1 to make it non-empty
        sibling_file = os.path.join(d1, "sibling.txt")
        with open(sibling_file, "w") as fp:
            fp.write("keep me")
        # Remove d3
        os.rmdir(d3)
        # Now remove empty parents from d2
        remove_empty_parents(d2, root)
        # d2 should be removed, but d1 should remain (has sibling file)
        assert not os.path.exists(d2)
        assert not os.path.exists(d3)
        assert os.path.exists(d1)
        assert os.path.exists(sibling_file)


def test_remove_empty_parents_stops_at_stop_dir():
    """Test that remove_empty_parents stops at stop_dir, not including it."""
    with tempfile.TemporaryDirectory() as root:
        d1 = os.path.join(root, "a")
        d2 = os.path.join(d1, "b")
        d3 = os.path.join(d2, "c")
        os.makedirs(d3)
        # Remove d3
        os.rmdir(d3)
        # Now remove empty parents, stopping at d1 (should not remove d1)
        remove_empty_parents(d2, d1)
        # d2 should be removed, but d1 should remain
        assert not os.path.exists(d2)
        assert os.path.exists(d1)


def test_remove_empty_parents_when_path_equals_stop_dir():
    """Test that remove_empty_parents stops immediately when path == stop_dir."""
    with tempfile.TemporaryDirectory() as root:
        d1 = os.path.join(root, "a")
        os.makedirs(d1)
        # Call remove_empty_parents with path == stop_dir
        remove_empty_parents(d1, d1)
        # d1 should remain (should not remove it since it's the stop_dir)
        assert os.path.exists(d1)


def test_remove_empty_parents_permission_denied():
    """Test that remove_empty_parents handles permission denied errors gracefully."""
    with tempfile.TemporaryDirectory() as root:
        d1 = os.path.join(root, "a")
        d2 = os.path.join(d1, "b")
        os.makedirs(d2)

        # Mock os.rmdir to raise PermissionError after first call
        original_rmdir = os.rmdir
        call_count = [0]

        def mock_rmdir(path):
            call_count[0] += 1
            if call_count[0] > 1:
                raise PermissionError("Access denied")
            original_rmdir(path)

        with patch("os.rmdir", side_effect=mock_rmdir):
            # Should handle the PermissionError gracefully and stop
            remove_empty_parents(d2, root)

        # d2 should be removed (first call succeeded), d1 should remain
        assert not os.path.exists(d2)
        assert os.path.exists(d1)


def test_remove_empty_parents_with_relative_paths():
    """Test that remove_empty_parents works with relative paths."""
    with tempfile.TemporaryDirectory() as root:
        # Change to the root directory
        original_cwd = os.getcwd()
        try:
            os.chdir(root)
            os.makedirs("a/b/c")
            # Use relative paths
            remove_empty_parents("a/b/c", ".")
            # a, b, c should be removed
            assert not os.path.exists("a/b/c")
            assert not os.path.exists("a/b")
            assert not os.path.exists("a")
        finally:
            os.chdir(original_cwd)


def test_remove_empty_parents_with_symlink():
    """Test that remove_empty_parents handles symlinks appropriately."""
    with tempfile.TemporaryDirectory() as root:
        d1 = os.path.join(root, "a")
        d2 = os.path.join(d1, "b")
        os.makedirs(d2)

        # Create a symlink to d2
        symlink_path = os.path.join(root, "link_to_b")
        try:
            os.symlink(d2, symlink_path)
        except OSError:
            # Skip test if symlinks not supported (e.g., Windows without admin)
            pytest.skip("Symlinks not supported on this system")

        # Verify symlink was created
        assert os.path.islink(symlink_path)

        # Remove empty parents starting from the symlink path
        remove_empty_parents(symlink_path, root)

        # The symlink should be removed
        assert not os.path.islink(symlink_path)
        # The target directory remains (symlink is removed, not the target)
        assert os.path.exists(d2)


@pytest.mark.parametrize("depth", [1, 5, 10, 20])
def test_remove_empty_parents_deep_nesting(depth):
    """Test remove_empty_parents with deeply nested directories."""
    with tempfile.TemporaryDirectory() as root:
        # Create deeply nested directories
        path = root
        for i in range(depth):
            path = os.path.join(path, f"level_{i}")
        os.makedirs(path)

        # Remove empty parents from the deepest level
        remove_empty_parents(path, root)

        # All nested directories should be removed
        assert not os.path.exists(path)
        assert os.path.exists(root)
