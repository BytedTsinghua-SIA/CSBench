# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: Apache-2.0
from typing import Tuple, Dict, Any
from pathlib import Path
from loguru import logger

class BaseRuntime:
    def __init__(self, image_name: str) -> None:
        self.image_name = image_name
        self.logger = logger
    
    #! === Base commands ===
    def start(self) -> None:
        # start a container
        raise NotImplementedError
    
    def stop(self) -> None:
        # stop the container
        raise NotImplementedError

    def execute(self, input: str, timeout: int | float = 30) -> Tuple[str, int]:
        """Executes a command.

        Args:
            input (str): command to execute
            timeout (int | float, optional): command timeout. Defaults to 30.

        Returns:
            Tuple[str, int]: output log of the command, exit code of the command.
        """
        raise NotImplementedError

    # File transfer between host and container
    def transfer_file(self, src: str | Path, dst: str | Path, to_container: bool = True) -> None:
        """Transfer a file between host and container.

        Args:
            src: source path (host if to_container=True, container if False)
            dst: destination path (container if to_container=True, host if False)
            to_container: direction flag; True to copy host->container, False for container->host
        """
        raise NotImplementedError

    def read_file(self, path: str | Path) -> str:
        """Read file content from container.

        Args:
            path: file path in the container

        Returns:
            str: file content exactly as stored
        """
        raise NotImplementedError

    def write_file(self, path: str | Path, content: str) -> None:
        """Write content to a file in the container.

        Args:
            path: file path in the container
            content: content to write (will be written exactly as provided)
        """
        raise NotImplementedError


class StatefulRuntime(BaseRuntime):
    # Interacting with the container.
    def __init__(self, image_name: str) -> None:
        super().__init__(image_name)
        self.screens: Dict[str, Any] = {}
    
    # Create screen
    def create_screen(self, screen_name: str) -> None:
        # Create a screen
        raise NotImplementedError
    
    # Stop screen
    def stop_screen(self, screen_name: str) -> None:
        # Stop the screen
        raise NotImplementedError
    
    # Capture screen
    def capture_screen(self, screen_name: str) -> str:
        # Capture the screen
        raise NotImplementedError
    
    # Send keys to screen
    def send_keys(self, screen_name: str, keys: str) -> None:
        # Send keys to the screen
        raise NotImplementedError
