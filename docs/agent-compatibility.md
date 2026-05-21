# Agent Compatibility

## Install Surface

Install the public skill with:

```bash
npx skills add AuJUngZ/capcut-assistance --skill dead-air-removal

The installable skill file lives at `skills/dead-air-removal/SKILL.md`.

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
