"""
Backend system for undockit - manages container runtimes
"""

import shutil
from .base import Backend
from .podman import PodmanBackend


def get_backend() -> Backend:
    """Auto-detect and return the best available backend"""
    # Check for podman first (preferred)
    if shutil.which("podman"):
        return PodmanBackend()

    # TODO: Add docker backend detection
    # if shutil.which("docker"):
    #     return DockerBackend()

    raise RuntimeError("No supported container backend found. Please install podman.")
