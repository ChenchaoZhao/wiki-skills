import fire
from loguru import logger


def main() -> None:
    """Entry point for wiki-skills CLI."""
    logger.info("wiki-skills CLI")
    fire.Fire()


if __name__ == "__main__":
    main()
