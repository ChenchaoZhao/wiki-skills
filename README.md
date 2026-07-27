# wiki-skills

[![CI](https://github.com/chenchaozhao/wiki-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/chenchaozhao/wiki-skills/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/wiki-skills?cacheSeconds=10)](https://pypi.org/project/wiki-skills/)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Agent tools and skills to read, write, navigate, and validate wikis in Open Knowledge Format (OKF).

---

## Why `wiki-skills`?

As AI agents work with larger and more complex codebases and documentation repositories, flat Markdown files quickly become difficult to navigate, query, and maintain. **Open Knowledge Format (OKF)** standardizes wiki bundles with structured frontmatter (`type`, `tags`, `timestamp`, etc.) and reserved documents (`index.md`, `log.md`).

`wiki-skills` provides:
- **CLI Utilities (`wiki-cli`)** — High-performance indexing into SQLite state, OKF conformance linting, raw concept querying, and skill installation.
- **Bundled Agent Skills (`skills/`)** — Purpose-built workflows for AI agents (`wiki-compose` and `wiki-find`) to author, validate, and search knowledge bases efficiently.
- **SQLite State Caching** — Incremental index rebuilding via content hashing for instant retrieval.

---

## Installation

### Package & CLI

```bash
# Install with uv (recommended)
uv tool install wiki-skills

# Or with pip
pip install wiki-skills
```

### Agent Skills

To install the bundled agent skills into your agent environment (`~/.agents/skills/` by default):

```bash
wiki-cli install
```

Or specify a custom target directory:
```bash
wiki-cli install --target ~/.config/opencode/skills/
```

---

## CLI Usage

`wiki-cli` exposes four core subcommands:

### 1. `wiki-cli index`
Walks an OKF bundle, parses frontmatter, and writes/updates SQLite state (`.wiki-skills/state.db`) using incremental content hashing.
```bash
wiki-cli index                # Indexes current working directory
wiki-cli index ./my-wiki      # Indexes specific bundle path
wiki-cli index --full         # Forces complete rebuild
```

### 2. `wiki-cli validate`
Lints an OKF bundle for conformance issues (missing required `type`, invalid frontmatter, malformed tags/timestamps) with structured output.
```bash
wiki-cli validate             # Validates current directory
wiki-cli validate ./my-wiki   # Validates specific bundle path
```

### 3. `wiki-cli query`
Executes SQL queries against the wiki SQLite state (`state.db`) with fallback handling.
```bash
wiki-cli query "SELECT concept_id, type FROM concepts WHERE type = 'concept'"
```

### 4. `wiki-cli install`
Copies bundled agent skills (`wiki-compose`, `wiki-find`) to the agent skill directory.
```bash
wiki-cli install --target ~/.agents/skills/
```

---

## Bundled Skills

The `skills/` directory contains ready-to-use agent skills:
- **`wiki-compose`** — Guidance for AI agents on writing and editing OKF wiki documents and validating conformance.
- **`wiki-find`** — Workflows for searching, querying SQLite state, and navigating wiki structures.

---

## Development

```bash
# Install hatch
uv tool install hatch

# Run full release check (linting, static typing with mypy, and test suite with coverage)
hatch run release
```

---

## License

MIT
