# CapCut Assistance Skills Collection Design

## Summary

This repository should be restructured from a single flat skill repo into a skills collection repo that is installable through the public `skills` CLI.

The first published skill will be `capcut-assistance`, and users should be able to install it with:

```bash
npx skills add <owner>/<repo> --skill capcut-assistance
```

The repo should be designed so future CapCut skills can be added without another top-level reorganization.

## Goals

- Make the repository compatible with `npx skills add ... --skill capcut-assistance`
- Publish `capcut-assistance` as the first installable skill in the repo
- Keep the actual editing logic in reusable Python modules rather than embedding behavior in the skill doc
- Preserve cross-agent portability for agents that support the same skill format
- Create a structure that can grow into a multi-skill CapCut collection

## Non-Goals

- Publishing multiple new skills in this change
- Adding agent-specific UI automation
- Rewriting the dead-air workflow engine
- Converting the implementation into a packaged Python library on PyPI

## Current State

The repository currently behaves like a single-skill project:

- root-level `SKILL.md`
- shared implementation under `scripts/`
- tests under `tests/`
- support tools under `tools/`
- compatibility notes in `docs/agent-compatibility.md`

This works for local use, but it does not match the typical public skills collection layout used by repositories installed via `npx skills add`.

## Proposed Repository Structure

The repository should become a collection with a dedicated `skills/` directory:

```text
capcut-skills/
  README.md
  skills/
    capcut-assistance/
      SKILL.md
      README.md                # optional short skill-specific notes
  scripts/
    capcut_schema.py
    detect_dead_air.py
    patch_capcut_draft.py
    validate_capcut_draft.py
    workflow.py
    write_cut_report.py
  tools/
    run_pytest.py
    inspect_silence.py
  tests/
  docs/
    agent-compatibility.md
    superpowers/
      specs/
      plans/
```

## Why This Structure

This layout separates two concerns clearly:

- `skills/capcut-assistance/` is the installable skill surface
- `scripts/`, `tools/`, and `tests/` are the reusable implementation and maintenance surface

That makes the public skill small and discoverable, while keeping the operational logic centralized and shareable across future CapCut skills.

## Skill Contract

The `capcut-assistance` skill should act as a thin orchestration entrypoint.

Responsibilities of `skills/capcut-assistance/SKILL.md`:

- describe when the skill should be used
- define preflight safety checks
- instruct the agent to run the Python workflow
- document required runtime dependencies
- point to the generated report files
- avoid agent-specific commands or slash-command dependencies

Responsibilities explicitly kept out of the skill doc:

- silence detection implementation details
- draft patching logic
- JSON mutation logic
- report generation logic

Those behaviors should remain in Python so the same skill can work across Claude, Codex, and other compatible agents.

## Naming

The first public skill should be named `capcut-assistance`.

Rationale:

- broad enough to remain accurate as the repo grows beyond dead-air removal
- specific enough to be discoverable for CapCut editing tasks
- stable install target for the public skill ecosystem

The repository may still be named something like `capcut-skills`, but the installable skill name should be `capcut-assistance`.

## Installation and Usage Contract

The public contract should be:

```bash
npx skills add <owner>/<repo> --skill capcut-assistance
```

After installation, the skill should instruct the agent to run a command equivalent to:

```bash
python -m scripts.workflow --draft-folder "<draft-folder>"
```

Optional tuned detection flags may also be documented for aggressive dead-air removal:

```bash
python -m scripts.workflow \
  --draft-folder "<draft-folder>" \
  --silence-threshold-db -28 \
  --min-silence-ms 150 \
  --lead-padding-ms 60 \
  --tail-padding-ms 90 \
  --max-gap-ms 40 \
  --min-keep-ms 250
```

## Dependency Contract

The repo should document these runtime assumptions:

- Python is available
- `ffmpeg` is available, either on `PATH` or via explicit `--ffmpeg-bin`
- the agent can read files and execute shell commands

The skill should not depend on:

- proprietary agent SDK features
- UI automation
- editor-specific command palettes
- MCP-only behavior

## Documentation Changes

The repository should gain a root `README.md` that explains:

- what the repo is
- the exact `npx skills add` install command
- the available skills in the collection
- local runtime requirements
- an example workflow command

The old root `SKILL.md` should no longer be the primary install surface. It should either:

- be removed after the skill is moved into `skills/capcut-assistance/SKILL.md`, or
- be replaced with a short pointer for repository visitors during the transition

`docs/agent-compatibility.md` should be updated to describe the collection model instead of the old flat-root skill layout.

## Future Growth Model

Future skills should be added as siblings under `skills/`, for example:

- `skills/capcut-subtitle-cleanup/`
- `skills/capcut-broll-assistance/`
- `skills/capcut-export-helper/`

All future skills should prefer shared reusable modules under `scripts/` whenever possible.

This avoids duplicating parsing, validation, backup, patching, or reporting logic.

## Migration Plan

1. Add `skills/capcut-assistance/`
2. Move or rewrite the current root skill content into `skills/capcut-assistance/SKILL.md`
3. Add a root `README.md` with install instructions
4. Update compatibility docs to reference `npx skills add ... --skill capcut-assistance`
5. Keep the current Python entrypoint stable so the new skill path does not change the implementation command
6. Verify the repo still works locally and that documentation points at the new skill location consistently

## Testing and Verification

Verification for this restructuring should cover:

- existing Python tests still pass
- the new `skills/capcut-assistance/SKILL.md` is present and internally consistent
- the root `README.md` exposes the correct install command
- documentation no longer tells users the root `SKILL.md` is the primary install target

If feasible, the repo should also be sanity-checked against the expected file layout used by public `skills` installers.

## Open Questions Resolved

- Single skill vs collection: collection
- Public skill name: `capcut-assistance`
- Runtime implementation location: shared Python modules outside the skill folder
- Portability target: any agent CLI that supports the same skill format and shell execution model

## Success Criteria

This design is successful when:

- a user can install the skill with `npx skills add <owner>/<repo> --skill capcut-assistance`
- the installed skill contains portable instructions rather than agent-specific hacks
- the repo can add a second CapCut skill later without another structural migration
- the existing dead-air workflow remains callable through the skill after the reorganization
