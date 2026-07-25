---
assignee: ""
status: "To Do"
priority: "Medium"
issue_type: "Task"
---
# [E2E] End-to-end integration tests via example OKF bundle

## Context
<!-- Reference the specific section of the Design Document. Explain the 'Why'. -->
Unit tests cover individual modules, but no test currently exercises the full CLI workflow end-to-end: creating a wiki bundle, indexing it, validating conformance, and querying the state DB. This gap means regressions in how modules interact (e.g. index producing a DB that validate or query can't consume) would only surface in production. An example bundle with shell-based test scripts provides both a runnable smoke test and a copy-pasteable reference for agents learning the CLI.

## Acceptance Criteria
<!-- Absolute, binary criteria derived from the design document. -->
- [ ] `examples/mini-wiki/` bundle created with at least 3 concept files, `index.md`, and `log.md`
- [ ] All concept files have valid OKF frontmatter matching Section 4 types (`type`, `title`, `description`, `tags`, `resource`, `timestamp`)
- [ ] `examples/mini-wiki/run-tests.sh` is executable and runs the full workflow: `index` → `validate` → `query`
- [ ] `run-tests.sh` exits non-zero on any command failure (`set -euo pipefail`)
- [ ] `run-tests.sh` validates: index produces `.wiki-skills/state.db`, validate exits 0, query returns expected rows
- [ ] `examples/mini-wiki/clean.sh` removes `.wiki-skills/` directory
- [ ] `examples/.gitignore` excludes `.wiki-skills/` so generated outputs are not committed
- [ ] Bundle frontmatter conforms to project OKF types — `type` is non-empty on all concept files
- [ ] Reserved files (`index.md`, `log.md`) have no `type` field in frontmatter

## Technical Notes and Implementation Hints
<!-- Map this to the system architecture described in the design doc. -->
- Core Files: `examples/mini-wiki/run-tests.sh`, `examples/mini-wiki/clean.sh`, `examples/.gitignore`, `examples/mini-wiki/*.md`
- Bundle structure per Section 3 of design doc:
  ```
  examples/mini-wiki/
  ├── index.md          # reserved — directory listing
  ├── log.md            # reserved — update history
  ├── users.md          # concept — root level
  └── tables/
      ├── orders.md     # concept — nested
      └── products.md   # concept — nested
  ```
- Frontmatter fields per Section 4: `type` (required), `title`, `description`, `resource`, `tags`, `timestamp`
- `run-tests.sh` should use `set -euo pipefail` and print each command before running
- `clean.sh` should only remove `.wiki-skills/` — leave source files untouched
- Test queries to run:
  - `wiki-cli query "SELECT path FROM files WHERE type = 'concept'"` — should return 3 rows
  - `wiki-cli query "SELECT path, tags FROM files WHERE tags LIKE '%db%'"` — tag-based lookup
- Use `SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"` in scripts so they work when invoked from any directory

## Resources and Design Context
- Design Doc Section: Section 3 (Bundle Structure), Section 4 (OKF Data Structures), Section 5 (CLI commands)
- OKF Spec: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
- Related Tickets: 001 (project scaffolding), 004 (index builder), 005 (OKF linter), 006 (query fallback), 008 (CLI entry point)
