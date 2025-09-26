"""
Argument parsing for undockit CLI
"""

import argparse
from pathlib import Path

from . import __version__


def get_parser():
    """Create the argument parser for undockit"""
    parser = argparse.ArgumentParser(
        prog="undockit",
        description="Run Dockerfiles as first-class CLI tools",
    )

    parser.add_argument("--version", "-V", action="version", version=f"undockit {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # install command
    install = subparsers.add_parser("install", help="Install a Docker image as a CLI tool")
    install.add_argument("image", help="Image name (repo/name:tag)")
    install.add_argument("--name", help="Custom tool name (default: derived from image)")
    install.add_argument("--to", choices=["env", "user", "sys"], default="user", help="Installation target")
    install.add_argument("--prefix", type=Path, help="Override installation prefix")
    install.add_argument("--timeout", type=int, default=600, help="Container timeout in seconds")
    install.add_argument("--no-undockit", action="store_true", help="Skip deploying undockit binary to target")

    return parser
