---
assignee: ""
status: "To Do"
priority: "High"
issue_type: "Task"
---
# [Scaffolding] Initialize hatch project structure

## Context

wiki-skills is a Python CLI and agent-skill package with a hatchling build system targeting Python >=3.11. This ticket establishes the foundational project structure including the package layout, entry points, dependencies, and build configuration so all subsequent development has a working foundation.

## Acceptance Criteria

- [ ] `pyproject.toml` created with hatchling build system, Python >=3.11
- [ ] `src/wiki_skills/` package directory exists with `__init__.py` and `__about__.py` containing a version string
- [ ] `wiki-cli` console_scripts entry point defined pointing to `wiki_skills.cli:main`
- [ ] Dependencies declared: `fire`, `loguru`, `markdown-it-py`
- [ ] `hatch fmt` and `hatch test` work (even if tests are empty)
- [ ] All functions have type annotations per AGENTS.md conventions
- [ ] GitHub Actions CI pipeline created (`.github/workflows/ci.yml`) — triggers on new PRs and pushes to `main`, runs `hatch run release` (fmt + typing + tests)
- [ ] GitHub Actions reviewer pipeline created (`.github/workflows/reviewer.yml`) — triggers on new PRs, runs opencode as a code reviewer

## Technical Notes and Implementation Hints

- Core Files: `pyproject.toml`, `src/wiki_skills/__init__.py`, `src/wiki_skills/__about__.py`, `.github/workflows/ci.yml`, `.github/workflows/reviewer.yml`
- API / Database Schema impact: None at this stage
- Security/Performance considerations: Follow AGENTS.md conventions: no magic numbers, type annotations on everything, UPPER_SNAKE_CASE constants

## Resources and Design Context

- Design Doc Section: 1 and 3
- Figma Frame: None
- Related Tickets: None (first ticket)
