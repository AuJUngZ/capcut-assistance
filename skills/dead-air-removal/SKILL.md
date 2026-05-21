---
name: dead-air-removal
description: Use when a CapCut draft already exists and an agent should safely remove dead air, preserve backups, and report timeline edits through shell commands.
---

# Dead Air Removal

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
Run `python -m scripts.workflow --draft-folder "<draft-folder>"` from the `skills/dead-air-removal/` directory (repo checkout) or the skill install directory.

## Gentler Silence Removal (less aggressive)
Run `python -m scripts.workflow --draft-folder "<draft-folder>" --silence-threshold-db -35 --min-silence-ms 250 --lead-padding-ms 120 --tail-padding-ms 180 --max-gap-ms 120 --min-keep-ms 300` from the same directory.

## Outputs
- `dead_air_report.json`
- `dead_air_report.md`
- timestamped backup files next to the patched draft

## Requirements
- Run this from the skill directory that contains `scripts/workflow.py`
- Python available in the local environment
- `ffmpeg` available on `PATH`, or pass `--ffmpeg-bin "<path-to-ffmpeg>"`
- Agent can read files and run shell commands
