from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest

from wiki_skills.install import DEFAULT_TARGET, SKILLS_DIR, install


def test_default_target_is_agents_skills() -> None:
    assert DEFAULT_TARGET == "~/.agents/skills/"


def test_skills_dir_points_to_bundled_skills() -> None:
    assert SKILLS_DIR.is_dir()


# --- install creates target directory ---


def test_install_creates_target_directory(tmp_path: Path) -> None:
    target = str(tmp_path / "new" / "skills")

    install(target)

    assert Path(target).is_dir()


def test_install_expands_tilde(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))

    install("~/.agents/skills/")

    assert (tmp_path / ".agents" / "skills").is_dir()


# --- install copies skill files ---


def test_install_copies_wiki_compose(tmp_path: Path) -> None:
    target = str(tmp_path / "skills")

    install(target)

    assert (Path(target) / "wiki-compose" / "SKILL.md").is_file()


def test_install_copies_wiki_find(tmp_path: Path) -> None:
    target = str(tmp_path / "skills")

    install(target)

    assert (Path(target) / "wiki-find" / "SKILL.md").is_file()


def test_install_preserves_skill_content(tmp_path: Path) -> None:
    target = str(tmp_path / "skills")

    install(target)

    source_content = (SKILLS_DIR / "wiki-compose" / "SKILL.md").read_text()
    dest_content = (Path(target) / "wiki-compose" / "SKILL.md").read_text()
    assert source_content == dest_content


# --- install is idempotent ---


def test_install_overwrites_existing_files(tmp_path: Path) -> None:
    target = str(tmp_path / "skills")
    dest = Path(target)
    dest.mkdir(parents=True)
    wiki_compose = dest / "wiki-compose" / "SKILL.md"
    wiki_compose.parent.mkdir(parents=True)
    wiki_compose.write_text("old content")

    install(target)

    source_content = (SKILLS_DIR / "wiki-compose" / "SKILL.md").read_text()
    assert wiki_compose.read_text() == source_content


def test_install_idempotent_on_clean_target(tmp_path: Path) -> None:
    target = str(tmp_path / "skills")

    install(target)
    install(target)

    assert (Path(target) / "wiki-compose" / "SKILL.md").is_file()
    assert (Path(target) / "wiki-find" / "SKILL.md").is_file()
