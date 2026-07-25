---
assignee: ""
status: "Done"
priority: "Medium"
issue_type: "Task"
---
# [Query] Implement SQL execution fallback

## Context
<!-- Reference the specific section of the Design Document. Explain the 'Why'. -->
Section 5 — `wiki-cli query`. Execute SQL against `state.db`. Fallback for when `sqlite3` CLI is unavailable.

## Acceptance Criteria
<!-- Absolute, binary criteria derived from the design document. -->
- [x] `query(sql: str, db: str | None = None) -> None` function in `query.py`
- [x] Default DB path: `<CWD>/.wiki-skills/state.db`
- [x] `--db` flag to override DB path
- [x] Uses Python's `sqlite3` module (stdlib)
- [x] Executes arbitrary SQL and prints results to stdout
- [x] Handles missing DB file gracefully with error message
- [x] Handles SQL syntax errors gracefully with error message
- [x] Output format: column-separated values with header row
- [x] Unit tests for: successful query, missing DB, invalid SQL
- [x] All type annotations present

## Technical Notes and Implementation Hints
<!-- Map this to the system architecture described in the design doc. -->
- Core Files: `src/wiki_skills/query.py`
- Pure stdlib: `sqlite3`, `pathlib`
- Do NOT use `loguru` for query output — print directly to stdout
- For error handling: catch `sqlite3.OperationalError` and `FileNotFoundError`

## Resources and Design Context
- Design Doc Section: Section 5 — `wiki-cli query`
- Related Tickets: 004 (index builder — creates the DB this queries)
