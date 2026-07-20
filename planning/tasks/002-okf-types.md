---
assignee: ""
status: "Done"
priority: "High"
issue_type: "Task"
---
# [Types] Define OKF metadata TypedDict and constants

## Context
<!-- Reference the specific section of the Design Document. Explain the 'Why'. -->
Section 4 of the design document defines OKF data structures in Python. These types are foundational for all downstream parsing, validation, and serialization of wiki concept documents. Without these types, no other component can correctly handle concept frontmatter.

## Acceptance Criteria
<!-- Absolute, binary criteria derived from the design document. -->
- [x] `DocumentMetadata` TypedDict defined in `wiki.py` with all fields from spec: `type`, `title`, `description`, `resource`, `tags`, `timestamp`
- [x] `type` field is required (not `NotRequired`), all others are `NotRequired`
- [x] `RESERVED_TYPES` constant defined as `frozenset({"index", "log"})`
- [x] `document_id_from_path(path: str, root: str) -> str` helper function that strips `.md` extension and returns relative path
- [x] All type annotations present, no `# type: ignore` without explanation
- [x] Unit tests for `concept_id_from_path` with nested paths, root-level files, and edge cases

## Technical Notes and Implementation Hints
<!-- Map this to the system architecture described in the design doc. -->
- Core Files: `src/wiki_skills/wiki.py`
- API / Database Schema impact: None — pure in-memory types
- Security/Performance considerations: None — no external I/O or user input handling in this ticket
- Use `from __future__ import annotations` for forward references
- Define `DEFAULT_TYPE` constant if there is a fallback type value
- Preserve unknown keys — use `total=False` on TypedDict so extra keys pass through

## Resources and Design Context
- Design Doc Section: Section 4 — OKF data structures
- Related Tickets: 001 (project scaffolding must exist first)
