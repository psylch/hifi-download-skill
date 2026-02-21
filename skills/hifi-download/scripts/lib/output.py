"""Shared output utilities for MusicMaster scripts.

Provides standard JSON output helpers following the skill runtime best practices:
- ok(): structured JSON to stdout with optional hint
- fail(): JSON error to stderr with error/hint/recoverable, exits 1 or 2
"""

import json
import sys


def ok(data: dict, hint: str = "") -> None:
    """Print structured JSON result to stdout."""
    if hint:
        data["hint"] = hint
    print(json.dumps(data, ensure_ascii=False, indent=2))


def fail(error: str, hint: str = "", recoverable: bool = True) -> None:
    """Print JSON error to stderr and exit."""
    msg = {"error": error}
    if hint:
        msg["hint"] = hint
    msg["recoverable"] = recoverable
    print(json.dumps(msg, ensure_ascii=False), file=sys.stderr)
    sys.exit(1 if recoverable else 2)
