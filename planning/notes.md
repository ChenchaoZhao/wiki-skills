# Design Session Notes

## Metadata
* **Status:** Complete
* **Current Topic:** All topics resolved
* **Resumption Token:** wiki-skills-v1

## Master TODO List
- [x] 1. OKF Data Structures — directory layout & markdown file schema
- [x] 2. CLI Commands — subcommands, flags, output format
- [x] 3. Index File Strategy — markdown index instead of SQLite
- [x] 4. validate subcommand — OKF conformance linter rules
- [x] 5. Bundled Skills — wiki-compose and wiki-find

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
* **Directory layout:** Bundle root → `index.md` (optional), `log.md` (optional), `<concept>.md` files, `<subdir>/` with same structure. Reserved filenames: `index.md` (type=`index`), `log.md` (type=`log`).
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
| `index` | Walk OKF bundle, update state.db | `--output <path>` (default: `<bundle>/.wiki-skills/`), `--full` (force complete rebuild) |
| `validate` | Lint OKF bundle for conformance + check index staleness | (none — ruff-style stdout output) |
| `query` | Execute SQL against state.db (fallback if sqlite3 CLI unavailable) | `--db <path>` (default: `<bundle>/.wiki-skills/state.db`), positional `SQL` arg |

* **Bundled skills:** `wiki-compose` (write OKF + lint) and `wiki-find` (index + sqlite3 query + glob). Installed via `wiki-cli install`.
* **Agent workflow:** `wiki-cli index` → updates `state.db` → agent uses `sqlite3` CLI to query by type, tags, description → agent uses `glob` on matching file paths to open actual files. No custom query engine. Agents already have sqlite3 and glob tools.
* **Search subcommand:** Not needed. Agents compose sqlite3 + glob natively.

### Index File Strategy — SQLite as Source of Truth
* **Approach:** `wiki-cli index` walks the OKF bundle directory tree, parses frontmatter from each `.md` file, and writes directly to a **SQLite database** (default: `<bundle>/.wiki-skills/state.db`). No markdown index is generated.
* **State format:** `.wiki-skills/state.db` — SQLite database as the sole cache/state. Schema:
  ```sql
  CREATE TABLE files (
      path TEXT PRIMARY KEY,
      type TEXT NOT NULL,
      title TEXT,
      description TEXT,
      resource TEXT,
      tags TEXT,          -- JSON array: '["db","schema"]'
      timestamp TEXT,
      content_hash TEXT NOT NULL,  -- SHA-256 of file content
      mtime REAL NOT NULL         -- file modification time (float, epoch seconds)
  );
  ```
* **Agent query workflow:** Agents use `sqlite3` CLI to query the database directly:
  ```bash
  sqlite3 .wiki-skills/state.db "SELECT path FROM files WHERE type = 'concept'"
  sqlite3 .wiki-skills/state.db "SELECT path FROM files WHERE tags LIKE '%db%'"
  sqlite3 .wiki-skills/state.db "SELECT path, description FROM files WHERE description LIKE '%users%'"
  ```
  If `sqlite3` CLI is unavailable, agents fall back to `wiki-cli query`:
  ```bash
  wiki-cli query "SELECT path FROM files WHERE type = 'concept'"
  ```
  No index regeneration needed — the DB is always current after `wiki-cli index`.
* **Incremental rebuild (content hashing):** No git dependency for change detection. Uses `content_hash` (SHA-256) and `mtime` stored per file:
  1. Walk bundle directory, collect all `.md` files with current `mtime`
  2. For each file: if `mtime` unchanged since last index → skip (fast path)
  3. If `mtime` changed or file is new → re-hash content, compare against stored `content_hash`
  4. Hash differs → re-parse frontmatter, `UPDATE` row
  5. New file → parse frontmatter, `INSERT` row
  6. Deleted file (in DB but not on disk) → `DELETE` row
* **Fallback mode (no git or `--full`):** Same content hashing logic, but skips the mtime optimization — re-hashes every file. Used when git is unavailable OR `--full` flag is passed.

### CLI Dependency Checks
* **Utility function:** `check_cli(name: str) -> bool` — wraps `shutil.which()` to verify a CLI tool is available on PATH. Used at startup by subcommands that depend on external tools.
* **Required CLIs:**

| CLI | Required by | Fallback |
|---|---|---|
| `sqlite3` | `index`, `validate` | Warn + agents use `wiki-cli query` instead (Python sqlite3 module) |
| `grep` | Agent workflows (via bundled skills) | No fallback — agent's responsibility |

* **Startup behavior:** `index` and `validate` call `check_cli("sqlite3")` first. If missing, log warning: `WARN — sqlite3 CLI not found, use 'wiki-cli query' to search state.db`.
* **Note:** `git` is NOT required. Content hashing handles change detection regardless of version control.

### Validate Subcommand — OKF Conformance Linter
* **Output model:** Ruff-style. Human-readable lines to stdout, exit code = worst severity.
  ```
  concepts/users.md:3: WARN — timestamp not ISO 8601
  concepts/old.md:1: ERROR — missing required 'type' field
  ```
* **Exit codes:** `0` = clean, `1` = warnings only, `2` = errors present.
* **No `--strict` flag.** Severity tiers are always shown. Exit code alone determines pass/fail.
* **DB staleness check:** validate checks if `state.db` is stale by comparing file mtimes in the DB against current filesystem mtimes. If any file's mtime is newer than what's stored, emit WARN: `WARN — state.db is stale, run 'wiki-cli index' to update`.
* **DB freshness check:** If `state.db` does not exist, emit WARN: `WARN — state.db not found, run 'wiki-cli index' first`.
* **Validation rules:**

| Rule | Severity | Description |
|---|---|---|
| Missing `type` | ERROR | Every non-reserved `.md` must have a non-empty `type` in frontmatter |
| Invalid frontmatter | ERROR | YAML can't be parsed |
| Bad timestamp format | WARN | Not ISO 8601 |
| Bad tags format | WARN | Not a list of strings |
| Empty bundle | WARN | No concept files found in bundle |
| Index stale | WARN | `state.db` out of date (detected via mtime comparison) |
* **Directory argument:** Optional positional arg for wiki root. Defaults to CWD. `.wiki-skills/` directory lives inside the wiki root.
  ```
  wiki-cli index                 # indexes CWD as wiki root (incremental if git available)
  wiki-cli index ./my-wiki       # indexes specific bundle
  wiki-cli index --full          # forces complete rebuild even if git available
  wiki-cli validate              # validates CWD
  wiki-cli validate ./my-wiki    # validates specific bundle
  wiki-cli query "SELECT path FROM files WHERE type = 'concept'"
  wiki-cli query --db ./my-wiki/.wiki-skills/state.db "SELECT * FROM files"
  ```

### Bundled Skills — Agent Workflows
* **Installed via:** `wiki-cli install` (copies SKILL.md + supporting files to `~/.agents/skills/`)

#### wiki-compose
* **Purpose:** Write or edit wiki content using OKF format. Runs `wiki-cli validate` at the end.
* **Workflow:**
  1. Agent reads OKF data structures from skill reference
  2. Agent writes/edits `.md` files with correct frontmatter
  3. Agent runs `wiki-cli validate [path]` to check conformance
  4. If errors, agent fixes and re-validates

#### wiki-find
* **Purpose:** Find document paths by metadata (type, tags, etc.). Runs `wiki-cli index` first to ensure state.db is current.
* **Workflow:**
  1. Agent runs `wiki-cli index [path]` to build/update state.db
  2. Agent checks if `sqlite3` CLI is available (`which sqlite3`)
  3. If available: agent uses `sqlite3` CLI to query state.db directly
  4. If not: agent uses `wiki-cli query "SQL"` as fallback
  5. Agent uses `glob` on matching paths to open actual files
* **SKILL.md instruction:** Will tell agent to prefer `sqlite3` CLI when available, fall back to `wiki-cli query`.

## Alternatives Considered (For Final Append)
* **SQLite + FTS5 database index:** Rejected — full-text search is over-engineered for the actual workload. Agents can compose `sqlite3` queries + `grep` for content search. FTS5 adds tokenizer config complexity with no payoff.
* **INDEX.md as cache:** Rejected — redundant with SQLite state. Agents can query `state.db` directly via `sqlite3` CLI. No need to regenerate a markdown file that duplicates the same data.
* **Parquet state (pandas):** Rejected — immutable columnar format requires full file rewrite on every row change. No stdlib support, adds pyarrow/fastparquet dependency (~50MB). Worse manual inspection story. SQLite gives native row-level CRUD, stdlib access, and `sqlite3` CLI for ad-hoc queries.
* **JSON state file:** Rejected — slower reads at scale, no columnar access, no standard query language.
* **Flag-based `search` subcommand:** Rejected — hits ceiling on complex queries (OR, joins, aggregations). Flag→SQL translation is maintenance for a caller that doesn't need the abstraction. Agents compose sqlite3 queries natively.
* **Hash-only incremental rebuild (no git):** Rejected — always walks full bundle to compare `content_hash`. Slower, no way to detect deletions without scanning. Content hashing with mtime optimization is strictly better.

## Open Questions (to resume)
* None — all design decisions resolved. Ready for implementation.

## Comprehensive Thoughts & Context
### Project Info
- **Name:** wiki-skills
- **Purpose:** Python CLI + agent-skill package for AI agents to navigate large OKF wikis
- **Key features:** Index generation (SQLite state.db), metadata queries via sqlite3 CLI, path glob, bundled skills (wiki-compose, wiki-find)
- **Stack:** Python >=3.11, hatchling build, fire CLI, loguru, markdown-it-py, sqlite3 (stdlib)
- **Current state:** Empty package (v0.1.0), no source code yet

### OKF Spec Sources
- **Canonical spec:** https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
- **Blog:** https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
- **Community guide:** https://openknowledgeformat.com/
