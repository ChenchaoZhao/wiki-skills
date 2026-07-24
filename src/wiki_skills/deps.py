import shutil

REQUIRED_CLI_TOOLS: frozenset[str] = frozenset({"sqlite3", "grep"})


def check_cli(name: str) -> bool:
    """Return True if *name* is found on PATH, False otherwise."""
    return shutil.which(name) is not None
