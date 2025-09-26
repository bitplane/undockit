"""
Podman backend implementation
"""

import json
import subprocess
import tempfile
from pathlib import Path

from .base import Backend


class PodmanBackend(Backend):
    """Backend implementation using Podman"""

    def build(self, dockerfile_path: Path) -> str:
        """Build image from dockerfile using podman build"""
        if not dockerfile_path.exists():
            raise RuntimeError(f"Dockerfile not found: {dockerfile_path}")

        # Use empty context - don't include random files from dockerfile directory
        with tempfile.TemporaryDirectory() as empty_context:
            # Run podman build with empty context
            cmd = ["podman", "build", "-f", str(dockerfile_path), empty_context]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Build failed: {e.stderr}") from e

            # Return the last line which should be the image ID
            output_lines = result.stdout.strip().split("\n")
            if output_lines:
                return output_lines[-1].strip()

            raise RuntimeError("No output from build command")

    def command(self, image_id: str) -> list[str]:
        """Extract default command from image using podman inspect"""
        # Get entrypoint - fail hard on any error
        entrypoint_result = subprocess.run(
            ["podman", "inspect", image_id, "--format", "{{json .Config.Entrypoint}}"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Get cmd - fail hard on any error
        cmd_result = subprocess.run(
            ["podman", "inspect", image_id, "--format", "{{json .Config.Cmd}}"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Parse JSON - fail hard on malformed JSON
        entrypoint = json.loads(entrypoint_result.stdout.strip())
        cmd = json.loads(cmd_result.stdout.strip())

        # Combine per Docker semantics
        return (entrypoint or []) + (cmd or [])

    def start(self, container_name: str, image_id: str) -> None:
        """Start a warm container - placeholder"""
        # TODO: Implement container starting
        pass

    def stop(self, container_name: str) -> None:
        """Stop a container - placeholder"""
        # TODO: Implement container stopping
        pass

    def is_running(self, container_name: str) -> bool:
        """Check if container is running - placeholder"""
        # TODO: Implement container status check
        return False

    def exec(self, container_name: str, script_path: str) -> int:
        """Execute script in container - placeholder"""
        # TODO: Implement container exec
        return 0
