from __future__ import annotations

import csv
import os
import shutil
from collections import Counter
from datetime import datetime
from html import escape
from pathlib import Path

from .constants import DOCS_DIR, REPORTS_DIR, ROOT, SUMMARIES_DIR

SCOPES = ("combined", "singles", "teams")
MAX_ARCHIVED_SNAPSHOTS = 3
STATS_TABLE_ROWS_DEFAULT = 12
SCOPE_LABELS = {
    "combined": "Combined",
    "singles": "Singles",
    "teams": "Teams",
}


def _stats_table_rows() -> int:
    raw_value = os.getenv("HELSMITH_STATS_TABLE_ROWS", str(STATS_TABLE_ROWS_DEFAULT))
    try:
        parsed = int(raw_value)
    except ValueError:
        return STATS_TABLE_ROWS_DEFAULT
    return parsed if parsed > 0 else STATS_TABLE_ROWS_DEFAULT


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

    header_html = "".join(
        f'<th scope="col">{escape(header)}</th>' for header in headers
    )
    body_html = "".join(
        "<tr>" + "".join(f"<td>{escape(value)}</td>" for value in row) + "</tr>"
        for row in rows
    )
    return f"""
<section class="card">
  <h3>{escape(title)}</h3>
  <div class="table-scroll-wrap">
    <table>
      <caption class="sr-only">{escape(title)}</caption>
      <thead><tr>{header_html}</tr></thead>
      <tbody>{body_html}</tbody>
    </table>
  </div>
</section>
"""


def _rows_from_csv(
    path: Path, keys: list[str], limit: int | None = None
) -> list[list[str]]:
    if limit is None:
        limit = _stats_table_rows()
    rows = _top_rows(path, limit)
    return [[row.get(key, "") for key in keys] for row in rows]


def _result_breakdown_rows(list_rows: list[dict[str, str]]) -> list[list[str]]:
    counts = Counter(row.get("result", "Unknown") for row in list_rows)
    ordered_results = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [[result, str(count)] for result, count in ordered_results]


def _stats_summary_text(
    result_rows: list[list[str]],
    presence_rows: list[list[str]],
    subfaction_rows: list[list[str]],
    unit_model_rows: list[list[str]],
) -> str:
    summary_parts: list[str] = []

    if result_rows and result_rows[0] and result_rows[0][0] != "—":
        top_result = result_rows[0][0]
        top_result_count = result_rows[0][1] if len(result_rows[0]) > 1 else "0"
        summary_parts.append(
            f"Most common result is {top_result} ({top_result_count} lists)."
        )

    if presence_rows and presence_rows[0] and presence_rows[0][0] != "—":
        top_presence_unit = presence_rows[0][0]
        top_presence_count = presence_rows[0][1] if len(presence_rows[0]) > 1 else "0"
        top_presence_percent = (
            presence_rows[0][2] if len(presence_rows[0]) > 2 else "0%"
        )
        summary_parts.append(
            f"Top unit presence is {top_presence_unit} in {top_presence_count} lists ({top_presence_percent})."
        )

    if subfaction_rows and subfaction_rows[0] and subfaction_rows[0][0] != "—":
        top_subfaction = subfaction_rows[0][0]
        top_subfaction_count = (
            subfaction_rows[0][1] if len(subfaction_rows[0]) > 1 else "0"
        )
        summary_parts.append(
            f"Most common subfaction is {top_subfaction} ({top_subfaction_count} lists)."
        )

    if unit_model_rows and unit_model_rows[0] and unit_model_rows[0][0] != "—":
        top_model_unit = unit_model_rows[0][0]
        top_model_count = unit_model_rows[0][1] if len(unit_model_rows[0]) > 1 else "0"
        summary_parts.append(
            f"Highest model count unit is {top_model_unit} ({top_model_count} models)."
        )

    if not summary_parts:
        return "No summary insights available for this scope yet."

    return " ".join(summary_parts)


def _list_level_rows(list_rows: list[dict[str, str]]) -> list[list[str]]:
    return [
        [
            row.get("source", ""),
            row.get("name", ""),
            row.get("result", ""),
            row.get("subfaction", ""),
            row.get("manifestation_lore", ""),
            row.get("unit_entries", ""),
            row.get("models", ""),
        ]
        for row in list_rows
    ]


def _row_regiment_count(row: dict[str, str]) -> int:
    import json as _json

    raw_units = row.get("units", "")
    try:
        units = _json.loads(raw_units) if raw_units else []
    except Exception:
        units = []

    regiments = {
        str(unit.get("regiment", "")).strip()
        for unit in units
        if isinstance(unit, dict) and str(unit.get("regiment", "")).strip()
    }
    return len(regiments)


def _render_lists_table(list_rows: list[dict[str, str]]) -> str:
    headers = [
        "Source",
        "Name",
        "Result",
        "Subfaction",
        "Manifestation lore",
        "Regiments",
        "Unit entries",
        "Models",
    ]

    if not list_rows:
        body_html = "<tr><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>"
    else:
        row_html_parts: list[str] = []
        for list_index, row in enumerate(list_rows):
            source = row.get("source", "")
            name = row.get("name", "")
            result = row.get("result", "")
            subfaction = row.get("subfaction", "")
            manifestation_lore = row.get("manifestation_lore", "")
            regiments = str(_row_regiment_count(row))
            unit_entries = row.get("unit_entries", "")
            models = row.get("models", "")

            row_html_parts.append(
                "<tr "
                f'data-list-index="{list_index}" '
                f'data-result="{escape(result.lower())}" '
                f'data-subfaction="{escape(subfaction.lower())}">'
                f"<td>{escape(source)}</td>"
                f"<td>{escape(name)}</td>"
                f"<td>{escape(result)}</td>"
                f"<td>{escape(subfaction)}</td>"
                f"<td>{escape(manifestation_lore)}</td>"
                f"<td>{escape(regiments)}</td>"
                f"<td>{escape(unit_entries)}</td>"
                f"<td>{escape(models)}</td>"
                "</tr>"
            )

        body_html = "".join(row_html_parts)

    header_html = "".join(
        f'<th scope="col">{escape(header)}</th>' for header in headers
    )
    return f"""
  <section class="card">
    <h3>Lists</h3>
    <div class="table-scroll-wrap">
      <table class="lists-table">
      <caption class="sr-only">Lists in this scope</caption>
      <thead><tr>{header_html}</tr></thead>
      <tbody>{body_html}</tbody>
      </table>
    </div>
  </section>
  """


def _render_lists_markdown(list_rows: list[dict[str, str]]) -> str:
    import json as _json

    if not list_rows:
        return '<article class="list-md"><p>No lists yet.</p></article>'

    blocks: list[str] = []
    for list_index, row in enumerate(list_rows):
        name = escape(row.get("name", "Unknown list"))
        source = escape(row.get("source", "Unknown"))
        result = escape(row.get("result", "Unknown"))
        subfaction = escape(row.get("subfaction", "Unknown"))
        manifestation = escape(row.get("manifestation_lore", "Unknown"))
        regiment_count = str(_row_regiment_count(row))
        unit_entries = escape(row.get("unit_entries", ""))
        models = escape(row.get("models", ""))

        raw_units = row.get("units", "")
        try:
            unit_rows = _json.loads(raw_units) if raw_units else []
        except Exception:
            unit_rows = []

        if unit_rows:
            unit_rows_html_parts: list[str] = []
            for unit in unit_rows:
                if isinstance(unit, dict):
                    regiment = escape(str(unit.get("regiment", ""))) or "—"
                    unit_name = escape(str(unit.get("name", "")))
                    points = escape(str(unit.get("points", "")))
                    unit_models = escape(str(unit.get("models", "")))
                    reinforced = "Yes" if unit.get("reinforced") else "No"
                    notes = unit.get("notes") or []
                    notes_text = escape(" · ".join(str(note) for note in notes)) or "—"
                else:
                    regiment = "—"
                    unit_name = escape(str(unit[0])) if len(unit) > 0 else ""
                    points = escape(str(unit[1])) if len(unit) > 1 else ""
                    unit_models = "—"
                    reinforced = "—"
                    notes_text = "—"

                unit_rows_html_parts.append(
                    f"<tr><td>{regiment}</td><td>{unit_name}</td><td class='unit-count'>{points}</td><td class='unit-count'>{unit_models}</td><td>{reinforced}</td><td>{notes_text}</td></tr>"
                )

            units_section = f"""
  <div class="list-units-wrap table-scroll-wrap">
    <table class="list-units-table">
      <thead><tr><th>Regiment</th><th>Unit</th><th>Pts</th><th>Models</th><th>Reinforced</th><th>Notes</th></tr></thead>
      <tbody>{"".join(unit_rows_html_parts)}</tbody>
    </table>
  </div>"""
        else:
            units_section = f"<p class='list-meta'>Unit entries: {unit_entries}</p>"

        blocks.append(
            f"""
<article class="list-md" data-list-index="{list_index}">
  <div class="list-md-header">
    <span class="list-md-name">{name}</span>
    <span class="list-md-tag">{source} · {result}</span>
  </div>
  <p class="list-meta">Subfaction: {subfaction} · Lore: {manifestation} · Regiments: {regiment_count} · Unit entries: {unit_entries} · Models: {models}</p>
{units_section}
</article>
"""
        )

    return "".join(blocks)


def _scope_section(
    scope: str,
    label: str,
    summaries_dir: Path,
    report_base_link: str,
    dataset_key: str,
) -> str:
    scope_dir = summaries_dir / scope
    list_rows = _read_csv(scope_dir / "list_level_summary.csv")
    presence_rows = [
        [
            row.get("unit_name", ""),
            row.get("lists_with_unit", ""),
            row.get("percent_of_lists", "") + "%",
        ]
        for row in _top_rows(
            scope_dir / "unit_presence_percent.csv", _stats_table_rows()
        )
    ]
    subfaction_rows = _rows_from_csv(
        scope_dir / "subfaction_counts.csv",
        ["subfaction", "list_count"],
        _stats_table_rows(),
    )
    manifestation_rows = _rows_from_csv(
        scope_dir / "manifestation_lore_counts.csv",
        ["manifestation_lore", "list_count"],
        _stats_table_rows(),
    )
    artifact_rows = _rows_from_csv(
        scope_dir / "artifact_counts.csv", ["artifact", "count"], _stats_table_rows()
    )
    command_trait_rows = _rows_from_csv(
        scope_dir / "command_trait_counts.csv",
        ["command_trait", "count"],
        _stats_table_rows(),
    )
    warmachine_trait_rows = _rows_from_csv(
        scope_dir / "warmachine_trait_counts.csv",
        ["warmachine_trait", "count"],
        _stats_table_rows(),
    )
    unit_entry_rows = _rows_from_csv(
        scope_dir / "unit_entry_counts.csv",
        ["unit_name", "unit_entries"],
        _stats_table_rows(),
    )
    unit_model_rows = _rows_from_csv(
        scope_dir / "unit_model_counts.csv",
        ["unit_name", "model_count"],
        _stats_table_rows(),
    )
    unplayed_rows = _rows_from_csv(
        scope_dir / "unplayed_units.csv",
        ["unit_name", "unit_size"],
        _stats_table_rows(),
    )
    result_rows = _result_breakdown_rows(list_rows)
    stats_summary_text = _stats_summary_text(
        result_rows=result_rows,
        presence_rows=presence_rows,
        subfaction_rows=subfaction_rows,
        unit_model_rows=unit_model_rows,
    )
    markdown_lists_html = _render_lists_markdown(list_rows)

    report_link = f"{report_base_link}/{scope}.md"
    lists_report_link = f"{report_base_link}/{scope}-lists.md"
    panel_id = f"scope-panel-{dataset_key}-{scope}"
    stats_panel_id = f"scope-view-{dataset_key}-{scope}-stats"
    lists_panel_id = f"scope-view-{dataset_key}-{scope}-lists"

    return f"""
<section class="scope scope-panel" id="{escape(panel_id)}" data-dataset-key="{escape(dataset_key)}" data-scope-key="{escape(scope)}">
  <div class="scope-head">
    <h2>{escape(label)}</h2>
    <button class="copy-link" type="button" data-dataset-key="{escape(dataset_key)}" data-scope-key="{escape(scope)}">Copy view link</button>
  </div>
  <p class="scope-meta">Lists parsed: <strong class="meta-count">{len(list_rows)}</strong></p>
  <nav class="scopeview-nav" aria-label="{escape(label)} view tabs" role="tablist">
    <button class="scopeview-tab" type="button" role="tab" aria-selected="false" aria-controls="{escape(stats_panel_id)}" data-dataset-key="{escape(dataset_key)}" data-scope-key="{escape(scope)}" data-view-key="stats">Stats</button>
    <button class="scopeview-tab" type="button" role="tab" aria-selected="false" aria-controls="{escape(lists_panel_id)}" data-dataset-key="{escape(dataset_key)}" data-scope-key="{escape(scope)}" data-view-key="lists">Lists</button>
  </nav>
  <section class="scope-view-panel" id="{escape(stats_panel_id)}" role="tabpanel" data-dataset-key="{escape(dataset_key)}" data-scope-key="{escape(scope)}" data-view-key="stats">
    <p class="view-link"><a href="{escape(report_link)}">Open markdown report</a></p>
    <p class="stats-summary" aria-live="polite">Summary: {escape(stats_summary_text)}</p>
    <div class="grid">
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
  <section class="scope-view-panel" id="{escape(lists_panel_id)}" role="tabpanel" data-dataset-key="{escape(dataset_key)}" data-scope-key="{escape(scope)}" data-view-key="lists">
    <p class="view-link"><a href="{escape(lists_report_link)}">Open markdown report</a></p>
    <div class="table-toolbar" aria-label="List controls">
      <label class="toolbar-field toolbar-field-search">
        <span>Search lists</span>
        <input class="list-search" type="search" placeholder="Search source, name, or unit" data-dataset-key="{escape(dataset_key)}" data-scope-key="{escape(scope)}" />
      </label>
      <label class="toolbar-field">
        <span>Result</span>
        <select class="list-filter-result" data-dataset-key="{escape(dataset_key)}" data-scope-key="{escape(scope)}">
          <option value="">All results</option>
        </select>
      </label>
      <label class="toolbar-field">
        <span>Subfaction</span>
        <select class="list-filter-subfaction" data-dataset-key="{escape(dataset_key)}" data-scope-key="{escape(scope)}">
          <option value="">All subfactions</option>
        </select>
      </label>
      <label class="toolbar-field toolbar-field-sort">
        <span>Sort</span>
        <select class="list-sort" data-dataset-key="{escape(dataset_key)}" data-scope-key="{escape(scope)}">
          <option value="default">Original order</option>
          <option value="regiments-desc">Regiments (high to low)</option>
          <option value="regiments-asc">Regiments (low to high)</option>
          <option value="models-desc">Models (high to low)</option>
          <option value="models-asc">Models (low to high)</option>
          <option value="entries-desc">Unit entries (high to low)</option>
          <option value="entries-asc">Unit entries (low to high)</option>
          <option value="name-asc">Name (A-Z)</option>
        </select>
      </label>
      <details class="toolbar-field toolbar-columns toolbar-field-columns">
        <summary>Columns</summary>
        <label><input class="list-column-toggle" type="checkbox" data-column-index="0" checked /> Source</label>
        <label><input class="list-column-toggle" type="checkbox" data-column-index="1" checked /> Name</label>
        <label><input class="list-column-toggle" type="checkbox" data-column-index="2" checked /> Result</label>
        <label><input class="list-column-toggle" type="checkbox" data-column-index="3" checked /> Subfaction</label>
        <label><input class="list-column-toggle" type="checkbox" data-column-index="4" checked /> Manifestation lore</label>
        <label><input class="list-column-toggle" type="checkbox" data-column-index="5" checked /> Regiments</label>
        <label><input class="list-column-toggle" type="checkbox" data-column-index="6" checked /> Unit entries</label>
        <label><input class="list-column-toggle" type="checkbox" data-column-index="7" checked /> Models</label>
      </details>
    </div>
    <p class="sr-only list-announcer" aria-live="polite" aria-atomic="true"></p>
    <p class="list-empty" hidden>No lists found.</p>
    <div class="list-pagination" hidden>
      <span class="list-pagination-meta" aria-live="polite"></span>
      <button class="list-show-more" type="button" data-dataset-key="{escape(dataset_key)}" data-scope-key="{escape(scope)}">Load more lists</button>
    </div>
    <section class="list-table-wrap">
      {_render_lists_table(list_rows)}
    </section>
    <section class="lists-markdown-wrap">
      {markdown_lists_html}
    </section>
  </section>
</section>
"""


def _discover_datasets() -> list[dict[str, Path | str]]:
    datasets: list[dict[str, Path | str]] = [
        {
            "key": "current",
            "label": "Current",
            "summaries_dir": SUMMARIES_DIR,
            "reports_dir": REPORTS_DIR,
        }
    ]

    history_dir = ROOT / "history"
    if history_dir.exists():
        archived = sorted(
            [entry for entry in history_dir.iterdir() if entry.is_dir()],
            key=lambda entry: entry.name,
            reverse=True,
        )

        for entry in archived[:MAX_ARCHIVED_SNAPSHOTS]:
            datasets.append(
                {
                    "key": f"archive-{entry.name}",
                    "label": f"Snapshot ({entry.name})",
                    "summaries_dir": entry / "summaries",
                    "reports_dir": entry / "reports",
                }
            )

    return datasets


def _copy_dataset_reports(dataset_key: str, reports_dir: Path) -> None:
    destination = DOCS_DIR / "reports" / dataset_key
    destination.mkdir(parents=True, exist_ok=True)
    for scope in SCOPES:
        for report_name in (f"{scope}.md", f"{scope}-lists.md"):
            source_report = reports_dir / report_name
            if source_report.exists():
                shutil.copy2(source_report, destination / source_report.name)


def _render_dataset_section(
    dataset_key: str,
    dataset_label: str,
    summaries_dir: Path,
    report_base_link: str,
) -> str:
    scope_links = "".join(
        (
            f'<button class="subtab" type="button" role="tab" aria-selected="false" '
            f'aria-controls="scope-panel-{dataset_key}-{scope}" '
            f'data-dataset-key="{dataset_key}" data-scope-key="{scope}">{SCOPE_LABELS[scope]}</button>'
        )
        for scope in SCOPES
    )
    scope_sections = "".join(
        _scope_section(
            scope=scope,
            label=SCOPE_LABELS[scope],
            summaries_dir=summaries_dir,
            report_base_link=report_base_link,
            dataset_key=dataset_key,
        )
        for scope in SCOPES
    )
    return f"""
<section class="dataset dataset-panel" id="dataset-panel-{escape(dataset_key)}" role="tabpanel" data-dataset-key="{escape(dataset_key)}">
  <h2 class="dataset-title">{escape(dataset_label)}</h2>
  <nav class="subnav" aria-label="{escape(dataset_label)} section navigation" role="tablist">{scope_links}</nav>
  {scope_sections}
</section>
"""


def build_web_page() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    docs_reports_root = DOCS_DIR / "reports"
    if docs_reports_root.exists():
        shutil.rmtree(docs_reports_root)
    docs_reports_root.mkdir(parents=True, exist_ok=True)

    datasets = _discover_datasets()
    for dataset in datasets:
        _copy_dataset_reports(dataset["key"], dataset["reports_dir"])

    first_dataset_key = str(datasets[0]["key"]) if datasets else "current"

    dataset_links = "".join(
        (
            f'<button class="tab" type="button" role="tab" aria-selected="false" '
            f'aria-controls="dataset-panel-{dataset["key"]}" '
            f'data-dataset-key="{dataset["key"]}">{escape(str(dataset["label"]))}</button>'
        )
        for dataset in datasets
    )
    dataset_sections = "".join(
        _render_dataset_section(
            dataset_key=str(dataset["key"]),
            dataset_label=str(dataset["label"]),
            summaries_dir=dataset["summaries_dir"],
            report_base_link=f"reports/{dataset['key']}",
        )
        for dataset in datasets
    )

    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Helsmith stats</title>
    <style>
      :root {{ font-family: Inter, Segoe UI, Arial, sans-serif; color-scheme: light dark; }}
      body {{ margin: 0; background: var(--color-bg); color: var(--color-text); }}
      main {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1rem 3rem; }}
      :root {{
        --table-cell-pad-y: .42rem;
        --table-cell-pad-x: .4rem;
        --radius-pill: 999px;
        --radius-control: 10px;
        --control-height: 2.75rem;
        --color-bg: #0f0b08;
        --color-bg-elevated: #1e1409;
        --color-bg-muted: #0c0807;
        --color-bg-input: #17100a;
        --color-bg-input-hover: #1e1409;
        --color-text: #fff7ef;
        --color-text-soft: #f1e6da;
        --color-muted: #d2beab;
        --color-accent: #c8921a;
        --color-accent-strong: #dcaa32;
        --color-accent-rgb: 200, 146, 26;
        --color-surface: #181009;
        --color-border: #5e4225;
        --color-focus: #00c8a8;
        --color-overlay: rgba(12, 8, 5, .93);
        --color-teal: #00c8a8;
        --color-magenta: #c84090;
        --motion-fast: .16s;
      }}
      h1 {{ margin: 0 0 .35rem; font-size: 1.75rem; letter-spacing: -.01em; }}
      .meta {{ color: var(--color-muted); margin: 0 0 .35rem; font-size: .88rem; }}
      .context-bar {{ margin: .1rem 0 1rem; color: var(--color-muted); font-size: .92rem; min-height: 1.25rem; }}
      .utility-row {{ display: flex; justify-content: flex-end; margin: -.45rem 0 .75rem; }}
      .nav {{ position: sticky; top: 0; z-index: 10; display: flex; gap: .65rem; flex-wrap: wrap; margin: 0 0 1rem; padding: .55rem .15rem .7rem; background: var(--color-overlay); border-bottom: 1px solid var(--color-border); }}
      .tab, .subtab, .scopeview-tab, .copy-link, .list-show-more {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: var(--control-height);
        padding: .28rem .62rem;
        border: 1px solid var(--color-border);
        border-radius: var(--radius-pill);
        text-decoration: none;
        background: var(--color-bg-muted);
        color: var(--color-accent);
        cursor: pointer;
        font-size: .9rem;
        font-weight: 500;
        transition: background-color var(--motion-fast) ease, border-color var(--motion-fast) ease, transform .12s ease, color var(--motion-fast) ease;
      }}
      .tab:hover, .subtab:hover, .scopeview-tab:hover, .copy-link:hover, .list-show-more:hover {{
        background: var(--color-bg-elevated);
        border-color: #5e4225;
        color: var(--color-accent-strong);
      }}
      .tab:active, .subtab:active, .scopeview-tab:active, .copy-link:active, .list-show-more:active {{ transform: translateY(1px); }}
      .tab.is-active, .subtab.is-active, .scopeview-tab.is-active {{ background: var(--color-bg-elevated); color: var(--color-text); border-color: #7a5a30; box-shadow: inset 0 0 0 1px rgba(var(--color-accent-rgb), .3), inset 0 -2px 0 var(--color-accent); font-weight: 600; }}
      .tab:focus-visible, .subtab:focus-visible, .scopeview-tab:focus-visible,
      .copy-link:focus-visible, .list-show-more:focus-visible,
      .toolbar-field input:focus-visible, .toolbar-field select:focus-visible,
      .toolbar-columns > summary:focus-visible,
      .th-sort-button:focus-visible {{
        outline: 2px solid var(--color-focus);
        outline-offset: 2px;
      }}
      .dataset {{ margin: 1.25rem 0 2.25rem; }}
      .dataset-title {{ margin: 0 0 .75rem; font-size: 1.08rem; color: var(--color-text); font-weight: 600; }}
      .subnav {{ display: flex; gap: .5rem; flex-wrap: wrap; margin: 0 0 .75rem; }}
      .dataset-panel, .scope-panel {{ display: none; }}
      .dataset-panel.is-active, .scope-panel.is-active {{ display: block; }}
      .scope {{ margin: 1.2rem 0 2rem; background: linear-gradient(180deg, rgba(24, 16, 9, .42), rgba(24, 16, 9, .2)); border: 1px solid var(--color-border); border-radius: 12px; padding: .9rem .9rem 1rem; }}
      .scope-head {{ display: flex; align-items: center; gap: .5rem; justify-content: space-between; margin-bottom: .22rem; }}
      .scope-head h2 {{ margin: 0; font-size: 1.12rem; line-height: 1.3; letter-spacing: -.01em; }}
      .scope-meta {{ margin: 0 0 .7rem; font-size: .86rem; color: var(--color-muted); }}
      .meta-count {{ font-size: .95rem; color: var(--color-text); font-weight: 600; }}
      .copy-link.copied {{ color: var(--color-text); background: var(--color-bg-elevated); border-color: #7a5a30; box-shadow: inset 0 0 0 1px rgba(var(--color-accent-rgb), .26); }}
      .scopeview-nav {{ display: flex; gap: .5rem; flex-wrap: wrap; margin: 0 0 .9rem; padding-bottom: .2rem; border-bottom: 1px solid var(--color-border); }}
      .scope-view-panel {{ display: none; }}
      .scope-view-panel.is-active {{ display: block; animation: panel-fade-in .18s ease-out; }}
      .table-toolbar {{ display: flex; gap: .55rem; flex-wrap: wrap; margin: .3rem 0 .65rem; }}
      .toolbar-field {{ display: flex; flex-direction: column; gap: .24rem; min-width: 160px; }}
      .toolbar-field > span {{ font-size: .79rem; color: var(--color-text-soft); letter-spacing: .02em; text-transform: uppercase; }}
      .toolbar-field input, .toolbar-field select {{ background: var(--color-bg-input); color: var(--color-text); border: 1px solid var(--color-border); border-radius: var(--radius-control); min-height: var(--control-height); padding: .5rem .65rem; font-size: .9rem; transition: border-color var(--motion-fast) ease, background-color var(--motion-fast) ease; }}
      .toolbar-field input:hover, .toolbar-field select:hover {{ border-color: #5e4225; background: var(--color-bg-input-hover); }}
      .toolbar-field select:disabled {{ opacity: .65; cursor: not-allowed; }}
      .toolbar-columns {{ border: 1px solid var(--color-border); border-radius: var(--radius-control); padding: .5rem .6rem; min-width: 190px; background: var(--color-bg-input); }}
      .toolbar-columns > summary {{ cursor: pointer; color: var(--color-text-soft); font-size: .9rem; min-height: var(--control-height); display: inline-flex; align-items: center; list-style: none; }}
      .toolbar-columns > summary::-webkit-details-marker {{ display: none; }}
      .toolbar-columns > summary::after {{ content: '▾'; margin-left: .35rem; color: var(--color-muted); }}
      .toolbar-columns[open] > summary::after {{ content: '▴'; }}
      .toolbar-columns > label {{ display: flex; align-items: center; gap: .4rem; color: var(--color-text-soft); font-size: .82rem; margin-top: .3rem; }}
      .toolbar-columns input[type='checkbox'] {{ accent-color: var(--color-accent); }}
      .list-empty {{ color: var(--color-text-soft); font-size: .9rem; margin: .3rem 0 .75rem; min-height: 1.1rem; }}
      .list-pagination {{ display: flex; align-items: center; justify-content: space-between; gap: .5rem; margin: .1rem 0 .55rem; }}
      .list-pagination-meta {{ color: var(--color-text-soft); font-size: .86rem; transition: color var(--motion-fast) ease; min-height: 1rem; }}
      .list-show-more {{ border: 1px solid var(--color-border); border-radius: 999px; padding: .2rem .55rem; background: transparent; color: var(--color-accent); cursor: pointer; font-size: .8rem; transition: background-color var(--motion-fast) ease, border-color var(--motion-fast) ease, transform .12s ease; }}
      .list-table-wrap {{ margin: .75rem 0 1rem; }}
      .scope-view-panel[data-view-key='lists'] .list-table-wrap {{ contain: layout paint; }}
      .table-scroll-wrap {{ position: relative; overflow-x: auto; }}
      .table-scroll-wrap::before, .table-scroll-wrap::after {{ content: ''; position: sticky; top: 0; bottom: 0; width: 16px; pointer-events: none; opacity: 0; transition: opacity .18s ease; z-index: 2; display: block; }}
      .table-scroll-wrap::before {{ left: 0; float: left; background: linear-gradient(90deg, rgba(15, 11, 8, .96), rgba(15, 11, 8, 0)); }}
      .table-scroll-wrap::after {{ right: 0; float: right; background: linear-gradient(270deg, rgba(15, 11, 8, .96), rgba(15, 11, 8, 0)); }}
      .table-scroll-wrap.can-scroll-left::before {{ opacity: 1; }}
      .table-scroll-wrap.can-scroll-right::after {{ opacity: 1; }}
      .view-link {{ margin: .1rem 0 .9rem; font-size: .87rem; color: var(--color-text-soft); }}
      .view-link a {{ text-decoration-thickness: .08em; text-underline-offset: .18em; }}
      .stats-summary {{ margin: .1rem 0 .8rem; font-size: .89rem; line-height: 1.45; color: var(--color-text-soft); }}
      .sr-only {{
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        border: 0;
        white-space: nowrap;
      }}
      .lists-markdown-wrap {{ display: grid; gap: .75rem; }}
      .scope-view-panel[data-view-key='lists'] .lists-markdown-wrap {{ contain: layout paint; }}
      .list-md {{ background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 10px; padding: .85rem; display: flex; flex-direction: column; gap: .5rem; }}
      .list-md[hidden] {{ display: none !important; }}
      .list-md-header {{ display: flex; justify-content: space-between; align-items: baseline; gap: .5rem; flex-wrap: wrap; }}
      .list-md-name {{ font-weight: 600; font-size: 1rem; line-height: 1.3; word-break: break-word; }}
      .list-md-tag {{ font-size: .8rem; color: var(--color-accent); white-space: nowrap; }}
      .list-meta {{ font-size: .89rem; color: var(--color-text-soft); margin: 0; }}
      .list-units-wrap {{ overflow-x: auto; }}
      .list-units-table {{ width: 100%; border-collapse: collapse; font-size: .85rem; margin-top: .25rem; min-width: 760px; }}
      .list-units-table th {{ color: var(--color-text-soft); font-weight: 600; padding: var(--table-cell-pad-y) var(--table-cell-pad-x); border-bottom: 1px solid var(--color-border); text-align: left; }}
      .list-units-table td {{ padding: var(--table-cell-pad-y) var(--table-cell-pad-x); border-bottom: 1px solid var(--color-border); }}
      .list-units-table .unit-count {{ text-align: right; color: var(--color-text-soft); width: 3rem; }}
      .list-units-table thead th {{ position: sticky; top: 0; background: var(--color-surface); z-index: 1; }}
      .list-units-table tbody tr:nth-child(even) {{ background: rgba(255, 255, 255, .02); }}
      .list-units-table tbody tr:hover {{ background: rgba(var(--color-accent-rgb), .12); }}
      .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 1rem; }}
      .card {{ background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 10px; padding: .75rem; }}
      .card h3 {{ margin: 0 0 .55rem; font-size: .95rem; color: var(--color-text); font-weight: 600; letter-spacing: .01em; }}
      table {{ width: 100%; border-collapse: collapse; font-size: .95rem; }}
      th, td {{ padding: var(--table-cell-pad-y) var(--table-cell-pad-x); border-bottom: 1px solid var(--color-border); text-align: left; }}
      th {{ min-height: 2.25rem; }}
      th {{ color: var(--color-text); font-size: .8rem; letter-spacing: .025em; text-transform: uppercase; font-weight: 600; }}
      th.sortable {{ cursor: pointer; user-select: none; position: relative; }}
      th.sortable:hover .th-sort-button {{ color: var(--color-text); }}
      .th-sort-button {{
        appearance: none;
        border: 0;
        background: transparent;
        color: inherit;
        font: inherit;
        text-transform: inherit;
        letter-spacing: inherit;
        font-size: inherit;
        font-weight: inherit;
        cursor: pointer;
        width: 100%;
        display: inline-flex;
        align-items: center;
        justify-content: flex-start;
        padding: 0;
      }}
      .th-sort-button::after {{ content: '⇅'; font-size: .74rem; margin-left: .34rem; color: var(--color-text-soft); opacity: .95; }}
      th.sortable.sort-asc .th-sort-button::after {{ content: '▲'; color: var(--color-accent); opacity: 1; }}
      th.sortable.sort-desc .th-sort-button::after {{ content: '▼'; color: var(--color-accent); opacity: 1; }}
      table thead th {{ position: sticky; top: 0; background: var(--color-surface); z-index: 1; border-bottom: 1px solid var(--color-border); }}
      td.numeric-col, th.numeric-col {{ text-align: right; font-variant-numeric: tabular-nums; }}
      td.numeric-col {{ color: var(--color-text-soft); font-weight: 500; }}
      table tbody tr:nth-child(even) {{ background: rgba(255, 255, 255, .018); }}
      table tbody tr:hover {{ background: rgba(var(--color-accent-rgb), .1); }}
      table tbody tr:nth-child(5n) td {{ border-bottom-color: #5e4225; }}
      .scope-view-panel[data-view-key='lists'].is-updating .list-pagination-meta {{ color: #d1d5db; }}
      .scope-view-panel[data-view-key='lists'].is-updating .list-show-more {{ transform: translateY(-1px); }}
      .copy-link.is-copying {{ animation: copy-success-pop .45s ease-out; }}
      a {{ color: var(--color-accent); }}

      @keyframes panel-fade-in {{
        from {{ opacity: .84; transform: translateY(2px); }}
        to {{ opacity: 1; transform: translateY(0); }}
      }}

      @keyframes copy-success-pop {{
        0% {{ transform: scale(1); }}
        35% {{ transform: scale(1.04); }}
        100% {{ transform: scale(1); }}
      }}

      @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{
          animation-duration: .01ms !important;
          animation-iteration-count: 1 !important;
          transition-duration: .01ms !important;
          scroll-behavior: auto !important;
        }}
      }}

      @supports ((backdrop-filter: blur(8px)) or (-webkit-backdrop-filter: blur(8px))) {{
        .nav {{
          backdrop-filter: blur(8px);
          -webkit-backdrop-filter: blur(8px);
        }}
      }}

      @supports (content-visibility: auto) {{
        .scope-view-panel[data-view-key='lists'] .list-table-wrap {{
          content-visibility: auto;
          contain-intrinsic-size: 1px 540px;
        }}

        .scope-view-panel[data-view-key='lists'] .lists-markdown-wrap {{
          content-visibility: auto;
          contain-intrinsic-size: 1px 920px;
        }}
      }}

      @media (prefers-color-scheme: light) {{
        :root {{
          --color-bg: #f9f4ee;
          --color-bg-elevated: #ffffff;
          --color-bg-muted: #f2ebe2;
          --color-bg-input: #ffffff;
          --color-bg-input-hover: #fcf8f3;
          --color-text: #2e2118;
          --color-text-soft: #3f2d21;
          --color-muted: #5a4333;
          --color-accent: #7a4e0e;
          --color-accent-strong: #63400b;
          --color-accent-rgb: 122, 78, 14;
          --color-surface: #ffffff;
          --color-border: #ddc8b5;
          --color-focus: #006e5a;
          --color-overlay: rgba(249, 244, 238, .95);
          --color-teal: #007a68;
          --color-magenta: #a0306e;
        }}

        :root:not([data-theme='dark']) .scope {{ background: linear-gradient(180deg, rgba(255, 255, 255, .92), rgba(241, 245, 249, .75)); }}
        :root:not([data-theme='dark']) .tab,
        :root:not([data-theme='dark']) .subtab,
        :root:not([data-theme='dark']) .scopeview-tab,
        :root:not([data-theme='dark']) .copy-link,
        :root:not([data-theme='dark']) .list-show-more {{ background: rgba(255, 255, 255, .88); }}
        :root:not([data-theme='dark']) .table-scroll-wrap::before {{ background: linear-gradient(90deg, rgba(249, 244, 238, .96), rgba(249, 244, 238, 0)); }}
        :root:not([data-theme='dark']) .table-scroll-wrap::after {{ background: linear-gradient(270deg, rgba(249, 244, 238, .96), rgba(249, 244, 238, 0)); }}
        :root:not([data-theme='dark']) .toolbar-columns {{ background: rgba(255, 255, 255, .92); }}
        :root:not([data-theme='dark']) .toolbar-columns > summary,
        :root:not([data-theme='dark']) .toolbar-columns > label {{ color: #473428; }}
        :root:not([data-theme='dark']) .list-md {{ background: #ffffff; border-color: #dbe2ea; }}
        :root:not([data-theme='dark']) .list-units-table thead th,
        :root:not([data-theme='dark']) table thead th {{ background: #fffaf4; }}
        :root:not([data-theme='dark']) .list-units-table th {{ color: #4a382c; border-bottom-color: #e6d7c9; }}
        :root:not([data-theme='dark']) .list-units-table td {{ border-bottom-color: #eee1d4; }}
        :root:not([data-theme='dark']) table tbody tr:nth-child(even),
        :root:not([data-theme='dark']) .list-units-table tbody tr:nth-child(even) {{ background: rgba(46, 33, 24, .03); }}
        :root:not([data-theme='dark']) table tbody tr:hover,
        :root:not([data-theme='dark']) .list-units-table tbody tr:hover {{ background: rgba(var(--color-accent-rgb), .14); }}
      }}

      :root[data-theme='dark'] {{
        --color-bg: #0f0b08;
        --color-bg-elevated: #1e1409;
        --color-bg-muted: #0c0807;
        --color-bg-input: #17100a;
        --color-bg-input-hover: #1e1409;
        --color-text: #fff7ef;
        --color-text-soft: #f1e6da;
        --color-muted: #d2beab;
        --color-accent: #c8921a;
        --color-accent-strong: #dcaa32;
        --color-accent-rgb: 200, 146, 26;
        --color-surface: #181009;
        --color-border: #5e4225;
        --color-focus: #00c8a8;
        --color-overlay: rgba(12, 8, 5, .93);
        --color-teal: #00c8a8;
        --color-magenta: #c84090;
      }}

      :root[data-theme='light'] {{
        --color-bg: #f9f4ee;
        --color-bg-elevated: #ffffff;
        --color-bg-muted: #f2ebe2;
        --color-bg-input: #ffffff;
        --color-bg-input-hover: #fcf8f3;
        --color-text: #2e2118;
        --color-text-soft: #3f2d21;
        --color-muted: #5a4333;
        --color-accent: #7a4e0e;
        --color-accent-strong: #63400b;
        --color-accent-rgb: 122, 78, 14;
        --color-surface: #ffffff;
        --color-border: #ddc8b5;
        --color-focus: #006e5a;
        --color-overlay: rgba(249, 244, 238, .95);
        --color-teal: #007a68;
        --color-magenta: #a0306e;
      }}

      @media (prefers-contrast: more) {{
        :root {{
          --color-border: #94a3b8;
          --color-muted: #e2e8f0;
          --color-focus: #ffffff;
          --color-accent: #dbeafe;
          --color-accent-strong: #ffffff;
        }}

        .tab, .subtab, .scopeview-tab, .copy-link, .list-show-more,
        .toolbar-columns, .card, .scope {{
          border-width: 2px;
        }}

        .tab.is-active, .subtab.is-active, .scopeview-tab.is-active {{
          box-shadow: inset 0 0 0 2px rgba(191, 219, 254, .6), inset 0 -3px 0 var(--color-accent);
        }}
      }}

      @media (prefers-color-scheme: light) and (prefers-contrast: more) {{
        :root {{
          --color-border: #475569;
          --color-muted: #0f172a;
          --color-focus: #0f172a;
          --color-accent: #1e40af;
          --color-accent-strong: #1e3a8a;
        }}
      }}

      @media (forced-colors: active) {{
        .tab, .subtab, .scopeview-tab, .copy-link, .list-show-more,
        .toolbar-field input, .toolbar-field select, .toolbar-columns,
        .th-sort-button {{
          forced-color-adjust: auto;
          border: 1px solid ButtonText;
        }}
      }}

      @media (max-width: 960px) {{
        .nav {{ overflow-x: auto; flex-wrap: nowrap; padding-bottom: .55rem; }}
        .subnav, .scopeview-nav {{ overflow-x: auto; flex-wrap: nowrap; scrollbar-width: thin; }}
        .grid {{ grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }}
        .table-toolbar {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); align-items: end; gap: .5rem; }}
        .toolbar-field {{ min-width: 0; flex: 1 1 auto; }}
        .toolbar-field-search, .toolbar-field-columns {{ grid-column: 1 / -1; }}
        .toolbar-columns {{ min-width: 0; width: 100%; }}
        .tab, .subtab, .scopeview-tab, .copy-link {{ padding: .28rem .52rem; font-size: .86rem; }}
      }}
      @media (max-width: 720px) {{
        main {{ padding: 1rem .75rem 2rem; }}
        .scope-head {{ flex-wrap: wrap; align-items: flex-start; gap: .4rem; }}
        .scopeview-nav {{ position: sticky; top: 2.85rem; z-index: 9; background: var(--color-overlay); padding: .25rem 0 .45rem; border-bottom: 1px solid var(--color-border); }}
        .table-toolbar {{ position: sticky; top: 5.45rem; z-index: 8; background: var(--color-overlay); padding: .35rem 0 .45rem; border-bottom: 1px solid var(--color-border); grid-template-columns: 1fr; }}
        .toolbar-field {{ min-width: 0; flex: 1 1 100%; }}
        .toolbar-field-search, .toolbar-field-columns {{ grid-column: auto; }}
        .toolbar-columns {{ width: 100%; }}
        .tab, .subtab, .scopeview-tab {{ white-space: nowrap; }}
        .table-scroll-wrap {{ -webkit-overflow-scrolling: touch; }}
      }}
    </style>
  </head>
  <body>
    <main>
      <h1>Helsmith Stats Dashboard</h1>
      <p class="meta">Generated: {escape(generated_at)}</p>
      <nav class="nav" aria-label="Dataset navigation" role="tablist">{dataset_links}</nav>
      <div class="utility-row">
        <button id="theme-toggle" class="copy-link" type="button" aria-label="Toggle color theme">Theme: Auto</button>
      </div>
      <p class="context-bar" id="context-bar" aria-live="polite"></p>
      {dataset_sections}
    </main>
    <script>
      (() => {{
        const firstDatasetKey = {first_dataset_key!r};
        const scopeOrder = {list(SCOPES)!r};
        const hashPrefix = '#tab=';
        const listRowsBatchSize = 20;
        const listFilterInputDebounceMs = 140;
        const panelUpdateTimers = new WeakMap();
        const listFilterTimers = new Map();
        const themeStorageKey = 'helsmithTheme';

        const parseHash = () => {{
          const value = window.location.hash || '';
          if (!value.startsWith(hashPrefix)) {{
            return null;
          }}

          const payload = value.slice(hashPrefix.length);
          const parts = payload.split('|');
          if (parts.length < 2 || parts.length > 3) {{
            return null;
          }}

          return {{ datasetKey: parts[0], scopeKey: parts[1], viewKey: parts[2] || 'stats' }};
        }};

        const updateHash = (datasetKey, scopeKey, viewKey = 'stats') => {{
          const next = `${{hashPrefix}}${{datasetKey}}|${{scopeKey}}|${{viewKey}}`;
          if (window.location.hash !== next) {{
            window.location.hash = next;
          }}
        }};

        const buildHash = (datasetKey, scopeKey, viewKey = 'stats') => `${{hashPrefix}}${{datasetKey}}|${{scopeKey}}|${{viewKey}}`;

        const getCurrentView = () => {{
          const active = document.querySelector('.scopeview-tab.is-active');
          return active ? active.dataset.viewKey : 'stats';
        }};

        const getActiveView = (datasetKey, scopeKey) => {{
          const active = document.querySelector(
            `.scopeview-tab.is-active[data-dataset-key="${{datasetKey}}"]` +
              `[data-scope-key="${{scopeKey}}"]`
          );
          return active ? active.dataset.viewKey : 'stats';
        }};

        const updateContextBar = (datasetKey, scopeKey, viewKey) => {{
          const contextBar = document.getElementById('context-bar');
          if (!contextBar) {{
            return;
          }}

          const datasetButton = document.querySelector(`.tab[data-dataset-key="${{datasetKey}}"]`);
          const scopeButton = document.querySelector(
            `.subtab[data-dataset-key="${{datasetKey}}"][data-scope-key="${{scopeKey}}"]`
          );

          const datasetLabel = datasetButton ? datasetButton.textContent.trim() : datasetKey;
          const scopeLabel = scopeButton ? scopeButton.textContent.trim() : scopeKey;
          const viewLabel = viewKey === 'lists' ? 'Lists' : 'Stats';

          contextBar.textContent = `${{datasetLabel}} > ${{scopeLabel}} > ${{viewLabel}}`;
        }};

        const getPreferredTheme = () =>
          window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';

        const setThemeLabel = (theme) => {{
          const button = document.getElementById('theme-toggle');
          if (!button) {{
            return;
          }}

          button.textContent = `Theme: ${{theme === 'dark' ? 'Dark' : 'Light'}}`;
        }};

        const applyTheme = (theme, save = true) => {{
          const root = document.documentElement;
          root.setAttribute('data-theme', theme);
          setThemeLabel(theme);
          if (save) {{
            window.localStorage.setItem(themeStorageKey, theme);
          }}
        }};

        const setupThemeToggle = () => {{
          const button = document.getElementById('theme-toggle');
          if (!button) {{
            return;
          }}

          const savedTheme = window.localStorage.getItem(themeStorageKey);
          const initialTheme = savedTheme === 'dark' || savedTheme === 'light'
            ? savedTheme
            : getPreferredTheme();
          applyTheme(initialTheme, false);

          button.addEventListener('click', () => {{
            const current = document.documentElement.getAttribute('data-theme') || getPreferredTheme();
            const nextTheme = current === 'dark' ? 'light' : 'dark';
            applyTheme(nextTheme, true);
          }});
        }};

        const applyListFilters = (datasetKey, scopeKey) => {{
          const panel = document.querySelector(
            `.scope-view-panel[data-view-key="lists"][data-dataset-key="${{datasetKey}}"][data-scope-key="${{scopeKey}}"]`
          );
          if (!panel) {{
            return;
          }}

          panel.classList.add('is-updating');
          const existingUpdateTimer = panelUpdateTimers.get(panel);
          if (existingUpdateTimer) {{
            window.clearTimeout(existingUpdateTimer);
          }}
          const nextUpdateTimer = window.setTimeout(() => panel.classList.remove('is-updating'), 120);
          panelUpdateTimers.set(panel, nextUpdateTimer);

          const input = panel.querySelector('.list-search');
          const resultSelect = panel.querySelector('.list-filter-result');
          const subfactionSelect = panel.querySelector('.list-filter-subfaction');

          const query = input ? input.value.trim().toLowerCase() : '';
          const resultFilter = resultSelect ? resultSelect.value.trim().toLowerCase() : '';
          const subfactionFilter = subfactionSelect
            ? subfactionSelect.value.trim().toLowerCase()
            : '';
          const sortSelect = panel.querySelector('.list-sort');
          const sortKey = sortSelect ? sortSelect.value : 'default';

          const rows = Array.from(panel.querySelectorAll('.list-table-wrap tbody tr'));
          const tbody = panel.querySelector('.list-table-wrap tbody');

          if (tbody && sortKey !== 'default') {{
            const nonPlaceholderRows = rows.filter(
              (row) => !Array.from(row.querySelectorAll('td')).every((cell) => cell.textContent.trim() === '—')
            );

            const getNumeric = (row, index) => {{
              const value = Number.parseFloat((row.children[index]?.textContent || '0').replace(/,/g, ''));
              return Number.isNaN(value) ? 0 : value;
            }};

            const getText = (row, index) => (row.children[index]?.textContent || '').trim().toLowerCase();

            nonPlaceholderRows.sort((a, b) => {{
              if (sortKey === 'models-desc') return getNumeric(b, 7) - getNumeric(a, 7);
              if (sortKey === 'models-asc') return getNumeric(a, 7) - getNumeric(b, 7);
              if (sortKey === 'entries-desc') return getNumeric(b, 6) - getNumeric(a, 6);
              if (sortKey === 'entries-asc') return getNumeric(a, 6) - getNumeric(b, 6);
              if (sortKey === 'regiments-desc') return getNumeric(b, 5) - getNumeric(a, 5);
              if (sortKey === 'regiments-asc') return getNumeric(a, 5) - getNumeric(b, 5);
              if (sortKey === 'name-asc') return getText(a, 1).localeCompare(getText(b, 1));
              return 0;
            }});

            nonPlaceholderRows.forEach((row) => tbody.appendChild(row));
          }}

          const hasActiveFilter =
            query.length > 0 ||
            resultFilter.length > 0 ||
            subfactionFilter.length > 0;
          const visibleLimitRaw = Number.parseInt(panel.dataset.listRowsVisible || `${{listRowsBatchSize}}`, 10);
          const visibleLimit = Number.isNaN(visibleLimitRaw) ? listRowsBatchSize : visibleLimitRaw;

          let matchedRows = 0;
          let shownRows = 0;
          let placeholderRow = null;

          rows.forEach((row) => {{
            const cells = Array.from(row.querySelectorAll('td'));
            const isPlaceholder =
              cells.length > 0 && cells.every((cell) => cell.textContent.trim() === '—');

            if (isPlaceholder) {{
              placeholderRow = row;
              return;
            }}

            const matchesSearch = row.textContent.toLowerCase().includes(query);
            const matchesResult = !resultFilter || row.dataset.result === resultFilter;
            const matchesSubfaction =
              !subfactionFilter || row.dataset.subfaction === subfactionFilter;
            const matches = matchesSearch && matchesResult && matchesSubfaction;

            if (!matches) {{
              row.hidden = true;
              return;
            }}

            matchedRows += 1;
            const shouldShow = matchedRows <= visibleLimit;
            row.hidden = !shouldShow;
            if (shouldShow) {{
              shownRows += 1;
            }}
          }});

          if (placeholderRow) {{
            placeholderRow.hidden = hasActiveFilter;
          }}

          const emptyState = panel.querySelector('.list-empty');
          if (emptyState) {{
            const activeControls = [];
            if (query.length > 0) {{
              activeControls.push('search');
            }}
            if (resultFilter.length > 0) {{
              activeControls.push('result');
            }}
            if (subfactionFilter.length > 0) {{
              activeControls.push('subfaction');
            }}

            if (activeControls.length === 0) {{
              emptyState.textContent = 'No lists found.';
            }} else if (activeControls.length === 1) {{
              emptyState.textContent = `No lists found for current ${{activeControls[0]}} filter.`;
            }} else {{
              emptyState.textContent = `No lists found for current ${{activeControls.join(' + ')}} filters.`;
            }}

            emptyState.hidden = !hasActiveFilter || matchedRows > 0;
          }}

          const pagination = panel.querySelector('.list-pagination');
          const paginationMeta = panel.querySelector('.list-pagination-meta');
          const showMoreButton = panel.querySelector('.list-show-more');
          if (pagination && paginationMeta) {{
            pagination.hidden = matchedRows === 0;
            paginationMeta.textContent = matchedRows
              ? `Showing ${{shownRows}} of ${{matchedRows}} lists`
              : '';
            if (showMoreButton) {{
              showMoreButton.hidden = matchedRows <= shownRows;
            }}
          }}

          syncListsMarkdownOrder(panel);
        }};

        const syncListsMarkdownOrder = (panel) => {{
          const markdownWrap = panel.querySelector('.lists-markdown-wrap');
          if (!markdownWrap) {{
            return;
          }}

          const cards = Array.from(markdownWrap.querySelectorAll('.list-md'));
          if (!cards.length) {{
            return;
          }}

          const cardsByIndex = new Map(
            cards
              .map((card) => [card.dataset.listIndex || '', card])
              .filter(([index]) => index.length > 0)
          );

          const tableRows = Array.from(panel.querySelectorAll('.list-table-wrap tbody tr')).filter((row) =>
            !Array.from(row.querySelectorAll('td')).every((cell) => cell.textContent.trim() === '—')
          );

          if (!tableRows.length || !cardsByIndex.size) {{
            return;
          }}

          const fragment = document.createDocumentFragment();
          const seenIndexes = new Set();

          tableRows.forEach((row) => {{
            const listIndex = row.dataset.listIndex || '';
            const card = cardsByIndex.get(listIndex);
            if (!card) {{
              return;
            }}

            seenIndexes.add(listIndex);
            card.hidden = row.hidden;
            fragment.appendChild(card);
          }});

          cards.forEach((card) => {{
            const listIndex = card.dataset.listIndex || '';
            if (seenIndexes.has(listIndex)) {{
              return;
            }}

            card.hidden = true;
            fragment.appendChild(card);
          }});

          markdownWrap.appendChild(fragment);
        }};

        const scheduleListFilters = (datasetKey, scopeKey, delay = 0) => {{
          const timerKey = `${{datasetKey}}|${{scopeKey}}`;
          const existingTimer = listFilterTimers.get(timerKey);
          if (existingTimer) {{
            window.clearTimeout(existingTimer);
          }}

          const timer = window.setTimeout(() => {{
            listFilterTimers.delete(timerKey);
            applyListFilters(datasetKey, scopeKey);
          }}, delay);
          listFilterTimers.set(timerKey, timer);
        }};

        const setupListPagination = () => {{
          document.querySelectorAll('.scope-view-panel[data-view-key="lists"]').forEach((panel) => {{
            panel.dataset.listRowsVisible = `${{listRowsBatchSize}}`;
          }});

          document.querySelectorAll('.list-show-more').forEach((button) => {{
            button.addEventListener('click', () => {{
              const panel = button.closest('.scope-view-panel[data-view-key="lists"]');
              if (!panel) {{
                return;
              }}

              const current = Number.parseInt(panel.dataset.listRowsVisible || `${{listRowsBatchSize}}`, 10);
              const nextCount = (Number.isNaN(current) ? listRowsBatchSize : current) + listRowsBatchSize;
              panel.dataset.listRowsVisible = `${{nextCount}}`;
              scheduleListFilters(button.dataset.datasetKey, button.dataset.scopeKey, 0);
            }});
          }});
        }};

        const setupHorizontalOverflowCues = () => {{
          const wrappers = Array.from(document.querySelectorAll('.table-scroll-wrap'));

          const refresh = (wrapper) => {{
            const maxScrollLeft = Math.max(0, wrapper.scrollWidth - wrapper.clientWidth);
            const canScroll = maxScrollLeft > 1;

            wrapper.classList.toggle('can-scroll-left', canScroll && wrapper.scrollLeft > 2);
            wrapper.classList.toggle('can-scroll-right', canScroll && wrapper.scrollLeft < maxScrollLeft - 2);
          }};

          wrappers.forEach((wrapper) => {{
            wrapper.addEventListener('scroll', () => refresh(wrapper));
            refresh(wrapper);
          }});

          window.addEventListener('resize', () => {{
            wrappers.forEach((wrapper) => refresh(wrapper));
          }});
        }};

        const setupListFilters = () => {{
          document.querySelectorAll('.scope-view-panel[data-view-key="lists"]').forEach((panel) => {{
            const rows = Array.from(panel.querySelectorAll('.list-table-wrap tbody tr')).filter((row) =>
              !Array.from(row.querySelectorAll('td')).every((cell) => cell.textContent.trim() === '—')
            );

            const resultSelect = panel.querySelector('.list-filter-result');
            const subfactionSelect = panel.querySelector('.list-filter-subfaction');

            const resultValues = Array.from(
              new Set(rows.map((row) => row.dataset.result || '').values())
            ).filter(Boolean);
            const subfactionValues = Array.from(
              new Set(rows.map((row) => row.dataset.subfaction || '').values())
            ).filter(Boolean);

            if (resultSelect) {{
              resultValues
                .sort((a, b) => a.localeCompare(b))
                .forEach((value) => {{
                  const option = document.createElement('option');
                  option.value = value;
                  option.textContent = value;
                  resultSelect.appendChild(option);
                }});
            }}

            if (subfactionSelect) {{
              subfactionValues
                .sort((a, b) => a.localeCompare(b))
                .forEach((value) => {{
                  const option = document.createElement('option');
                  option.value = value;
                  option.textContent = value;
                  subfactionSelect.appendChild(option);
                }});
            }}
          }});
        }};

        const applyListColumnVisibility = (panel) => {{
          const table = panel.querySelector('.list-table-wrap .lists-table');
          if (!table) {{
            return;
          }}

          const toggles = Array.from(panel.querySelectorAll('.list-column-toggle'));
          const headerCells = Array.from(table.querySelectorAll('thead th'));
          const rowCells = Array.from(table.querySelectorAll('tbody tr')).map((row) =>
            Array.from(row.querySelectorAll('td'))
          );

          toggles.forEach((toggle) => {{
            const columnIndex = Number.parseInt(toggle.dataset.columnIndex || '-1', 10);
            if (Number.isNaN(columnIndex) || columnIndex < 0) {{
              return;
            }}

            const visible = toggle.checked;
            const header = headerCells[columnIndex];
            if (header) {{
              header.style.display = visible ? '' : 'none';
            }}

            rowCells.forEach((cells) => {{
              const cell = cells[columnIndex];
              if (cell) {{
                cell.style.display = visible ? '' : 'none';
              }}
            }});
          }});
        }};

        const setupListColumnToggles = () => {{
          document.querySelectorAll('.scope-view-panel[data-view-key="lists"]').forEach((panel) => {{
            panel.querySelectorAll('.list-column-toggle').forEach((toggle) => {{
              toggle.addEventListener('change', () => applyListColumnVisibility(panel));
            }});

            applyListColumnVisibility(panel);
          }});
        }};

        const isNumericHeader = (headerText) => {{
          const label = headerText.trim().toLowerCase();
          return (
            label === 'count' ||
            label === 'lists' ||
            label === '% of lists' ||
            label === 'entries' ||
            label === 'models' ||
            label === 'regiments' ||
            label === 'unit entries'
          );
        }};

        const parseSortableValue = (text, numeric) => {{
          if (!numeric) {{
            return text.trim().toLowerCase();
          }}

          const cleaned = text.replace(/[%,$\\s]/g, '').replace(/,/g, '');
          const value = Number.parseFloat(cleaned);
          return Number.isNaN(value) ? Number.NEGATIVE_INFINITY : value;
        }};

        const applyTableSorting = (table, columnIndex, direction, numeric) => {{
          const tbody = table.querySelector('tbody');
          if (!tbody) {{
            return;
          }}

          const rows = Array.from(tbody.querySelectorAll('tr'));
          const placeholders = rows.filter((row) =>
            Array.from(row.querySelectorAll('td')).every((cell) => cell.textContent.trim() === '—')
          );
          const sortableRows = rows.filter((row) => !placeholders.includes(row));

          sortableRows.sort((rowA, rowB) => {{
            const cellA = rowA.children[columnIndex];
            const cellB = rowB.children[columnIndex];
            const valueA = parseSortableValue(cellA ? cellA.textContent : '', numeric);
            const valueB = parseSortableValue(cellB ? cellB.textContent : '', numeric);

            if (valueA < valueB) {{
              return direction === 'asc' ? -1 : 1;
            }}
            if (valueA > valueB) {{
              return direction === 'asc' ? 1 : -1;
            }}
            return 0;
          }});

          tbody.innerHTML = '';
          sortableRows.forEach((row) => tbody.appendChild(row));
          placeholders.forEach((row) => tbody.appendChild(row));

          const listPanel = table.closest('.scope-view-panel[data-view-key="lists"]');
          if (listPanel) {{
            syncListsMarkdownOrder(listPanel);
          }}
        }};

        const setupSortableTables = () => {{
          document.querySelectorAll('table').forEach((table) => {{
            const headers = Array.from(table.querySelectorAll('thead th'));
            if (!headers.length) {{
              return;
            }}

            headers.forEach((header, columnIndex) => {{
              const numeric = isNumericHeader(header.textContent || '');
              if (!numeric) {{
                return;
              }}

              const headerLabel = (header.textContent || '').trim();
              header.classList.add('sortable');
              header.classList.add('numeric-col');
              header.dataset.sortDirection = 'none';
              header.setAttribute('aria-sort', 'none');

              let sortButton = header.querySelector('.th-sort-button');
              if (!sortButton) {{
                header.textContent = '';
                sortButton = document.createElement('button');
                sortButton.type = 'button';
                sortButton.className = 'th-sort-button';
                sortButton.textContent = headerLabel;
                header.appendChild(sortButton);
              }}
              sortButton.setAttribute('aria-label', `Sort by ${{headerLabel}}`);

              const bodyRows = Array.from(table.querySelectorAll('tbody tr'));
              bodyRows.forEach((row) => {{
                const cell = row.children[columnIndex];
                if (cell) {{
                  cell.classList.add('numeric-col');
                }}
              }});

              const triggerSort = () => {{
                headers.forEach((item) => {{
                  if (item !== header) {{
                    item.dataset.sortDirection = 'none';
                    item.classList.remove('sort-asc', 'sort-desc');
                    item.setAttribute('aria-sort', 'none');
                  }}
                }});

                const currentDirection = header.dataset.sortDirection || 'none';
                const nextDirection = currentDirection === 'asc' ? 'desc' : 'asc';
                header.dataset.sortDirection = nextDirection;
                header.classList.toggle('sort-asc', nextDirection === 'asc');
                header.classList.toggle('sort-desc', nextDirection === 'desc');
                header.setAttribute('aria-sort', nextDirection === 'asc' ? 'ascending' : 'descending');

                applyTableSorting(table, columnIndex, nextDirection, numeric);

                const listPanel = table.closest('.scope-view-panel[data-view-key="lists"]');
                if (listPanel) {{
                  const announcer = listPanel.querySelector('.list-announcer');
                  if (announcer) {{
                    const directionLabel = nextDirection === 'asc' ? 'ascending' : 'descending';
                    announcer.textContent = `Sorted by ${{headerLabel}} in ${{directionLabel}} order.`;
                  }}
                }}
              }};

              sortButton.addEventListener('click', triggerSort);
            }});
          }});
        }};

        const copyLink = async (datasetKey, scopeKey, button) => {{
          const viewKey = getActiveView(datasetKey, scopeKey);
          const url = `${{window.location.origin}}${{window.location.pathname}}${{buildHash(datasetKey, scopeKey, viewKey)}}`;

          try {{
            if (navigator.clipboard && navigator.clipboard.writeText) {{
              await navigator.clipboard.writeText(url);
            }} else {{
              window.prompt('Copy this link:', url);
            }}

            const original = button.textContent;
            button.textContent = 'Copied';
            button.classList.add('copied');
            button.classList.add('is-copying');
            window.setTimeout(() => {{
              button.textContent = original;
              button.classList.remove('copied');
              button.classList.remove('is-copying');
            }}, 1200);
          }} catch (_error) {{
            window.prompt('Copy this link:', url);
          }}
        }};

        const ensureActiveNavigationVisibility = () => {{
          if (!window.matchMedia('(max-width: 960px)').matches) {{
            return;
          }}

          const activeSelectors = ['.tab.is-active', '.subtab.is-active', '.scopeview-tab.is-active'];
          activeSelectors.forEach((selector) => {{
            const element = document.querySelector(selector);
            if (element) {{
              element.scrollIntoView({{ block: 'nearest', inline: 'center' }});
            }}
          }});
        }};

        const setScopeView = (datasetKey, scopeKey, viewKey, skipHash = false) => {{
          document.querySelectorAll('.scopeview-tab').forEach((button) => {{
            const isMatch =
              button.dataset.datasetKey === datasetKey &&
              button.dataset.scopeKey === scopeKey &&
              button.dataset.viewKey === viewKey;
            button.classList.toggle('is-active', isMatch);
            button.setAttribute('aria-selected', isMatch ? 'true' : 'false');
          }});

          document.querySelectorAll('.scope-view-panel').forEach((panel) => {{
            const isMatch =
              panel.dataset.datasetKey === datasetKey &&
              panel.dataset.scopeKey === scopeKey &&
              panel.dataset.viewKey === viewKey;
            panel.classList.toggle('is-active', isMatch);
            panel.hidden = !isMatch;
          }});

          updateContextBar(datasetKey, scopeKey, viewKey);
          ensureActiveNavigationVisibility();

          if (!skipHash) {{
            updateHash(datasetKey, scopeKey, viewKey);
          }}
        }};

        const getDefaultScope = (datasetKey) => {{
          const candidate = document.querySelector(`.subtab[data-dataset-key="${{datasetKey}}"]`);
          return candidate ? candidate.dataset.scopeKey : scopeOrder[0];
        }};

        const isValidDataset = (datasetKey) => {{
          return Boolean(document.querySelector(`.dataset-panel[data-dataset-key="${{datasetKey}}"]`));
        }};

        const isValidScope = (datasetKey, scopeKey) => {{
          return Boolean(
            document.querySelector(
              `.scope-panel[data-dataset-key="${{datasetKey}}"][data-scope-key="${{scopeKey}}"]`
            )
          );
        }};

        const setScope = (datasetKey, scopeKey, viewKey = 'stats', skipHash = false) => {{
          document.querySelectorAll('.subtab').forEach((button) => {{
            const isMatch = button.dataset.datasetKey === datasetKey && button.dataset.scopeKey === scopeKey;
            button.classList.toggle('is-active', isMatch);
            button.setAttribute('aria-selected', isMatch ? 'true' : 'false');
          }});

          document.querySelectorAll('.scope-panel').forEach((panel) => {{
            const isMatch = panel.dataset.datasetKey === datasetKey && panel.dataset.scopeKey === scopeKey;
            panel.classList.toggle('is-active', isMatch);
            panel.hidden = !isMatch;
          }});

          setScopeView(datasetKey, scopeKey, viewKey, true);

          if (!skipHash) {{
            updateHash(datasetKey, scopeKey, viewKey);
          }}
        }};

        const setDataset = (datasetKey, viewKey = 'stats', skipHash = false) => {{
          document.querySelectorAll('.tab').forEach((button) => {{
            const isMatch = button.dataset.datasetKey === datasetKey;
            button.classList.toggle('is-active', isMatch);
            button.setAttribute('aria-selected', isMatch ? 'true' : 'false');
          }});

          document.querySelectorAll('.dataset-panel').forEach((panel) => {{
            const isMatch = panel.dataset.datasetKey === datasetKey;
            panel.classList.toggle('is-active', isMatch);
            panel.hidden = !isMatch;
          }});

          const firstScope = getDefaultScope(datasetKey);
          setScope(datasetKey, firstScope, viewKey, skipHash);
        }};

        const setupTabKeyboardNavigation = () => {{
          const wire = (containerSelector, itemSelector) => {{
            document.querySelectorAll(containerSelector).forEach((container) => {{
              const items = Array.from(container.querySelectorAll(itemSelector));
              if (items.length < 2) {{
                return;
              }}

              items.forEach((item, index) => {{
                item.addEventListener('keydown', (event) => {{
                  const horizontalNav = event.key === 'ArrowRight' || event.key === 'ArrowLeft';
                  const boundaryNav = event.key === 'Home' || event.key === 'End';
                  if (!horizontalNav && !boundaryNav) {{
                    return;
                  }}

                  event.preventDefault();

                  let nextIndex = index;
                  if (event.key === 'ArrowRight') {{
                    nextIndex = (index + 1) % items.length;
                  }} else if (event.key === 'ArrowLeft') {{
                    nextIndex = (index - 1 + items.length) % items.length;
                  }} else if (event.key === 'Home') {{
                    nextIndex = 0;
                  }} else if (event.key === 'End') {{
                    nextIndex = items.length - 1;
                  }}

                  items[nextIndex].focus();
                  items[nextIndex].click();
                }});
              }});
            }});
          }};

          wire('.nav', '.tab');
          wire('.subnav', '.subtab');
          wire('.scopeview-nav', '.scopeview-tab');
        }};

        document.querySelectorAll('.tab').forEach((button) => {{
          button.addEventListener('click', () => setDataset(button.dataset.datasetKey));
        }});

        document.querySelectorAll('.subtab').forEach((button) => {{
          button.addEventListener('click', () =>
            setScope(button.dataset.datasetKey, button.dataset.scopeKey, getCurrentView())
          );
        }});

        document.querySelectorAll('.scopeview-tab').forEach((button) => {{
          button.addEventListener('click', () =>
            setScopeView(button.dataset.datasetKey, button.dataset.scopeKey, button.dataset.viewKey)
          );
        }});

        document.querySelectorAll('.list-search').forEach((input) => {{
          input.addEventListener('input', () => {{
            const panel = input.closest('.scope-view-panel[data-view-key="lists"]');
            if (panel) {{
              panel.dataset.listRowsVisible = `${{listRowsBatchSize}}`;
            }}
            scheduleListFilters(input.dataset.datasetKey, input.dataset.scopeKey, listFilterInputDebounceMs);
          }});
        }});

        document.querySelectorAll('.list-filter-result, .list-filter-subfaction, .list-sort').forEach((select) => {{
          select.addEventListener('change', () => {{
            const panel = select.closest('.scope-view-panel[data-view-key="lists"]');
            if (panel) {{
              panel.dataset.listRowsVisible = `${{listRowsBatchSize}}`;
            }}
            scheduleListFilters(select.dataset.datasetKey, select.dataset.scopeKey, 0);
          }});
        }});

        document.querySelectorAll('.copy-link').forEach((button) => {{
          button.addEventListener('click', () => copyLink(button.dataset.datasetKey, button.dataset.scopeKey, button));
        }});

        setupSortableTables();
        setupListFilters();
        setupListPagination();
        setupListColumnToggles();
        setupHorizontalOverflowCues();
        setupTabKeyboardNavigation();
        setupThemeToggle();

        document.querySelectorAll('.list-search').forEach((input) => {{
          applyListFilters(input.dataset.datasetKey, input.dataset.scopeKey);
        }});

        const restoreFromHash = () => {{
          const next = parseHash();
          if (!next || !isValidDataset(next.datasetKey)) {{
            setDataset(firstDatasetKey, 'stats');
            return;
          }}

          const scopeKey = isValidScope(next.datasetKey, next.scopeKey)
            ? next.scopeKey
            : getDefaultScope(next.datasetKey);
          setDataset(next.datasetKey, next.viewKey, true);
          setScope(next.datasetKey, scopeKey, next.viewKey, true);
        }};

        restoreFromHash();

        window.addEventListener('hashchange', () => {{
          restoreFromHash();
        }});

        window.addEventListener('pageshow', (event) => {{
          if (event.persisted) {{
            restoreFromHash();
          }}
        }});
      }})();
    </script>
  </body>
</html>
"""
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
