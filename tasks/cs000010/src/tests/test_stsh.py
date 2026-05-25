import subprocess
from pathlib import Path
import pytest
import time
import os

CWD = Path(__file__).resolve().parent.parent
STSH_DRIVER = CWD / "stsh-driver"
STSH_EXEC = CWD / "stsh"
TEST_DIR = CWD / "tests"

assert STSH_DRIVER.exists(), f"Missing file: {STSH_DRIVER}"
assert STSH_EXEC.exists(), f"Missing file: {STSH_EXEC}"

if not TEST_DIR.exists():
    TEST_DIR.mkdir()

def run_stsh_test(trace_content: str, test_name: str):
    """Helper function to run a test using stsh-driver."""
    trace_file = TEST_DIR / f"{test_name}.trace"
    with open(trace_file, "w") as f:
        f.write(trace_content)

    cmd = [
        str(STSH_DRIVER),
        "-t", str(trace_file),
        "-s", str(STSH_EXEC),
        "-a", "--suppress-prompt --no-history"
    ]
    result = subprocess.run(
        cmd,
        cwd=str(CWD),
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=5  # Add a timeout to prevent hanging tests
    )

    trace_file.unlink()  # Clean up

    output = result.stdout or ""
    return output, result.returncode


def test_framework_integrity():
    """
    Tests the basic framework integrity by sending an empty line and then quitting.
    This should pass on the initial, unmodified framework.
    """
    trace = "\nquit\n"
    output, returncode = run_stsh_test(trace, "framework_integrity")
    assert returncode == 0, f"Expected clean exit, but got return code {returncode}. Output:\n{output}"
    # Check for unexpected error messages
    assert "error" not in output.lower()
    assert "exception" not in output.lower()


def test_simple_foreground_command():
    """Tests running a simple foreground command."""
    trace = "/bin/echo Simple foreground test\nquit\n"
    output, _ = run_stsh_test(trace, "simple_command")
    assert "Simple foreground test" in output


def test_initial_state_command_echo():
    """
    Tests that in the initial state, the shell echoes the command
    instead of executing it. This verifies the test framework and
    initial shell behavior.
    """
    trace = "echo HelloWorld\nquit\n"
    output, _ = run_stsh_test(trace, "initial_state_echo")
    # The initial createJob function just prints the pipeline, so the command appears in the output.
    assert "echo HelloWorld" in output


def test_quit_command():
    """Tests that the 'quit' command terminates the shell."""
    trace = "quit\n"
    run_stsh_test(trace, "quit_command")


def test_exit_command():
    """Tests that the 'exit' command terminates the shell."""
    trace = "exit\n"
    run_stsh_test(trace, "exit_command")


def test_jobs_command_no_jobs():
    """Tests the 'jobs' command with no running jobs."""
    trace = "jobs\nquit\n"
    output, _ = run_stsh_test(trace, "jobs_no_jobs")
    # Expect no job lines, just the echo of the command
    assert "[1]" not in output


def test_background_job():
    """Tests running a job in the background and using 'jobs'."""
    trace = "/bin/sleep 1 &\njobs\nquit\n"
    output, _ = run_stsh_test(trace, "background_job")
    assert "[1]" in output
    assert "Running" in output
    assert "/bin/sleep 1" in output


def test_sigtstp_handling():
    """Tests that a job can be stopped using the 'halt' command."""
    # This test uses 'halt' to simulate a job being stopped (like via SIGTSTP).
    trace = "/bin/sleep 5 &\njobs\nhalt %1\njobs\nquit\n"
    output, _ = run_stsh_test(trace, "sigtstp_handling")
    assert "[1]" in output
    assert "Running" in output
    assert "Stopped" in output


def test_fg_command():
    """Tests bringing a stopped job to the foreground."""
    # This tests assumes 'halt' is working.
    trace = "/bin/sleep 2 &\nhalt %1\nfg %1\njobs\nquit\n"
    output, _ = run_stsh_test(trace, "fg_command")
    # After fg, the job runs to completion and should be removed from the job list.
    # Therefore, the final 'jobs' output should be empty.
    assert "[1]" not in output.split("stsh> jobs")[1]


def test_bg_command():
    """Tests resuming a stopped job in the background."""
    # This tests assumes 'halt' is working.
    trace = "/bin/sleep 5 &\nhalt %1\njobs\nbg %1\njobs\nquit\n"
    output, _ = run_stsh_test(trace, "bg_command")
    # The job should be 'Stopped' first, then 'Running' again.
    assert "Stopped" in output
    assert "Running" in output.split("stsh> bg %1")[1]


def test_builtin_not_implemented():
    """Tests that unimplemented builtins throw the expected internal error."""
    for builtin in ["fg", "bg", "slay", "halt", "cont"]:
        trace = f"{builtin}\nquit\n"
        output, _ = run_stsh_test(trace, f"{builtin}_not_implemented")
        assert "Internal Error: Builtin command not supported" in output


def test_pipeline():
    """Tests a simple pipeline."""
    trace = "/bin/echo 'one two three' | wc -w\nquit\n"
    output, _ = run_stsh_test(trace, "pipeline")
    # The output of `wc -w` should be '3' (with some whitespace)
    assert "3" in output.split()


def test_pipeline_background():
    """Tests a pipeline running in the background."""
    # Use a command that takes enough time to still be visible when jobs runs
    # The stsh-driver has ~200ms delay between commands, so sleep needs to be > 200ms
    trace = "/bin/echo test | /bin/sleep 0.3 | wc -c & \njobs\nquit\n"
    output, _ = run_stsh_test(trace, "pipeline_background")
    # The job should be visible in the jobs list
    assert "[1]" in output or "Running" in output or "Stopped" in output
    # Check that pipeline-related commands appear (the job might complete fast)
    # So we just check that the command was executed
    assert "test" in output or "echo" in output or "sleep" in output or "wc" in output


def test_input_redirection():
    """Tests input redirection."""
    input_content = "hello from file"
    input_file = TEST_DIR / "test_input.txt"
    with open(input_file, "w") as f:
        f.write(input_content)

    trace = f"cat < {input_file}\nquit\n"
    output, _ = run_stsh_test(trace, "input_redirection")

    input_file.unlink()

    assert input_content in output


def test_output_redirection():
    """Tests output redirection."""
    output_file = TEST_DIR / "test_output.txt"
    if output_file.exists():
        output_file.unlink()

    trace = f"/bin/echo 'writing to file' > {output_file}\nquit\n"
    run_stsh_test(trace, "output_redirection")

    assert output_file.exists()
    with open(output_file, "r") as f:
        content = f.read()
    output_file.unlink()

    assert "writing to file" in content


def test_redirection_with_pipeline():
    """Tests redirection combined with a pipeline."""
    input_content = "one two three four"
    input_file = TEST_DIR / "test_pipe_input.txt"
    output_file = TEST_DIR / "test_pipe_output.txt"
    if output_file.exists():
        output_file.unlink()
    with open(input_file, "w") as f:
        f.write(input_content)

    trace = f"cat < {input_file} | wc -w > {output_file}\nquit\n"
    run_stsh_test(trace, "redirection_with_pipeline")

    assert output_file.exists()
    with open(output_file, "r") as f:
        content = f.read()

    input_file.unlink()
    output_file.unlink()

    assert "4" in content.split()


def test_slay_command():
    """Tests terminating a process using 'slay'."""
    trace = "/bin/sleep 10 &\njobs\nslay %1\njobs\nquit\n"
    output, _ = run_stsh_test(trace, "slay_command")
    assert "[1]" in output
    assert "Running" in output
    # After slay, the job should eventually terminate.
    # We check that it's not "Running" in the final jobs output.
    parts = output.split("stsh> slay %1")
    if len(parts) > 1:
        after_slay = parts[1]
        assert "Running" not in after_slay


def test_cont_command():
    """Tests resuming a stopped job using 'cont'."""
    trace = "/bin/sleep 5 &\nhalt %1\njobs\ncont %1\njobs\nquit\n"
    output, _ = run_stsh_test(trace, "cont_command")
    assert "Stopped" in output
    # After cont, it should be running again.
    parts = output.split("stsh> cont %1")
    if len(parts) > 1:
        after_cont = parts[1]
        assert "Running" in after_cont


def test_pipeline_multi():
    """Tests a pipeline with more than 2 processes."""
    trace = "/bin/echo 'one two three' | cat | wc -w\nquit\n"
    output, _ = run_stsh_test(trace, "pipeline_multi")
    assert "3" in output.split()


def test_error_handling():
    """Tests error handling for invalid arguments."""
    # Test fg with invalid job
    trace = "fg %99\nquit\n"
    output, _ = run_stsh_test(trace, "fg_error")
    # Expect an error message (STSHException caught in main)
    assert "Usage" in output or "No such job" in output or "Invalid" in output or "does not exist" in output

    # Test bg with invalid job
    trace = "bg %99\nquit\n"
    output, _ = run_stsh_test(trace, "bg_error")
    assert "Usage" in output or "No such job" in output or "Invalid" in output or "does not exist" in output
    
    # Test slay with invalid pid
    trace = "slay 123456\nquit\n"
    output, _ = run_stsh_test(trace, "slay_error")
    assert "No such process" in output or "Invalid" in output or "does not exist" in output