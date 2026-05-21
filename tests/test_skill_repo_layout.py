from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_text(*parts: str) -> str:
    return ROOT.joinpath(*parts).read_text(encoding="utf-8")


def test_installable_skill_lives_under_skills_directory() -> None:
    text = read_text("skills", "capcut-assistance", "SKILL.md")
    assert "name: capcut-assistance" in text
    assert "python -m scripts.workflow --draft-folder" in text
    assert "repository checkout that contains `scripts/workflow.py`" in text


def test_skill_readme_mentions_repo_layout_contract() -> None:
    text = read_text("skills", "capcut-assistance", "README.md")
    assert "repository checkout that contains `scripts/workflow.py`" in text


def test_root_skill_file_is_removed() -> None:
    assert not ROOT.joinpath("SKILL.md").exists()
