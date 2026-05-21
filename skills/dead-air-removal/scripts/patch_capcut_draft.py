from copy import deepcopy

from .detect_dead_air import KeepRange


def clone_segment(
    segment: dict,
    *,
    segment_id: str,
    source_start: int,
    source_duration: int,
    target_start: int,
) -> dict:
    cloned = deepcopy(segment)
    cloned["id"] = segment_id
    cloned["source_timerange"] = {"start": source_start, "duration": source_duration}
    cloned["target_timerange"] = {"start": target_start, "duration": source_duration}
    return cloned


def build_split_segment_id(segment_id: str, piece_index: int, total_pieces: int) -> str:
    if total_pieces == 1 and piece_index == 0:
        return segment_id
    return f"{segment_id}__{piece_index + 1}"


def patch_video_track(
    segments: list[dict],
    keep_ranges_by_segment_id: dict[str, list[KeepRange]],
) -> list[dict]:
    patched: list[dict] = []
    cursor_us = 0
    for segment in segments:
        segment_id = segment["id"]
        source_start = segment["source_timerange"]["start"]
        keep_ranges = keep_ranges_by_segment_id.get(segment_id)
        if not keep_ranges:
            duration = segment["source_timerange"]["duration"]
            patched.append(
                clone_segment(
                    segment,
                    segment_id=segment_id,
                    source_start=source_start,
                    source_duration=duration,
                    target_start=cursor_us,
                )
            )
            cursor_us += duration
            continue
        for piece_index, keep_range in enumerate(keep_ranges):
            duration = keep_range.end_us - keep_range.start_us
            patched.append(
                clone_segment(
                    segment,
                    segment_id=build_split_segment_id(segment_id, piece_index, len(keep_ranges)),
                    source_start=keep_range.start_us,
                    source_duration=duration,
                    target_start=cursor_us,
                )
            )
            cursor_us += duration
    return patched


def patch_project(
    project: dict,
    keep_ranges_by_segment_id: dict[str, list[KeepRange]],
) -> dict:
    patched_project = deepcopy(project)
    for track in patched_project.get("tracks", []):
        if track.get("type") != "video":
            continue
        track["segments"] = patch_video_track(track.get("segments", []), keep_ranges_by_segment_id)
    return patched_project
