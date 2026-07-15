---
assignee: ""
status: "To Do"
priority: "Medium"
issue_type: "Task"
---
# [Validate] Build OKF conformance linter

## Context
<!-- Reference the specific section of the Design Document. Explain the 'Why'. -->
Lints an OKF bundle for conformance against the rules defined in Section 4. Provides Ruff-style stdout output so users can quickly identify issues in their wiki bundles before indexing or publishing.

## Acceptance Criteria
<!-- Absolute, binary criteria derived from the design document. -->
- [ ] `validate(path: str = ".") -> int` function in `validate.py`, returns exit code (0/1/2)
- [ ] Checks every non-reserved `.md` file has non-empty `type` in frontmatter (ERROR)
- [ ] Handles unparseable YAML frontmatter gracefully (ERROR)
- [ ] Validates `timestamp` is ISO 8601 format (WARN)
- [ ] Validates `tags` is a list of strings (WARN)
- [ ] Detects empty bundle — no concept files found (WARN)
- [ ] Checks `state.db` staleness by comparing file mtimes (WARN)
- [ ] If `state.db` missing, emits WARN
- [ ] Ruff-style output format: `path:line: type: message`
- [ ] Reserved files (`index.md`, `log.md`) are skipped for `type` checks
- [ ] Unit tests for each conformance rule
- [ ] All type annotations present

## Technical Notes and Implementation Hints
<!-- Map this to the system architecture described in the design doc. -->
- Core Files: `src/wiki_skills/validate.py`
- Import `check_cli` from `deps.py` for sqlite3 check
- Import reserved types from `wiki.py`
- For ISO 8601 validation: use `datetime.fromisoformat()` or a simple regex pattern
- For mtime comparison: read stored mtimes from `state.db`, compare with `path.stat().st_mtime`
- API / Database Schema impact: Reads `state.db` for staleness detection; no schema changes
- Security/Performance considerations: Read-only access to `state.db` and filesystem. No subprocess calls beyond stdlib. Must handle missing or corrupt `state.db` gracefully.

## Resources and Design Context
- Design Doc Section: Section 5 — `wiki-cli validate`, Section 4 — Conformance Rules
- Related Tickets: 002 (OKF types), 003 (dependency checks), 004 (index builder — for DB access)
