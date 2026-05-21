import json
from pathlib import Path
import shutil

from scripts.detect_dead_air import KeepRange


def test_skill_bundle_contains_portable_entrypoints():
    root = Path(__file__).resolve().parents[1]

    assert (root / "skills" / "dead-air-removal" / "SKILL.md").exists()
    assert (root / "docs" / "agent-compatibility.md").exists()
    assert (root / "scripts" / "workflow.py").exists()
    assert (root / "scripts" / "capcut_schema.py").exists()


def test_build_backup_path_uses_timestamp_suffix():
    from scripts.workflow import build_backup_path

    backup = build_backup_path(Path("draft_content.json"), "20260521T090000Z")

    assert backup.name == "draft_content.json.bak.20260521T090000Z"


def test_generate_timestamp_uses_utc_style_format():
    from scripts.workflow import generate_timestamp

    stamp = generate_timestamp()

    assert len(stamp) == 16
    assert stamp.endswith("Z")


def test_skill_doc_mentions_backup_validation_and_report():
    root = Path(__file__).resolve().parents[1]
    text = (root / "skills" / "dead-air-removal" / "SKILL.md").read_text(encoding="utf-8")

    assert "backup" in text.lower()
    assert "validation" in text.lower()
    assert "report" in text.lower()
    assert "nearly all content" in text.lower()


def test_run_workflow_writes_backup_and_reports(tmp_path: Path):
    from scripts.workflow import run_workflow

    sample_draft = Path(__file__).resolve().parent / "fixtures" / "sample_draft"
    working_copy = tmp_path / "draft"
    shutil.copytree(sample_draft, working_copy)

    media_dir = tmp_path / "media"
    media_dir.mkdir()
    clip_a = media_dir / "clip-a.mp4"
    clip_b = media_dir / "clip-b.mp4"
    clip_a.write_bytes(b"a")
    clip_b.write_bytes(b"b")

    draft_content_path = working_copy / "draft_content.json"
    draft_content = json.loads(draft_content_path.read_text(encoding="utf-8"))
    draft_content["materials"]["videos"][0]["path"] = clip_a.as_posix()
    draft_content["materials"]["videos"][1]["path"] = clip_b.as_posix()
    draft_content_path.write_text(json.dumps(draft_content, indent=2), encoding="utf-8")

    def fake_detector(media_path: str, clip_start_us: int, clip_duration_us: int, settings) -> list[KeepRange]:
        if media_path.endswith("clip-a.mp4"):
            return [KeepRange(0, 2_000_000), KeepRange(3_000_000, 5_000_000)]
        return [KeepRange(clip_start_us, clip_start_us + clip_duration_us)]

    result = run_workflow(
        source_draft=working_copy,
        working_draft=working_copy,
        detect_keep_ranges=fake_detector,
        timestamp="20260521T090000Z",
    )

    assert result.report_json.exists()
    assert result.report_markdown.exists()
    assert len(result.backups) == 2

    project = json.loads((working_copy / "Timelines" / "project.json").read_text(encoding="utf-8"))
    segments = project["tracks"][0]["segments"]
    assert len(segments) == 3
    assert segments[1]["target_timerange"]["start"] == 2_000_000
    assert segments[2]["target_timerange"]["start"] == 4_000_000

    report = json.loads(result.report_json.read_text(encoding="utf-8"))
    assert report["original_timeline_duration_us"] == 13_000_000
    assert report["new_timeline_duration_us"] == 9_000_000
    assert report["removed_duration_us"] == 4_000_000


def test_run_workflow_updates_draft_content_when_tracks_live_there(tmp_path: Path):
    from scripts.workflow import run_workflow

    sample_draft = Path(__file__).resolve().parent / "fixtures" / "sample_draft"
    working_copy = tmp_path / "draft-content-tracks"
    shutil.copytree(sample_draft, working_copy)

    project_path = working_copy / "Timelines" / "project.json"
    project_data = json.loads(project_path.read_text(encoding="utf-8"))
    draft_content_path = working_copy / "draft_content.json"
    draft_content = json.loads(draft_content_path.read_text(encoding="utf-8"))
    draft_content["tracks"] = project_data["tracks"]
    draft_content_path.write_text(json.dumps(draft_content, indent=2), encoding="utf-8")
    project_path.write_text(json.dumps({"main_timeline_id": "timeline-only"}, indent=2), encoding="utf-8")

    media_dir = tmp_path / "media-2"
    media_dir.mkdir()
    clip_a = media_dir / "clip-a.mp4"
    clip_b = media_dir / "clip-b.mp4"
    clip_a.write_bytes(b"a")
    clip_b.write_bytes(b"b")

    draft_content = json.loads(draft_content_path.read_text(encoding="utf-8"))
    draft_content["materials"]["videos"][0]["path"] = clip_a.as_posix()
    draft_content["materials"]["videos"][1]["path"] = clip_b.as_posix()
    draft_content_path.write_text(json.dumps(draft_content, indent=2), encoding="utf-8")

    def fake_detector(media_path: str, clip_start_us: int, clip_duration_us: int, settings) -> list[KeepRange]:
        if media_path.endswith("clip-a.mp4"):
            return [KeepRange(0, 2_000_000), KeepRange(3_000_000, 5_000_000)]
        return [KeepRange(clip_start_us, clip_start_us + clip_duration_us)]

    run_workflow(
        source_draft=working_copy,
        working_draft=working_copy,
        detect_keep_ranges=fake_detector,
        timestamp="20260521T090000Z",
    )

    updated_draft_content = json.loads(draft_content_path.read_text(encoding="utf-8"))
    segments = updated_draft_content["tracks"][0]["segments"]
    assert len(segments) == 3
    assert segments[2]["target_timerange"]["start"] == 4_000_000
