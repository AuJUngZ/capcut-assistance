# CapCut Skills

Portable CapCut skills for agent CLIs that support the shared `SKILL.md` format.

## Install

Install the first public skill with:

```bash
npx skills add AuJUngZ/capcut-assistance --skill dead-air-removal
```

## Available Skills

- `dead-air-removal`: safely remove dead air from an existing CapCut draft, preserve backups, and write edit reports

## Skill Location

The installable skill lives at `skills/dead-air-removal/SKILL.md`.

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
