# Agent Compatibility

## Shared assumptions
- Agent can read files
- Agent can run shell commands
- Agent can report command output back to the user

## Claude
Use the skill by loading `SKILL.md` and running the documented shell command.

## Codex CLI
Use the skill by loading `SKILL.md` and running the documented shell command.

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
