from __future__ import annotations

from pathlib import Path
from typing import NotRequired, TypedDict

DEFAULT_TYPE: str = "concept"
RESERVED_TYPES: frozenset[str] = frozenset({"index", "log"})


class DocumentMetadata(TypedDict):
    """OKF frontmatter for a document."""

    type: str
    title: NotRequired[str]
    description: NotRequired[str]
    resource: NotRequired[str]
    tags: NotRequired[list[str]]
    timestamp: NotRequired[str]


def document_id_from_path(path: str, root: str) -> str:
    """Derive document ID from file path relative to bundle root.

    Strips the ``.md`` extension and returns the POSIX relative path.
    """
    return Path(path).relative_to(root).with_suffix("").as_posix()
