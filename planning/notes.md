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
| `index` | Walk OKF bundle, generate INDEX.md + state.parquet | `--output <path>` (default: `<bundle>/.wiki-skills/`) |
| `validate` | Lint OKF bundle for conformance + check index staleness | (none — ruff-style stdout output) |

* **Bundled skills:** `wiki-compose` (write OKF + lint) and `wiki-find` (index + grep + glob). Installed via `wiki-cli install`.
* **Agent workflow:** `wiki-cli index` → generates INDEX.md → agent uses `grep` to search metadata (type, tags, etc.) → agent uses `glob` on matching file paths. No database, no custom query engine. Agents already have grep and glob tools.
* **Search subcommand:** Not needed. Agents compose grep + glob natively.

### Index File Strategy — Markdown over SQLite
* **Approach:** `wiki-cli index` walks the OKF bundle directory tree, parses frontmatter from each `.md` file, and writes a single **markdown index file** (default: `<bundle>/.wiki-skills/INDEX.md`).
* **State format:** `.wiki-skills/state.parquet` — pandas DataFrame as the cache/state. INDEX.md is always derived from this state, never the source of truth. Columns: `path`, `type`, `title`, `description`, `resource`, `tags` (list[str], parquet list column), `timestamp`, `content_hash`. Sorted by: `path`, `type`, `timestamp`.
* **Incremental rebuild:** Load existing parquet into DataFrame, walk bundle, compare `content_hash` per file. In-place updates:
  - New files → parse frontmatter, `pd.concat` new row
  - Changed files → re-parse, update row in-place
  - Deleted files → `df.drop` row
  - Write parquet → regenerate INDEX.md from DataFrame
* **Index format:** Three sections, all grep-friendly.
  ```markdown
  # Wiki Index

  ## Table

  | Path | Type | Title | Tags | Timestamp |
  |---|---|---|---|---|
  | concepts/index.md | index | Concepts Index | | 2026-07-01 |
  | concepts/log.md | log | Concepts Log | | 2026-07-01 |
  | concepts/tables.md | concept | Tables | schema, db | 2026-07-01 |
  | concepts/tables/users.md | concept | Users Table | schema, db | 2026-07-02 |

  ## Documents by Tags

  ### tag :: db
  - concepts/tables.md
  - concepts/tables/users.md

  ### tag :: schema
  - concepts/tables.md
  - concepts/tables/users.md

  ## Documents by Types

  ### type :: concept
  - concepts/tables.md
  - concepts/tables/users.md

  ### type :: index
  - concepts/index.md

  ### type :: log
  - concepts/log.md
  ```
* **Agent grep patterns:**
  - `grep "type :: concept" INDEX.md` → all concept files
  - `grep "tag :: db" INDEX.md` → all files tagged "db"
  - `grep "| concept |" INDEX.md` → concept rows in table
* **Generation from DataFrame:**
  ```python
  def generate_index_md(df: pd.DataFrame) -> str:
      lines: list[str] = ["# Wiki Index", ""]

      # Section 1: Table
      lines += ["## Table", ""]
      lines += ["| Path | Type | Title | Tags | Timestamp |",
                 "|---|---|---|---|---|"]
      for _, row in df.iterrows():
          tags = ", ".join(row["tags"]) if row["tags"] else ""
          lines.append(f"| {row['path']} | {row['type']} | {row['title']} | {tags} | {row['timestamp']} |")

      # Section 2: Documents by Tags (explode for speed)
      lines += ["", "## Documents by Tags", ""]
      has_tags = df[df["tags"].apply(lambda x: isinstance(x, list) and len(x) > 0)]
      exploded = has_tags.explode("tags")
      for tag, group in exploded.groupby("tags")["path"].apply(sorted).items():
          lines += [f"### tag :: {tag}", ""]
          lines += [f"- {p}" for p in group]
          lines.append("")

      # Section 3: Documents by Types
      lines += ["## Documents by Types", ""]
      for type_name, group in df.groupby("type")["path"].apply(list).items():
          lines += [f"### type :: {type_name}", ""]
          lines += [f"- {p}" for p in group]
          lines.append("")

      return "\n".join(lines)
  ```

### Validate Subcommand — OKF Conformance Linter
* **Output model:** Ruff-style. Human-readable lines to stdout, exit code = worst severity.
  ```
  concepts/users.md:3: WARN — timestamp not ISO 8601
  concepts/old.md:1: ERROR — missing required 'type' field
  ```
* **Exit codes:** `0` = clean, `1` = warnings only, `2` = errors present.
* **No `--strict` flag.** Severity tiers are always shown. Exit code alone determines pass/fail.
* **Index staleness check:** validate also checks if `.wiki-skills/index.md` is up to date. It walks the bundle, builds what the index *should* contain, then diffs against the existing index file. Warns if stale (files added/removed/changed since last `index` run).
* **Validation rules:**

| Rule | Severity | Description |
|---|---|---|
| Missing `type` | ERROR | Every non-reserved `.md` must have a non-empty `type` in frontmatter |
| Invalid frontmatter | ERROR | YAML can't be parsed |
| Bad timestamp format | WARN | Not ISO 8601 |
| Bad tags format | WARN | Not a list of strings |
| Empty bundle | WARN | No concept files found in bundle |
| Index stale | WARN | `.wiki-skills/INDEX.md` out of date (or missing) |
* **Directory argument:** Optional positional arg for wiki root. Defaults to CWD. `.wiki-skills/` directory lives inside the wiki root.
  ```
  wiki-cli index                 # indexes CWD as wiki root
  wiki-cli index ./my-wiki       # indexes specific bundle
  wiki-cli validate              # validates CWD
  wiki-cli validate ./my-wiki    # validates specific bundle
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
* **Purpose:** Find document paths by metadata (type, tags, etc.). Runs `wiki-cli index` first to ensure index is current.
* **Workflow:**
  1. Agent runs `wiki-cli index [path]` to build/update INDEX.md
  2. Agent uses `grep` on INDEX.md to search by type, tag, or content
  3. Agent uses `glob` on matching paths to open actual files

## Alternatives Considered (For Final Append)
* **SQLite + FTS5 database index:** Rejected — over-engineered for the actual caller (AI agents). Agents already have grep/glob. SQLite adds complexity (FTS5 tokenizer config, WAL mode, foreign keys, schema migration) with no payoff over a simple markdown file that grep can search.
* **INDEX.md as cache (parse-and-diff):** Rejected — couples output format to rebuild logic. If INDEX.md format changes, rebuild breaks. Cleaner to have a structured state (parquet) and derive output from it.
* **JSON state file:** Rejected — slower reads at scale, no columnar access. Parquet with pandas gives in-place row updates and fast I/O.
* **Flag-based `search` subcommand:** Rejected — hits ceiling on complex queries (OR, joins, aggregations). Flag→SQL translation is maintenance for a caller that doesn't need the abstraction. May revisit as sugar later.
* **Unified `search --sql` passthrough:** Rejected — two modes in one command creates ambiguity (combine flags + SQL? or mutually exclusive?). Doubled error surface. Separate `query` is cleaner.
* **Hardcoded skills directory for `install`:** Rejected in favor of configurable `--target` with default `~/.agents/skills/`. More agent-agnostic.
* **JSONL output format:** Deferred — markdown table is sufficient and more human-readable. Can add `--format jsonl` later if needed.
* **Comma-separated tags string:** Replaced with `list[str]` in parquet. Avoids delimiter ambiguity with multi-word tags, leverages parquet's native list column type.

## Open Questions (to resume)
* None — all design decisions resolved. Ready for implementation.

## Comprehensive Thoughts & Context
### Project Info
- **Name:** wiki-skills
- **Purpose:** Python CLI + agent-skill package for AI agents to navigate large OKF wikis
- **Key features:** Index generation (parquet state → markdown output), metadata grep, path glob, bundled skills (wiki-compose, wiki-find)
- **Stack:** Python >=3.11, hatchling build, fire CLI, loguru, markdown-it-py, pandas (parquet I/O)
- **Current state:** Empty package (v0.1.0), no source code yet

### OKF Spec Sources
- **Canonical spec:** https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
- **Blog:** https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
- **Community guide:** https://openknowledgeformat.com/
