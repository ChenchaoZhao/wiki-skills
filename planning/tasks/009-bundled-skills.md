---
assignee: ""
status: "To Do"
priority: "Medium"
issue_type: "Task"
---
# [Skills] Write bundled wiki-compose and wiki-find SKILL.md files

## Context
Section 7 (Bundled Skills) of the Design Document defines two bundled SKILL.md files that agents load at runtime to know how to compose and find wiki content. wiki-compose teaches the agent OKF frontmatter conventions and the validate workflow. wiki-find teaches the agent to build an index, prefer the sqlite3 CLI for querying state.db, fall back to `wiki-cli query`, and use glob to resolve file paths. Without these skill files the agent has no instructions for interacting with the wiki system.

## Acceptance Criteria
- [ ] `src/wiki_skills/skills/wiki-compose/SKILL.md` created
- [ ] `src/wiki_skills/skills/wiki-find/SKILL.md` created
- [ ] wiki-compose SKILL.md includes: OKF frontmatter reference, workflow steps, validate command usage
- [ ] wiki-find SKILL.md includes: index workflow, sqlite3 preference, wiki-cli query fallback, glob usage
- [ ] SKILL.md files follow agent skill conventions (clear instructions, trigger conditions, step-by-step workflow)
- [ ] Skills are included in package data via pyproject.toml
- [ ] Unit test or smoke test that skill files exist and are non-empty
- [ ] All referenced CLI commands match actual subcommand names

## Technical Notes and Implementation Hints
- Core Files: `src/wiki_skills/skills/wiki-compose/SKILL.md`, `src/wiki_skills/skills/wiki-find/SKILL.md`
- API / Database Schema impact: None — skill files are pure documentation read by agents at runtime
- Include these in package data: configure `[tool.hatch.build.targets.wheel]` or use `include` in pyproject.toml so the SKILL.md files ship with the wheel
- SKILL.md files should be self-contained — agent reads them to know what to do
- Reference actual CLI commands: `wiki-cli index`, `wiki-cli validate`, `wiki-cli query`
- wiki-find should instruct the agent to run `which sqlite3` before deciding which query path to use

## Resources and Design Context
- Design Doc Section: Section 7 — Bundled Skills
- Related Tickets: 004 (index — wiki-find depends on index), 005 (validate — wiki-compose depends on validate), 001 (project scaffolding)
