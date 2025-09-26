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
    def start(self, container_name: str, image_id: str) -> None:
        """Start a warm container

        Args:
            container_name: Unique name for the container
            image_id: Image ID to run
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
    def exec(self, container_name: str, script_path: str) -> int:
        """Execute a script in the container

        Args:
            container_name: Name of running container
            script_path: Path to script file inside container

        Returns:
            Exit code from the executed script
        """
        pass
