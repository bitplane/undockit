"""
Binary deployment for undockit - installs the undockit zipapp to target directory
"""

import zipapp
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import undockit


# --- Pure Logic Functions (testable) ---


def get_installed_version(binary_path: Path) -> Optional[str]:
    """Get version of installed undockit binary, or None if not installed"""
    if not binary_path.exists():
        return None

    # Try to execute it and get version
    try:
        result = subprocess.run([str(binary_path), "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            # Parse "undockit X.Y.Z" from output
            output = result.stdout.strip()
            if output.startswith("undockit "):
                return output.split(" ", 1)[1]
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass

    return None


def needs_update(binary_path: Path, current_version: str) -> bool:
    """Check if binary needs updating based on version"""
    installed = get_installed_version(binary_path)
    if installed is None:
        return True  # Not installed

    # Simple version comparison - could be made more sophisticated
    return installed != current_version


def create_zipapp(
    source_dir: Path,
    output_path: Path,
    main_module: str = "undockit.main:main",
    python_shebang: str = "/usr/bin/env python3",
) -> None:
    """Create a zipapp from source directory

    Args:
        source_dir: Directory containing the package source
        output_path: Where to write the zipapp
        main_module: Entry point in module:function format
        python_shebang: Shebang line for the zipapp
    """
    from . import __version__

    # Create a temporary directory for the zipapp contents
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Copy the package to the temp directory
        pkg_name = source_dir.name
        shutil.copytree(source_dir, tmp_path / pkg_name)

        # Overwrite __version__.py with hardcoded version
        version_file = tmp_path / pkg_name / "__version__.py"
        version_file.write_text(f'__version__ = "{__version__}"\n')

        # Create __main__.py
        main_content = f"""#!/usr/bin/env python3
import sys
from {main_module.replace(':', ' import ')}

if __name__ == '__main__':
    sys.exit(main())
"""
        (tmp_path / "__main__.py").write_text(main_content)

        # Create the zipapp
        zipapp.create_archive(
            source=tmp_path,
            target=output_path,
            interpreter=python_shebang,
            main=None,  # We already have __main__.py
            compressed=True,
        )

        # Make executable
        output_path.chmod(0o755)


def find_package_source() -> Path:
    """Find the source directory of the undockit package"""
    module_file = Path(undockit.__file__)

    # Should be something like .../src/undockit/__init__.py
    # We want .../src/undockit
    return module_file.parent


# --- System Interface Functions ---


def ensure_binary(target_dir: Path, binary_name: str = "undockit", force: bool = False) -> Optional[Path]:
    """Ensure undockit binary is deployed to target directory

    Args:
        target_dir: Directory to install binary to
        binary_name: Name for the binary (default: undockit)
        force: Force reinstall even if up to date

    Returns:
        Path to installed binary, or None if skipped
    """
    from . import __version__

    binary_path = target_dir / binary_name

    # Check if update needed
    if not force and not needs_update(binary_path, __version__):
        return None  # Already up to date

    # Find source directory
    source_dir = find_package_source()

    # Create zipapp in temp location
    with tempfile.NamedTemporaryFile(suffix=".pyz", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        create_zipapp(source_dir, tmp_path)

        # Move to final location
        shutil.move(str(tmp_path), str(binary_path))
        binary_path.chmod(0o755)

        return binary_path
    finally:
        # Clean up temp file if it still exists
        if tmp_path.exists():
            tmp_path.unlink()
