"""
Argument parsing for undockit CLI
"""

import argparse
from pathlib import Path

from . import __version__


def add_install_parser(subparsers):
    """Add the install subcommand parser"""
    install = subparsers.add_parser("install", help="Install a Docker image as a CLI tool")
    install.add_argument("image", help="Image name (repo/name:tag)")
    install.add_argument("--name", help="Custom tool name (default: derived from image)")
    install.add_argument("--to", choices=["env", "user", "sys"], default="user", help="Installation target")
    install.add_argument("--prefix", type=Path, help="Override installation prefix")
    install.add_argument("--timeout", type=int, default=600, help="Container timeout in seconds")
    install.add_argument("--no-undockit", action="store_true", help="Skip deploying undockit binary to target")
    return install


def add_build_parser(subparsers):
    """Add the build subcommand parser"""
    build = subparsers.add_parser("build", help="Build a Dockerfile and return image ID")
    build.add_argument("dockerfile", type=Path, help="Path to Dockerfile to build")
    return build


def add_run_parser(subparsers):
    """Add the run subcommand parser"""
    run = subparsers.add_parser("run", help="Run a command in a Docker container")
    run.add_argument("--timeout", type=int, default=600, help="Container timeout in seconds")
    run.add_argument("dockerfile", type=Path, help="Path to Dockerfile to run")
    run.add_argument("args", nargs=argparse.REMAINDER, help="Arguments to pass to the image's default command")
    return run


def get_parser():
    """Create the argument parser for undockit"""
    parser = argparse.ArgumentParser(
        prog="undockit",
        description="Run Dockerfiles as first-class CLI tools",
    )

    parser.add_argument("--version", "-V", action="version", version=f"undockit {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add subcommands
    add_install_parser(subparsers)
    add_build_parser(subparsers)
    add_run_parser(subparsers)

    return parser
