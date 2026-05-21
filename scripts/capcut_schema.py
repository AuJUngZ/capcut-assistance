from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(slots=True)
class DraftBundle:
    root: Path
    draft_content_path: Path
    project_path: Path
    draft_content: dict
    project: dict


@dataclass(slots=True)
class VideoSegment:
    segment_id: str
    material_id: str
    material_path: str
    source_start_us: int
    source_duration_us: int
    target_start_us: int
    target_duration_us: int
    raw_segment: dict


def load_draft_bundle(root: Path) -> DraftBundle:
    draft_content_path = root / "draft_content.json"
    project_path = root / "Timelines" / "project.json"
    return DraftBundle(
        root=root,
        draft_content_path=draft_content_path,
        project_path=project_path,
        draft_content=json.loads(draft_content_path.read_text(encoding="utf-8")),
        project=json.loads(project_path.read_text(encoding="utf-8")),
    )


def resolve_video_segments(bundle: DraftBundle) -> list[VideoSegment]:
    materials = {
        item["id"]: item["path"]
        for item in bundle.draft_content["materials"]["videos"]
    }
    segments: list[VideoSegment] = []
    for track in bundle.project["tracks"]:
        if track.get("type") != "video":
            continue
        for segment in track.get("segments", []):
            source = segment["source_timerange"]
            target = segment["target_timerange"]
            segments.append(
                VideoSegment(
                    segment_id=segment["id"],
                    material_id=segment["material_id"],
                    material_path=materials[segment["material_id"]],
                    source_start_us=source["start"],
                    source_duration_us=source["duration"],
                    target_start_us=target["start"],
                    target_duration_us=target["duration"],
                    raw_segment=segment,
                )
            )
    return segments
