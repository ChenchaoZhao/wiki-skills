---
name: wiki-compose
description: Write or edit wiki content using Open Knowledge Format (OKF). Use when creating, editing, or validating .md files in an OKF wiki bundle.
---

# wiki-compose

Write or edit wiki content using Open Knowledge Format (OKF) conventions and validate it with `wiki-cli`.

## Trigger

Use this skill when the user wants to:
- Create a new wiki page or concept document
- Edit an existing `.md` file in a wiki bundle
- Add or fix OKF frontmatter in markdown files
- Validate wiki content for OKF conformance

## OKF Frontmatter Reference

Every non-reserved `.md` file in a wiki bundle MUST have a YAML frontmatter block delimited by `---`. The `type` field is the only required field.

```yaml
---
type: concept
title: My Concept Title
description: A short description of this concept.
resource: https://example.com/reference
tags:
  - database
  - schema
timestamp: "2026-07-15T10:30:00Z"
---
```

### Fields

| Field | Required | Format | Description |
|---|---|---|---|
| `type` | Yes | Non-empty string | Document type. Defaults to `concept` if absent. |
| `title` | No | String | Human-readable title. |
| `description` | No | String | Short summary of the document. |
| `resource` | No | String (URL) | External reference link. |
| `tags` | No | List of strings | Categorization tags. |
| `timestamp` | No | ISO 8601 | When the document was created or last updated. |

### Reserved Types

Filenames `index.md` and `log.md` are **reserved** and should not be edited with this skill. Their type is inferred from the filename.

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

### Step 1: Understand the bundle structure

Wiki bundles store `.md` files in a directory tree. Each file has a concept ID derived from its path relative to the bundle root (minus the `.md` extension). For example:

```
bundle-root/
├── index.md              # reserved (type=index)
├── users.md              # concept ID: users
└── tables/
    ├── index.md          # reserved (type=index)
    └── orders.md         # concept ID: tables/orders
```

### Step 2: Create or edit the `.md` file

Write the file with correct OKF frontmatter at the top:

```markdown
---
type: concept
title: Orders
description: Order records for the e-commerce system.
tags:
  - database
  - orders
timestamp: "2026-07-15T10:30:00Z"
---

# Orders

Content goes here...
```

### Step 3: Validate the file

Run `wiki-cli validate` to check for conformance errors:

```bash
wiki-cli validate [path]
```

- `[path]` defaults to the current working directory if omitted.
- Exit code `0` means clean, `1` means warnings only, `2` means errors.

### Step 4: Fix and re-validate

If the validate step reports errors, fix the frontmatter and re-run:

```bash
wiki-cli validate [path]
```

Repeat until the output is clean (exit code 0).

## Conformance Rules

| Rule | Severity | Description |
|---|---|---|
| Missing `type` | ERROR | Every non-reserved `.md` must have a non-empty `type` in frontmatter. |
| Invalid frontmatter | ERROR | YAML block cannot be parsed. |
| Bad `timestamp` | WARN | Not valid ISO 8601 format. |
| Bad `tags` | WARN | Not a list of strings. |
| Empty bundle | WARN | No concept files found. |
| Stale index | WARN | `state.db` is out of date; run `wiki-cli index` first. |
