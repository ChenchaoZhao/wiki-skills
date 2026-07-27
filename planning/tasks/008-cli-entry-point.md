---
assignee: ""
status: "Done"
priority: "Medium"
issue_type: "Task"
---
# [CLI] Wire fire-based entry point with all subcommands

## Context
<!-- Reference the specific section of the Design Document. Explain the 'Why'. -->
Section 5 — CLI Entry Point. The CLI is the primary interface for agents. It must be discoverable via `wiki-cli --help` and expose all subcommands: `install`, `index`, `validate`, `query`. Built on `google-python-fire` for automatic flag parsing and help generation.

## Acceptance Criteria
<!-- Absolute, binary criteria derived from the design document. -->
- [x] `cli.py` with `main()` function using `fire.Fire`
- [x] All 4 subcommands wired: `install`, `index`, `validate`, `query` ~~(3/4 done; `install` pending ticket 007)~~
- [x] `wiki-cli --help` shows all subcommands with descriptions
- [x] `wiki-cli <subcommand> --help` shows flags for each subcommand
- [x] Entry point registered in `pyproject.toml` as `wiki-cli = "wiki_skills.cli:main"`
- [x] Graceful error handling for missing subcommand arguments
- [x] No logic in `cli.py` beyond wiring — all logic in respective modules
- [x] Unit test that `main()` can be invoked without error (smoke test)
- [x] All type annotations present

## Technical Notes and Implementation Hints
<!-- Map this to the system architecture described in the design doc. -->
- Core Files: `src/wiki_skills/cli.py`
- `fire` is declared as a dependency in pyproject.toml (ticket 001)
- Do NOT implement any business logic in this file — pure wiring only
- Use `loguru` for any CLI-level logging if needed

## Resources and Design Context
- Design Doc Section: Section 5 — CLI Entry Point
- Related Tickets: 004 (index), 005 (validate), 006 (query), 007 (install)

## Notes
- `install` subcommand deferred to ticket 007 — will be wired into `cli.py` once `install.py` is implemented.
- Removed `loguru` import from `cli.py` as it was unused (fire handles all CLI output).
