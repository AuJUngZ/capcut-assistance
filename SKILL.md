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
