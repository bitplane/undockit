"""
Tests for undockit.args.get_args function
"""

from undockit.args import get_args


def test_normal_args_unchanged():
    """Normal arguments should pass through unchanged"""
    args = ["undockit", "install", "some/image"]
    result = get_args(args)
    assert result == args


def test_run_subcommand_unchanged():
    """Normal run subcommand should pass through unchanged"""
    args = ["undockit", "run", "dockerfile.df"]
    result = get_args(args)
    assert result == args


def test_shebang_run_basic():
    """Basic shebang run case should be split"""
    args = ["undockit", "run --timeout=300", "script.df"]
    result = get_args(args)
    expected = ["undockit", "run", "--timeout=300", "script.df"]
    assert result == expected


def test_shebang_run_multiple_flags():
    """Multiple flags in shebang should be split correctly"""
    args = ["undockit", "run --timeout=300 --no-gpu", "script.df"]
    result = get_args(args)
    expected = ["undockit", "run", "--timeout=300", "--no-gpu", "script.df"]
    assert result == expected


def test_shebang_run_with_values():
    """Flags with values should be handled correctly"""
    args = ["undockit", "run --timeout=600 --prefix=/opt", "script.df"]
    result = get_args(args)
    expected = ["undockit", "run", "--timeout=600", "--prefix=/opt", "script.df"]
    assert result == expected


def test_shebang_run_quoted_values():
    """Quoted values should be handled correctly"""
    args = ["undockit", 'run --env="PATH=/usr/bin" --timeout=300', "script.df"]
    result = get_args(args)
    expected = ["undockit", "run", "--env=PATH=/usr/bin", "--timeout=300", "script.df"]
    assert result == expected


def test_non_run_smooshed_unchanged():
    """Smooshed arguments that don't start with 'run ' should be unchanged"""
    args = ["undockit", "install --to=user some/image", "script.df"]
    result = get_args(args)
    assert result == args


def test_wrong_length_unchanged():
    """Arguments with wrong length should be unchanged"""
    # Too few args
    args = ["undockit", "run --timeout=300"]
    result = get_args(args)
    assert result == args

    # Too many args
    args = ["undockit", "run", "--timeout=300", "script.df", "extra"]
    result = get_args(args)
    assert result == args


def test_malformed_quotes_unchanged():
    """Malformed quotes should leave args unchanged"""
    args = ["undockit", 'run --env="unclosed quote', "script.df"]
    result = get_args(args)
    # Should be unchanged since shlex.split will fail
    assert result == args


def test_empty_run_args():
    """Just 'run' with no additional args should work"""
    args = ["undockit", "run", "script.df"]
    result = get_args(args)
    assert result == args


def test_run_with_spaces_in_filename():
    """Should handle filenames with spaces"""
    args = ["undockit", "run --timeout=300", "my script.df"]
    result = get_args(args)
    expected = ["undockit", "run", "--timeout=300", "my script.df"]
    assert result == expected


def test_original_args_not_mutated():
    """Original args list should not be modified"""
    original = ["undockit", "run --timeout=300", "script.df"]
    args_copy = original.copy()
    result = get_args(args_copy)

    # Original should be unchanged
    assert args_copy == original
    # But result should be different
    assert result != original
    assert result == ["undockit", "run", "--timeout=300", "script.df"]
