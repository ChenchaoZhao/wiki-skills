---
name: wiki-find
description: Find wiki documents by metadata (type, tags, description) using the SQLite index. Use when searching, querying, or navigating an OKF wiki bundle.
---

# wiki-find

Find document paths in an OKF wiki bundle by querying the SQLite index (`state.db`).

## Trigger

Use this skill when the user wants to:
- Find wiki pages by type, tags, or other metadata
- Search for documents matching a description
- List all concepts, indexes, or logs in a bundle
- Navigate or explore a wiki bundle's contents

## Workflow

### Step 0: Ensure `wiki-skills` is installed

The `wiki-cli` commands require the `wiki-skills` package. Verify it is installed:

```bash
wiki-cli --version
```

If the command fails, install the package first:

```bash
uv tool install wiki-skills
```

### Step 1: Build or update the index

Before querying, ensure the index is current:

```bash
wiki-cli index [path]
```

- `[path]` defaults to the current working directory if omitted.
- This creates or updates `.wiki-skills/state.db` with metadata from all `.md` files.

### Step 2: Check for `sqlite3` CLI

Determine the preferred query method:

```bash
which sqlite3
```

### Step 3: Query the index

#### Preferred: `sqlite3` CLI (when available)

```bash
sqlite3 .wiki-skills/state.db "SELECT path FROM files WHERE type = 'concept'"
```

#### Fallback: `wiki-cli query`

```bash
wiki-cli query "SELECT path FROM files WHERE type = 'concept'"
```

- When `--db` is omitted, `wiki-cli query` uses `<CWD>/.wiki-skills/state.db`.

### Step 4: Resolve file paths

Query results return relative paths. Use the `glob` tool to resolve these to actual filesystem paths: e.g. `tables/orders` glob pattern: `**/tables/orders.md`


## Database Schema

The `files` table in `state.db` has these columns:

| Column | Type | Description |
|---|---|---|
| `path` | TEXT (PK) | Relative path from bundle root (e.g., `tables/orders.md`). |
| `type` | TEXT | Document type (e.g., `concept`, `index`, `log`). |
| `title` | TEXT | Document title (nullable). |
| `description` | TEXT | Short description (nullable). |
| `resource` | TEXT | External reference URL (nullable). |
| `tags` | TEXT | JSON array of tag strings (nullable). |
| `timestamp` | TEXT | ISO 8601 timestamp (nullable). |
| `content_hash` | TEXT | SHA-256 hash of file content. |
| `mtime` | REAL | File modification time (epoch seconds). |

## Example Queries

```sql
-- Find all concept files
SELECT path FROM files WHERE type = 'concept';

-- Find files tagged "database"
SELECT path FROM files WHERE tags LIKE '%database%';

-- Find files with a specific title
SELECT path, title FROM files WHERE title = 'Orders';

-- Search descriptions
SELECT path, description FROM files WHERE description LIKE '%users%';

-- List all unique types
SELECT DISTINCT type FROM files;

-- Find files modified after a timestamp
SELECT path, mtime FROM files WHERE mtime > 1700000000;
```
