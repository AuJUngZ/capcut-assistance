from pathlib import Path


def test_skill_bundle_contains_portable_entrypoints():
    root = Path(__file__).resolve().parents[1]

    assert (root / "SKILL.md").exists()
    assert (root / "docs" / "agent-compatibility.md").exists()
    assert (root / "scripts" / "workflow.py").exists()
    assert (root / "scripts" / "capcut_schema.py").exists()


def test_build_backup_path_uses_timestamp_suffix():
    from scripts.workflow import build_backup_path

    backup = build_backup_path(Path("draft_content.json"), "20260521T090000Z")

    assert backup.name == "draft_content.json.bak.20260521T090000Z"


def test_skill_doc_mentions_backup_validation_and_report():
    text = Path("C:/Coding/capcut-skills/.worktrees/capcut-dead-air-portable/SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "backup" in text.lower()
    assert "validate" in text.lower()
    assert "report" in text.lower()
    assert "heavily edited" in text.lower()
