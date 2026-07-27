from __future__ import annotations

import shutil
from pathlib import Path

from loguru import logger

DEFAULT_TARGET: str = "~/.agents/skills/"

SKILLS_DIR: Path = Path(__file__).parent / "skills"


def install(target: str = DEFAULT_TARGET) -> None:
    """Copy bundled skills to the agent skills directory."""
    dest = Path(target).expanduser()
    dest.mkdir(parents=True, exist_ok=True)

    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        dest_skill = dest / skill_dir.name
        shutil.copytree(skill_dir, dest_skill, dirs_exist_ok=True)
        logger.info("Installed {} -> {}", skill_dir.name, dest_skill)
