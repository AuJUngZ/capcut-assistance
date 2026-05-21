from scripts.validate_capcut_draft import validate_contiguous_target_ranges


def test_validate_contiguous_target_ranges_rejects_gaps():
    segments = [
        {"target_timerange": {"start": 0, "duration": 1_000_000}},
        {"target_timerange": {"start": 1_200_000, "duration": 1_000_000}},
    ]

    errors = validate_contiguous_target_ranges(segments)

    assert errors == ["segment timeline is not contiguous at index 1"]
