---
assignee: ""
status: "To Do"
priority: "Medium"
issue_type: "Task"
---
# [CLI] Wire fire-based entry point with all subcommands

## Context
<!-- Reference the specific section of the Design Document. Explain the 'Why'. -->
Section 5 — CLI Entry Point. The CLI is the primary interface for agents. It must be discoverable via `wiki-cli --help` and expose all subcommands: `install`, `index`, `validate`, `query`. Built on `google-python-fire` for automatic flag parsing and help generation.

## Acceptance Criteria
<!-- Absolute, binary criteria derived from the design document. -->
- [ ] `cli.py` with `main()` function using `fire.Fire`
- [ ] All 4 subcommands wired: `install`, `index`, `validate`, `query`
- [ ] `wiki-cli --help` shows all subcommands with descriptions
- [ ] `wiki-cli <subcommand> --help` shows flags for each subcommand
- [ ] Entry point registered in `pyproject.toml` as `wiki-cli = "wiki_skills.cli:main"`
- [ ] Graceful error handling for missing subcommand arguments
- [ ] No logic in `cli.py` beyond wiring — all logic in respective modules
- [ ] Unit test that `main()` can be invoked without error (smoke test)
- [ ] All type annotations present

## Technical Notes and Implementation Hints
<!-- Map this to the system architecture described in the design doc. -->
- Core Files: `src/wiki_skills/cli.py`
- `fire` is declared as a dependency in pyproject.toml (ticket 001)
- Do NOT implement any business logic in this file — pure wiring only
- Use `loguru` for any CLI-level logging if needed

## Resources and Design Context
- Design Doc Section: Section 5 — CLI Entry Point
- Related Tickets: 004 (index), 005 (validate), 006 (query), 007 (install)
