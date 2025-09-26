"""
Argument handling for undockit, including shebang argument parsing.
"""

import sys
import shlex


def get_args(args=sys.argv):
    """
    Handle shebang argument smooshing for 'run' subcommand.

    When a shebang line like:
        #!/usr/bin/env undockit run --timeout=300 --no-gpu

    is executed, the kernel passes arguments as:
        ["undockit", "run --timeout=300 --no-gpu", "script.df"]

    This function detects and fixes that case by splitting the smooshed
    arguments using shlex.split().

    Args:
        args: List of arguments (defaults to sys.argv)

    Returns:
        List of properly split arguments

    Examples:
        >>> get_args(["undockit", "run --timeout=300", "script.df"])
        ["undockit", "run", "--timeout=300", "script.df"]

        >>> get_args(["undockit", "install", "some/image"])
        ["undockit", "install", "some/image"]
    """
    # Make a copy to avoid mutating the original
    result = args[:]

    # Only handle the specific case: shebang with 'run ...' smooshed
    if len(result) == 3 and result[1].startswith("run "):
        try:
            # Split "run --timeout=300 --no-gpu" -> ["run", "--timeout=300", "--no-gpu"]
            split_args = shlex.split(result[1])
            # Reconstruct: [script, "run", "--timeout=300", "--no-gpu", dockerfile]
            result = [result[0]] + split_args + [result[2]]
        except ValueError:
            # shlex failed (e.g., unmatched quotes), leave as-is
            pass

    return result
