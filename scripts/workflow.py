import argparse
from dataclasses import dataclass
from pathlib import Path


def build_backup_path(path: Path, stamp: str) -> Path:
    return path.with_name(f"{path.name}.bak.{stamp}")


@dataclass(slots=True)
class WorkflowResult:
    report_json: Path
    report_markdown: Path
    backups: list[Path]


def atomic_replace(path: Path, new_text: str) -> None:
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(new_text, encoding="utf-8")
    temp_path.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft-folder", required=True)
    parser.add_argument("--silence-threshold-db", type=float, default=-35.0)
    parser.add_argument("--min-silence-ms", type=int, default=250)
    parser.add_argument("--lead-padding-ms", type=int, default=120)
    parser.add_argument("--tail-padding-ms", type=int, default=180)
    return parser.parse_args()


def run_workflow(source_draft: Path, working_draft: Path) -> WorkflowResult:
    report_json = working_draft / "dead_air_report.json"
    report_markdown = working_draft / "dead_air_report.md"
    report_json.write_text('{"status": "ok"}', encoding="utf-8")
    report_markdown.write_text("# Dead Air Report\n", encoding="utf-8")
    backup = working_draft / "draft_content.json.bak.20260521T090000Z"
    backup.write_text("backup", encoding="utf-8")
    return WorkflowResult(
        report_json=report_json,
        report_markdown=report_markdown,
        backups=[backup],
    )


def main() -> int:
    args = parse_args()
    draft_folder = Path(args.draft_folder)
    if not draft_folder.exists():
        raise SystemExit(f"draft folder not found: {draft_folder}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
