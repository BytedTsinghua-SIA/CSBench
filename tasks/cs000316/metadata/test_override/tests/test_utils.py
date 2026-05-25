import subprocess
import os
import tempfile
import signal
import time
from typing import List, Optional, Tuple


class ProgramRunner:
    """Utility class for running and testing satellite control programs"""

    def __init__(self, program_path: str):
        # Normalize the path first
        program_path = os.path.normpath(program_path)

        # Check if we're in Docker environment
        if os.path.exists('/testbed'):
            # In Docker, if path is absolute and starts with /testbed, use as-is
            if os.path.isabs(program_path) and program_path.startswith('/testbed/'):
                self.program_path = program_path
            else:
                # Assume it's a relative path from tests directory
                self.program_path = os.path.join('/testbed', os.path.basename(program_path))
        else:
            # Local development
            self.program_path = program_path
        self.timeout = 30  # seconds

    def run_with_input(self, input_args: List[str]) -> Tuple[int, str, str]:
        """
        Run program with given arguments and return (exit_code, stdout, stderr)

        Args:
            input_args: List of command line arguments

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        try:
            cmd = [self.program_path] + input_args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Process timed out"
        except FileNotFoundError:
            return -2, "", "Program not found"

    def run_with_stdin(self, input_args: List[str], stdin_data: str) -> Tuple[int, str, str]:
        """
        Run program with stdin input

        Args:
            input_args: Command line arguments
            stdin_data: Data to send to stdin

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        try:
            cmd = [self.program_path] + input_args
            result = subprocess.run(
                cmd,
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Process timed out"


class MockSatelliteSystem:
    """Mock satellite system for testing"""

    def __init__(self):
        self.commands_sent = []
        self.system_status = "nominal"

    def send_command(self, command: str) -> bool:
        """Send command to satellite system"""
        self.commands_sent.append(command)
        if command == "launch":
            self.system_status = "launched"
        elif command == "shutdown":
            self.system_status = "shutdown"
        return True

    def get_status(self) -> str:
        """Get current satellite system status"""
        return self.system_status

    def reset(self):
        """Reset mock system to initial state"""
        self.commands_sent.clear()
        self.system_status = "nominal"
