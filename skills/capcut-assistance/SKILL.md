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
- Run this from the repository checkout that contains `scripts/workflow.py`
- Python available in the local environment
- `ffmpeg` available on `PATH`, or pass `--ffmpeg-bin "<path-to-ffmpeg>"`
- Agent can read files and run shell commands
