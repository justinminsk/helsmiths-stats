from __future__ import annotations

from datetime import datetime

from .constants import INPUT_FILE, README_FILE
from .parser import parse_lists
from .writers import write_scope_outputs


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


def run() -> None:
    text = INPUT_FILE.read_text(encoding="utf-8")
    all_lists = parse_lists(text)

    singles_lists = [army_list for army_list in all_lists if army_list.source == "Singles"]
    teams_lists = [army_list for army_list in all_lists if army_list.source == "Teams"]

    write_scope_outputs("combined", "Combined", all_lists)
    write_scope_outputs("singles", "Singles", singles_lists)
    write_scope_outputs("teams", "Teams", teams_lists)
    update_readme_run_date()
