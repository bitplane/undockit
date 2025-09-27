# undockit

Run docker container endpoints like they're native commands.

## Setup

Deps:

1. nvidia drivers
2. nvidia container runtime
3. `podman`

Now create a CDI config:

```bash
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
```

Then install `undockit` from pypi. You could use pipx or uv, it'll work all
the same:

```bash
pip install undockit
```

## Usage

To install a container as an executable, use the install command:

```bash
undockit install dockerhub.io/bitplanenet/whisper
```

This will add an executable Dockerfile with the undockit runtime as the shebang
into your `~/.local/bin` dir or `$PREFIX`. You can override that location;
see `--help` for details

You can now run it:

```bash
whisper --help
```
