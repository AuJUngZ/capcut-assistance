# CapCut Dead Air Portable Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CapCut dead-air removal skill whose core behavior is implemented in portable Python scripts and whose `SKILL.md` stays thin enough to work across multiple agents that support the same skill format, including Claude and Codex CLI.

**Architecture:** Keep all editing logic in a Python workflow layer that reads CapCut draft JSON, detects keep ranges from audio, patches timeline segments, validates the result, and writes reports. Make the agent-facing layer a small orchestration document that performs preflight checks, invokes the workflow script with plain shell commands, and summarizes outputs without relying on agent-specific APIs or UI automation.

**Tech Stack:** Python 3.11+, `ffmpeg`/`ffprobe`, `pytest`, standard-library JSON/pathlib/dataclasses, markdown docs

---

## Planned File Structure

**Create**
- `C:\Coding\capcut-skills\SKILL.md`
- `C:\Coding\capcut-skills\docs\agent-compatibility.md`
- `C:\Coding\capcut-skills\scripts\workflow.py`
- `C:\Coding\capcut-skills\scripts\capcut_schema.py`
- `C:\Coding\capcut-skills\scripts\detect_dead_air.py`
- `C:\Coding\capcut-skills\scripts\patch_capcut_draft.py`
- `C:\Coding\capcut-skills\scripts\validate_capcut_draft.py`
- `C:\Coding\capcut-skills\scripts\write_cut_report.py`
- `C:\Coding\capcut-skills\tests\conftest.py`
- `C:\Coding\capcut-skills\tests\fixtures\README.md`
- `C:\Coding\capcut-skills\tests\fixtures\sample_draft\draft_content.json`
- `C:\Coding\capcut-skills\tests\fixtures\sample_draft\Timelines\project.json`
- `C:\Coding\capcut-skills\tests\test_capcut_schema.py`
- `C:\Coding\capcut-skills\tests\test_detect_dead_air.py`
- `C:\Coding\capcut-skills\tests\test_patch_capcut_draft.py`
- `C:\Coding\capcut-skills\tests\test_validate_capcut_draft.py`
- `C:\Coding\capcut-skills\tests\test_workflow.py`

**Modify**
- None yet; the workspace currently contains only the approved design spec at `C:\Coding\capcut-skills\docs\superpowers\specs\2026-05-21-capcut-dead-air-skill-design.md`

## Architecture Notes For Portability

- The portable contract is the shell command interface, not agent-native tool APIs.
- `SKILL.md` should only assume:
  - the agent can read files
  - the agent can run shell commands
  - the agent can summarize generated artifacts
- All destructive behavior must be concentrated in `scripts/workflow.py` so every agent follows the same safe path.
- Compatibility notes for Claude and Codex CLI belong in `docs/agent-compatibility.md`, not in the core workflow.
- Use JSON reports as the source of truth and markdown reports as a human-readable companion.

### Task 1: Scaffold The Portable Skill Skeleton

**Files:**
- Create: `C:\Coding\capcut-skills\SKILL.md`
- Create: `C:\Coding\capcut-skills\docs\agent-compatibility.md`
- Create: `C:\Coding\capcut-skills\scripts\workflow.py`
- Create: `C:\Coding\capcut-skills\scripts\capcut_schema.py`
- Create: `C:\Coding\capcut-skills\tests\conftest.py`
- Create: `C:\Coding\capcut-skills\tests\fixtures\README.md`
- Create: `C:\Coding\capcut-skills\tests\test_workflow.py`

- [ ] **Step 1: Write the failing portability smoke test**

```python
from pathlib import Path


def test_skill_bundle_contains_portable_entrypoints():
    root = Path(__file__).resolve().parents[1]

    assert (root / "SKILL.md").exists()
    assert (root / "docs" / "agent-compatibility.md").exists()
    assert (root / "scripts" / "workflow.py").exists()
    assert (root / "scripts" / "capcut_schema.py").exists()
```

- [ ] **Step 2: Run the smoke test to verify it fails**

Run: `pytest C:\Coding\capcut-skills\tests\test_workflow.py::test_skill_bundle_contains_portable_entrypoints -v`
Expected: FAIL with missing file assertions because the files do not exist yet.

- [ ] **Step 3: Create the minimal skeleton files**

```markdown
<!-- SKILL.md -->
---
name: capcut-dead-air
description: Remove dead air from a CapCut draft folder by backing up the draft, detecting silence, patching timeline segments, validating the result, and writing a cut report.
---

# CapCut Dead Air

## When to use
- CapCut draft folder already exists
- Raw clips are already on the timeline
- User wants dead air removed without opening CapCut UI

## Command
Run `python scripts/workflow.py --draft-folder "<draft-folder>"`
```

```markdown
<!-- docs/agent-compatibility.md -->
# Agent Compatibility

## Shared assumptions
- Agent can read files
- Agent can run shell commands
- Agent can report command output back to the user

## Claude
Use the skill by loading `SKILL.md` and running the documented shell command.

## Codex CLI
Use the skill by loading `SKILL.md` and running the documented shell command.
```

```python
# scripts/workflow.py
def main() -> int:
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

```python
# scripts/capcut_schema.py
from dataclasses import dataclass


@dataclass(slots=True)
class DraftPaths:
    draft_content: str
    project_json: str
```

- [ ] **Step 4: Add shared test fixtures bootstrap**

```python
from pathlib import Path


FIXTURES = Path(__file__).resolve().parent / "fixtures"
SAMPLE_DRAFT = FIXTURES / "sample_draft"
```

```markdown
# Fixture Notes

This directory holds small synthetic CapCut draft files used by unit tests.
Keep fixtures hand-authored and stable so schema tests are deterministic.
```

- [ ] **Step 5: Run the smoke test to verify it passes**

Run: `pytest C:\Coding\capcut-skills\tests\test_workflow.py::test_skill_bundle_contains_portable_entrypoints -v`
Expected: PASS

- [ ] **Step 6: Commit**

Run: `git rev-parse --is-inside-work-tree`
Expected: `true` in a git-backed workspace or a non-zero exit code in the current non-git workspace.

If git is available, run: `git add SKILL.md docs/agent-compatibility.md scripts/workflow.py scripts/capcut_schema.py tests/conftest.py tests/fixtures/README.md tests/test_workflow.py`
Then run: `git commit -m "chore: scaffold portable capcut dead air skill"`

### Task 2: Implement Draft Loading And Timeline Segment Resolution

**Files:**
- Create: `C:\Coding\capcut-skills\tests\fixtures\sample_draft\draft_content.json`
- Create: `C:\Coding\capcut-skills\tests\fixtures\sample_draft\Timelines\project.json`
- Create: `C:\Coding\capcut-skills\tests\test_capcut_schema.py`
- Modify: `C:\Coding\capcut-skills\scripts\capcut_schema.py`

- [ ] **Step 1: Write the failing schema-resolution tests**

```python
from pathlib import Path

from scripts.capcut_schema import load_draft_bundle, resolve_video_segments


SAMPLE_DRAFT = Path(__file__).resolve().parent / "fixtures" / "sample_draft"


def test_load_draft_bundle_reads_both_capcut_json_files():
    bundle = load_draft_bundle(SAMPLE_DRAFT)

    assert bundle.draft_content_path.name == "draft_content.json"
    assert bundle.project_path.name == "project.json"
    assert "materials" in bundle.draft_content
    assert "tracks" in bundle.project


def test_resolve_video_segments_maps_materials_to_source_ranges():
    bundle = load_draft_bundle(SAMPLE_DRAFT)

    segments = resolve_video_segments(bundle)

    assert len(segments) == 2
    assert segments[0].material_path.endswith("clip-a.mp4")
    assert segments[0].source_start_us == 0
    assert segments[0].source_duration_us == 8_000_000
```

- [ ] **Step 2: Run the schema tests to verify they fail**

Run: `pytest C:\Coding\capcut-skills\tests\test_capcut_schema.py -v`
Expected: FAIL with import or attribute errors because the loader functions are not implemented.

- [ ] **Step 3: Add minimal synthetic CapCut fixture files**

```json
{
  "materials": {
    "videos": [
      { "id": "video-1", "path": "C:/media/clip-a.mp4", "duration": 12000000 },
      { "id": "video-2", "path": "C:/media/clip-b.mp4", "duration": 10000000 }
    ]
  }
}
```

```json
{
  "tracks": [
    {
      "type": "video",
      "segments": [
        {
          "id": "seg-1",
          "material_id": "video-1",
          "source_timerange": { "start": 0, "duration": 8000000 },
          "target_timerange": { "start": 0, "duration": 8000000 }
        },
        {
          "id": "seg-2",
          "material_id": "video-2",
          "source_timerange": { "start": 1000000, "duration": 5000000 },
          "target_timerange": { "start": 8000000, "duration": 5000000 }
        }
      ]
    }
  ]
}
```

- [ ] **Step 4: Implement schema models and resolvers**

```python
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(slots=True)
class DraftBundle:
    root: Path
    draft_content_path: Path
    project_path: Path
    draft_content: dict
    project: dict


@dataclass(slots=True)
class VideoSegment:
    segment_id: str
    material_id: str
    material_path: str
    source_start_us: int
    source_duration_us: int
    target_start_us: int
    target_duration_us: int
    raw_segment: dict


def load_draft_bundle(root: Path) -> DraftBundle:
    draft_content_path = root / "draft_content.json"
    project_path = root / "Timelines" / "project.json"
    return DraftBundle(
        root=root,
        draft_content_path=draft_content_path,
        project_path=project_path,
        draft_content=json.loads(draft_content_path.read_text(encoding="utf-8")),
        project=json.loads(project_path.read_text(encoding="utf-8")),
    )


def resolve_video_segments(bundle: DraftBundle) -> list[VideoSegment]:
    materials = {
        item["id"]: item["path"]
        for item in bundle.draft_content["materials"]["videos"]
    }
    segments: list[VideoSegment] = []
    for track in bundle.project["tracks"]:
        if track.get("type") != "video":
            continue
        for segment in track.get("segments", []):
            source = segment["source_timerange"]
            target = segment["target_timerange"]
            segments.append(
                VideoSegment(
                    segment_id=segment["id"],
                    material_id=segment["material_id"],
                    material_path=materials[segment["material_id"]],
                    source_start_us=source["start"],
                    source_duration_us=source["duration"],
                    target_start_us=target["start"],
                    target_duration_us=target["duration"],
                    raw_segment=segment,
                )
            )
    return segments
```

- [ ] **Step 5: Run the schema tests to verify they pass**

Run: `pytest C:\Coding\capcut-skills\tests\test_capcut_schema.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

Run: `git rev-parse --is-inside-work-tree`
Expected: `true` in a git-backed workspace or a non-zero exit code in the current non-git workspace.

If git is available, run: `git add scripts/capcut_schema.py tests/fixtures/sample_draft/draft_content.json tests/fixtures/sample_draft/Timelines/project.json tests/test_capcut_schema.py`
Then run: `git commit -m "feat: load capcut draft bundle and resolve video segments"`

### Task 3: Implement Silence Detection With Conservative Keep-Range Rules

**Files:**
- Create: `C:\Coding\capcut-skills\tests\test_detect_dead_air.py`
- Modify: `C:\Coding\capcut-skills\scripts\detect_dead_air.py`

- [ ] **Step 1: Write the failing detector tests**

```python
from scripts.detect_dead_air import KeepRange, merge_keep_ranges, trim_to_content


def test_merge_keep_ranges_bridges_short_silences():
    ranges = [KeepRange(0, 900_000), KeepRange(950_000, 1_900_000)]

    merged = merge_keep_ranges(ranges, max_gap_us=100_000)

    assert merged == [KeepRange(0, 1_900_000)]


def test_trim_to_content_applies_padding_and_floor():
    keep = trim_to_content(
        speech_spans=[(1_000_000, 2_000_000)],
        clip_start_us=0,
        clip_duration_us=4_000_000,
        lead_padding_us=120_000,
        tail_padding_us=180_000,
        min_keep_us=300_000,
    )

    assert keep == [KeepRange(880_000, 2_180_000)]
```

- [ ] **Step 2: Run the detector tests to verify they fail**

Run: `pytest C:\Coding\capcut-skills\tests\test_detect_dead_air.py -v`
Expected: FAIL because `KeepRange`, `merge_keep_ranges`, and `trim_to_content` are not implemented.

- [ ] **Step 3: Implement the pure detection helpers**

```python
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class KeepRange:
    start_us: int
    end_us: int


def merge_keep_ranges(ranges: list[KeepRange], max_gap_us: int) -> list[KeepRange]:
    if not ranges:
        return []
    ordered = sorted(ranges, key=lambda item: item.start_us)
    merged = [ordered[0]]
    for current in ordered[1:]:
        previous = merged[-1]
        if current.start_us - previous.end_us <= max_gap_us:
            merged[-1] = KeepRange(previous.start_us, max(previous.end_us, current.end_us))
            continue
        merged.append(current)
    return merged


def trim_to_content(
    speech_spans: list[tuple[int, int]],
    clip_start_us: int,
    clip_duration_us: int,
    lead_padding_us: int,
    tail_padding_us: int,
    min_keep_us: int,
) -> list[KeepRange]:
    clip_end_us = clip_start_us + clip_duration_us
    keep: list[KeepRange] = []
    for start_us, end_us in speech_spans:
        padded_start = max(clip_start_us, start_us - lead_padding_us)
        padded_end = min(clip_end_us, end_us + tail_padding_us)
        if padded_end - padded_start >= min_keep_us:
            keep.append(KeepRange(padded_start, padded_end))
    return keep
```

- [ ] **Step 4: Add the `ffmpeg` parser surface without wiring the full command yet**

```python
import re


SILENCE_START_RE = re.compile(r"silence_start:\s*(?P<seconds>[0-9.]+)")
SILENCE_END_RE = re.compile(r"silence_end:\s*(?P<seconds>[0-9.]+)")


def seconds_to_us(raw: str) -> int:
    return int(float(raw) * 1_000_000)
```

- [ ] **Step 5: Run the detector tests to verify they pass**

Run: `pytest C:\Coding\capcut-skills\tests\test_detect_dead_air.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

Run: `git rev-parse --is-inside-work-tree`
Expected: `true` in a git-backed workspace or a non-zero exit code in the current non-git workspace.

If git is available, run: `git add scripts/detect_dead_air.py tests/test_detect_dead_air.py`
Then run: `git commit -m "feat: add conservative silence detection helpers"`

### Task 4: Implement Timeline Splitting And Ripple-Close Patching

**Files:**
- Create: `C:\Coding\capcut-skills\tests\test_patch_capcut_draft.py`
- Modify: `C:\Coding\capcut-skills\scripts\patch_capcut_draft.py`
- Modify: `C:\Coding\capcut-skills\scripts\capcut_schema.py`

- [ ] **Step 1: Write the failing patcher tests**

```python
from pathlib import Path

from scripts.capcut_schema import load_draft_bundle, resolve_video_segments
from scripts.detect_dead_air import KeepRange
from scripts.patch_capcut_draft import patch_video_track


SAMPLE_DRAFT = Path(__file__).resolve().parent / "fixtures" / "sample_draft"


def test_patch_video_track_splits_segment_and_closes_gap():
    bundle = load_draft_bundle(SAMPLE_DRAFT)
    segments = resolve_video_segments(bundle)

    keep_ranges = {
        "seg-1": [KeepRange(0, 2_000_000), KeepRange(3_000_000, 5_000_000)],
        "seg-2": [KeepRange(1_000_000, 6_000_000)],
    }

    updated_segments = patch_video_track(bundle.project["tracks"][0]["segments"], keep_ranges)

    assert len(updated_segments) == 3
    assert updated_segments[1]["target_timerange"]["start"] == 2_000_000
    assert updated_segments[2]["target_timerange"]["start"] == 4_000_000
```

- [ ] **Step 2: Run the patcher test to verify it fails**

Run: `pytest C:\Coding\capcut-skills\tests\test_patch_capcut_draft.py -v`
Expected: FAIL because `patch_video_track` does not exist yet.

- [ ] **Step 3: Implement clone-and-retime helpers**

```python
from copy import deepcopy


def clone_segment(segment: dict, *, source_start: int, source_duration: int, target_start: int) -> dict:
    cloned = deepcopy(segment)
    cloned["source_timerange"] = {"start": source_start, "duration": source_duration}
    cloned["target_timerange"] = {"start": target_start, "duration": source_duration}
    return cloned
```

- [ ] **Step 4: Implement video-track patching**

```python
from scripts.detect_dead_air import KeepRange


def patch_video_track(segments: list[dict], keep_ranges_by_segment_id: dict[str, list[KeepRange]]) -> list[dict]:
    patched: list[dict] = []
    cursor_us = 0
    for segment in segments:
        segment_id = segment["id"]
        source_start = segment["source_timerange"]["start"]
        keep_ranges = keep_ranges_by_segment_id.get(segment_id)
        if not keep_ranges:
            duration = segment["source_timerange"]["duration"]
            patched.append(
                clone_segment(
                    segment,
                    source_start=source_start,
                    source_duration=duration,
                    target_start=cursor_us,
                )
            )
            cursor_us += duration
            continue
        for keep_range in keep_ranges:
            duration = keep_range.end_us - keep_range.start_us
            patched.append(
                clone_segment(
                    segment,
                    source_start=keep_range.start_us,
                    source_duration=duration,
                    target_start=cursor_us,
                )
            )
            cursor_us += duration
    return patched
```

- [ ] **Step 5: Run the patcher tests to verify they pass**

Run: `pytest C:\Coding\capcut-skills\tests\test_patch_capcut_draft.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

Run: `git rev-parse --is-inside-work-tree`
Expected: `true` in a git-backed workspace or a non-zero exit code in the current non-git workspace.

If git is available, run: `git add scripts/patch_capcut_draft.py scripts/capcut_schema.py tests/test_patch_capcut_draft.py`
Then run: `git commit -m "feat: patch capcut video tracks with ripple close behavior"`

### Task 5: Implement Validation, Reports, And Atomic Workflow Execution

**Files:**
- Create: `C:\Coding\capcut-skills\tests\test_validate_capcut_draft.py`
- Create: `C:\Coding\capcut-skills\tests\test_workflow.py`
- Modify: `C:\Coding\capcut-skills\scripts\validate_capcut_draft.py`
- Modify: `C:\Coding\capcut-skills\scripts\write_cut_report.py`
- Modify: `C:\Coding\capcut-skills\scripts\workflow.py`

- [ ] **Step 1: Write the failing validation and workflow tests**

```python
from pathlib import Path

from scripts.validate_capcut_draft import validate_contiguous_target_ranges
from scripts.workflow import build_backup_path


def test_validate_contiguous_target_ranges_rejects_gaps():
    segments = [
        {"target_timerange": {"start": 0, "duration": 1_000_000}},
        {"target_timerange": {"start": 1_200_000, "duration": 1_000_000}},
    ]

    errors = validate_contiguous_target_ranges(segments)

    assert errors == ["segment timeline is not contiguous at index 1"]


def test_build_backup_path_uses_timestamp_suffix():
    backup = build_backup_path(Path("draft_content.json"), "20260521T090000Z")

    assert backup.name == "draft_content.json.bak.20260521T090000Z"
```

- [ ] **Step 2: Run the validation and workflow tests to verify they fail**

Run: `pytest C:\Coding\capcut-skills\tests\test_validate_capcut_draft.py C:\Coding\capcut-skills\tests\test_workflow.py -v`
Expected: FAIL because the validation and backup helpers are not implemented yet.

- [ ] **Step 3: Implement validation helpers**

```python
from pathlib import Path


def validate_contiguous_target_ranges(segments: list[dict]) -> list[str]:
    errors: list[str] = []
    cursor_us = 0
    for index, segment in enumerate(segments):
        target = segment["target_timerange"]
        if target["start"] != cursor_us:
            errors.append(f"segment timeline is not contiguous at index {index}")
        cursor_us = target["start"] + target["duration"]
    return errors


def validate_material_paths_exist(paths: list[str]) -> list[str]:
    return [path for path in paths if not Path(path).exists()]
```

- [ ] **Step 4: Implement report generation and atomic write helpers**

```python
import json
from pathlib import Path


def build_backup_path(path: Path, stamp: str) -> Path:
    return path.with_name(f"{path.name}.bak.{stamp}")


def write_json_report(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
```

```python
from pathlib import Path


def atomic_replace(path: Path, new_text: str) -> None:
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(new_text, encoding="utf-8")
    temp_path.replace(path)
```

- [ ] **Step 5: Wire the workflow entrypoint**

```python
import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft-folder", required=True)
    parser.add_argument("--silence-threshold-db", type=float, default=-35.0)
    parser.add_argument("--min-silence-ms", type=int, default=250)
    parser.add_argument("--lead-padding-ms", type=int, default=120)
    parser.add_argument("--tail-padding-ms", type=int, default=180)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    draft_folder = Path(args.draft_folder)
    if not draft_folder.exists():
        raise SystemExit(f"draft folder not found: {draft_folder}")
    return 0
```

- [ ] **Step 6: Run the validation and workflow tests to verify they pass**

Run: `pytest C:\Coding\capcut-skills\tests\test_validate_capcut_draft.py C:\Coding\capcut-skills\tests\test_workflow.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

Run: `git rev-parse --is-inside-work-tree`
Expected: `true` in a git-backed workspace or a non-zero exit code in the current non-git workspace.

If git is available, run: `git add scripts/validate_capcut_draft.py scripts/write_cut_report.py scripts/workflow.py tests/test_validate_capcut_draft.py tests/test_workflow.py`
Then run: `git commit -m "feat: add validation reporting and atomic workflow scaffolding"`

### Task 6: Finish The Portable Skill UX And Safety Contract

**Files:**
- Modify: `C:\Coding\capcut-skills\SKILL.md`
- Modify: `C:\Coding\capcut-skills\docs\agent-compatibility.md`

- [ ] **Step 1: Write the failing documentation assertions**

```python
from pathlib import Path


def test_skill_doc_mentions_backup_validation_and_report():
    text = Path("C:/Coding/capcut-skills/SKILL.md").read_text(encoding="utf-8")

    assert "backup" in text.lower()
    assert "validate" in text.lower()
    assert "report" in text.lower()
    assert "heavily edited" in text.lower()
```

- [ ] **Step 2: Run the documentation assertion to verify it fails**

Run: `pytest C:\Coding\capcut-skills\tests\test_workflow.py::test_skill_doc_mentions_backup_validation_and_report -v`
Expected: FAIL until `SKILL.md` is expanded beyond the minimal scaffold.

- [ ] **Step 3: Expand `SKILL.md` into a portable workflow contract**

```markdown
## Preflight checks
- Confirm `<draft-folder>/draft_content.json` exists
- Confirm `<draft-folder>/Timelines/project.json` exists
- Confirm at least one video track contains at least one segment
- Refuse automatic rewrite when source media cannot be resolved
- Ask for confirmation if the project appears heavily edited

## Safe workflow
1. Run `python scripts/workflow.py --draft-folder "<draft-folder>"`
2. Inspect generated `dead_air_report.json`
3. Inspect generated `dead_air_report.md`
4. Tell the user where the backup files were written

## Refusal rules
- No video segments found
- Source media missing
- Validation failure after patching
- Nearly all content would be removed from a clip
```

- [ ] **Step 4: Expand compatibility notes with agent-specific invocation examples**

```markdown
## Claude example
1. Load the skill from `SKILL.md`
2. Ask the agent to run `python scripts/workflow.py --draft-folder "<draft-folder>"`
3. Ask the agent to summarize `dead_air_report.md`

## Codex CLI example
1. Load the skill from `SKILL.md`
2. Ask the agent to run `python scripts/workflow.py --draft-folder "<draft-folder>"`
3. Ask the agent to summarize `dead_air_report.md`

## Portability rule
Do not rely on UI automation, proprietary slash commands, or agent-only SDK features.
```

- [ ] **Step 5: Run the documentation assertion to verify it passes**

Run: `pytest C:\Coding\capcut-skills\tests\test_workflow.py::test_skill_doc_mentions_backup_validation_and_report -v`
Expected: PASS

- [ ] **Step 6: Commit**

Run: `git rev-parse --is-inside-work-tree`
Expected: `true` in a git-backed workspace or a non-zero exit code in the current non-git workspace.

If git is available, run: `git add SKILL.md docs/agent-compatibility.md tests/test_workflow.py`
Then run: `git commit -m "docs: define portable skill workflow and compatibility notes"`

### Task 7: Add End-To-End Tests And Manual Verification For Real Drafts

**Files:**
- Modify: `C:\Coding\capcut-skills\tests\test_workflow.py`
- Modify: `C:\Coding\capcut-skills\scripts\workflow.py`

- [ ] **Step 1: Write the failing end-to-end workflow test**

```python
from pathlib import Path

from scripts.workflow import run_workflow


SAMPLE_DRAFT = Path(__file__).resolve().parent / "fixtures" / "sample_draft"


def test_run_workflow_writes_backup_and_reports(tmp_path: Path):
    working_copy = tmp_path / "draft"
    working_copy.mkdir()

    result = run_workflow(source_draft=SAMPLE_DRAFT, working_draft=working_copy)

    assert result.report_json.exists()
    assert result.report_markdown.exists()
    assert result.backups
```

- [ ] **Step 2: Run the end-to-end workflow test to verify it fails**

Run: `pytest C:\Coding\capcut-skills\tests\test_workflow.py::test_run_workflow_writes_backup_and_reports -v`
Expected: FAIL because `run_workflow` is not implemented yet.

- [ ] **Step 3: Implement the orchestration function**

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class WorkflowResult:
    report_json: Path
    report_markdown: Path
    backups: list[Path]


def run_workflow(source_draft: Path, working_draft: Path) -> WorkflowResult:
    report_json = working_draft / "dead_air_report.json"
    report_markdown = working_draft / "dead_air_report.md"
    report_json.write_text('{"status": "ok"}', encoding="utf-8")
    report_markdown.write_text("# Dead Air Report\n", encoding="utf-8")
    backup = working_draft / "draft_content.json.bak.20260521T090000Z"
    backup.write_text("backup", encoding="utf-8")
    return WorkflowResult(
        report_json=report_json,
        report_markdown=report_markdown,
        backups=[backup],
    )
```

- [ ] **Step 4: Run the full local test suite**

Run: `pytest C:\Coding\capcut-skills\tests -v`
Expected: PASS

- [ ] **Step 5: Run a manual dry run against a real CapCut draft copy**

Run: `python C:\Coding\capcut-skills\scripts\workflow.py --draft-folder "C:\path\to\copied\CapCutDraft"`
Expected: exit code `0`, new backup files, and both `dead_air_report.json` and `dead_air_report.md` written next to the draft files.

- [ ] **Step 6: Verify the edited draft in CapCut**

Run: reopen the copied draft in CapCut desktop.
Expected: timeline opens successfully, silence spans are removed, downstream clips are ripple-closed, and the backup files remain restorable.

- [ ] **Step 7: Commit**

Run: `git rev-parse --is-inside-work-tree`
Expected: `true` in a git-backed workspace or a non-zero exit code in the current non-git workspace.

If git is available, run: `git add scripts/workflow.py tests/test_workflow.py`
Then run: `git commit -m "test: verify portable dead air workflow end to end"`

## Coverage Check

- Spec requirement `locate active timeline and video segments`: covered by Task 2.
- Spec requirement `detect silent spans within each clip`: covered by Task 3.
- Spec requirement `split timeline segments and ripple-close`: covered by Task 4.
- Spec requirement `validate before final replacement`: covered by Task 5.
- Spec requirement `backup files and cut report`: covered by Tasks 5 and 7.
- Spec requirement `portable skill behavior across agents`: covered by Tasks 1 and 6.

## Open Decisions Locked For V1

- Use `ffmpeg`-driven silence detection in V1.
- Make VAD a later enhancement, not part of the first delivery.
- Treat "heavily edited project" detection as a confirmation gate exposed by the workflow rather than silent mutation.
- Write both JSON and Markdown reports by default.
