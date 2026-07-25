from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import pytest

from wiki_skills.query import DEFAULT_QUERY_DB, query

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_db(db_path: Path, rows: list[tuple[str, str, str]] | None = None) -> None:
    """Create a minimal state.db for testing."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "CREATE TABLE files (    path TEXT PRIMARY KEY,    type TEXT NOT NULL,    title TEXT)",
    )
    if rows:
        conn.executemany("INSERT INTO files (path, type, title) VALUES (?, ?, ?)", rows)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# query — successful query
# ---------------------------------------------------------------------------


class TestQuerySuccess:
    def test_prints_header_and_rows(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        db_path = tmp_path / "state.db"
        _create_db(db_path, [("a.md", "concept", "A"), ("b.md", "reference", "B")])

        query("SELECT path, type FROM files", db=str(db_path))

        output = capsys.readouterr().out
        lines = output.strip().splitlines()
        header, row_a, row_b = lines
        assert header == "path  type"
        assert row_a == "a.md  concept"
        assert row_b == "b.md  reference"

    def test_returns_no_results_message(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        db_path = tmp_path / "state.db"
        _create_db(db_path)

        query("SELECT * FROM files WHERE path = 'nonexistent.md'", db=str(db_path))

        output = capsys.readouterr().out
        lines = output.strip().splitlines()
        assert lines[0] == "path  type  title"

    def test_select_star(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        db_path = tmp_path / "state.db"
        _create_db(db_path, [("doc.md", "concept", "Doc")])

        query("SELECT * FROM files", db=str(db_path))

        output = capsys.readouterr().out
        lines = output.strip().splitlines()
        assert lines[0] == "path  type  title"
        assert lines[1] == "doc.md  concept  Doc"


# ---------------------------------------------------------------------------
# query — missing DB
# ---------------------------------------------------------------------------


class TestQueryMissingDB:
    def test_exits_with_error_when_db_missing(self, tmp_path: Path) -> None:
        missing = tmp_path / "nope" / "state.db"

        with pytest.raises(SystemExit, match="1"):
            query("SELECT 1", db=str(missing))

    def test_prints_error_to_stderr(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        missing = tmp_path / "nope" / "state.db"

        with pytest.raises(SystemExit, match="1"):
            query("SELECT 1", db=str(missing))

        err = capsys.readouterr().err
        assert "ERROR" in err
        assert str(missing) in err


# ---------------------------------------------------------------------------
# query — invalid SQL
# ---------------------------------------------------------------------------


class TestQueryInvalidSQL:
    def test_exits_with_error_on_bad_sql(self, tmp_path: Path) -> None:
        db_path = tmp_path / "state.db"
        _create_db(db_path)

        with pytest.raises(SystemExit, match="1"):
            query("SELCT * FROM nonexistent", db=str(db_path))

    def test_prints_sql_error_to_stderr(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        db_path = tmp_path / "state.db"
        _create_db(db_path)

        with pytest.raises(SystemExit, match="1"):
            query("SELCT * FROM nonexistent", db=str(db_path))

        err = capsys.readouterr().err
        assert "ERROR" in err
        assert "SQL error" in err


# ---------------------------------------------------------------------------
# query — default DB path
# ---------------------------------------------------------------------------


class TestQueryDefaultDB:
    def test_default_db_constant(self) -> None:
        assert DEFAULT_QUERY_DB == ""

    def test_uses_cwd_default_when_no_db(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        db_dir = tmp_path / ".wiki-skills"
        _create_db(db_dir / "state.db", [("x.md", "concept", "X")])

        monkeypatch.chdir(tmp_path)
        query("SELECT path FROM files")

        output = capsys.readouterr().out
        assert "x.md" in output


# ---------------------------------------------------------------------------
# query — exit code
# ---------------------------------------------------------------------------


class TestQueryExitCode:
    def test_exits_1_on_missing_db(self, tmp_path: Path) -> None:
        with pytest.raises(SystemExit) as exc_info:
            query("SELECT 1", db=str(tmp_path / "missing.db"))
        assert exc_info.value.code == 1

    def test_exits_1_on_invalid_sql(self, tmp_path: Path) -> None:
        db_path = tmp_path / "state.db"
        _create_db(db_path)
        with pytest.raises(SystemExit) as exc_info:
            query("NOT VALID SQL", db=str(db_path))
        assert exc_info.value.code == 1
