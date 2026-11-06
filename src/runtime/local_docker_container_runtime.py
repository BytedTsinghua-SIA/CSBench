# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations


import os
import select
import shlex
import subprocess
import time
import uuid
import pty
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from pathlib import Path

from .base_runtime import BaseRuntime, StatefulRuntime


class LocalDockerContainerRuntime(StatefulRuntime):
    """Local Docker runtime with basic exec and interactive screen support.

    - start/stop/execute: thin wrappers over `docker run/stop/rm/exec`.
    - screens: implemented via `docker attach` bound to a PTY; supports sending keys and capturing output.
    """

    def __init__(self, image_name: str, container_name: Optional[str] = None) -> None:
        super().__init__(image_name)
        self.container_name = container_name or f"csbench-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        self.platform = "linux/amd64"

    # === BaseRuntime ===
    def start(self) -> None:
        cmd = [
            "docker",
            "run",
            "-d",
            "--platform",
            self.platform,
            "--name",
            self.container_name,
            self.image_name,
            "sleep",
            "infinity",
        ]
        self.logger.info(f"Starting container: {' '.join(shlex.quote(c) for c in cmd)}")
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)

    def stop(self) -> None:
        subprocess.run(["docker", "stop", self.container_name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        subprocess.run(["docker", "rm", self.container_name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.logger.info(f"Stopped and removed container: {self.container_name}")

    def execute(self, input: str, timeout: int | float = 30, use_tty: bool = False, interactive: bool = False) -> Tuple[str, int]:
        """Executes a command inside the container using `docker exec`.

        Returns (combined_output, return_code).
        """
        timeout = max(min(timeout, 3600), 10)
        exec_cmd = [
            "docker",
            "exec",
        ]
        if use_tty:
            exec_cmd.append("-t")
        if interactive:
            exec_cmd.append("-i")
        exec_cmd.extend([
            self.container_name,
            "bash",
            "-lc",
            input,
        ])
        self.logger.info(f"Exec: {input}")
        # proc = subprocess.run(exec_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=False, timeout=timeout)
        # return proc.stdout.decode("utf-8", errors="replace"), proc.returncode
        try:
            proc = subprocess.run(exec_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=False, timeout=timeout)
            return proc.stdout, proc.returncode
        except subprocess.TimeoutExpired:
            # 超时异常：命令执行时间超过了 timeout
            error_msg = f"Command timed out after {timeout} seconds"
            self.logger.warning(f"Exec timeout: {input} - {error_msg}")
            return error_msg.encode(), -1            

    def transfer_file(self, src: str | Path, dst: str | Path, to_container: bool = True) -> None:
        src_s = str(src)
        dst_s = str(dst)
        if to_container:
            subprocess.run(["docker", "cp", src_s, f"{self.container_name}:{dst_s}"], check=True)
            # Change ownership to student user (UID 1000) and set 777 permissions
            chown_cmd = f"sudo chown -R 1000:1000 {shlex.quote(dst_s)} && sudo chmod -R 777 {shlex.quote(dst_s)}"
            self.execute(chown_cmd, timeout=360, use_tty=False)
        else:
            subprocess.run(["docker", "cp", f"{self.container_name}:{src_s}", dst_s], check=True)

    def read_file(self, path: str | Path) -> str:
        """Read file content from container using docker cp.

        Copies the file from the container to a temp file on host,
        reads it with Python (preserving exact content), then cleans up.
        """
        import tempfile
        path_s = str(path)
        
        with tempfile.NamedTemporaryFile(mode='rb', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Copy file from container to host
            subprocess.run(
                ["docker", "cp", f"{self.container_name}:{path_s}", tmp_path],
                check=True,
                capture_output=True
            )
            # Read with Python - exact content preservation
            with open(tmp_path, 'r', encoding='utf-8', newline='') as f:
                return f.read()
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def write_file(self, path: str | Path, content: str) -> None:
        """Write content to a file in the container using shell command with shlex.

        Uses echo and shell redirection to write content directly to the file in container.
        """
        path_s = str(path)
        
        # Ensure parent directory exists in container
        dir_path = os.path.dirname(path_s)
        if dir_path:
            self.execute(f"mkdir -p {shlex.quote(dir_path)}", use_tty=False)
        
        # Use echo with proper escaping to write content to file
        escaped_content = shlex.quote(content)
        cmd = f"echo -n {escaped_content} > {shlex.quote(path_s)}"
        self.execute(cmd, use_tty=False)

    # === StatefulRuntime ===
    DETACH_BYTES = b"\x10\x11"  # Docker detach: CTRL-p, CTRL-q

    @dataclass
    class _ScreenSession:
        process: subprocess.Popen
        master_fd: int

    def create_screen(self, screen_name: str) -> None:
        if screen_name in self.screens:
            raise ValueError(f"Screen already exists: {screen_name}")
        master_fd, slave_fd = pty.openpty()
        proc = subprocess.Popen(
            [
                "docker",
                "attach",
                "--detach-keys",
                "ctrl-p,ctrl-q",
                self.container_name,
            ],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=subprocess.STDOUT,
            close_fds=True,
        )
        os.close(slave_fd)
        self.screens[screen_name] = LocalDockerContainerRuntime._ScreenSession(process=proc, master_fd=master_fd)
        # Give shell a brief moment to render prompt
        time.sleep(0.1)

    def stop_screen(self, screen_name: str) -> None:
        sess = self.screens.get(screen_name)
        if not sess:
            return
        try:
            os.write(sess.master_fd, LocalDockerContainerRuntime.DETACH_BYTES)
        except OSError:
            pass
        try:
            sess.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            sess.process.kill()
        try:
            os.close(sess.master_fd)
        except OSError:
            pass
        self.screens.pop(screen_name, None)

    def capture_screen(self, screen_name: str) -> str:
        time.sleep(0.1)
        sess = self.screens.get(screen_name)
        if not sess:
            raise ValueError(f"Screen not found: {screen_name}")
        data = self._read_available(sess.master_fd, timeout=0.2)
        return data.decode("utf-8", errors="replace")

    def send_keys(self, screen_name: str, keys: str) -> None:
        sess = self.screens.get(screen_name)
        if not sess:
            raise ValueError(f"Screen not found: {screen_name}")
        payload = self._encode_keys(keys)
        if payload:
            os.write(sess.master_fd, payload)
        # Allow shell to process
        time.sleep(0.05)

    # === Helpers ===
    @staticmethod
    def _encode_keys(keys: str) -> bytes:
        # Handle custom key sequence format
        # Supported formats:
        # - [enter] or [return] for carriage return
        # - [ctrl-c] or [^c] for Ctrl+C
        # - [ctrl-d] or [^d] for Ctrl+D
        # - [tab] for tab key
        # - [space] for space key
        # - [esc] for escape key
        # - [[ for literal [
        # - ]] for literal ]
        # - Plain text for regular characters
        
        # If the entire string is a single special key name (legacy support)
        low = keys.lower()
        if low in {"enter", "return"}:
            return b"\r"
        if low in {"ctrl-c", "^c"}:
            return b"\x03"
        if low in {"ctrl-d", "^d"}:
            return b"\x04"
        
        # Process custom format with brackets
        result = bytearray()
        i = 0
        while i < len(keys):
            # Handle escape sequences for literal brackets
            if keys[i:i+2] == '[[':
                result.extend(b'[')
                i += 2
                continue
            if keys[i:i+2] == ']]':
                result.extend(b']')
                i += 2
                continue
            
            # Handle special key sequences
            if keys[i] == '[' and ']' in keys[i:]:
                # Find the closing bracket
                end = keys.find(']', i)
                if end != -1:
                    # Extract the key name
                    key_name = keys[i+1:end].lower()
                    # Handle special keys
                    if key_name in {"enter", "return"}:
                        result.extend(b"\r")
                    elif key_name in {"ctrl-c", "^c"}:
                        result.extend(b"\x03")
                    elif key_name in {"ctrl-d", "^d"}:
                        result.extend(b"\x04")
                    elif key_name == "tab":
                        result.extend(b"\t")
                    elif key_name == "space":
                        result.extend(b" ")
                    elif key_name == "esc":
                        result.extend(b"\x1b")
                    else:
                        # If not a recognized special key, treat as literal text
                        result.extend(keys[i:end+1].encode("utf-8"))
                    i = end + 1
                    continue
            
            # Handle regular characters
            result.extend(keys[i].encode("utf-8"))
            i += 1
        
        # Replace any remaining literal \n with carriage returns for compatibility
        return bytes(result).replace(b'\n', b'\r')

    @staticmethod
    def _read_available(master_fd: int, timeout: float) -> bytes:
        chunks: list[bytes] = []
        end_time = time.time() + max(0.0, timeout)
        while True:
            remaining = end_time - time.time()
            if remaining <= 0:
                break
            r, _, _ = select.select([master_fd], [], [], remaining)
            if not r:
                break
            try:
                data = os.read(master_fd, 4096)
            except OSError:
                break
            if not data:
                break
            chunks.append(data)
            # Drain quickly if more data is ready
            r2, _, _ = select.select([master_fd], [], [], 0)
            if not r2:
                continue
        return b"".join(chunks)


if __name__ == "__main__":
    from src.config import get_default_image_name

    # Example 1: BaseRuntime usage
    image = get_default_image_name("cmu-cs-ics-attack-lab-phase1")
    rt = LocalDockerContainerRuntime(image)
    print("[Example 1] Starting container and running bash test.sh …")
    rt.start()
    try:
        out, code = rt.execute("bash test.sh", timeout=120)
        print("--- output ---\n" + out + "\n---------------")
        print(f"exit code: {code}")
    finally:
        print("[Example 1] Stopping container …")
        rt.stop()

    # Example 2: StatefulRuntime usage (interactive gdb driving)
    rt2 = LocalDockerContainerRuntime(image)
    print("\n[Example 2] Starting container for interactive session …")
    rt2.start()
    try:
        screen = "s1"
        rt2.create_screen(screen)

        # Start gdb
        rt2.send_keys(screen, "gdb")
        rt2.send_keys(screen, "enter")
        print("[screen] after gdb:\n" + rt2.capture_screen(screen))

        # Run ./ctarget
        rt2.send_keys(screen, "./ctarget")
        rt2.send_keys(screen, "enter")
        print("[screen] after ./ctarget enter:\n" + rt2.capture_screen(screen))

        # 'r' several times (with ENTER), capture between steps
        for _ in range(3):
            rt2.send_keys(screen, "r")
            rt2.send_keys(screen, "enter")
            print("[screen] after r:\n" + rt2.capture_screen(screen))

        # Continue program
        rt2.send_keys(screen, "c")
        rt2.send_keys(screen, "enter")
        print("[screen] after c:\n" + rt2.capture_screen(screen))

        # Exit gdb with Ctrl-D
        rt2.send_keys(screen, "ctrl-d")
        time.sleep(0.1)
        print("[screen] after ctrl-d:\n" + rt2.capture_screen(screen))

        rt2.stop_screen(screen)
    finally:
        print("[Example 2] Stopping container …")
        rt2.stop()
