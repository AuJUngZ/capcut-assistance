from scripts.detect_dead_air import (
    KeepRange,
    merge_keep_ranges,
    parse_silence_spans,
    silence_spans_to_keep_ranges,
    trim_to_content,
)


def test_merge_keep_ranges_bridges_short_silences():
    ranges = [KeepRange(0, 900_000), KeepRange(950_000, 1_900_000)]

    merged = merge_keep_ranges(ranges, max_gap_us=100_000)

    assert merged == [KeepRange(0, 1_900_000)]


def test_trim_to_content_applies_padding_and_floor():
    keep = trim_to_content(
        speech_spans=[(1_000_000, 2_000_000)],
        clip_start_us=0,
        clip_duration_us=4_000_000,
        lead_padding_us=120_000,
        tail_padding_us=180_000,
        min_keep_us=300_000,
    )

    assert keep == [KeepRange(880_000, 2_180_000)]


def test_parse_silence_spans_reads_ffmpeg_pairs():
    stderr = """
    [silencedetect @ 000001] silence_start: 0.5
    [silencedetect @ 000001] silence_end: 1.0 | silence_duration: 0.5
    [silencedetect @ 000001] silence_start: 1.7
    """

    spans = parse_silence_spans(stderr, clip_duration_us=2_000_000)

    assert spans == [(500_000, 1_000_000), (1_700_000, 2_000_000)]


def test_silence_spans_to_keep_ranges_merges_short_pauses():
    keep = silence_spans_to_keep_ranges(
        silence_spans=[(500_000, 700_000), (760_000, 900_000)],
        clip_start_us=1_000_000,
        clip_duration_us=1_500_000,
        lead_padding_us=100_000,
        tail_padding_us=100_000,
        min_keep_us=150_000,
        max_gap_us=120_000,
    )

    assert keep == [KeepRange(1_000_000, 2_500_000)]
