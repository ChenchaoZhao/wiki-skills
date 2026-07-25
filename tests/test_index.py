from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from typing import TYPE_CHECKING
from unittest.mock import patch

if TYPE_CHECKING:
    from pathlib import Path

import pytest  # noqa: TC002

from wiki_skills.index import (
    DB_DIR_NAME,
    DB_NAME,
    FILES_TABLE,
    hash_content,
    index,
    parse_frontmatter,
)

# ---------------------------------------------------------------------------
# hash_content
# ---------------------------------------------------------------------------


def test_hash_content_returns_sha256_hexdigest(tmp_path: Path) -> None:
    file = tmp_path / "doc.md"
    file.write_text("hello world")
    expected = hashlib.sha256(b"hello world").hexdigest()
    assert hash_content(file) == expected


def test_hash_content_different_for_different_content(tmp_path: Path) -> None:
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    a.write_text("alpha")
    b.write_text("beta")
    assert hash_content(a) != hash_content(b)


# ---------------------------------------------------------------------------
# parse_frontmatter
# ---------------------------------------------------------------------------


class TestParseFrontmatter:
    def test_returns_type_concept_when_no_frontmatter(self, tmp_path: Path) -> None:
        f = tmp_path / "plain.md"
        f.write_text("# Title\n\nBody text.\n")
        assert parse_frontmatter(f) == {"type": "concept"}

    def test_warns_when_no_frontmatter(self, tmp_path: Path) -> None:
        f = tmp_path / "plain.md"
        f.write_text("# Title\n\nBody text.\n")
        with patch("wiki_skills.index.logger.warning") as mock_warning:
            parse_frontmatter(f)
            mock_warning.assert_called_once_with("No frontmatter found in {}", f)

    def test_extracts_type(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text("---\ntype: reference\n---\n# Body\n")
        assert parse_frontmatter(f)["type"] == "reference"

    def test_extracts_title(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text('---\ntype: concept\ntitle: "My Title"\n---\n')
        assert parse_frontmatter(f).get("title") == "My Title"

    def test_extracts_description(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text('---\ntype: concept\ndescription: "A description"\n---\n')
        assert parse_frontmatter(f).get("description") == "A description"

    def test_extracts_resource(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text('---\ntype: reference\nresource: "https://example.com"\n---\n')
        assert parse_frontmatter(f).get("resource") == "https://example.com"

    def test_extracts_tags_as_list(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text("---\ntype: concept\ntags: [db, schema]\n---\n")
        assert parse_frontmatter(f).get("tags") == ["db", "schema"]

    def test_extracts_timestamp(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text('---\ntype: concept\ntimestamp: "2024-01-01T00:00:00Z"\n---\n')
        assert parse_frontmatter(f).get("timestamp") == "2024-01-01T00:00:00Z"

    def test_all_fields(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text(
            "---\n"
            "type: reference\n"
            'title: "Full"\n'
            'description: "All fields"\n'
            'resource: "https://example.com"\n'
            "tags: [a, b]\n"
            'timestamp: "2024-06-01"\n'
            "---\n"
        )
        meta = parse_frontmatter(f)
        assert meta == {
            "type": "reference",
            "title": "Full",
            "description": "All fields",
            "resource": "https://example.com",
            "tags": ["a", "b"],
            "timestamp": "2024-06-01",
        }

    def test_skips_comment_lines(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text("---\n# this is a comment\ntype: log\n---\n")
        assert parse_frontmatter(f)["type"] == "log"


# ---------------------------------------------------------------------------
# index — DB creation and table schema
# ---------------------------------------------------------------------------


class TestIndexDB:
    def test_creates_db_file(self, tmp_path: Path) -> None:
        index(path=str(tmp_path))
        db_path = tmp_path / DB_DIR_NAME / DB_NAME
        assert db_path.exists()

    def test_creates_files_table(self, tmp_path: Path) -> None:
        index(path=str(tmp_path))
        db_path = tmp_path / DB_DIR_NAME / DB_NAME
        conn = sqlite3.connect(str(db_path))
        try:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'",
            ).fetchall()
            table_names = [t[0] for t in tables]
            assert FILES_TABLE in table_names
        finally:
            conn.close()

    def test_is_idempotent(self, tmp_path: Path) -> None:
        index(path=str(tmp_path))
        index(path=str(tmp_path))
        db_path = tmp_path / DB_DIR_NAME / DB_NAME
        assert db_path.exists()


# ---------------------------------------------------------------------------
# index — incremental vs full rebuild
# ---------------------------------------------------------------------------


class TestIndexRebuild:
    def _write_md(self, bundle: Path, name: str, content: str) -> Path:
        f = bundle / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content)
        return f

    def _query_paths(self, bundle: Path) -> list[str]:
        db_path = bundle / DB_DIR_NAME / DB_NAME
        conn = sqlite3.connect(str(db_path))
        try:
            rows = conn.execute(f"SELECT path FROM {FILES_TABLE}").fetchall()
            return sorted(r[0] for r in rows)
        finally:
            conn.close()

    def _query_hashes(self, bundle: Path) -> dict[str, str]:
        db_path = bundle / DB_DIR_NAME / DB_NAME
        conn = sqlite3.connect(str(db_path))
        try:
            rows = conn.execute(
                f"SELECT path, content_hash FROM {FILES_TABLE}",
            ).fetchall()
            return {r[0]: r[1] for r in rows}
        finally:
            conn.close()

    def _query_row(self, bundle: Path, rel_path: str) -> tuple | None:
        db_path = bundle / DB_DIR_NAME / DB_NAME
        conn = sqlite3.connect(str(db_path))
        try:
            return conn.execute(
                f"SELECT * FROM {FILES_TABLE} WHERE path = ?",
                (rel_path,),
            ).fetchone()
        finally:
            conn.close()

    def test_index_indexes_markdown_files(self, tmp_path: Path) -> None:
        self._write_md(tmp_path, "a.md", "---\ntype: concept\n---\n# A\n")
        self._write_md(tmp_path, "b.md", "---\ntype: reference\n---\n# B\n")
        index(path=str(tmp_path))
        paths = self._query_paths(tmp_path)
        assert paths == ["a.md", "b.md"]

    def test_index_ignores_non_markdown_files(self, tmp_path: Path) -> None:
        self._write_md(tmp_path, "readme.md", "---\ntype: concept\n---\n")
        (tmp_path / "image.png").write_bytes(b"\x89PNG")
        index(path=str(tmp_path))
        paths = self._query_paths(tmp_path)
        assert paths == ["readme.md"]

    def test_index_nested_directories(self, tmp_path: Path) -> None:
        self._write_md(tmp_path, "sub/dir/doc.md", "---\ntype: concept\n---\n")
        index(path=str(tmp_path))
        paths = self._query_paths(tmp_path)
        assert paths == ["sub/dir/doc.md"]

    def test_incremental_skips_unchanged_mtime(self, tmp_path: Path) -> None:
        f = self._write_md(tmp_path, "a.md", "---\ntype: concept\n---\n")
        index(path=str(tmp_path))
        first_hashes = self._query_hashes(tmp_path)

        # Rewrite the file and explicitly preserve mtime to test the skip path.
        original_mtime = os.stat(f).st_mtime
        f.write_text("---\ntype: concept\n---\n")
        os.utime(f, (original_mtime, original_mtime))

        index(path=str(tmp_path))
        second_hashes = self._query_hashes(tmp_path)
        assert first_hashes == second_hashes

    def test_full_rebuild_rehashes_all_files(self, tmp_path: Path) -> None:
        f = self._write_md(tmp_path, "a.md", "---\ntype: concept\n---\n# A\n")
        index(path=str(tmp_path))
        first_hash = self._query_hashes(tmp_path)["a.md"]

        f.write_text("---\ntype: reference\n---\n# A updated\n")
        index(path=str(tmp_path), full=True)
        second_hash = self._query_hashes(tmp_path)["a.md"]
        assert first_hash != second_hash

    def test_tags_stored_as_json(self, tmp_path: Path) -> None:
        self._write_md(tmp_path, "doc.md", "---\ntype: concept\ntags: [db, schema]\n---\n")
        index(path=str(tmp_path))
        row = self._query_row(tmp_path, "doc.md")
        assert row is not None
        tags_col = row[5]  # tags column index
        assert json.loads(tags_col) == ["db", "schema"]

    def test_title_and_description_stored(self, tmp_path: Path) -> None:
        self._write_md(
            tmp_path,
            "doc.md",
            '---\ntype: reference\ntitle: "My Doc"\ndescription: "Desc"\n---\n',
        )
        index(path=str(tmp_path))
        row = self._query_row(tmp_path, "doc.md")
        assert row is not None
        assert row[2] == "My Doc"  # title column
        assert row[3] == "Desc"  # description column


# ---------------------------------------------------------------------------
# index — deleted file cleanup
# ---------------------------------------------------------------------------


class TestIndexDeletedCleanup:
    def test_deleted_file_removed_from_db(self, tmp_path: Path) -> None:
        f = tmp_path / "to_delete.md"
        f.write_text("---\ntype: concept\n---\n")
        index(path=str(tmp_path))

        db_path = tmp_path / DB_DIR_NAME / DB_NAME
        conn = sqlite3.connect(str(db_path))
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {FILES_TABLE}").fetchone()[0]
            assert count == 1
        finally:
            conn.close()

        f.unlink()
        index(path=str(tmp_path))

        conn = sqlite3.connect(str(db_path))
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {FILES_TABLE}").fetchone()[0]
            assert count == 0
        finally:
            conn.close()

    def test_surviving_files_not_deleted(self, tmp_path: Path) -> None:
        keep = tmp_path / "keep.md"
        remove = tmp_path / "remove.md"
        keep.write_text("---\ntype: concept\n---\n")
        remove.write_text("---\ntype: reference\n---\n")
        index(path=str(tmp_path))

        remove.unlink()
        index(path=str(tmp_path))

        db_path = tmp_path / DB_DIR_NAME / DB_NAME
        conn = sqlite3.connect(str(db_path))
        try:
            paths = [r[0] for r in conn.execute(f"SELECT path FROM {FILES_TABLE}")]
            assert paths == ["keep.md"]
        finally:
            conn.close()


# ---------------------------------------------------------------------------
# index — sqlite3 CLI check
# ---------------------------------------------------------------------------


def test_index_warns_when_sqlite3_cli_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("wiki_skills.index.check_cli", lambda _name: False)
    with patch("wiki_skills.index.logger.warning") as mock_warning:
        index(path=str(tmp_path))
        mock_warning.assert_called_once_with(
            "sqlite3 CLI not found on PATH — DB queries may fail",
        )
