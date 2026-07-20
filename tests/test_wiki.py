import pytest

from wiki_skills.wiki import (
    DEFAULT_TYPE,
    RESERVED_TYPES,
    DocumentMetadata,
    document_id_from_path,
)


def test_default_type_is_concept() -> None:
    assert DEFAULT_TYPE == "concept"


def test_reserved_types_are_frozenset() -> None:
    assert frozenset({"index", "log"}) == RESERVED_TYPES


def test_document_metadata_has_type_field() -> None:
    metadata: DocumentMetadata = {"type": "document"}
    assert metadata["type"] == "document"


def test_document_metadata_allows_optional_fields() -> None:
    metadata: DocumentMetadata = {
        "type": "document",
        "title": "Users",
        "description": "User documents",
        "resource": "https://example.com",
        "tags": ["users", "people"],
        "timestamp": "2024-01-01T00:00:00Z",
    }
    assert metadata["title"] == "Users"
    assert metadata["tags"] == ["users", "people"]


@pytest.mark.parametrize(
    ("path", "root", "expected"),
    [
        ("tables/users.md", ".", "tables/users"),
        ("users.md", ".", "users"),
        ("a/b/c/document.md", ".", "a/b/c/document"),
        ("tables/users.md", "tables", "users"),
        ("users", ".", "users"),
        ("index.md", ".", "index"),
    ],
)
def test_document_id_from_path_returns_relative_path_without_extension(path: str, root: str, expected: str) -> None:
    assert document_id_from_path(path, root) == expected


def test_document_id_from_path_with_absolute_root() -> None:
    assert document_id_from_path("/tmp/bundle/tables/users.md", "/tmp/bundle") == "tables/users"


def test_document_id_from_path_raises_on_non_relative_path() -> None:
    with pytest.raises(ValueError, match="is not in the subpath"):
        document_id_from_path("other/file.md", "tables")
