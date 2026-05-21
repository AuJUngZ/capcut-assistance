from dataclasses import dataclass
import re
import shutil
import subprocess
from pathlib import Path


SILENCE_START_RE = re.compile(r"silence_start:\s*(?P<seconds>[0-9.]+)")
SILENCE_END_RE = re.compile(r"silence_end:\s*(?P<seconds>[0-9.]+)")


@dataclass(slots=True, frozen=True)
class KeepRange:
    start_us: int
    end_us: int


@dataclass(slots=True, frozen=True)
class DetectionSettings:
    silence_threshold_db: float = -35.0
    min_silence_ms: int = 250
    lead_padding_ms: int = 120
    tail_padding_ms: int = 180
    min_keep_ms: int = 300
    max_gap_ms: int = 120
    ffmpeg_bin: str = "ffmpeg"


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


def parse_silence_spans(stderr: str, clip_duration_us: int) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    silence_start_us: int | None = None
    for line in stderr.splitlines():
        start_match = SILENCE_START_RE.search(line)
        if start_match:
            silence_start_us = min(seconds_to_us(start_match.group("seconds")), clip_duration_us)
            continue
        end_match = SILENCE_END_RE.search(line)
        if end_match and silence_start_us is not None:
            silence_end_us = min(seconds_to_us(end_match.group("seconds")), clip_duration_us)
            spans.append((silence_start_us, max(silence_start_us, silence_end_us)))
            silence_start_us = None
    if silence_start_us is not None:
        spans.append((silence_start_us, clip_duration_us))
    return spans


def silence_spans_to_keep_ranges(
    silence_spans: list[tuple[int, int]],
    clip_start_us: int,
    clip_duration_us: int,
    lead_padding_us: int,
    tail_padding_us: int,
    min_keep_us: int,
    max_gap_us: int,
) -> list[KeepRange]:
    clip_end_us = clip_start_us + clip_duration_us
    speech_spans: list[tuple[int, int]] = []
    cursor_us = 0
    for silence_start_us, silence_end_us in sorted(silence_spans):
        if silence_start_us > cursor_us:
            speech_spans.append((clip_start_us + cursor_us, clip_start_us + silence_start_us))
        cursor_us = max(cursor_us, silence_end_us)
    if cursor_us < clip_duration_us:
        speech_spans.append((clip_start_us + cursor_us, clip_end_us))
    keep_ranges = trim_to_content(
        speech_spans=speech_spans,
        clip_start_us=clip_start_us,
        clip_duration_us=clip_duration_us,
        lead_padding_us=lead_padding_us,
        tail_padding_us=tail_padding_us,
        min_keep_us=min_keep_us,
    )
    return merge_keep_ranges(keep_ranges, max_gap_us=max_gap_us)


def detect_keep_ranges_ffmpeg(
    media_path: str,
    clip_start_us: int,
    clip_duration_us: int,
    settings: DetectionSettings,
) -> list[KeepRange]:
    ffmpeg_bin = settings.ffmpeg_bin
    if shutil.which(ffmpeg_bin) is None and not Path(ffmpeg_bin).exists():
        raise RuntimeError(
            f"ffmpeg not found: {ffmpeg_bin}. Install ffmpeg or pass --ffmpeg-bin with a valid path."
        )

    command = [
        ffmpeg_bin,
        "-hide_banner",
        "-nostats",
        "-ss",
        f"{clip_start_us / 1_000_000:.6f}",
        "-t",
        f"{clip_duration_us / 1_000_000:.6f}",
        "-i",
        media_path,
        "-af",
        f"silencedetect=noise={settings.silence_threshold_db}dB:d={settings.min_silence_ms / 1000:.3f}",
        "-f",
        "null",
        "-",
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg silencedetect failed for {media_path}: {result.stderr.strip()}")

    silence_spans = parse_silence_spans(result.stderr, clip_duration_us=clip_duration_us)
    return silence_spans_to_keep_ranges(
        silence_spans=silence_spans,
        clip_start_us=clip_start_us,
        clip_duration_us=clip_duration_us,
        lead_padding_us=settings.lead_padding_ms * 1_000,
        tail_padding_us=settings.tail_padding_ms * 1_000,
        min_keep_us=settings.min_keep_ms * 1_000,
        max_gap_us=settings.max_gap_ms * 1_000,
    )
