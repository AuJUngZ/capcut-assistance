from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_text(*parts: str) -> str:
    return ROOT.joinpath(*parts).read_text(encoding="utf-8")


def test_installable_skill_lives_under_skills_directory() -> None:
    text = read_text("skills", "dead-air-removal", "SKILL.md")
    assert "name: dead-air-removal" in text
    assert "python -m scripts.workflow --draft-folder" in text
    assert "repository checkout that contains `scripts/workflow.py`" in text


def test_skill_readme_mentions_repo_layout_contract() -> None:
    text = read_text("skills", "dead-air-removal", "README.md")
    assert "repository checkout that contains `scripts/workflow.py`" in text


def test_root_readme_contains_install_command() -> None:
    text = read_text("README.md")
    assert "npx skills add" in text
    assert "--skill dead-air-removal" in text
    assert "skills/dead-air-removal/SKILL.md" in text


def test_root_readme_documents_runtime_requirements() -> None:
    text = read_text("README.md")
    assert "Python" in text
    assert "ffmpeg" in text
    assert "python -m scripts.workflow --draft-folder" in text


def test_root_skill_file_is_removed() -> None:
    assert not ROOT.joinpath("SKILL.md").exists()


def test_compatibility_doc_uses_collection_layout() -> None:
    text = read_text("docs", "agent-compatibility.md")
    assert "--skill dead-air-removal" in text
    assert "skills/dead-air-removal/SKILL.md" in text
    assert "root-level `SKILL.md`" not in text


def test_gitignore_excludes_local_draft_artifacts() -> None:
    text = read_text(".gitignore")
    assert "real-drafts/" in text
    assert "*.bak.*" in text
