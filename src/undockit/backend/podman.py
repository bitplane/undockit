"""
Podman backend implementation
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from .base import Backend


# Startup script template for containers
STARTUP_SCRIPT = """#!/bin/sh
# Create directories with image-specific namespace
mkdir -p /tmp/undockit/{image_name}/pid /tmp/undockit/{image_name}/bin

# Deploy exec script
cat > /tmp/undockit/{image_name}/exec << EXEC_EOF
#!/bin/sh
pidfile="/tmp/undockit/{image_name}/pid/\$$"
workdir="$1"
shift
touch "$pidfile"
cd "$workdir" || exit 1

# Set up XDG directories to use host filesystem
export HOME=/host/home/{host_user}
export XDG_CACHE_HOME=/host/home/{host_user}/.cache
export XDG_CONFIG_HOME=/host/home/{host_user}/.config
export XDG_DATA_HOME=/host/home/{host_user}/.local/share
export MODEL_PATH="$XDG_DATA_HOME/models"
mkdir -p "$XDG_CACHE_HOME" "$XDG_CONFIG_HOME" "$XDG_DATA_HOME" "$MODEL_PATH"

"$@"
exitcode=$?
rm -f "$pidfile"
exit $exitcode
EXEC_EOF
chmod +x /tmp/undockit/{image_name}/exec

# Wait loop with timeout
timeout_seconds={timeout}
while true; do
    count=$(ls /tmp/undockit/{image_name}/pid/ 2>/dev/null | wc -l)
    if [ "$count" -eq 0 ]; then
        mtime=$(stat -c %Y /tmp/undockit/{image_name}/pid/ 2>/dev/null || echo 0)
        now=$(date +%s)
        if [ $((now - mtime)) -gt $timeout_seconds ]; then
            exit 0  # Timeout reached, shut down
        fi
    fi
    sleep 30
done
"""


class PodmanBackend(Backend):
    def _get_gpu_flags(self) -> list[str]:
        """Detect and return appropriate GPU device flags"""
        flags = []

        # NVIDIA GPU support via Container Toolkit CDI
        if self._has_nvidia_cdi():
            flags.extend(["--device", "nvidia.com/gpu=all"])

        return flags

    def _has_nvidia_cdi(self) -> bool:
        """Check if NVIDIA CDI devices are available"""
        try:
            # Check if CDI config exists
            cdi_paths = ["/etc/cdi/nvidia.yaml", "/var/run/cdi/nvidia.yaml"]
            return any(os.path.exists(path) for path in cdi_paths)
        except Exception:
            return False

    def build(self, dockerfile_path: Path) -> str:
        """Build image from dockerfile using podman build"""
        if not dockerfile_path.exists():
            raise RuntimeError(f"Dockerfile not found: {dockerfile_path}")

        # Use empty context - don't include random files from dockerfile directory
        with tempfile.TemporaryDirectory() as empty_context:
            # Run podman build with empty context
            cmd = ["podman", "build", "-f", str(dockerfile_path), empty_context]

            # Build with real-time output
            result = subprocess.run(cmd, check=False)

            if result.returncode != 0:
                raise RuntimeError(f"Build failed with exit code {result.returncode}")

            # Get the most recently created image
            get_image_cmd = ["podman", "images", "--format", "{{.ID}}", "--sort", "created"]
            image_result = subprocess.run(get_image_cmd, capture_output=True, text=True, check=True)

            image_ids = image_result.stdout.strip().split("\n")
            if not image_ids or not image_ids[0]:
                raise RuntimeError("Could not determine image ID")

            return image_ids[0]  # Return the first (most recent) image ID

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

    def start(self, container_name: str, image_id: str, timeout: int = 600) -> None:
        """Start a warm container with host integration and timeout management"""
        # Get host username
        import getpass

        host_user = getpass.getuser()

        # Format the startup script with timeout value, container name, and host user
        startup_script = STARTUP_SCRIPT.format(timeout=timeout, image_name=container_name, host_user=host_user)

        cmd = [
            "podman",
            "run",
            "-d",  # detached
            "--replace",  # replace existing container with same name
            "--name",
            container_name,
            "--userns=keep-id",  # run as current user
            "--mount",
            "type=bind,source=/,target=/host",  # mount host filesystem
            "--mount",
            "type=bind,source=/tmp,target=/tmp",  # mount host /tmp
            "--entrypoint",
            "/bin/sh",  # use shell to run our script
        ]

        # Add GPU device flags
        cmd.extend(self._get_gpu_flags())

        cmd.extend(
            [
                image_id,
                "-c",
                startup_script,
            ]
        )

        subprocess.run(cmd, check=True)

    def stop(self, container_name: str) -> None:
        """Stop and remove container"""
        # Stop the container - fail hard if it doesn't exist
        subprocess.run(["podman", "stop", container_name], check=True)
        # Remove the container - fail hard if it doesn't exist
        subprocess.run(["podman", "rm", container_name], check=True)

    def is_running(self, container_name: str) -> bool:
        """Check if container is currently running"""
        try:
            result = subprocess.run(
                ["podman", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                check=True,
            )

            # If container name appears in running containers, it's running
            return container_name in result.stdout.strip().split("\n")
        except subprocess.CalledProcessError:
            # If podman command fails, assume not running
            return False

    def exec(self, container_name: str, argv: list[str]) -> int:
        """Execute command in container with proper workdir"""
        # Get current working directory and map to container path
        host_cwd = os.getcwd()
        container_workdir = f"/host{host_cwd}"

        # Build exec command - call our exec script with workdir and user command
        cmd = [
            "podman",
            "exec",
            "-i",  # interactive for stdin
        ]

        # Add TTY flag if stdin is a terminal
        if sys.stdin.isatty():
            cmd.append("-t")

        cmd.extend([container_name, f"/tmp/undockit/{container_name}/exec", container_workdir] + argv)

        # Run with full stdin/stdout/stderr passthrough
        result = subprocess.run(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, check=False)
        return result.returncode

    def name(self, image_id: str) -> str:
        """Get container name for an image ID"""
        return f"undockit-{os.getuid()}-{image_id[:12]}"
