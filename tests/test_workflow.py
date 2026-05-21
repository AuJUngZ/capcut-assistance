from pathlib import Path


def test_skill_bundle_contains_portable_entrypoints():
    root = Path(__file__).resolve().parents[1]

    assert (root / "SKILL.md").exists()
    assert (root / "docs" / "agent-compatibility.md").exists()
    assert (root / "scripts" / "workflow.py").exists()
    assert (root / "scripts" / "capcut_schema.py").exists()
