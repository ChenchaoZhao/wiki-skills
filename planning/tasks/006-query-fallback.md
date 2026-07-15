---
assignee: ""
status: "To Do"
priority: "Medium"
issue_type: "Task"
---
# [Query] Implement SQL execution fallback

## Context
<!-- Reference the specific section of the Design Document. Explain the 'Why'. -->
Section 5 — `wiki-cli query`. Execute SQL against `state.db`. Fallback for when `sqlite3` CLI is unavailable.

## Acceptance Criteria
<!-- Absolute, binary criteria derived from the design document. -->
- [ ] `query(sql: str, db: str | None = None) -> None` function in `query.py`
- [ ] Default DB path: `<CWD>/.wiki-skills/state.db`
- [ ] `--db` flag to override DB path
- [ ] Uses Python's `sqlite3` module (stdlib)
- [ ] Executes arbitrary SQL and prints results to stdout
- [ ] Handles missing DB file gracefully with error message
- [ ] Handles SQL syntax errors gracefully with error message
- [ ] Output format: column-separated values with header row
- [ ] Unit tests for: successful query, missing DB, invalid SQL
- [ ] All type annotations present

## Technical Notes and Implementation Hints
<!-- Map this to the system architecture described in the design doc. -->
- Core Files: `src/wiki_skills/query.py`
- Pure stdlib: `sqlite3`, `pathlib`
- Do NOT use `loguru` for query output — print directly to stdout
- For error handling: catch `sqlite3.OperationalError` and `FileNotFoundError`

## Resources and Design Context
- Design Doc Section: Section 5 — `wiki-cli query`
- Related Tickets: 004 (index builder — creates the DB this queries)
