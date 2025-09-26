"""
Main entry point for undockit CLI
"""

import sys
from undockit.args import get_parser
from undockit.install import install, resolve_target
from undockit import deploy
from undockit.backend import get_backend


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

    elif parsed.command == "build":
        try:
            backend = get_backend()
            image_id = backend.build(parsed.dockerfile)
            print(image_id)
            return 0
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    elif parsed.command == "run":
        try:
            backend = get_backend()

            # Build the image
            image_id = backend.build(parsed.dockerfile)

            # Get container name
            container_name = backend.name(image_id)

            # Start container if not running
            if not backend.is_running(container_name):
                backend.start(container_name, image_id, parsed.timeout)

            # Get command to run - always use entrypoint+cmd, append args
            command = backend.command(image_id)
            if parsed.args:
                command.extend(parsed.args)

            # Execute command
            return backend.exec(container_name, command)

        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    else:
        # No command given, show help
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
