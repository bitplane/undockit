"""
Tests for deploy module
"""

import zipfile
import subprocess


from undockit.deploy import (
    needs_update,
    create_zipapp,
    find_package_source,
)


def test_needs_update_not_installed(tmp_path):
    """Non-existent binary needs update"""
    binary_path = tmp_path / "undockit"
    assert needs_update(binary_path, "1.0.0") is True


def test_needs_update_same_version(tmp_path):
    """Same version doesn't need update"""
    # Create a fake binary that outputs version
    binary_path = tmp_path / "undockit"
    binary_path.write_text("#!/bin/sh\necho 'undockit 1.0.0'")
    binary_path.chmod(0o755)

    assert needs_update(binary_path, "1.0.0") is False


def test_needs_update_different_version(tmp_path):
    """Different version needs update"""
    # Create a fake binary that outputs different version
    binary_path = tmp_path / "undockit"
    binary_path.write_text("#!/bin/sh\necho 'undockit 0.9.0'")
    binary_path.chmod(0o755)

    assert needs_update(binary_path, "1.0.0") is True


def test_needs_update_broken_binary(tmp_path):
    """Broken binary needs update"""
    binary_path = tmp_path / "undockit"
    binary_path.write_text("#!/bin/sh\nexit 1")
    binary_path.chmod(0o755)

    assert needs_update(binary_path, "1.0.0") is True


def test_create_zipapp_basic(tmp_path):
    """Creates a valid zipapp"""
    # Create a fake package
    source_dir = tmp_path / "mypackage"
    source_dir.mkdir()
    (source_dir / "__init__.py").write_text("__version__ = '1.0.0'")
    (source_dir / "main.py").write_text("""
def main():
    print("Hello from mypackage")
    return 0
""")

    output_path = tmp_path / "myapp.pyz"
    create_zipapp(source_dir=source_dir, output_path=output_path, main_module="mypackage.main:main")

    # Verify the zipapp was created
    assert output_path.exists()
    assert output_path.stat().st_mode & 0o755 == 0o755

    # Check it's a valid zip
    assert zipfile.is_zipfile(output_path)

    # Check contents
    with zipfile.ZipFile(output_path, "r") as zf:
        files = zf.namelist()
        assert "__main__.py" in files
        assert "mypackage/__init__.py" in files
        assert "mypackage/main.py" in files

    # Verify it's executable (basic test)
    result = subprocess.run([str(output_path)], capture_output=True, text=True)
    assert result.stdout.strip() == "Hello from mypackage"
    assert result.returncode == 0


def test_create_zipapp_custom_shebang(tmp_path):
    """Uses custom shebang"""
    source_dir = tmp_path / "mypackage"
    source_dir.mkdir()
    (source_dir / "__init__.py").write_text("")
    (source_dir / "main.py").write_text("def main(): return 0")

    output_path = tmp_path / "myapp.pyz"
    create_zipapp(
        source_dir=source_dir,
        output_path=output_path,
        main_module="mypackage.main:main",
        python_shebang="/usr/bin/python3",
    )

    # Read and verify the shebang
    with open(output_path, "rb") as f:
        first_line = f.readline().decode("utf-8")
        assert first_line.startswith("#!/usr/bin/python3")


def test_find_package_source():
    """Finds the undockit source directory"""
    source = find_package_source()
    assert source.name == "undockit"
    assert (source / "__init__.py").exists()
    # Should also have our main modules
    assert (source / "main.py").exists()
    assert (source / "install.py").exists()
    assert (source / "deploy.py").exists()


def test_create_zipapp_with_subdirectories(tmp_path):
    """Creates zipapp with nested package structure"""
    # Create a package with subdirectories
    source_dir = tmp_path / "mypackage"
    source_dir.mkdir()
    (source_dir / "__init__.py").write_text("")

    subdir = source_dir / "submodule"
    subdir.mkdir()
    (subdir / "__init__.py").write_text("")
    (subdir / "worker.py").write_text("def work(): return 'working'")

    (source_dir / "main.py").write_text("""
from mypackage.submodule.worker import work
def main():
    print(work())
    return 0
""")

    output_path = tmp_path / "myapp.pyz"
    create_zipapp(source_dir=source_dir, output_path=output_path, main_module="mypackage.main:main")

    # Verify nested structure is preserved
    with zipfile.ZipFile(output_path, "r") as zf:
        files = zf.namelist()
        assert "mypackage/submodule/__init__.py" in files
        assert "mypackage/submodule/worker.py" in files

    # Verify it works
    result = subprocess.run([str(output_path)], capture_output=True, text=True)
    assert result.stdout.strip() == "working"
    assert result.returncode == 0
