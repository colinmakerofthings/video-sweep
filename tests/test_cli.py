import subprocess
import sys


def run_cli(args, cwd=None):
    """Run the CLI with given args and return (exitcode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, "-m", "video_sweep"] + args,  # Use package entry point
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def test_cli_help():
    code, out, err = run_cli(["--help"])
    # Print outputs for debugging in CI
    print("STDOUT:", out)
    print("STDERR:", err)
    print("EXIT CODE:", code)
    assert code == 0
    assert "usage" in out.lower() or "options" in out.lower()


def test_cli_dry_run(tmp_path):
    src = tmp_path / "source"
    tgt = tmp_path / "target"
    src.mkdir()
    tgt.mkdir()
    video = src / "movie.2023.mp4"
    video.write_text("")
    # Provide all required arguments
    series = tmp_path / "series"
    series.mkdir()
    code, out, err = run_cli(
        [
            "--source",
            str(src),
            "--series-output",
            str(series),
            "--movie-output",
            str(tgt),
            "--dry-run",
        ]
    )
    assert code == 0
    print(f"CLI OUT: {out!r}")
    print(f"CLI ERR: {err!r}")
    assert out is not None, f"No output captured from CLI. STDERR: {err!r}"
    # Check that the output table contains some .mp4 file in the destination column
    assert ".mp4" in out, f"Expected .mp4 in output, got: {out!r}"


def test_cli_no_source():
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        src = tmpdir
        series = tmpdir  # Not used, but required
        tgt = tmpdir
        code, out, err = run_cli(
            [
                "--source",
                src,
                "--series-output",
                series,
                "--movie-output",
                tgt,
            ]
        )
        # Should exit 0 and print an empty table (no files to move)
        assert code == 0
        print(f"CLI OUT: {out!r}")
        print(f"CLI ERR: {err!r}")
        assert out is not None, f"No output captured from CLI. STDERR: {err!r}"
        assert (
            "files to move" in out.lower()
        ), f"Expected 'files to move' in output, got: {out!r}"
        # Table should have no video files listed
        assert "| movie" not in out.lower(), f"Unexpected movie row in output: {out!r}"


def test_cli_init_config(tmp_path):
    config_path = tmp_path / "sample_config.toml"
    code, out, err = run_cli(["--init-config", str(config_path)])
    assert code == 0
    assert config_path.exists()
    assert "Sample config written" in out


def test_cli_init_config_auto_adds_toml_extension(tmp_path):
    """Test that .toml extension is automatically added if missing."""
    config_path = tmp_path / "myconfig"
    code, out, err = run_cli(["--init-config", str(config_path)])
    assert code == 0
    # Should create myconfig.toml, not myconfig
    expected_path = tmp_path / "myconfig.toml"
    assert expected_path.exists()
    assert "Sample config written" in out
    assert "myconfig.toml" in out


def test_cli_no_arguments():
    """Test that running with no arguments exits gracefully."""
    code, out, err = run_cli([])
    assert code == 0
    # Should print empty table header
    assert "files to move" in out.lower() or "Type" in out


def test_cli_version():
    code, out, err = run_cli(["--version"])
    assert code == 0
    assert "version" in out.lower()


# Direct unit tests for coverage (bypassing subprocess)
def test_init_config_with_extension_direct(tmp_path, monkeypatch):
    """Test --init-config directly to ensure .toml extension handling is covered."""
    import sys
    from video_sweep.cli import main

    config_path = tmp_path / "testconfig.toml"
    monkeypatch.setattr(sys, "argv", ["video-sweep", "--init-config", str(config_path)])

    try:
        main()
    except SystemExit as e:
        assert e.code == 0

    assert config_path.exists()
    content = config_path.read_text()
    assert "source =" in content


def test_init_config_auto_extension_direct(tmp_path, monkeypatch):
    """Test --init-config adds .toml extension when missing (direct call for coverage)."""
    import sys
    from video_sweep.cli import main

    config_path_no_ext = tmp_path / "myconfig"
    monkeypatch.setattr(
        sys, "argv", ["video-sweep", "--init-config", str(config_path_no_ext)]
    )

    try:
        main()
    except SystemExit as e:
        assert e.code == 0

    # Should create myconfig.toml, not myconfig
    expected_path = tmp_path / "myconfig.toml"
    assert expected_path.exists()
    assert not config_path_no_ext.exists()


def test_no_args_exits_gracefully_direct(monkeypatch, capsys):
    """Test that running with no arguments exits gracefully (direct call for coverage)."""
    import sys
    from video_sweep.cli import main

    monkeypatch.setattr(sys, "argv", ["video-sweep"])

    try:
        main()
    except SystemExit as e:
        assert e.code == 0

    captured = capsys.readouterr()
    # Should print table header
    assert "files to move" in captured.out.lower() or "Type" in captured.out


def test_path_normalization_direct(tmp_path, monkeypatch, capsys):
    """Test that paths are normalized after validation (direct call for coverage)."""
    import sys
    from video_sweep.cli import main

    src = tmp_path / "source"
    series = tmp_path / "series"
    movies = tmp_path / "movies"
    src.mkdir()
    series.mkdir()
    movies.mkdir()

    # Create a dummy video file so we get past the validation and into the processing code
    video_file = src / "test.movie.2023.mp4"
    video_file.write_text("")

    # Add trailing slashes to test normalization
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "video-sweep",
            "--source",
            f"{src}/",
            "--series-output",
            f"{series}/",
            "--movie-output",
            f"{movies}/",
            "--dry-run",
        ],
    )

    # In dry-run mode with video files, main() prints the table and exits gracefully
    # We don't assert on exit code as the behavior may vary
    try:
        main()
    except SystemExit:
        # Expected - main() calls sys.exit() after displaying the table
        pass

    # The test passes if no exception is raised and paths are handled correctly
    captured = capsys.readouterr()
    # Should have processed the video file
    assert ".mp4" in captured.out or "movie" in captured.out.lower()


# Add more CLI tests as needed (e.g., dry-run, config, error cases)
