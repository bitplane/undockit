"""
Main entry point for undockit CLI
"""

import sys
from undockit.args import get_parser
from undockit.install import install, resolve_target
from undockit import deploy


def main():
    """Main entry point for undockit CLI"""
    parser = get_parser()
    parsed = parser.parse_args()

    if parsed.command == "install":
        try:
            tool_path = install(
                image=parsed.image,
                to=parsed.to,
                name=parsed.name,
                prefix=parsed.prefix,
                timeout=parsed.timeout,
                no_undockit=parsed.no_undockit,
            )
            print(f"Installed {parsed.image} as {tool_path}")

            # Deploy undockit binary unless disabled
            if not parsed.no_undockit:
                target_dir = resolve_target(parsed.to, parsed.prefix)
                deployed = deploy.ensure_binary(target_dir)
                if deployed:
                    print(f"Deployed undockit binary to {deployed}")

            return 0
        except (ValueError, PermissionError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    else:
        # No command given, show help
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
