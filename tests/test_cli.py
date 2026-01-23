import subprocess
import sys
import pytest
from pathlib import Path

def run_cli(args, cwd=None):
    """Run the CLI with given args and return (exitcode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, '-m', 'video_sweep'] + args,  # Use package entry point
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr

def test_cli_help():
    code, out, err = run_cli(['--help'])
    assert code == 0
    assert 'usage' in out.lower() or 'options' in out.lower()

# Add more CLI tests as needed (e.g., dry-run, config, error cases)
