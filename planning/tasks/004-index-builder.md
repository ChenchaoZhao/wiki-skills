---
assignee: ""
status: "To Do"
priority: "High"
issue_type: "Task"
---
# [Index] Implement SQLite state and incremental rebuild

## Context
<!-- Reference the specific section of the Design Document. Explain the 'Why'. -->
Section 6 — Index Strategy. The index tracks all markdown files in a bundle so the search and lookup layers can query structured metadata without re-parsing every file on each run. An incremental rebuild keeps indexing fast for large bundles by only re-hashing files whose `mtime` has changed, while a `--full` flag allows forcing a complete rebuild when needed.

## Acceptance Criteria
<!-- Absolute, binary criteria derived from the design document. -->
- [ ] `index(path: str = ".", full: bool = False) -> None` function in `index.py`
- [ ] Creates `.wiki-skills/` directory and `state.db` if not exists
- [ ] `CREATE TABLE IF NOT EXISTS` for the `files` table
- [ ] Content hashing uses `hashlib.sha256`
- [ ] Frontmatter extraction from `.md` files (YAML between `---` delimiters)
- [ ] Incremental mode: skips files with unchanged mtime
- [ ] Full mode: re-hashes all files regardless of mtime
- [ ] Deleted files (in DB but not on disk) are removed from DB
- [ ] `tags` stored as JSON string in DB
- [ ] Uses `check_cli("sqlite3")` from deps.py at startup with warning if missing
- [ ] Unit tests for: frontmatter parsing, content hashing, incremental vs full rebuild, deleted file cleanup
- [ ] All type annotations present

## Technical Notes and Implementation Hints
<!-- Map this to the system architecture described in the design doc. -->
- Core Files: `src/wiki_skills/index.py`
- Database Schema: single `files` table as specified below:
  ```sql
  CREATE TABLE files (
      path TEXT PRIMARY KEY,
      type TEXT NOT NULL,
      title TEXT,
      description TEXT,
      resource TEXT,
      tags TEXT,
      timestamp TEXT,
      content_hash TEXT NOT NULL,
      mtime REAL NOT NULL
  );
  ```
- Dependencies: `hashlib` (stdlib), `sqlite3` (stdlib), `json` (stdlib), `pathlib` (stdlib)
- For YAML parsing: check if `yaml` (PyYAML) is available; if not, implement minimal frontmatter parser for the subset needed
- Store DB path as `<bundle_root>/.wiki-skills/state.db`
- Use `loguru` for logging warnings
- CLI usage: `wiki-cli index`, `wiki-cli index ./my-wiki`, `wiki-cli index --full`

## Resources and Design Context
- Design Doc Section: Section 6 — Index Strategy
- Related Tickets: 002 (OKF types), 003 (dependency checks)
