from copy import deepcopy

from scripts.detect_dead_air import KeepRange


def clone_segment(
    segment: dict,
    *,
    source_start: int,
    source_duration: int,
    target_start: int,
) -> dict:
    cloned = deepcopy(segment)
    cloned["source_timerange"] = {"start": source_start, "duration": source_duration}
    cloned["target_timerange"] = {"start": target_start, "duration": source_duration}
    return cloned


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
                    source_start=source_start,
                    source_duration=duration,
                    target_start=cursor_us,
                )
            )
            cursor_us += duration
            continue
        for keep_range in keep_ranges:
            duration = keep_range.end_us - keep_range.start_us
            patched.append(
                clone_segment(
                    segment,
                    source_start=keep_range.start_us,
                    source_duration=duration,
                    target_start=cursor_us,
                )
            )
            cursor_us += duration
    return patched
