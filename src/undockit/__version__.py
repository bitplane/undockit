from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("undockit")
except PackageNotFoundError:
    __version__ = "unknown"
