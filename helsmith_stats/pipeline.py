from __future__ import annotations

from datetime import datetime

from .constants import INPUT_FILE, README_FILE, ROOT
from .parser import parse_lists
from .web import build_web_page
from .writers import write_scope_outputs, write_scope_outputs_to_dirs


def update_readme_run_date() -> None:
    if not README_FILE.exists():
        return

    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    marker_prefix = "- Last run date:"
    new_line = f"{marker_prefix} {timestamp}"

    lines = README_FILE.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.startswith(marker_prefix):
            lines[index] = new_line
            README_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return

    insert_at = 3 if len(lines) >= 3 else len(lines)
    lines.insert(insert_at, new_line)
    README_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _split_lists(all_lists: list) -> tuple[list, list]:
    singles_lists = [
        army_list for army_list in all_lists if army_list.source == "Singles"
    ]
    teams_lists = [army_list for army_list in all_lists if army_list.source == "Teams"]
    return singles_lists, teams_lists


def _rebuild_history_snapshots() -> None:
    history_dir = ROOT / "history"
    if not history_dir.exists():
        return

    for snapshot_dir in sorted(
        entry for entry in history_dir.iterdir() if entry.is_dir()
    ):
        input_file = snapshot_dir / "Helsmiths 5-0s.md"
        if not input_file.exists():
            continue

        text = input_file.read_text(encoding="utf-8")
        all_lists = parse_lists(text)
        singles_lists, teams_lists = _split_lists(all_lists)
        reports_dir = snapshot_dir / "reports"
        summaries_dir = snapshot_dir / "summaries"

        write_scope_outputs_to_dirs(
            "combined", "Combined", all_lists, summaries_dir, reports_dir
        )
        write_scope_outputs_to_dirs(
            "singles", "Singles", singles_lists, summaries_dir, reports_dir
        )
        write_scope_outputs_to_dirs(
            "teams", "Teams", teams_lists, summaries_dir, reports_dir
        )


def run() -> None:
    text = INPUT_FILE.read_text(encoding="utf-8")
    all_lists = parse_lists(text)

    singles_lists, teams_lists = _split_lists(all_lists)

    write_scope_outputs("combined", "Combined", all_lists)
    write_scope_outputs("singles", "Singles", singles_lists)
    write_scope_outputs("teams", "Teams", teams_lists)
    _rebuild_history_snapshots()
    build_web_page()
    update_readme_run_date()
