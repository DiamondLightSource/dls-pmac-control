import subprocess
import sys

from dls_pmac_control import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "dls_pmac_control", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
