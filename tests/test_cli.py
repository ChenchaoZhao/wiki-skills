import pytest

from wiki_skills import __about__
from wiki_skills.cli import main


def test_version_is_defined() -> None:
    assert __about__.__version__ == "0.1.0"


def test_main_exits_via_system_exit() -> None:
    with pytest.raises(SystemExit):
        main()
