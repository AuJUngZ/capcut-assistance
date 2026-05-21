import json
from pathlib import Path


def write_json_report(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_markdown_report(path: Path, payload: dict) -> None:
    lines = [
        "# Dead Air Report",
        "",
        f"- Original timeline duration (us): {payload['original_timeline_duration_us']}",
        f"- New timeline duration (us): {payload['new_timeline_duration_us']}",
        f"- Removed duration (us): {payload['removed_duration_us']}",
        "",
        "## Segment Summary",
    ]
    for segment in payload.get("segments", []):
        lines.append(
            f"- {segment['segment_id']}: removed {segment['removed_duration_us']} us across "
            f"{segment['keep_range_count']} keep range(s)"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
