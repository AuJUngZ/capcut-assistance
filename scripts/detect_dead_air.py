from dataclasses import dataclass
import re


SILENCE_START_RE = re.compile(r"silence_start:\s*(?P<seconds>[0-9.]+)")
SILENCE_END_RE = re.compile(r"silence_end:\s*(?P<seconds>[0-9.]+)")


@dataclass(slots=True, frozen=True)
class KeepRange:
    start_us: int
    end_us: int


def merge_keep_ranges(ranges: list[KeepRange], max_gap_us: int) -> list[KeepRange]:
    if not ranges:
        return []
    ordered = sorted(ranges, key=lambda item: item.start_us)
    merged = [ordered[0]]
    for current in ordered[1:]:
        previous = merged[-1]
        if current.start_us - previous.end_us <= max_gap_us:
            merged[-1] = KeepRange(previous.start_us, max(previous.end_us, current.end_us))
            continue
        merged.append(current)
    return merged


def trim_to_content(
    speech_spans: list[tuple[int, int]],
    clip_start_us: int,
    clip_duration_us: int,
    lead_padding_us: int,
    tail_padding_us: int,
    min_keep_us: int,
) -> list[KeepRange]:
    clip_end_us = clip_start_us + clip_duration_us
    keep: list[KeepRange] = []
    for start_us, end_us in speech_spans:
        padded_start = max(clip_start_us, start_us - lead_padding_us)
        padded_end = min(clip_end_us, end_us + tail_padding_us)
        if padded_end - padded_start >= min_keep_us:
            keep.append(KeepRange(padded_start, padded_end))
    return keep


def seconds_to_us(raw: str) -> int:
    return int(float(raw) * 1_000_000)
