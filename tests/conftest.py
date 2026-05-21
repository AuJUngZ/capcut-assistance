import sys
from pathlib import Path


FIXTURES = Path(__file__).resolve().parent / "fixtures"
SAMPLE_DRAFT = FIXTURES / "sample_draft"

skill_dir = Path(__file__).resolve().parents[1] / "skills" / "dead-air-removal"
sys.path.insert(0, str(skill_dir))
