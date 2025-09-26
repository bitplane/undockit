"""
Abstract base class for container backends
"""

from abc import ABC, abstractmethod
from pathlib import Path


class Backend(ABC):
    """Abstract base class for container runtime backends"""

    @abstractmethod
    def build(self, dockerfile_path: Path) -> str:
        """Build image from dockerfile and return image ID

        Args:
            dockerfile_path: Path to the dockerfile to build

        Returns:
            Image ID/hash that can be used to reference the built image

        Raises:
            RuntimeError: If build fails
        """
        pass

    @abstractmethod
    def command(self, image_id: str) -> list[str]:
        """Extract default command from image

        Args:
            image_id: Image ID returned from build()

        Returns:
            List of command arguments (ENTRYPOINT + CMD combined)
        """
        pass

    @abstractmethod
    def start(self, container_name: str, image_id: str, timeout: int = 600) -> None:
        """Start a warm container

        Args:
            container_name: Unique name for the container
            image_id: Image ID to run
            timeout: Seconds of inactivity before container shuts down
        """
        pass

    @abstractmethod
    def stop(self, container_name: str) -> None:
        """Stop and remove a container

        Args:
            container_name: Name of container to stop
        """
        pass

    @abstractmethod
    def is_running(self, container_name: str) -> bool:
        """Check if a container is currently running

        Args:
            container_name: Name of container to check

        Returns:
            True if container is running, False otherwise
        """
        pass

    @abstractmethod
    def exec(self, container_name: str, argv: list[str]) -> int:
        """Execute a command in the container

        Args:
            container_name: Name of running container
            argv: Command and arguments to execute

        Returns:
            Exit code from the executed command
        """
        pass

    @abstractmethod
    def name(self, image_id: str) -> str:
        """Get container name for an image ID

        Args:
            image_id: Image ID returned from build()

        Returns:
            Container name to use for this image
        """
        pass
