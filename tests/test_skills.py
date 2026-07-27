from __future__ import annotations

from pathlib import Path

SKILLS_DIR: Path = Path(__file__).resolve().parent.parent / "src" / "wiki_skills" / "skills"


def test_wiki_compose_skill_exists() -> None:
    skill = SKILLS_DIR / "wiki-compose" / "SKILL.md"
    assert skill.exists(), f"Missing {skill}"


def test_wiki_compose_skill_is_nonempty() -> None:
    skill = SKILLS_DIR / "wiki-compose" / "SKILL.md"
    assert skill.stat().st_size > 0, f"{skill} is empty"


def test_wiki_compose_skill_has_frontmatter() -> None:
    skill = SKILLS_DIR / "wiki-compose" / "SKILL.md"
    content = skill.read_text()
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter"


def test_wiki_find_skill_exists() -> None:
    skill = SKILLS_DIR / "wiki-find" / "SKILL.md"
    assert skill.exists(), f"Missing {skill}"


def test_wiki_find_skill_is_nonempty() -> None:
    skill = SKILLS_DIR / "wiki-find" / "SKILL.md"
    assert skill.stat().st_size > 0, f"{skill} is empty"


def test_wiki_find_skill_has_frontmatter() -> None:
    skill = SKILLS_DIR / "wiki-find" / "SKILL.md"
    content = skill.read_text()
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter"


def test_wiki_compose_mentions_validate_command() -> None:
    skill = SKILLS_DIR / "wiki-compose" / "SKILL.md"
    content = skill.read_text()
    assert "wiki-cli validate" in content


def test_wiki_compose_mentions_okf_frontmatter() -> None:
    skill = SKILLS_DIR / "wiki-compose" / "SKILL.md"
    content = skill.read_text()
    assert "type:" in content


def test_wiki_find_mentions_index_command() -> None:
    skill = SKILLS_DIR / "wiki-find" / "SKILL.md"
    content = skill.read_text()
    assert "wiki-cli index" in content


def test_wiki_find_mentions_sqlite3_cli() -> None:
    skill = SKILLS_DIR / "wiki-find" / "SKILL.md"
    content = skill.read_text()
    assert "sqlite3" in content


def test_wiki_find_mentions_query_fallback() -> None:
    skill = SKILLS_DIR / "wiki-find" / "SKILL.md"
    content = skill.read_text()
    assert "wiki-cli query" in content


def test_wiki_find_mentions_glob() -> None:
    skill = SKILLS_DIR / "wiki-find" / "SKILL.md"
    content = skill.read_text()
    assert "glob" in content
