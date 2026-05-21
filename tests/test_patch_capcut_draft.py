from pathlib import Path

from scripts.capcut_schema import load_draft_bundle, resolve_video_segments
from scripts.detect_dead_air import KeepRange
from scripts.patch_capcut_draft import patch_video_track


SAMPLE_DRAFT = Path(__file__).resolve().parent / "fixtures" / "sample_draft"


def test_patch_video_track_splits_segment_and_closes_gap():
    bundle = load_draft_bundle(SAMPLE_DRAFT)
    resolve_video_segments(bundle)

    keep_ranges = {
        "seg-1": [KeepRange(0, 2_000_000), KeepRange(3_000_000, 5_000_000)],
        "seg-2": [KeepRange(1_000_000, 6_000_000)],
    }

    updated_segments = patch_video_track(bundle.project["tracks"][0]["segments"], keep_ranges)

    assert len(updated_segments) == 3
    assert updated_segments[1]["target_timerange"]["start"] == 2_000_000
    assert updated_segments[2]["target_timerange"]["start"] == 4_000_000
    assert len({segment["id"] for segment in updated_segments}) == 3
