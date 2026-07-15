---
assignee: ""
status: "To Do"
priority: "Medium"
issue_type: "Task"
---
# [Install] Implement skill installation command

## Context
<!-- Reference the specific section of the Design Document. Explain the 'Why'. -->
Section 5 — `wiki-cli install`. Copy bundled skills to the agent skills directory.

| Flag | Default | Description |
|---|---|---|
| `--target` | `~/.agents/skills/` | Destination directory |

Bundled skills live in `src/wiki_skills/skills/` and include:
- `wiki-compose/SKILL.md`
- `wiki-find/SKILL.md`

The install command copies these to the target directory, preserving the directory structure.

## Acceptance Criteria
<!-- Absolute, binary criteria derived from the design document. -->
- [ ] `install(target: str = "~/.agents/skills/") -> None` function (could be in `install.py` or `cli.py`)
- [ ] Default target: `~/.agents/skills/`
- [ ] Expands `~` in target path
- [ ] Creates target directory if it doesn't exist
- [ ] Copies `wiki-compose/SKILL.md` and `wiki-find/SKILL.md` to `<target>/wiki-compose/` and `<target>/wiki-find/`
- [ ] Overwrites existing files silently (idempotent)
- [ ] Uses `shutil.copytree` or equivalent
- [ ] Logs each copied file path
- [ ] Unit tests for: default target expansion, directory creation, file copying
- [ ] All type annotations present

## Technical Notes and Implementation Hints
<!-- Map this to the system architecture described in the design doc. -->
- Core Files: `src/wiki_skills/install.py`
- API / Database Schema impact: None
- Security/Performance considerations: Use `importlib.resources` or `pathlib.Path(__file__).parent / "skills"` to locate bundled files. Use `shutil.copytree(dirs_exist_ok=True)` for Python 3.8+ compatibility (we require 3.11+ so this is fine). Expand `~` with `Path.expanduser()`.

## Resources and Design Context
- Design Doc Section: 5 — `wiki-cli install`
- Related Tickets: 009 (bundled skills must exist to be installed), 001 (project scaffolding)
