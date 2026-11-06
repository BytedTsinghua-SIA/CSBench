#!/usr/bin/env python3
"""Execute a command with variables loaded from a dotenv file."""

from __future__ import annotations

import argparse
import os

from dotenv import dotenv_values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not args.command:
        parser.error("a command is required")
    environment = os.environ.copy()
    for key, value in dotenv_values(args.env_file).items():
        if value is not None:
            environment[key] = value
    environment["CSBENCH_ENV_LOADED"] = "1"
    os.execvpe(args.command[0], args.command, environment)


if __name__ == "__main__":
    main()
