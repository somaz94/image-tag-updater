"""Logging utilities for image tag updater."""
import sys
from typing import NoReturn


class ActionError(RuntimeError):
    """Error raised for fatal action failures instead of calling sys.exit()."""
    pass


class Logger:
    """Simple logger with debug support."""

    def __init__(self, debug: bool = False):
        self.debug_mode = debug

    def print_header(self, message: str) -> None:
        """Print section header."""
        print(f"\n{'=' * 42}")
        print(f">> {message}")
        print(f"{'=' * 42}\n")

    def debug(self, message: str) -> None:
        """Print debug message."""
        if self.debug_mode:
            print(message)

    def info(self, message: str) -> None:
        """Print info message."""
        print(message)

    def success(self, message: str) -> None:
        """Print success message."""
        print(f"[O] {message}")

    def warning(self, message: str) -> None:
        """Print warning message."""
        print(f"[!] {message}")

    def error(self, message: str) -> NoReturn:
        """Print error message and raise ActionError."""
        print(f"[X] Error: {message}", file=sys.stderr)
        raise ActionError(message)
