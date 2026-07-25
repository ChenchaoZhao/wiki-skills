import fire

from wiki_skills.index import index
from wiki_skills.query import query
from wiki_skills.validate import validate


def main() -> None:
    """Entry point for wiki-skills CLI."""
    fire.Fire({
        "index": index,
        "validate": validate,
        "query": query,
    })


if __name__ == "__main__":
    main()
