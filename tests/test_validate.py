from __future__ import annotations

import os
import sqlite3
from typing import TYPE_CHECKING
from unittest.mock import patch

if TYPE_CHECKING:
    from pathlib import Path

import pytest

from wiki_skills.index import DB_DIR_NAME, DB_NAME, FILES_TABLE
from wiki_skills.validate import (
    DEFAULT_FRONTMATTER_LINE,
    ExitCode,
    _find_line_number,
    _is_bad_tags,
    _is_bad_timestamp,
    _is_invalid_frontmatter,
    _is_missing_type,
    validate,
)


def _setup_db(
    bundle: Path,
    *,
    entries: list[tuple[str, str]] | None = None,
) -> None:
    """Create state.db with the files table and entries using actual file mtimes."""
    db_dir = bundle / DB_DIR_NAME
    db_dir.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(db_dir / DB_NAME))
    try:
        conn.execute(f"CREATE TABLE IF NOT EXISTS {FILES_TABLE} (path TEXT PRIMARY KEY, type TEXT, mtime REAL)")
        for rel_path, type_ in entries or []:
            full = bundle / rel_path
            mtime = full.stat().st_mtime if full.exists() else 0.0
            conn.execute(
                f"INSERT INTO {FILES_TABLE} VALUES (?, ?, ?)",
                (rel_path, type_, mtime),
            )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# _is_missing_type
# ---------------------------------------------------------------------------


class TestIsMissingType:
    def test_none_value(self) -> None:
        assert _is_missing_type({}) is True

    def test_empty_string(self) -> None:
        assert _is_missing_type({"type": ""}) is True

    def test_whitespace_only(self) -> None:
        assert _is_missing_type({"type": "  "}) is True

    def test_valid_type(self) -> None:
        assert _is_missing_type({"type": "concept"}) is False

    def test_non_string_value(self) -> None:
        assert _is_missing_type({"type": 42}) is True


# ---------------------------------------------------------------------------
# _is_bad_timestamp
# ---------------------------------------------------------------------------


class TestIsBadTimestamp:
    @pytest.mark.parametrize(
        "value",
        [
            "2024-01-01",
            "2024-06-15T10:30:00",
            "2024-06-15T10:30:00Z",
            "2024-06-15T10:30:00+05:30",
        ],
    )
    def test_valid_iso8601(self, value: str) -> None:
        assert _is_bad_timestamp(value) is False

    @pytest.mark.parametrize(
        "value",
        [
            "not-a-date",
            "2024/01/01",
            "01-01-2024",
            "",
        ],
    )
    def test_invalid_timestamp(self, value: str) -> None:
        assert _is_bad_timestamp(value) is True


# ---------------------------------------------------------------------------
# _is_bad_tags
# ---------------------------------------------------------------------------


class TestIsBadTags:
    def test_list_of_strings(self) -> None:
        assert _is_bad_tags(["a", "b"]) is False

    def test_empty_list(self) -> None:
        assert _is_bad_tags([]) is False

    def test_not_a_list(self) -> None:
        assert _is_bad_tags("not-a-list") is True

    def test_list_with_non_string(self) -> None:
        assert _is_bad_tags(["a", 1]) is True

    def test_none_value(self) -> None:
        assert _is_bad_tags(None) is True

    def test_dict_value(self) -> None:
        assert _is_bad_tags({"a": 1}) is True


# ---------------------------------------------------------------------------
# _is_invalid_frontmatter
# ---------------------------------------------------------------------------


class TestIsInvalidFrontmatter:
    def test_valid_frontmatter(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text("---\ntype: concept\n---\n")
        assert _is_invalid_frontmatter(f) is False

    def test_no_frontmatter(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text("# Title\n\nBody.\n")
        assert _is_invalid_frontmatter(f) is False

    def test_broken_yaml(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text("---\ntype: [unclosed\n---\n")
        assert _is_invalid_frontmatter(f) is True

    def test_missing_closing_delimiter(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text("---\ntype: concept\n")
        assert _is_invalid_frontmatter(f) is True

    def test_binary_file(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_bytes(b"\xff\xfe")
        assert _is_invalid_frontmatter(f) is True


# ---------------------------------------------------------------------------
# _find_line_number
# ---------------------------------------------------------------------------


EXPECTED_TIMESTAMP_LINE: int = 2


class TestFindLineNumber:
    def test_finds_key(self) -> None:
        lines = ["---\n", "timestamp: 2024-01-01\n", "tags: [a]\n", "---\n"]
        assert _find_line_number(lines, "timestamp") == EXPECTED_TIMESTAMP_LINE

    def test_returns_default_when_not_found(self) -> None:
        lines = ["---\n", "type: concept\n", "---\n"]
        assert _find_line_number(lines, "timestamp") == DEFAULT_FRONTMATTER_LINE

    def test_finds_multiple_keys(self) -> None:
        lines = ["---\n", "timestamp: a\n", "timestamp: b\n", "---\n"]
        assert _find_line_number(lines, "timestamp") == EXPECTED_TIMESTAMP_LINE


# ---------------------------------------------------------------------------
# validate — return codes
# ---------------------------------------------------------------------------


class TestValidateReturnCodes:
    def test_clean_bundle_returns_zero(self, tmp_path: Path) -> None:
        (tmp_path / "doc.md").write_text("---\ntype: concept\n---\n")
        _setup_db(tmp_path, entries=[("doc.md", "concept")])
        assert validate(str(tmp_path)) == ExitCode.CLEAN

    def test_errors_return_two(self, tmp_path: Path) -> None:
        (tmp_path / "doc.md").write_text("---\ntitle: no type\n---\n")
        assert validate(str(tmp_path)) == ExitCode.ERRORS

    def test_warnings_return_one(self, tmp_path: Path) -> None:
        (tmp_path / "doc.md").write_text('---\ntype: concept\ntimestamp: "bad"\n---\n')
        assert validate(str(tmp_path)) == ExitCode.WARNINGS

    def test_no_md_files_returns_one(self, tmp_path: Path) -> None:
        assert validate(str(tmp_path)) == 1


# ---------------------------------------------------------------------------
# validate — missing type (ERROR)
# ---------------------------------------------------------------------------


class TestValidateMissingType:
    def test_missing_type_field(self, tmp_path: Path) -> None:
        (tmp_path / "doc.md").write_text("---\ntitle: Hello\n---\n")
        with patch("builtins.print") as mock_print:
            validate(str(tmp_path))
            mock_print.assert_any_call("doc.md:2: ERROR — missing or empty 'type' in frontmatter")

    def test_empty_type_field(self, tmp_path: Path) -> None:
        (tmp_path / "doc.md").write_text("---\ntype: \n---\n")
        with patch("builtins.print") as mock_print:
            validate(str(tmp_path))
            mock_print.assert_any_call("doc.md:2: ERROR — missing or empty 'type' in frontmatter")


# ---------------------------------------------------------------------------
# validate — unparseable YAML (ERROR)
# ---------------------------------------------------------------------------


class TestValidateUnparseableYaml:
    def test_broken_yaml(self, tmp_path: Path) -> None:
        (tmp_path / "doc.md").write_text("---\ntype: [unclosed\n---\n")
        with patch("builtins.print") as mock_print:
            validate(str(tmp_path))
            mock_print.assert_any_call("doc.md:1: ERROR — unparseable YAML frontmatter")


# ---------------------------------------------------------------------------
# validate — bad timestamp (WARN)
# ---------------------------------------------------------------------------


class TestValidateBadTimestamp:
    def test_invalid_timestamp(self, tmp_path: Path) -> None:
        (tmp_path / "doc.md").write_text('---\ntype: concept\ntimestamp: "not-a-date"\n---\n')
        with patch("builtins.print") as mock_print:
            validate(str(tmp_path))
            mock_print.assert_any_call("doc.md:3: WARN — 'timestamp' is not ISO 8601: 'not-a-date'")

    def test_valid_timestamp_no_warning(self, tmp_path: Path) -> None:
        (tmp_path / "doc.md").write_text('---\ntype: concept\ntimestamp: "2024-01-01T00:00:00Z"\n---\n')
        with patch("builtins.print") as mock_print:
            validate(str(tmp_path))
            for call_args in mock_print.call_args_list:
                assert "timestamp" not in str(call_args)


# ---------------------------------------------------------------------------
# validate — bad tags (WARN)
# ---------------------------------------------------------------------------


class TestValidateBadTags:
    def test_tags_not_a_list(self, tmp_path: Path) -> None:
        (tmp_path / "doc.md").write_text('---\ntype: concept\ntags: "not-a-list"\n---\n')
        with patch("builtins.print") as mock_print:
            validate(str(tmp_path))
            mock_print.assert_any_call("doc.md:3: WARN — 'tags' is not a list of strings: 'not-a-list'")

    def test_tags_with_non_string_items(self, tmp_path: Path) -> None:
        (tmp_path / "doc.md").write_text("---\ntype: concept\ntags: [a, 1]\n---\n")
        with patch("builtins.print") as mock_print:
            validate(str(tmp_path))
            found = any("tags" in str(call) for call in mock_print.call_args_list)
            assert found

    def test_valid_tags_no_warning(self, tmp_path: Path) -> None:
        (tmp_path / "doc.md").write_text("---\ntype: concept\ntags: [a, b]\n---\n")
        with patch("builtins.print") as mock_print:
            validate(str(tmp_path))
            for call_args in mock_print.call_args_list:
                assert "tags" not in str(call_args)


# ---------------------------------------------------------------------------
# validate — empty bundle (WARN)
# ---------------------------------------------------------------------------


class TestValidateEmptyBundle:
    def test_no_concept_files(self, tmp_path: Path) -> None:
        _setup_db(tmp_path)
        with patch("builtins.print") as mock_print:
            validate(str(tmp_path))
            mock_print.assert_any_call(".:1: WARN — empty bundle, no concept files found")

    def test_only_reserved_files(self, tmp_path: Path) -> None:
        (tmp_path / "index.md").write_text("---\ntype: index\n---\n")
        (tmp_path / "log.md").write_text("---\ntype: log\n---\n")
        _setup_db(tmp_path)
        with patch("builtins.print") as mock_print:
            validate(str(tmp_path))
            mock_print.assert_any_call(".:1: WARN — empty bundle, no concept files found")


# ---------------------------------------------------------------------------
# validate — state.db checks
# ---------------------------------------------------------------------------


class TestValidateStateDB:
    def test_missing_db_warns(self, tmp_path: Path) -> None:
        (tmp_path / "doc.md").write_text("---\ntype: concept\n---\n")
        with patch("builtins.print") as mock_print:
            validate(str(tmp_path))
            mock_print.assert_any_call(".:1: WARN — state.db not found, run 'wiki-cli index' first")

    def test_stale_file_warns(self, tmp_path: Path) -> None:
        (tmp_path / "doc.md").write_text("---\ntype: concept\n---\n")
        _setup_db(tmp_path, entries=[("doc.md", "concept")])
        os.utime(tmp_path / "doc.md", (0.0, 0.0))
        (tmp_path / "doc.md").write_text("---\ntype: concept\n---\n")
        with patch("builtins.print") as mock_print:
            validate(str(tmp_path))
            mock_print.assert_any_call("doc.md:1: WARN — file has changed since last index")


# ---------------------------------------------------------------------------
# validate — reserved files skipped
# ---------------------------------------------------------------------------


class TestValidateReservedFiles:
    def test_index_md_skipped_for_type_check(self, tmp_path: Path) -> None:
        (tmp_path / "index.md").write_text("---\ntitle: Index\n---\n")
        (tmp_path / "doc.md").write_text("---\ntype: concept\n---\n")
        _setup_db(tmp_path, entries=[("doc.md", "concept")])
        with patch("builtins.print") as mock_print:
            result = validate(str(tmp_path))
            assert result == 0
            printed = " ".join(str(c) for c in mock_print.call_args_list)
            assert "index.md" not in printed

    def test_log_md_skipped_for_type_check(self, tmp_path: Path) -> None:
        (tmp_path / "log.md").write_text("---\ntitle: Log\n---\n")
        (tmp_path / "doc.md").write_text("---\ntype: concept\n---\n")
        _setup_db(tmp_path, entries=[("doc.md", "concept")])
        with patch("builtins.print") as mock_print:
            result = validate(str(tmp_path))
            assert result == 0
            printed = " ".join(str(c) for c in mock_print.call_args_list)
            assert "log.md" not in printed


# ---------------------------------------------------------------------------
# validate — output format
# ---------------------------------------------------------------------------


class TestValidateOutputFormat:
    def test_ruff_style_format(self, tmp_path: Path) -> None:
        (tmp_path / "doc.md").write_text("---\ntitle: No type\n---\n")
        with patch("builtins.print") as mock_print:
            validate(str(tmp_path))
            call_args = mock_print.call_args_list[0]
            output = call_args[0][0]
            assert output.startswith("doc.md:")
            assert ": ERROR —" in output
