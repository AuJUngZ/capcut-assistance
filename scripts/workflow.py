import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import shutil
from typing import Callable

from scripts.capcut_schema import get_track_container, load_draft_bundle, resolve_video_segments
from scripts.detect_dead_air import DetectionSettings, KeepRange, detect_keep_ranges_ffmpeg
from scripts.patch_capcut_draft import patch_project
from scripts.validate_capcut_draft import (
    validate_contiguous_target_ranges,
    validate_material_paths_exist,
)
from scripts.write_cut_report import write_json_report, write_markdown_report


def build_backup_path(path: Path, stamp: str) -> Path:
    return path.with_name(f"{path.name}.bak.{stamp}")


def generate_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


@dataclass(slots=True)
class WorkflowResult:
    report_json: Path
    report_markdown: Path
    backups: list[Path]


def atomic_replace(path: Path, new_text: str) -> None:
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(new_text, encoding="utf-8")
    temp_path.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft-folder", required=True)
    parser.add_argument("--silence-threshold-db", type=float, default=-35.0)
    parser.add_argument("--min-silence-ms", type=int, default=250)
    parser.add_argument("--lead-padding-ms", type=int, default=120)
    parser.add_argument("--tail-padding-ms", type=int, default=180)
    parser.add_argument("--min-keep-ms", type=int, default=300)
    parser.add_argument("--max-gap-ms", type=int, default=120)
    parser.add_argument("--ffmpeg-bin", default="ffmpeg")
    return parser.parse_args()


def build_report_payload(
    keep_ranges_by_segment_id: dict[str, list[KeepRange]],
    segments,
    settings: DetectionSettings,
) -> dict:
    original_timeline_duration_us = sum(segment.target_duration_us for segment in segments)
    new_timeline_duration_us = sum(
        keep_range.end_us - keep_range.start_us
        for keep_ranges in keep_ranges_by_segment_id.values()
        for keep_range in keep_ranges
    )
    removed_duration_us = original_timeline_duration_us - new_timeline_duration_us
    return {
        "original_timeline_duration_us": original_timeline_duration_us,
        "new_timeline_duration_us": new_timeline_duration_us,
        "removed_duration_us": removed_duration_us,
        "settings": {
            "silence_threshold_db": settings.silence_threshold_db,
            "min_silence_ms": settings.min_silence_ms,
            "lead_padding_ms": settings.lead_padding_ms,
            "tail_padding_ms": settings.tail_padding_ms,
            "min_keep_ms": settings.min_keep_ms,
            "max_gap_ms": settings.max_gap_ms,
            "ffmpeg_bin": settings.ffmpeg_bin,
        },
        "segments": [
            {
                "segment_id": segment.segment_id,
                "material_path": segment.material_path,
                "original_duration_us": segment.source_duration_us,
                "kept_duration_us": sum(
                    keep_range.end_us - keep_range.start_us
                    for keep_range in keep_ranges_by_segment_id[segment.segment_id]
                ),
                "removed_duration_us": segment.source_duration_us
                - sum(
                    keep_range.end_us - keep_range.start_us
                    for keep_range in keep_ranges_by_segment_id[segment.segment_id]
                ),
                "keep_range_count": len(keep_ranges_by_segment_id[segment.segment_id]),
            }
            for segment in segments
        ],
    }


def ensure_working_draft(source_draft: Path, working_draft: Path) -> Path:
    if source_draft.resolve() == working_draft.resolve():
        return working_draft
    if working_draft.exists():
        raise RuntimeError(f"working draft already exists: {working_draft}")
    shutil.copytree(source_draft, working_draft)
    return working_draft


def backup_file(path: Path, timestamp: str) -> Path:
    backup_path = build_backup_path(path, timestamp)
    backup_path.write_bytes(path.read_bytes())
    return backup_path


def run_workflow(
    source_draft: Path,
    working_draft: Path,
    detect_keep_ranges: Callable[[str, int, int, DetectionSettings], list[KeepRange]] | None = None,
    timestamp: str | None = None,
    settings: DetectionSettings | None = None,
) -> WorkflowResult:
    active_draft = ensure_working_draft(source_draft, working_draft)
    stamp = timestamp or generate_timestamp()
    settings = settings or DetectionSettings()
    detect_keep_ranges = detect_keep_ranges or detect_keep_ranges_ffmpeg

    bundle = load_draft_bundle(active_draft)
    segments = resolve_video_segments(bundle)
    if not segments:
        raise RuntimeError("no video segments found in draft")

    missing_paths = validate_material_paths_exist([segment.material_path for segment in segments])
    if missing_paths:
        raise RuntimeError(f"source media missing: {missing_paths}")

    backups = [
        backup_file(bundle.draft_content_path, stamp),
        backup_file(bundle.project_path, stamp),
    ]

    keep_ranges_by_segment_id: dict[str, list[KeepRange]] = {}
    for segment in segments:
        keep_ranges = detect_keep_ranges(
            segment.material_path,
            segment.source_start_us,
            segment.source_duration_us,
            settings,
        )
        if not keep_ranges:
            raise RuntimeError(f"analysis would remove all content from segment {segment.segment_id}")
        keep_ranges_by_segment_id[segment.segment_id] = keep_ranges

    track_container = get_track_container(bundle)
    patched_root = patch_project(track_container, keep_ranges_by_segment_id)
    for track in patched_root.get("tracks", []):
        if track.get("type") != "video":
            continue
        errors = validate_contiguous_target_ranges(track.get("segments", []))
        if errors:
            raise RuntimeError("; ".join(errors))

    if track_container is bundle.draft_content:
        atomic_replace(bundle.draft_content_path, json.dumps(patched_root, indent=2))
    else:
        atomic_replace(bundle.project_path, json.dumps(patched_root, indent=2))

    report_payload = build_report_payload(keep_ranges_by_segment_id, segments, settings)
    report_json = active_draft / "dead_air_report.json"
    report_markdown = active_draft / "dead_air_report.md"
    write_json_report(report_json, report_payload)
    write_markdown_report(report_markdown, report_payload)
    return WorkflowResult(
        report_json=report_json,
        report_markdown=report_markdown,
        backups=backups,
    )


def main() -> int:
    args = parse_args()
    draft_folder = Path(args.draft_folder)
    if not draft_folder.exists():
        raise SystemExit(f"draft folder not found: {draft_folder}")
    settings = DetectionSettings(
        silence_threshold_db=args.silence_threshold_db,
        min_silence_ms=args.min_silence_ms,
        lead_padding_ms=args.lead_padding_ms,
        tail_padding_ms=args.tail_padding_ms,
        min_keep_ms=args.min_keep_ms,
        max_gap_ms=args.max_gap_ms,
        ffmpeg_bin=args.ffmpeg_bin,
    )
    run_workflow(
        source_draft=draft_folder,
        working_draft=draft_folder,
        settings=settings,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
