import fire
from loguru import logger

from wiki_skills.query import query


def main() -> None:
    """Entry point for wiki-skills CLI."""
    logger.info("wiki-skills CLI")
    fire.Fire({"query": query})


if __name__ == "__main__":
    main()
