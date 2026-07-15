---
assignee: ""
status: "To Do"
priority: "High"
issue_type: "Task"
---
# [Deps] Implement CLI dependency check utility

## Context
<!-- Reference the specific section of the Design Document. Explain the 'Why'. -->
CLI tools like `sqlite3` and `grep` are used by various commands and agent workflows, but are not guaranteed to be present on every system. Rather than failing hard at runtime, the CLI should detect missing tools early and either warn or fall back gracefully. This utility provides the foundation for that behavior.

## Acceptance Criteria
<!-- Absolute, binary criteria derived from the design document. -->
- [ ] `check_cli(name: str) -> bool` function exists in `deps.py`
- [ ] Uses `shutil.which()` internally
- [ ] Returns `True` if tool is found on PATH, `False` otherwise
- [ ] `REQUIRED_CLI_TOOLS` constant defined as `frozenset({"sqlite3", "grep"})`
- [ ] Unit tests for `check_cli` — test with a known tool (e.g., `"python"`) and a non-existent tool
- [ ] No external dependencies beyond stdlib

## Technical Notes and Implementation Hints
<!-- Map this to the system architecture described in the design doc. -->
- Core Files: `src/wiki_skills/deps.py`
- API / Database Schema impact: None
- Security/Performance considerations: Pure stdlib — `shutil.which` only. No subprocess calls. Loguru is available for warning output at call sites (not inside `check_cli` itself — it just returns bool).

## Resources and Design Context
- Design Doc Section: Section 5 — CLI Dependency Checks
- Related Tickets: 001 (project scaffolding must exist first)
