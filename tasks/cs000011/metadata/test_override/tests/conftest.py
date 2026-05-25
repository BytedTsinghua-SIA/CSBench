import subprocess
from pathlib import Path
import pytest


@pytest.fixture
def run_aggregator():
    def _run(cmd: str):
        cwd = Path(__file__).resolve().parent.parent
        # Ensure the command runs from the correct directory and captures output
        return subprocess.run(
            cmd,
            cwd=str(cwd),
            shell=True,
            check=False,
            text=True,
            input="\n",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    return _run