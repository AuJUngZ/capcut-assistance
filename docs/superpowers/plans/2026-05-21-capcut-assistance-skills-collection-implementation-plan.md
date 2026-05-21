# CapCut Assistance Skills Collection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure this repository into a public skills collection that exposes `capcut-assistance` as an installable skill via `npx skills add <owner>/<repo> --skill capcut-assistance`.

**Architecture:** Keep the CapCut editing logic in shared Python modules under `scripts/`, and move the installable skill surface into `skills/capcut-assistance/`. Publish the repository contract through a root `README.md`, update compatibility docs to match the collection layout, and add a small repo-structure test that verifies the new install surface stays intact.

**Tech Stack:** Markdown skill files, Python 3, pytest via `tools/run_pytest.py`, GitHub-hosted skills collection layout

---

## File Structure

### Create

- `C:\Coding\capcut-skills\README.md`
- `C:\Coding\capcut-skills\skills\capcut-assistance\SKILL.md`
- `C:\Coding\capcut-skills\skills\capcut-assistance\README.md`
- `C:\Coding\capcut-skills\tests\test_skill_repo_layout.py`

### Modify

- `C:\Coding\capcut-skills\.gitignore`
- `C:\Coding\capcut-skills\docs\agent-compatibility.md`

### Delete

- `C:\Coding\capcut-skills\SKILL.md`

### Responsibilities

- `README.md`: public landing page, exact install command, dependency list, usage examples
- `skills/capcut-assistance/SKILL.md`: installable portable skill entrypoint for agent CLIs
- `skills/capcut-assistance/README.md`: short skill-local notes for humans browsing the repo
- `docs/agent-compatibility.md`: collection-oriented compatibility guidance instead of flat-root guidance
- `tests/test_skill_repo_layout.py`: regression checks for skill location, install docs, and collection contract
- `.gitignore`: keep local draft fixtures and generated artifacts out of the public repo

### Task 1: Move the Install Surface into `skills/capcut-assistance`

**Files:**
- Create: `C:\Coding\capcut-skills\skills\capcut-assistance\SKILL.md`
- Create: `C:\Coding\capcut-skills\skills\capcut-assistance\README.md`
- Create: `C:\Coding\capcut-skills\tests\test_skill_repo_layout.py`
- Delete: `C:\Coding\capcut-skills\SKILL.md`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_text(*parts: str) -> str:
    return ROOT.joinpath(*parts).read_text(encoding="utf-8")


def test_installable_skill_lives_under_skills_directory() -> None:
    text = read_text("skills", "capcut-assistance", "SKILL.md")
    assert "name: capcut-assistance" in text
    assert "python -m scripts.workflow --draft-folder" in text


def test_root_skill_file_is_removed() -> None:
    assert not ROOT.joinpath("SKILL.md").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
rtk powershell -Command "& 'C:\Users\nonga\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'C:\Coding\capcut-skills\tools\run_pytest.py' 'C:\Coding\capcut-skills\tests\test_skill_repo_layout.py' -v"
```

Expected:

- FAIL because `skills/capcut-assistance/SKILL.md` does not exist yet
- FAIL because root `SKILL.md` still exists

- [ ] **Step 3: Write the minimal implementation**

Create `C:\Coding\capcut-skills\skills\capcut-assistance\SKILL.md` with this content:

```md
---
name: capcut-assistance
description: Use when a CapCut draft already exists and an agent should safely remove dead air, preserve backups, and report timeline edits through shell commands.
---

# CapCut Assistance

## When to Use
- A CapCut draft folder already exists
- Source media is already present on the timeline
- The user wants silence trimming without manual CapCut UI editing

## Preflight Checks
- Confirm `<draft-folder>/draft_content.json` exists
- Confirm `<draft-folder>/Timelines/project.json` exists
- Confirm source media paths still resolve
- Refuse to patch when validation fails or nearly all content would be removed

## Default Command
Run `python -m scripts.workflow --draft-folder "<draft-folder>"`

## More Aggressive Silence Removal
Run `python -m scripts.workflow --draft-folder "<draft-folder>" --silence-threshold-db -28 --min-silence-ms 150 --lead-padding-ms 60 --tail-padding-ms 90 --max-gap-ms 40 --min-keep-ms 250`

## Outputs
- `dead_air_report.json`
- `dead_air_report.md`
- timestamped backup files next to the patched draft

## Requirements
- Python available in the local environment
- `ffmpeg` available on `PATH`, or pass `--ffmpeg-bin "<path-to-ffmpeg>"`
- Agent can read files and run shell commands
```

Create `C:\Coding\capcut-skills\skills\capcut-assistance\README.md` with this content:

````md
# capcut-assistance

Install with:

```bash
npx skills add <owner>/<repo> --skill capcut-assistance
```

This skill is a thin portable wrapper around the shared Python workflow in `scripts/workflow.py`.
````

Delete `C:\Coding\capcut-skills\SKILL.md`.

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
rtk powershell -Command "& 'C:\Users\nonga\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'C:\Coding\capcut-skills\tools\run_pytest.py' 'C:\Coding\capcut-skills\tests\test_skill_repo_layout.py' -v"
```

Expected:

- PASS for `test_installable_skill_lives_under_skills_directory`
- PASS for `test_root_skill_file_is_removed`

- [ ] **Step 5: Commit**

```bash
rtk git add skills/capcut-assistance/SKILL.md skills/capcut-assistance/README.md tests/test_skill_repo_layout.py SKILL.md
rtk git commit -m "feat: move capcut assistance skill into collection"
```

### Task 2: Publish the Public Install Contract at the Repo Root

**Files:**
- Create: `C:\Coding\capcut-skills\README.md`
- Modify: `C:\Coding\capcut-skills\tests\test_skill_repo_layout.py`

- [ ] **Step 1: Extend the test with README expectations**

Add these tests to `C:\Coding\capcut-skills\tests\test_skill_repo_layout.py`:

```python
def test_root_readme_contains_install_command() -> None:
    text = read_text("README.md")
    assert "npx skills add" in text
    assert "--skill capcut-assistance" in text
    assert "skills/capcut-assistance/SKILL.md" in text


def test_root_readme_documents_runtime_requirements() -> None:
    text = read_text("README.md")
    assert "Python" in text
    assert "ffmpeg" in text
    assert "python -m scripts.workflow --draft-folder" in text
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run:

```bash
rtk powershell -Command "& 'C:\Users\nonga\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'C:\Coding\capcut-skills\tools\run_pytest.py' 'C:\Coding\capcut-skills\tests\test_skill_repo_layout.py' -v"
```

Expected:

- FAIL because `README.md` does not exist yet

- [ ] **Step 3: Write the minimal implementation**

Create `C:\Coding\capcut-skills\README.md` with this content:

````md
# CapCut Skills

Portable CapCut skills for agent CLIs that support the shared `SKILL.md` format.

## Install

Install the first public skill with:

```bash
npx skills add <owner>/<repo> --skill capcut-assistance
```

## Available Skills

- `capcut-assistance`: safely remove dead air from an existing CapCut draft, preserve backups, and write edit reports

## Skill Location

The installable skill lives at `skills/capcut-assistance/SKILL.md`.

## Runtime Requirements

- Python
- `ffmpeg` on `PATH`, or pass `--ffmpeg-bin "<path-to-ffmpeg>"`
- an existing CapCut draft folder with valid source media paths

## Example Usage

```bash
python -m scripts.workflow --draft-folder "<draft-folder>"
```

More aggressive silence trimming:

```bash
python -m scripts.workflow --draft-folder "<draft-folder>" --silence-threshold-db -28 --min-silence-ms 150 --lead-padding-ms 60 --tail-padding-ms 90 --max-gap-ms 40 --min-keep-ms 250
```
````

- [ ] **Step 4: Run the focused test to verify it passes**

Run:

```bash
rtk powershell -Command "& 'C:\Users\nonga\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'C:\Coding\capcut-skills\tools\run_pytest.py' 'C:\Coding\capcut-skills\tests\test_skill_repo_layout.py' -v"
```

Expected:

- PASS for the new `README.md` checks
- existing Task 1 tests remain green

- [ ] **Step 5: Commit**

```bash
rtk git add README.md tests/test_skill_repo_layout.py
rtk git commit -m "docs: publish capcut assistance install contract"
```

### Task 3: Update Compatibility Docs and Repo Hygiene for Public Publishing

**Files:**
- Modify: `C:\Coding\capcut-skills\docs\agent-compatibility.md`
- Modify: `C:\Coding\capcut-skills\.gitignore`
- Modify: `C:\Coding\capcut-skills\tests\test_skill_repo_layout.py`

- [ ] **Step 1: Extend the test for compatibility and ignore rules**

Add these tests to `C:\Coding\capcut-skills\tests\test_skill_repo_layout.py`:

```python
def test_compatibility_doc_uses_collection_layout() -> None:
    text = read_text("docs", "agent-compatibility.md")
    assert "--skill capcut-assistance" in text
    assert "skills/capcut-assistance/SKILL.md" in text
    assert "root-level `SKILL.md`" not in text


def test_gitignore_excludes_local_draft_artifacts() -> None:
    text = read_text(".gitignore")
    assert "real-drafts/" in text
    assert "*.bak.*" in text
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run:

```bash
rtk powershell -Command "& 'C:\Users\nonga\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'C:\Coding\capcut-skills\tools\run_pytest.py' 'C:\Coding\capcut-skills\tests\test_skill_repo_layout.py' -v"
```

Expected:

- FAIL because `docs/agent-compatibility.md` still describes the old root skill usage
- FAIL because `.gitignore` does not yet ignore local draft artifacts

- [ ] **Step 3: Write the minimal implementation**

Replace `C:\Coding\capcut-skills\docs\agent-compatibility.md` with:

````md
# Agent Compatibility

## Install Surface

Install the public skill with:

```bash
npx skills add <owner>/<repo> --skill capcut-assistance
```

The installable skill file lives at `skills/capcut-assistance/SKILL.md`.

## Shared Assumptions

- The agent can read files
- The agent can run shell commands
- Python is available
- `ffmpeg` is available on `PATH`, or the user can provide `--ffmpeg-bin`

## Portability Rule

Do not rely on UI automation, proprietary slash commands, or agent-only SDK features.

## Execution Contract

Agents should use the shared workflow command:

```bash
python -m scripts.workflow --draft-folder "<draft-folder>"
```
````

Update `C:\Coding\capcut-skills\.gitignore` so it contains at least:

```gitignore
.vendor/
.pytest_cache/
__pycache__/
real-drafts/
*.bak.*
dead_air_report.json
dead_air_report.md
```

- [ ] **Step 4: Run the focused test to verify it passes**

Run:

```bash
rtk powershell -Command "& 'C:\Users\nonga\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'C:\Coding\capcut-skills\tools\run_pytest.py' 'C:\Coding\capcut-skills\tests\test_skill_repo_layout.py' -v"
```

Expected:

- PASS for compatibility-doc checks
- PASS for `.gitignore` checks
- earlier tests remain green

- [ ] **Step 5: Commit**

```bash
rtk git add docs/agent-compatibility.md .gitignore tests/test_skill_repo_layout.py
rtk git commit -m "chore: align docs and ignore rules for skills collection"
```

### Task 4: Run Full Verification and Tighten Any Drift

**Files:**
- Modify: `C:\Coding\capcut-skills\README.md` if verification finds wording drift
- Modify: `C:\Coding\capcut-skills\skills\capcut-assistance\SKILL.md` if verification finds command drift
- Modify: `C:\Coding\capcut-skills\docs\agent-compatibility.md` if verification finds install drift

- [ ] **Step 1: Run the full automated test suite**

Run:

```bash
rtk powershell -Command "& 'C:\Users\nonga\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'C:\Coding\capcut-skills\tools\run_pytest.py' 'C:\Coding\capcut-skills\tests' -v"
```

Expected:

- PASS for the existing workflow tests
- PASS for `tests/test_skill_repo_layout.py`

- [ ] **Step 2: Manually check the three public entrypoints for contract drift**

Verify these exact strings still match across all docs:

```text
npx skills add <owner>/<repo> --skill capcut-assistance
python -m scripts.workflow --draft-folder "<draft-folder>"
```

Files to compare:

- `C:\Coding\capcut-skills\README.md`
- `C:\Coding\capcut-skills\skills\capcut-assistance\SKILL.md`
- `C:\Coding\capcut-skills\docs\agent-compatibility.md`

- [ ] **Step 3: If any drift is found, make the minimal text-only correction**

Use this corrected block everywhere it appears:

```md
Install with `npx skills add <owner>/<repo> --skill capcut-assistance`.

Run `python -m scripts.workflow --draft-folder "<draft-folder>"`.
```

- [ ] **Step 4: Re-run the full test suite after any text correction**

Run:

```bash
rtk powershell -Command "& 'C:\Users\nonga\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'C:\Coding\capcut-skills\tools\run_pytest.py' 'C:\Coding\capcut-skills\tests' -v"
```

Expected:

- PASS with no regressions

- [ ] **Step 5: Commit**

```bash
rtk git add README.md skills/capcut-assistance/SKILL.md docs/agent-compatibility.md tests/test_skill_repo_layout.py .gitignore
rtk git commit -m "test: verify capcut assistance skills collection layout"
```

## Self-Review

### Spec Coverage

- Collection layout under `skills/`: covered by Task 1
- Public skill name `capcut-assistance`: covered by Tasks 1, 2, and 3
- Root install command for `npx skills add`: covered by Tasks 2 and 3
- Shared Python workflow contract unchanged: covered by Tasks 1, 2, and 4
- Cross-agent portability language: covered by Task 3
- Future multi-skill repo growth path: enabled by Task 1 structure and Task 2 root README

### Placeholder Scan

- No `TODO`, `TBD`, or deferred implementation markers remain
- Each task includes exact files, exact commands, expected failures, expected passes, and commit points

### Type Consistency

- Public skill name is consistently `capcut-assistance`
- Shared workflow command is consistently `python -m scripts.workflow --draft-folder "<draft-folder>"`
- Install command is consistently `npx skills add <owner>/<repo> --skill capcut-assistance`
