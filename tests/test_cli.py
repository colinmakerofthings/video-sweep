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


def test_cli_version():
    code, out, err = run_cli(["--version"])
    assert code == 0
    assert "version" in out.lower()


# Add more CLI tests as needed (e.g., dry-run, config, error cases)
