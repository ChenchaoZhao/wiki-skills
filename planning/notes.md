# Design Session Notes

## Metadata
* **Status:** In Progress
* **Current Topic:** CLI Commands — resolved, proceed to next topic
* **Resumption Token:** wiki-skills-v1

## Master TODO List
- [x] 1. OKF Data Structures — directory layout & markdown file schema
- [x] 2. CLI Commands — subcommands, flags, output format
- [ ] 3. Database Schema — SQLite tables, indexes, FTS config
- [ ] 4. Sync Strategy — keeping DB in sync with live-edited OKF docs
- [ ] 5. validate subcommand — OKF conformance linter rules

## Finalized Decisions

### OKF Data Structures — Python Representation
* **OKF metadata → `TypedDict`** with `type` as required field, all others optional:
  ```python
  class ConceptMetadata(TypedDict, total=False):
      type: str  # REQUIRED — non-empty
      title: NotRequired[str]
      description: NotRequired[str]
      resource: NotRequired[str]
      tags: NotRequired[list[str]]
      timestamp: NotRequired[str]  # ISO 8601
  ```
* **Directory layout:** Bundle root → `index.md` (optional), `log.md` (optional), `<concept>.md` files, `<subdir>/` with same structure. Reserved filenames: `index.md`, `log.md`.
* **Concept ID:** File path minus `.md` extension (e.g., `tables/users.md` → `tables/users`).
* **Frontmatter:** `type` (REQUIRED), `title`, `description`, `resource`, `tags`, `timestamp` (recommended). Any additional k/v allowed. Consumers must preserve unknown keys.
* **Conformance:** Non-reserved `.md` files must have parseable YAML frontmatter with non-empty `type`. Consumers MUST NOT reject for missing optional fields, unknown types/keys, broken links, or missing `index.md`.

### CLI Commands — wiki-cli entrypoint
* **Entry point:** `wiki-cli` (installed via `uv tool run` or `uv tool install`).
* **Primary caller:** AI agent. Agent installs package, invokes CLI directly.
* **Subcommands:**

| Subcommand | Purpose | Key flags |
|---|---|---|
| `install` | Install SKILL.md + supporting files to agent skills dir | `--target <dir>` (default: `~/.agents/skills/`) |
| `index` | Build/update SQLite index of an OKF bundle | `--output <path>` (default: `<bundle>/.wiki-skills/index.db`) |
| `query` | Execute raw SQL against the index | positional: SQL string |
| `schema` | Print table DDL + example queries | (none) |
| `validate` | Lint OKF bundle for conformance | (TBD) |

* **Query interface:** Raw SQL only (no flag-based search sugar). Agents can generate SQL trivially; flag→SQL translation layer is unnecessary maintenance. `schema` subcommand makes `query` self-serve by exposing table structure + examples.
* **Search subcommand:** Deferred. May add as sugar later once real agent usage reveals which flag combos are common.

## Alternatives Considered (For Final Append)
* **Flag-based `search` subcommand:** Rejected — hits ceiling on complex queries (OR, joins, aggregations). Flag→SQL translation is maintenance for a caller that doesn't need the abstraction. May revisit as sugar later.
* **Unified `search --sql` passthrough:** Rejected — two modes in one command creates ambiguity (combine flags + SQL? or mutually exclusive?). Doubled error surface. Separate `query` is cleaner.
* **Hardcoded skills directory for `install`:** Rejected in favor of configurable `--target` with default `~/.agents/skills/`. More agent-agnostic.

### Query Output Format
* **Default:** Plain text, one relative path per line. Zero parsing overhead, minimal tokens for agents.
* **`--format jsonl`:** Opt-in for structured output with metadata (title, tags, timestamp, etc.).
* **No table format** — agents don't need pretty-printed columns.

### Incremental Indexing
* **Change detection:** Mtime + SHA-256 content hash. Check mtime first, re-hash only if mtime changed. Fast for unchanged files, accurate for all edits.

## Open Questions (to resume)
* `validate` subcommand — rules to check: (1) required frontmatter with non-empty `type`, (2) reserved filename conventions, (3) ISO 8601 timestamps, (4) tags as list of strings, (5) broken cross-links, (6) empty bundle warnings. Strictness mode TBD (strict vs lenient vs configurable `--strict`).

## Comprehensive Thoughts & Context
### Project Info
- **Name:** wiki-skills
- **Purpose:** Python CLI + agent-skill package for AI agents to navigate large OKF wikis
- **Key features:** High-performance indexing, SQL querying, metadata-based file search
- **Stack:** Python >=3.11, hatchling build, fire CLI, loguru, markdown-it-py
- **Current state:** Empty package (v0.1.0), no source code yet

### OKF Spec Sources
- **Canonical spec:** https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
- **Blog:** https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
- **Community guide:** https://openknowledgeformat.com/
