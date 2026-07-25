from __future__ import annotations

import sqlite3
from datetime import datetime
from enum import IntEnum
from pathlib import Path

import frontmatter

from wiki_skills.index import DB_DIR_NAME, DB_NAME, FILES_TABLE
from wiki_skills.wiki import RESERVED_TYPES

DELIMITER_COUNT_MIN: int = 2
DEFAULT_FRONTMATTER_LINE: int = 2


class ExitCode(IntEnum):
    """validate() return codes per design doc Section 5."""

    CLEAN = 0
    WARNINGS = 1
    ERRORS = 2


def _is_missing_type(metadata: dict[str, object]) -> bool:
    """Return True if ``type`` is absent or empty."""
    t = metadata.get("type")
    if t is None:
        return True
    if isinstance(t, str):
        return not t.strip()
    return True


def _is_invalid_frontmatter(path: Path) -> bool:
    """Return True if the file has ``---`` delimiters but YAML is broken."""
    try:
        content = path.read_text()
    except (UnicodeDecodeError, ValueError, OSError):
        return True
    lines = content.splitlines(keepends=True)
    if not lines or not lines[0].startswith("---"):
        return False
    # Missing closing delimiter
    if content.count("---") < DELIMITER_COUNT_MIN:
        return True
    try:
        frontmatter.loads(content)
    except Exception:  # noqa: BLE001
        return True
    return False


def _is_bad_timestamp(value: str) -> bool:
    """Return True if *value* is not valid ISO 8601."""
    try:
        datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return True
    return False


def _is_bad_tags(value: object) -> bool:
    """Return True if *value* is not a list of strings."""
    if not isinstance(value, list):
        return True
    return not all(isinstance(item, str) for item in value)


def _find_line_number(lines: list[str], key: str) -> int:
    """Return the 1-based line number where *key* appears in YAML."""
    for i, line in enumerate(lines, start=1):
        if line.startswith(f"{key}:"):
            return i
    return DEFAULT_FRONTMATTER_LINE


def validate(path: str = ".") -> int:
    """Lint an OKF bundle for conformance.

    Returns an exit code: 0 = clean, 1 = warnings, 2 = errors.
    """
    bundle_root = Path(path).resolve()
    errors: list[tuple[str, int, str]] = []
    warnings: list[tuple[str, int, str]] = []
    concept_count: int = 0

    # Check state.db staleness
    db_path = bundle_root / DB_DIR_NAME / DB_NAME
    if not db_path.exists():
        warnings.append((".", 1, "WARN — state.db not found, run 'wiki-cli index' first"))
    else:
        conn = sqlite3.connect(str(db_path))
        try:
            # FILES_TABLE is a module constant, not user-controlled
            rows = conn.execute(f"SELECT path, mtime FROM {FILES_TABLE}").fetchall()  # noqa: S608
        finally:
            conn.close()
        for rel, stored_mtime in rows:
            full = bundle_root / rel
            if full.exists() and full.stat().st_mtime > stored_mtime:
                warnings.append((rel, 1, "WARN — file has changed since last index"))
                break

    # Scan .md files
    for md_file in sorted(bundle_root.rglob("*.md")):
        rel = md_file.relative_to(bundle_root).as_posix()
        stem = md_file.stem

        if stem in RESERVED_TYPES:
            continue

        # Parse frontmatter
        if _is_invalid_frontmatter(md_file):
            errors.append((rel, 1, "ERROR — unparseable YAML frontmatter"))
            continue

        try:
            post = frontmatter.load(str(md_file))
        except Exception:  # noqa: BLE001
            errors.append((rel, 1, "ERROR — unparseable YAML frontmatter"))
            continue

        metadata = post.metadata if post.metadata else {}
        lines = md_file.read_text().splitlines(keepends=True)

        # Check: missing or empty type
        if _is_missing_type(metadata):
            errors.append((rel, 2, "ERROR — missing or empty 'type' in frontmatter"))
        else:
            concept_count += 1

            # Check: bad timestamp format
            ts = metadata.get("timestamp")
            if ts is not None and _is_bad_timestamp(str(ts)):
                line = _find_line_number(lines, "timestamp")
                warnings.append((rel, line, f"WARN — 'timestamp' is not ISO 8601: {ts!r}"))

            # Check: bad tags format
            tags = metadata.get("tags")
            if tags is not None and _is_bad_tags(tags):
                line = _find_line_number(lines, "tags")
                warnings.append((rel, line, f"WARN — 'tags' is not a list of strings: {tags!r}"))

    # Check: empty bundle
    if concept_count == 0:
        warnings.append((".", 1, "WARN — empty bundle, no concept files found"))

    # Output
    for rel, line, msg in sorted(errors):
        print(f"{rel}:{line}: {msg}")  # noqa: T201
    for rel, line, msg in sorted(warnings):
        print(f"{rel}:{line}: {msg}")  # noqa: T201

    if errors:
        return ExitCode.ERRORS
    if warnings:
        return ExitCode.WARNINGS
    return ExitCode.CLEAN
