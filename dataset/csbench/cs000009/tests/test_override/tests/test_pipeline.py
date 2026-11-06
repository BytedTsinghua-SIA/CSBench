import subprocess
from pathlib import Path

def test_pipeline():
    """Tests the pipeline-test executable."""
    cwd = Path(__file__).resolve().parent.parent
    executable = cwd / "pipeline-test"

    assert executable.exists(), f"Missing file: {executable}"

    cmd = f"./{executable.name}"
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = result.stdout or ""
    expected_summary = "Pipeline: cat /etc/group -> wc"

    assert expected_summary in output, (
        f"Expected summary line not found in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )

    # The output of `wc` should be three numbers. We can check for that.
    lines = output.strip().split('\n')
    assert len(lines) >= 2, f"Expected at least 2 lines of output, got {len(lines)}"
    
    # The last line should be the summary, the second to last should be wc output
    wc_output_line = lines[-2]
    wc_output_parts = wc_output_line.split()
    assert len(wc_output_parts) == 3, f"Expected `wc` to output 3 numbers, got {len(wc_output_parts)}"
    assert all(part.isdigit() for part in wc_output_parts), f"Expected `wc` output to be numbers, got {wc_output_parts}"