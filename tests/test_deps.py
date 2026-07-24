from wiki_skills.deps import REQUIRED_CLI_TOOLS, check_cli


def test_required_cli_tools_is_frozenset() -> None:
    assert frozenset({"sqlite3", "grep"}) == REQUIRED_CLI_TOOLS


def test_check_cli_returns_true_for_existing_tool() -> None:
    assert check_cli("python3") is True


def test_check_cli_returns_false_for_nonexistent_tool() -> None:
    assert check_cli("nonexistent_tool_xyz_12345") is False
