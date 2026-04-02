from __future__ import annotations

import argparse
import shutil
from datetime import date
from pathlib import Path

from helsmith_stats.constants import DOCS_DIR, INPUT_FILE, REPORTS_DIR, ROOT, SUMMARIES_DIR


def build_template(start_date: str) -> str:
    return (
        "# Helsmiths post-points reset\n\n"
        f"Tracking period starts: {start_date}\n\n"
        "Add new 5-0 / 4-1 lists below using the same export formats as before.\n\n"
        "# **Singles**\n\n"
        "##### 5-0\n\n"
        "##### 4-1\n\n"
        "# **Teams**\n\n"
        "##### 5-0\n\n"
        "##### 4-1\n"
    )


def copy_tree_if_exists(source: Path, destination: Path) -> None:
    if source.exists():
        shutil.copytree(source, destination)


def copy_file_if_exists(source: Path, destination: Path) -> None:
    if source.exists():
        shutil.copy2(source, destination)


def _print_plan(archive_dir: Path, start_date: str) -> None:
    print(f"Archive target: {archive_dir}")
    print(f"- copy file: {INPUT_FILE} -> {archive_dir / INPUT_FILE.name}")
    print(f"- copy dir: {REPORTS_DIR} -> {archive_dir / 'reports'}")
    print(f"- copy dir: {SUMMARIES_DIR} -> {archive_dir / 'summaries'}")
    print(f"- copy dir: {DOCS_DIR} -> {archive_dir / 'docs'}")
    print(f"- reset source file with start date: {start_date}")


def run(label: str, start_date: str, dry_run: bool) -> None:
    archive_dir = ROOT / "history" / label
    if archive_dir.exists():
        raise FileExistsError(f"Archive already exists: {archive_dir}")

    if dry_run:
        _print_plan(archive_dir, start_date)
        print("Dry run only: no files were modified.")
        return

    archive_dir.mkdir(parents=True)

    copy_file_if_exists(INPUT_FILE, archive_dir / INPUT_FILE.name)
    copy_tree_if_exists(REPORTS_DIR, archive_dir / "reports")
    copy_tree_if_exists(SUMMARIES_DIR, archive_dir / "summaries")
    copy_tree_if_exists(DOCS_DIR, archive_dir / "docs")

    INPUT_FILE.write_text(build_template(start_date), encoding="utf-8")

    print(f"Created archive: {archive_dir}")
    print(f"Reset source file: {INPUT_FILE}")


def parse_args() -> argparse.Namespace:
    today = date.today().isoformat()
    parser = argparse.ArgumentParser(
        description="Archive current stats outputs and reset source markdown for next points cycle."
    )
    parser.add_argument(
        "--label",
        default=f"{today}-pre-points",
        help="Archive folder name under history/.",
    )
    parser.add_argument(
        "--start-date",
        default=today,
        help="Start date to write into the reset source template (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned archive/reset actions without writing files.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run(arguments.label, arguments.start_date, arguments.dry_run)
