---
name: implement-task-ticket
description: Implement a task ticket from planning/tasks/. Use when the user says "implement ticket NNN", "do ticket NNN", or similar.
---

# Implement Task Ticket

Implement a single task ticket from `planning/tasks/` end-to-end: read it, implement it, test it, verify it, and mark it done.

## Trigger

User says something like:
- "implement ticket 004"
- "do ticket 002"
- "work on ticket 006"

Extract the ticket number (NNN) from the user's message.

## Workflow

### Step 1: Prepare workspace

Before doing anything else, prepare the git workspace:

```bash
git checkout main
git pull
```

If `git pull` hits a merge conflict, **stop and ask the user** how to resolve it. Do not proceed until the conflict is resolved.

### Step 2: Gather context via subagents

Delegate context gathering to **five parallel subagents**. Each returns a structured summary to you. Do NOT read these files yourself — let the subagents do it.

#### Subagent A — Read ticket
**Type:** `explore`
**Task:** Read `planning/tasks/NNN-*.md` and return the full file contents. If no file matches, return an error.

#### Subagent B — Check prerequisites
**Type:** `explore`
**Task:** Read the ticket at `planning/tasks/NNN-*.md`. Look in the `## Resources and Design Context` section for the `Related Tickets` bullet point. For each related ticket number, read that ticket's YAML frontmatter and return its `status`. If ANY dependency has `status: "To Do"`, return a BLOCKED result listing which tickets must be completed first.

#### Subagent C — Read design doc
**Type:** `explore`
**Task:** Read `planning/design.md`. Look in the ticket's `## Resources and Design Context` section for the `Design Doc Section` bullet point. Identify the matching section(s) in the design doc. Return the full content of those relevant sections plus a brief summary of how they relate to the ticket.

#### Subagent D — Read AGENTS.md
**Type:** `explore`
**Task:** Read `AGENTS.md` in the repo root. Return the full contents. This file contains all coding conventions the implementation must follow.

#### Subagent E — Explore existing code
**Type:** `explore`
**Task:** Read the ticket at `planning/tasks/NNN-*.md` to find the `Core Files` listed in `Technical Notes and Implementation Hints`. Read each listed core file and 2-3 neighboring files. Return the contents of all files read, noting the code style, imports, and patterns used.

### Step 3: Assess and decide

After all five subagents return:

1. **If Subagent A found no ticket** — tell the user and list available tickets. Stop.
2. **If Subagent B returned BLOCKED** — tell the user which prerequisites are incomplete. Stop.
3. **Otherwise** — create the feature branch now that the ticket filename is known:

```bash
git checkout -b ticket/NNN-<slug>
```

Where `<slug>` comes from the ticket filename (e.g., `ticket/004-index-builder`). Then combine the subagent summaries into a mental model of:
   - What the ticket requires (A)
   - What design constraints apply (C)
   - What conventions to follow (D)
   - What existing code looks like (E)

Proceed to implementation.

### Step 4: Implement

Write the code described in the ticket's acceptance criteria:

1. Work through each unchecked `- [ ]` item in `Acceptance Criteria` one by one.
2. Create or modify files as specified in `Technical Notes and Implementation Hints` and ask user for feedback.
3. Follow the database schema exactly if one is specified.
4. Use only the dependencies listed in `pyproject.toml` — do not add new ones without asking.
5. Match the existing code style exactly.
6. Don't assume anything, ask clarification questions if any acceptance criteria are ambiguous.

### Step 5: Write tests

Create or extend test files following AGENTS.md conventions:

- Test file: `tests/test_<module>.py`
- One concept per test, no logic in tests
- Use `@pytest.mark.parametrize` for input variations
- Cover every acceptance criterion that is testable

### Step 6: Verify

Run the full toolchain and fix any issues:

```bash
hatch fmt        # format + lint
hatch test       # run tests
hatch run typing # type check
```

If any step fails, fix the issues and re-run until all three pass cleanly.

Once all three pass, ask the user if they want to commit and push. If yes:

```bash
git add -A
git commit -m "<meaningful commit message summarizing the changes>"
git push -u origin ticket/NNN-<slug>
```

Write a concise commit message that describes what was implemented and why — not just the ticket number. Use imperative mood (e.g., "Add index builder with incremental refresh support").

### Step 7: Mark done

Check off every item in `Acceptance Criteria` that has been implemented and verified

```markdown
- [x] Criterion 1
- [x] Criterion 2
```

If there are any items that could not be implemented, ask user whether we should implement them in this session. If user says no, add a note at the end of the ticket explaining why which also serve as a checkpoint of the progress.

Update the ticket file's frontmatter to reflect the final status:

- **If all criteria are complete**, set `status: "Done"`.
- **If some criteria are incomplete**, set `status: "In Progress"`.

### Step 8: Report

Tell the user:
- Which ticket was implemented
- Which feature branch was created
- What files were created/modified
- Test results (pass count)
- Any decisions or trade-offs made
