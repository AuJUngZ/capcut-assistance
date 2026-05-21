from dataclasses import dataclass


@dataclass(slots=True)
class DraftPaths:
    draft_content: str
    project_json: str
