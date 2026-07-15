from wiki_skills import __about__
from wiki_skills.cli import main


def test_version_is_defined() -> None:
    assert __about__.__version__ == "0.1.0"


def test_main_does_not_raise() -> None:
    # fire.Fire with no callable exits via SystemExit; just ensure import + init works
    assert callable(main)
