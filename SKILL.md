---
name: capcut-dead-air
description: Remove dead air from a CapCut draft folder by backing up the draft, detecting silence, patching timeline segments, validating the result, and writing a cut report.
---

# CapCut Dead Air

## When to use
- CapCut draft folder already exists
- Raw clips are already on the timeline
- User wants dead air removed without opening CapCut UI

## Preflight checks
- Confirm `<draft-folder>/draft_content.json` exists
- Confirm `<draft-folder>/Timelines/project.json` exists
- Confirm at least one video track contains at least one segment
- Refuse automatic rewrite when source media cannot be resolved
- Ask for confirmation if the project appears heavily edited

## Command
Run `python scripts/workflow.py --draft-folder "<draft-folder>"`

## Safe workflow
1. Run `python scripts/workflow.py --draft-folder "<draft-folder>"`
2. Validate the patched draft before treating the edit as final
3. Inspect generated `dead_air_report.json`
4. Inspect generated `dead_air_report.md`
5. Tell the user where the backup files were written

## Refusal rules
- No video segments found
- Source media missing
- Validation failure after patching
- Nearly all content would be removed from a clip
