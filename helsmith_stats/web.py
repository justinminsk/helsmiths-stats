from __future__ import annotations

import csv
from datetime import datetime
from html import escape
from pathlib import Path
from collections import Counter

from .constants import DOCS_DIR, SUMMARIES_DIR


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def _top_rows(path: Path, limit: int = 5) -> list[dict[str, str]]:
    return _read_csv(path)[:limit]


def _render_table(title: str, headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        rows = [["—" for _ in headers]]

    header_html = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body_html = "".join(
        "<tr>" + "".join(f"<td>{escape(value)}</td>" for value in row) + "</tr>"
        for row in rows
    )
    return f"""
<section class=\"card\">
  <h3>{escape(title)}</h3>
  <table>
    <thead><tr>{header_html}</tr></thead>
    <tbody>{body_html}</tbody>
  </table>
</section>
"""


def _rows_from_csv(path: Path, keys: list[str], limit: int = 8) -> list[list[str]]:
    rows = _top_rows(path, limit)
    return [[row.get(key, "") for key in keys] for row in rows]


def _result_breakdown_rows(list_rows: list[dict[str, str]]) -> list[list[str]]:
    counts = Counter(row.get("result", "Unknown") for row in list_rows)
    ordered_results = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [[result, str(count)] for result, count in ordered_results]


def _scope_section(scope: str, label: str) -> str:
    scope_dir = SUMMARIES_DIR / scope
    list_rows = _read_csv(scope_dir / "list_level_summary.csv")
    presence_rows = [
        [
            row.get("unit_name", ""),
            row.get("lists_with_unit", ""),
            row.get("percent_of_lists", "") + "%",
        ]
        for row in _top_rows(scope_dir / "unit_presence_percent.csv", 8)
    ]
    subfaction_rows = _rows_from_csv(
        scope_dir / "subfaction_counts.csv",
        ["subfaction", "list_count"],
        8,
    )
    manifestation_rows = _rows_from_csv(
        scope_dir / "manifestation_lore_counts.csv",
        ["manifestation_lore", "list_count"],
        8,
    )
    artifact_rows = _rows_from_csv(
        scope_dir / "artifact_counts.csv", ["artifact", "count"], 8
    )
    command_trait_rows = _rows_from_csv(
        scope_dir / "command_trait_counts.csv",
        ["command_trait", "count"],
        8,
    )
    warmachine_trait_rows = _rows_from_csv(
        scope_dir / "warmachine_trait_counts.csv",
        ["warmachine_trait", "count"],
        8,
    )
    unit_entry_rows = _rows_from_csv(
        scope_dir / "unit_entry_counts.csv",
        ["unit_name", "unit_entries"],
        8,
    )
    unit_model_rows = _rows_from_csv(
        scope_dir / "unit_model_counts.csv",
        ["unit_name", "model_count"],
        8,
    )
    unplayed_rows = _rows_from_csv(
        scope_dir / "unplayed_units.csv", ["unit_name", "unit_size"], 8
    )
    result_rows = _result_breakdown_rows(list_rows)

    report_link = f"../reports/{scope}.md"

    return f"""
<section class=\"scope\">
    <a id=\"{escape(scope)}\"></a>
  <h2>{escape(label)}</h2>
  <p>Lists parsed: <strong>{len(list_rows)}</strong> · <a href=\"{escape(report_link)}\">View full markdown report</a></p>
  <div class=\"grid\">
  {_render_table("Result breakdown", ["Result", "Lists"], result_rows)}
  {_render_table("Top unit presence", ["Unit", "Lists", "% of lists"], presence_rows)}
  {_render_table("Top unit entries", ["Unit", "Entries"], unit_entry_rows)}
  {_render_table("Top model counts", ["Unit", "Models"], unit_model_rows)}
  {_render_table("Top subfactions", ["Subfaction", "Count"], subfaction_rows)}
  {_render_table("Manifestation lores", ["Manifestation lore", "Count"], manifestation_rows)}
  {_render_table("Artifacts", ["Artifact", "Count"], artifact_rows)}
  {_render_table("Command traits", ["Command trait", "Count"], command_trait_rows)}
  {_render_table("Warmachine traits", ["Warmachine trait", "Count"], warmachine_trait_rows)}
  {_render_table("Unplayed known units", ["Unit", "Unit size"], unplayed_rows)}
  </div>
</section>
"""


def build_web_page() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    html = f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Helsmith stats</title>
    <style>
      :root {{ font-family: Inter, Segoe UI, Arial, sans-serif; color-scheme: dark; }}
      body {{ margin: 0; background: #111827; color: #f3f4f6; }}
      main {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1rem 3rem; }}
      h1 {{ margin: 0 0 .25rem; }}
      .meta {{ color: #9ca3af; margin-bottom: 1.5rem; }}
    .nav {{ position: sticky; top: 0; z-index: 10; display: flex; gap: .75rem; flex-wrap: wrap; margin: 0 0 1.25rem; padding: .5rem 0; background: rgba(17, 24, 39, .82); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); border-bottom: 1px solid #374151; }}
    .nav a {{ display: inline-block; padding: .35rem .65rem; border: 1px solid #374151; border-radius: 999px; text-decoration: none; }}
      .scope {{ margin: 1.5rem 0 2rem; }}
      .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 1rem; }}
      .card {{ background: #1f2937; border: 1px solid #374151; border-radius: 10px; padding: .75rem; }}
      table {{ width: 100%; border-collapse: collapse; font-size: .95rem; }}
      th, td {{ padding: .45rem .4rem; border-bottom: 1px solid #374151; text-align: left; }}
      th {{ color: #d1d5db; }}
      a {{ color: #93c5fd; }}
    </style>
  </head>
  <body>
    <main>
      <h1>Helsmith Stats Dashboard</h1>
      <p class=\"meta\">Generated: {escape(generated_at)}</p>
            <nav class=\"nav\" aria-label=\"Section navigation\">
                <a href=\"#combined\">Combined</a>
                <a href=\"#singles\">Singles</a>
                <a href=\"#teams\">Teams</a>
            </nav>
      {_scope_section("combined", "Combined")}
      {_scope_section("singles", "Singles")}
      {_scope_section("teams", "Teams")}
    </main>
  </body>
</html>
"""
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
