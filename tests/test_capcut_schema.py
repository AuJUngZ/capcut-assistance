from pathlib import Path

from scripts.capcut_schema import load_draft_bundle, resolve_video_segments


SAMPLE_DRAFT = Path(__file__).resolve().parent / "fixtures" / "sample_draft"


def test_load_draft_bundle_reads_both_capcut_json_files():
    bundle = load_draft_bundle(SAMPLE_DRAFT)

    assert bundle.draft_content_path.name == "draft_content.json"
    assert bundle.project_path.name == "project.json"
    assert "materials" in bundle.draft_content
    assert "tracks" in bundle.project


def test_resolve_video_segments_maps_materials_to_source_ranges():
    bundle = load_draft_bundle(SAMPLE_DRAFT)

    segments = resolve_video_segments(bundle)

    assert len(segments) == 2
    assert segments[0].material_path.endswith("clip-a.mp4")
    assert segments[0].source_start_us == 0
    assert segments[0].source_duration_us == 8_000_000


def test_resolve_video_segments_falls_back_to_draft_content_tracks():
    bundle = load_draft_bundle(SAMPLE_DRAFT)
    bundle.draft_content["tracks"] = bundle.project["tracks"]
    bundle.project = {"main_timeline_id": "timeline-only"}

    segments = resolve_video_segments(bundle)

    assert len(segments) == 2
    assert segments[1].material_path.endswith("clip-b.mp4")
