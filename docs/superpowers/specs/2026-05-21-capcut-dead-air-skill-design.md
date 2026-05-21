# CapCut Dead Air Skill Design

Date: 2026-05-21
Status: Approved for spec drafting
Target location: C:\Coding\capcut-skills

## Goal
Build a reusable Codex Skill that removes dead air from any CapCut draft folder where raw video clips are already placed on the timeline. The Skill must work without opening the CapCut UI and must update the CapCut draft so the user can reopen the project and see the tightened timeline immediately.

## Primary Outcome
Given a CapCut draft folder path, the Skill:
1. Locates the active timeline and video segments in the draft.
2. Resolves each timeline segment back to its source media file and source time range.
3. Detects silent spans within each clip.
4. Splits timeline segments at speech boundaries.
5. Removes silent spans.
6. Ripple-closes the remaining segments so pacing is tighter.
7. Saves a backup and a cut report.

## Non-Goals For V1
- Do not generate subtitles.
- Do not apply visual styling, transitions, or B-roll logic.
- Do not recompose the edit semantically beyond silence removal.
- Do not require CapCut desktop UI automation.

## Scope Assumptions
- The draft folder contains a valid `draft_content.json` and `Timelines/project.json`.
- Video media is already placed on at least one timeline track.
- The project may contain multiple video segments and multiple source files.
- The Skill should support unedited or lightly edited raw timelines; it should not silently rewrite heavily hand-edited projects unless explicitly told to do so.

## Recommended Architecture
Use a Skill plus bundled scripts.

### Skill Layer
`SKILL.md` should describe:
- when to use the Skill
- preflight checks
- safe invocation flow
- rollback behavior
- how to inspect the generated cut report
- when to refuse or ask for confirmation

### Script Layer
Include at least these scripts:

1. `scripts/detect_dead_air.py`
- Reads media paths and source time spans.
- Runs audio analysis for silence detection.
- Emits keep ranges and cut ranges per source segment.

2. `scripts/patch_capcut_draft.py`
- Reads the CapCut draft JSON.
- Splits affected timeline segments.
- Rewrites `source_timerange` and `target_timerange`.
- Ripple-closes downstream segments.
- Preserves unrelated tracks and materials as much as possible.

3. `scripts/validate_capcut_draft.py`
- Confirms all referenced materials still exist.
- Confirms durations and bounds are valid.
- Confirms target timeline ranges are continuous after editing.
- Blocks final replacement if validation fails.

4. `scripts/write_cut_report.py` or integrated report generation
- Writes a human-readable summary of removed spans and duration savings.

## Detection Strategy
V1 should use external audio analysis rather than CapCut-only heuristics.

### Recommended Initial Detector
Start with `ffmpeg`-driven silence analysis because it is inspectable, script-friendly, and easier to debug in a local environment.

### Future Enhancement
Add VAD as an optional second pass for better handling of:
- room tone
- breaths
- low-volume speech
- noisy recordings

### V1 Detection Rules
- Remove clear silence automatically.
- Keep short natural pauses.
- Add lead-in padding before speech.
- Add tail padding after speech.
- Merge nearby speech spans separated by very short silence.
- Ignore cuts that would produce unusably short kept fragments.
- Prefer under-cutting over over-cutting when confidence is low.

## Timeline Rewrite Strategy
For each timeline segment:
1. Resolve the segment's source media file via its material reference.
2. Restrict analysis to the segment's current `source_timerange`.
3. Convert detected keep spans into one or more new segment definitions.
4. Recalculate each new segment's `source_timerange`.
5. Recalculate each new segment's `target_timerange`.
6. Shift downstream `target_timerange.start` values left by the removed duration.

### Editing Behavior
- Automatically split clips when silence occurs inside a segment.
- Remove silent spans inside clips, not just between existing clips.
- Preserve clip-level transform, scale, visibility, and related metadata when cloning split segments.
- Preserve non-target tracks where possible.
- Preserve text/subtitle tracks unless the user later asks for subtitle synchronization logic.

## Safety Rules
The Skill must be conservative and explicit.

### Backups
Always create backups before editing:
- `draft_content.json.bak.<timestamp>`
- `Timelines/project.json.bak.<timestamp>` when touched

### Refusal Conditions
Refuse or ask for confirmation when:
- no video track is present
- no video segments are present
- source files cannot be resolved
- the project appears heavily edited already
- analysis would remove nearly all content from a clip

### Atomic Write Pattern
- Read original JSON.
- Write proposed output to a temp file.
- Validate the temp file.
- Replace the active file only after validation succeeds.

## Output Artifacts
Each run should produce:
- updated `draft_content.json`
- backup files
- cut report, for example `dead_air_report.json` and/or `dead_air_report.md`

The report should include:
- original timeline duration
- removed duration
- new timeline duration
- per-source clip removed spans
- thresholds used
- refusal or warning notes

## Skill UX
The Skill should guide Codex through this flow:
1. Confirm the folder looks like a CapCut draft.
2. Confirm media is already on the timeline.
3. Backup the project.
4. Run detection.
5. Patch the timeline.
6. Validate the edited draft.
7. Summarize the cut report.
8. Tell the user how to reopen the project in CapCut for inspection.

## Testing Plan
Test the Skill on these cases:
1. One long raw clip with obvious silence.
2. Multiple raw clips already arranged on the timeline.
3. A clip with almost no silence, which should remain mostly unchanged.
4. A noisy clip, ensuring the detector does not destroy pacing.
5. A draft with subtitle or text tracks present, ensuring they are preserved in v1.
6. A draft with unresolved media, ensuring safe refusal.

## Risks
- CapCut draft schema may vary by app version.
- Silence thresholds may need tuning across different microphones and noise floors.
- Subtitle/text track timing may drift relative to edited video in v1 because subtitle synchronization is out of scope.
- Projects with complex prior edits may require a confirmation gate rather than automatic rewrite.

## Recommended V1 Delivery Plan
1. Scaffold the Skill folder in `C:\Coding\capcut-skills`.
2. Implement detection script.
3. Implement timeline patching script.
4. Implement validation and reporting.
5. Write `SKILL.md` with clear refusal conditions and workflow.
6. Forward-test on one or more real CapCut draft folders.
7. Tighten thresholds and schema handling based on failures.

## Open Decisions Deferred To Implementation Planning
- Exact silence thresholds and padding defaults.
- Whether VAD is part of V1 or V1.1.
- How to detect a heavily edited project robustly.
- Whether reports should default to JSON, Markdown, or both.

## Success Criteria
The Skill is successful when a user can point Codex at a CapCut draft folder containing raw clips already on the timeline, run the Skill, and reopen CapCut to find that silent parts have been removed, internal clip silences have been split out, the remaining clips have been ripple-closed, and the original draft can still be restored from backups if needed.
