---
assignee: ""
status: "Done"
priority: "High"
issue_type: "Task"
---
# [Release & Documentation] Repository Structure & README Frontpage

## Context

Finalize task 011 for `wiki-skills`. Reorganize repository management skills from `skills/` to `.skills/`, update `.opencode/skills` symlink, create root `skills/` directory surfacing bundled agent skills (`wiki-compose`, `wiki-find`), and write a polished README.md frontpage with badges, installation instructions (UV and Pip), package purpose, and skill usage.

## Acceptance Criteria

- [x] Current root `skills/` moved to `/.skills/`
- [x] `.opencode/skills` symlink updated to point to `../.skills`
- [x] New root `skills/` directory created with symlinks to `src/wiki_skills/skills/wiki-compose` and `src/wiki_skills/skills/wiki-find`
- [x] Comprehensive `README.md` created at project root with badges (CI, PyPI, Python, License)
- [x] README explains package purpose (Open Knowledge Format / OKF wiki tools for AI agents)
- [x] README includes installation instructions for CLI (UV and Pip) and skill installation (`wiki-cli install`)
- [x] `hatch test`, `hatch fmt`, and `hatch run typing` pass successfully
- [x] Package release github workflow
