import sys

import fire

from wiki_skills.__about__ import __version__
from wiki_skills.index import index
from wiki_skills.install import install
from wiki_skills.query import query
from wiki_skills.validate import validate

_VERSION_FLAG = "--version"


def _version() -> str:
    """Return the installed version."""
    return __version__


def main() -> None:
    """Entry point for wiki-skills CLI."""
    if _VERSION_FLAG in sys.argv:
        print(__version__)  # noqa: T201
        raise SystemExit(0)

    fire.Fire(
        {
            "version": _version,
            "install": install,
            "index": index,
            "validate": validate,
            "query": query,
        }
    )


if __name__ == "__main__":
    main()
