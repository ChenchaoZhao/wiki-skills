from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING, cast

import frontmatter
from loguru import logger

from wiki_skills.deps import check_cli

if TYPE_CHECKING:
    from wiki_skills.wiki import DocumentMetadata

DEFAULT_INDEX_PATH: str = "."
DEFAULT_FULL: bool = False
DB_DIR_NAME: str = ".wiki-skills"
DB_NAME: str = "state.db"
FILES_TABLE: str = "files"

_CREATE_TABLE_SQL: str = f"""\
CREATE TABLE IF NOT EXISTS {FILES_TABLE} (
    path TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    title TEXT,
    description TEXT,
    resource TEXT,
    tags TEXT,
    timestamp TEXT,
    content_hash TEXT NOT NULL,
    mtime REAL NOT NULL
);
"""

_UPSERT_SQL: str = """\
INSERT INTO files
    (path, type, title, description, resource, tags, timestamp, content_hash, mtime)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(path) DO UPDATE SET
    type = excluded.type,
    title = excluded.title,
    description = excluded.description,
    resource = excluded.resource,
    tags = excluded.tags,
    timestamp = excluded.timestamp,
    content_hash = excluded.content_hash,
    mtime = excluded.mtime
"""


def hash_content(path: Path) -> str:
    """Return the SHA-256 hex digest of the file content at *path*."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_frontmatter(path: Path) -> DocumentMetadata:
    """Extract OKF frontmatter from a Markdown file.

    Uses ``python-frontmatter`` to parse the YAML block between ``---``
    delimiters.  Returns a :class:`~wiki_skills.wiki.DocumentMetadata` dict
    with at least a ``type`` key (defaulting to ``"concept"`` when absent).
    """
    post = frontmatter.load(str(path))
    if not post.metadata:
        logger.warning("No frontmatter found in {}", path)
        return {"type": "concept"}

    metadata: DocumentMetadata = {
        "type": str(post.metadata.get("type", "concept")),
    }
    for key in ("title", "description", "resource", "timestamp"):
        if key in post.metadata:
            metadata[key] = str(post.metadata[key])  # type: ignore[assignment]
    if "tags" in post.metadata:
        metadata["tags"] = cast("list[str]", post.metadata["tags"])

    return metadata


def _db_path(bundle_root: Path) -> Path:
    """Return the path to ``state.db`` inside the bundle root."""
    return bundle_root / DB_DIR_NAME / DB_NAME


def _ensure_db(conn: sqlite3.Connection) -> None:
    """Create the ``files`` table if it does not already exist."""
    conn.execute(_CREATE_TABLE_SQL)
    conn.commit()


def _index_one(
    conn: sqlite3.Connection,
    file_path: Path,
    bundle_root: Path,
    *,
    full: bool,
) -> bool:
    """Index a single file. Returns True if the file was updated or inserted."""
    rel = file_path.relative_to(bundle_root).as_posix()
    current_mtime = file_path.stat().st_mtime

    if not full:
        row = conn.execute(
            # FILES_TABLE is a module constant, not user-controlled
            f"SELECT mtime FROM {FILES_TABLE} WHERE path = ?",  # noqa: S608
            (rel,),
        ).fetchone()
        if row and row[0] == current_mtime:
            return False

    content_hash = hash_content(file_path)

    metadata = parse_frontmatter(file_path)
    tags_json = json.dumps(metadata.get("tags")) if "tags" in metadata else None

    conn.execute(
        _UPSERT_SQL,
        (
            rel,
            metadata["type"],
            metadata.get("title"),
            metadata.get("description"),
            metadata.get("resource"),
            tags_json,
            metadata.get("timestamp"),
            content_hash,
            current_mtime,
        ),
    )
    return True


def index(path: str = DEFAULT_INDEX_PATH, *, full: bool = DEFAULT_FULL) -> None:
    """Build or update the SQLite index for a wiki bundle.

    When *full* is ``False`` (the default), only files whose ``mtime`` has
    changed since the last index are re-processed.  Pass ``full=True`` to
    force a complete rebuild.
    """
    if not check_cli("sqlite3"):
        logger.warning("sqlite3 CLI not found on PATH — DB queries may fail")

    bundle_root = Path(path).resolve()
    db_dir = bundle_root / DB_DIR_NAME
    db_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(_db_path(bundle_root)))
    try:
        _ensure_db(conn)

        on_disk: set[str] = set()
        for md_file in bundle_root.rglob("*.md"):
            rel = md_file.relative_to(bundle_root).as_posix()
            on_disk.add(rel)
            _index_one(conn, md_file, bundle_root, full=full)

        # Remove files that no longer exist on disk.
        # FILES_TABLE is a module constant, not user-controlled
        rows = conn.execute(f"SELECT path FROM {FILES_TABLE}").fetchall()  # noqa: S608
        for (db_path,) in rows:
            if db_path not in on_disk:
                conn.execute(
                    # FILES_TABLE is a module constant, not user-controlled
                    f"DELETE FROM {FILES_TABLE} WHERE path = ?",  # noqa: S608
                    (db_path,),
                )
                logger.debug("Removed deleted file from index: {}", db_path)

        conn.commit()
    finally:
        conn.close()
