import pytest

from wiki_skills import __about__
from wiki_skills.cli import main


def test_version_is_defined() -> None:
    assert __about__.__version__ == "0.1.0"


def test_main_exits_via_system_exit() -> None:
    with pytest.raises(SystemExit):
        main()


def test_main_help_shows_subcommands(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("sys.argv", ["wiki-cli", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "index" in captured.err
    assert "validate" in captured.err
    assert "query" in captured.err
