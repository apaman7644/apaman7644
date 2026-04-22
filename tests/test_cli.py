import os
import subprocess
import sys


def test_cli_init_project():
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    cmd = [
        sys.executable,
        "-m",
        "novel_auto_gen.cli.main",
        "--config",
        "configs/default.toml",
        "init-project",
        "--name",
        "cli-test",
    ]
    out = subprocess.check_output(cmd, text=True, env=env)
    assert "project_id" in out
