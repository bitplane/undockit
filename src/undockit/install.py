"""
Tool installation functionality for undockit
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict


# --- Pure Logic Functions (testable) ---


def resolve_target_path(
    to: str, env: Dict[str, str], sys_prefix: str, base_prefix: str, prefix: Optional[Path] = None
) -> Path:
    """Return the directory where tool should be installed (pure logic)"""
    if prefix:
        return prefix / "bin"

    # Get PREFIX from environment if set
    env_prefix = env.get("PREFIX")

    if to == "env":
        # Install to current environment (venv/conda/etc)
        if sys_prefix != base_prefix:
            # Standard venv/virtualenv
            return Path(sys_prefix) / "bin"
        elif conda_prefix := env.get("CONDA_PREFIX"):
            # Conda environment
            return Path(conda_prefix) / "bin"
        else:
            raise ValueError("No active environment found (use --to=user instead)")

    elif to == "user":
        # User-local installation
        if env_prefix:
            return Path(env_prefix) / "bin"
        else:
            # XDG spec with fallback
            xdg_bin = env.get("XDG_BIN_HOME")
            return Path(xdg_bin) if xdg_bin else Path.home() / ".local" / "bin"

    elif to == "sys":
        # System-wide installation
        if env_prefix:
            return Path(env_prefix) / "bin"
        else:
            # Try /usr/local/bin first, fall back to /usr/bin
            for path in [Path("/usr/local/bin"), Path("/usr/bin")]:
                if path.exists() and os.access(path, os.W_OK):
                    return path
            raise PermissionError("No writable system directory found")

    else:
        raise ValueError(f"Invalid target: {to}")


def extract_name(image: str) -> str:
    """Extract tool name from image string"""
    # Handle registry URLs with ports (localhost:5000/image)
    # vs image tags (image:tag)
    # If there's a slash after the colon, it's a registry URL
    if ":" in image and "/" in image:
        colon_idx = image.index(":")
        slash_idx = image.index("/")
        if colon_idx < slash_idx:
            # It's a registry URL like localhost:5000/my-app:tag
            # Remove everything up to the last slash
            image = image.split("/")[-1]

    # Remove tag if present: spleeter:latest -> spleeter
    if ":" in image:
        image = image.rsplit(":", 1)[0]

    # Get the last part: deezer/spleeter -> spleeter
    if "/" in image:
        return image.split("/")[-1]

    return image


def make_dockerfile(image: str, timeout: int = 600) -> str:
    """Generate wrapper dockerfile with shebang"""
    # Build shebang arguments
    args = ["undockit", "run"]

    # Always include timeout for visibility
    args.append(f"--timeout={timeout}")

    shebang = f"#!/usr/bin/env -S {' '.join(args)}"

    return f"""{shebang}
FROM {image}
# Wrapper dockerfile created by undockit
"""


# --- System Interface Functions ---


def resolve_target(to: str = "user", prefix: Optional[Path] = None) -> Path:
    """Wrapper that calls resolve_target_path with actual system values"""
    return resolve_target_path(to=to, env=os.environ, sys_prefix=sys.prefix, base_prefix=sys.base_prefix, prefix=prefix)


def install(
    image: str,
    to: str = "user",
    name: Optional[str] = None,
    prefix: Optional[Path] = None,
    timeout: int = 600,
    no_undockit: bool = False,
) -> Path:
    """Install tool to target directory"""
    # Resolve target directory
    target_dir = resolve_target(to, prefix)
    target_dir.mkdir(parents=True, exist_ok=True)

    # Get tool name
    tool_name = name if name else extract_name(image)
    tool_path = target_dir / tool_name

    # Generate dockerfile content
    dockerfile_content = make_dockerfile(image, timeout=timeout)

    # Write file
    tool_path.write_text(dockerfile_content)

    # Make executable
    tool_path.chmod(0o755)

    return tool_path
