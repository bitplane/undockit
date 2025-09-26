"""
Tests for install.py functions
"""

from pathlib import Path
import pytest
from undockit.install import extract_name, make_dockerfile, resolve_target_path


def test_extract_name_simple():
    """Test extracting name from simple image"""
    assert extract_name("spleeter") == "spleeter"


def test_extract_name_with_org():
    """Test extracting name from org/image"""
    assert extract_name("deezer/spleeter") == "spleeter"


def test_extract_name_with_tag():
    """Test extracting name from image:tag"""
    assert extract_name("deezer/spleeter:latest") == "spleeter"
    assert extract_name("spleeter:v1.2.3") == "spleeter"


def test_extract_name_complex():
    """Test extracting name from complex paths"""
    assert extract_name("ghcr.io/org/repo:tag") == "repo"
    assert extract_name("localhost:5000/my-app:dev") == "my-app"


def test_make_dockerfile_default():
    """Test dockerfile generation with defaults"""
    result = make_dockerfile("alpine")
    assert result.startswith("#!/usr/bin/env -S undockit run --timeout=600\n")
    assert "FROM alpine" in result


def test_make_dockerfile_custom_timeout():
    """Test dockerfile generation with custom timeout"""
    result = make_dockerfile("alpine", timeout=300)
    assert "--timeout=300" in result


def test_make_dockerfile_no_gpu():
    """Test dockerfile generation with GPU disabled"""
    result = make_dockerfile("alpine", no_gpu=True)
    assert "--no-gpu" in result
    assert "--timeout=600" in result  # Still includes timeout


def test_make_dockerfile_all_options():
    """Test dockerfile generation with all options"""
    result = make_dockerfile("nvidia/cuda", timeout=900, no_gpu=True)
    assert "#!/usr/bin/env -S undockit run --timeout=900 --no-gpu" in result
    assert "FROM nvidia/cuda" in result


def test_resolve_target_path_prefix_override():
    """Test that explicit prefix overrides everything"""
    path = resolve_target_path(to="user", env={}, sys_prefix="/usr", base_prefix="/usr", prefix=Path("/custom"))
    assert path == Path("/custom/bin")


def test_resolve_target_path_user_with_prefix_env():
    """Test user target with PREFIX environment variable"""
    path = resolve_target_path(
        to="user",
        env={"PREFIX": "/opt/tools"},
        sys_prefix="/usr",
        base_prefix="/usr",
    )
    assert path == Path("/opt/tools/bin")


def test_resolve_target_path_user_with_xdg():
    """Test user target with XDG_BIN_HOME"""
    path = resolve_target_path(
        to="user",
        env={"XDG_BIN_HOME": "/home/user/mybin"},
        sys_prefix="/usr",
        base_prefix="/usr",
    )
    assert path == Path("/home/user/mybin")


def test_resolve_target_path_user_default():
    """Test user target with no env vars uses ~/.local/bin"""
    path = resolve_target_path(
        to="user",
        env={},
        sys_prefix="/usr",
        base_prefix="/usr",
    )
    assert path == Path.home() / ".local" / "bin"


def test_resolve_target_path_env_venv():
    """Test env target in a virtual environment"""
    path = resolve_target_path(
        to="env",
        env={},
        sys_prefix="/home/user/project/.venv",
        base_prefix="/usr",
    )
    assert path == Path("/home/user/project/.venv/bin")


def test_resolve_target_path_env_conda():
    """Test env target in a conda environment"""
    path = resolve_target_path(
        to="env",
        env={"CONDA_PREFIX": "/opt/conda/envs/myenv"},
        sys_prefix="/usr",
        base_prefix="/usr",
    )
    assert path == Path("/opt/conda/envs/myenv/bin")


def test_resolve_target_path_env_no_env():
    """Test env target with no active environment raises error"""
    with pytest.raises(ValueError, match="No active environment"):
        resolve_target_path(
            to="env",
            env={},
            sys_prefix="/usr",
            base_prefix="/usr",
        )


def test_resolve_target_path_invalid_target():
    """Test invalid target raises error"""
    with pytest.raises(ValueError, match="Invalid target"):
        resolve_target_path(
            to="invalid",
            env={},
            sys_prefix="/usr",
            base_prefix="/usr",
        )
