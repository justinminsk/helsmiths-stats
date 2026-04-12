from __future__ import annotations

import csv
import shutil
from collections import Counter
from datetime import datetime
from html import escape
from pathlib import Path

from .constants import DOCS_DIR, REPORTS_DIR, ROOT, SUMMARIES_DIR

SCOPES = ("combined", "singles", "teams")
MAX_ARCHIVED_SNAPSHOTS = 3
SCOPE_LABELS = {
    "combined": "Combined",
    "singles": "Singles",
    "teams": "Teams",
}


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
<section class="card">
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


def _render_lists_markdown(list_rows: list[dict[str, str]]) -> str:
    import json as _json

    if not list_rows:
        return '<article class="list-md"><p>No lists yet.</p></article>'

    blocks: list[str] = []
    for row in list_rows:
        name = escape(row.get("name", "Unknown list"))
        source = escape(row.get("source", "Unknown"))
        result = escape(row.get("result", "Unknown"))
        subfaction = escape(row.get("subfaction", "Unknown"))
        manifestation = escape(row.get("manifestation_lore", "Unknown"))
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
  <div class="list-units-wrap">
    <table class="list-units-table">
      <thead><tr><th>Regiment</th><th>Unit</th><th>Pts</th><th>Models</th><th>Reinforced</th><th>Notes</th></tr></thead>
      <tbody>{"".join(unit_rows_html_parts)}</tbody>
    </table>
  </div>"""
        else:
            units_section = f"<p class='list-meta'>Unit entries: {unit_entries}</p>"

        blocks.append(
            f"""
<article class="list-md">
  <div class="list-md-header">
    <span class="list-md-name">{name}</span>
    <span class="list-md-tag">{source} · {result}</span>
  </div>
  <p class="list-meta">Subfaction: {subfaction} · Lore: {manifestation} · Unit entries: {unit_entries} · Models: {models}</p>
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
    list_level_rows = _list_level_rows(list_rows)
    markdown_lists_html = _render_lists_markdown(list_rows)

    report_link = f"{report_base_link}/{scope}.md"
    lists_report_link = f"{report_base_link}/{scope}-lists.md"
    panel_id = f"scope-panel-{dataset_key}-{scope}"

    return f"""
<section class="scope scope-panel" id="{escape(panel_id)}" data-dataset-key="{escape(dataset_key)}" data-scope-key="{escape(scope)}">
  <div class="scope-head">
    <h2>{escape(label)}</h2>
    <button class="copy-link" type="button" data-dataset-key="{escape(dataset_key)}" data-scope-key="{escape(scope)}">Copy link</button>
  </div>
  <p>Lists parsed: <strong>{len(list_rows)}</strong></p>
  <nav class="scopeview-nav" aria-label="{escape(label)} view tabs">
    <button class="scopeview-tab" type="button" data-dataset-key="{escape(dataset_key)}" data-scope-key="{escape(scope)}" data-view-key="stats">Stats</button>
    <button class="scopeview-tab" type="button" data-dataset-key="{escape(dataset_key)}" data-scope-key="{escape(scope)}" data-view-key="lists">Lists</button>
  </nav>
  <section class="scope-view-panel" data-dataset-key="{escape(dataset_key)}" data-scope-key="{escape(scope)}" data-view-key="stats">
    <p class="view-link"><a href="{escape(report_link)}">View full markdown report</a></p>
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
  <section class="scope-view-panel" data-dataset-key="{escape(dataset_key)}" data-scope-key="{escape(scope)}" data-view-key="lists">
    <p class="view-link"><a href="{escape(lists_report_link)}">View full markdown report</a></p>
    <section class="list-table-wrap">
      {_render_table("Lists in this scope", ["Source", "Name", "Result", "Subfaction", "Manifestation lore", "Unit entries", "Models"], list_level_rows)}
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
            f'<button class="subtab" type="button" '
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
<section class="dataset dataset-panel" id="dataset-panel-{escape(dataset_key)}" data-dataset-key="{escape(dataset_key)}">
  <h2 class="dataset-title">{escape(dataset_label)}</h2>
  <nav class="subnav" aria-label="{escape(dataset_label)} section navigation">{scope_links}</nav>
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
            f'<button class="tab" type="button" '
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
      :root {{ font-family: Inter, Segoe UI, Arial, sans-serif; color-scheme: dark; }}
      body {{ margin: 0; background: #111827; color: #f3f4f6; }}
      main {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1rem 3rem; }}
      h1 {{ margin: 0 0 .25rem; }}
      .meta {{ color: #9ca3af; margin-bottom: 1.5rem; }}
      .nav {{ position: sticky; top: 0; z-index: 10; display: flex; gap: .75rem; flex-wrap: wrap; margin: 0 0 1.25rem; padding: .5rem 0; background: rgba(17, 24, 39, .82); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); border-bottom: 1px solid #374151; }}
      .tab, .subtab {{ display: inline-block; padding: .35rem .65rem; border: 1px solid #374151; border-radius: 999px; text-decoration: none; background: transparent; color: #93c5fd; cursor: pointer; }}
      .tab.is-active, .subtab.is-active {{ background: #1f2937; color: #f3f4f6; }}
      .dataset {{ margin: 1.5rem 0 2.25rem; }}
      .dataset-title {{ margin: 0 0 .75rem; }}
      .subnav {{ display: flex; gap: .5rem; flex-wrap: wrap; margin: 0 0 .75rem; }}
      .dataset-panel, .scope-panel {{ display: none; }}
      .dataset-panel.is-active, .scope-panel.is-active {{ display: block; }}
      .scope-head {{ display: flex; align-items: center; gap: .5rem; justify-content: space-between; }}
      .copy-link {{ border: 1px solid #374151; border-radius: 999px; padding: .25rem .55rem; background: transparent; color: #93c5fd; cursor: pointer; }}
      .copy-link.copied {{ color: #f3f4f6; background: #1f2937; }}
      .scopeview-nav {{ display: flex; gap: .5rem; flex-wrap: wrap; margin: .4rem 0 .9rem; }}
      .scopeview-tab {{ border: 1px solid #374151; border-radius: 999px; padding: .25rem .55rem; background: transparent; color: #93c5fd; cursor: pointer; }}
      .scopeview-tab.is-active {{ color: #f3f4f6; background: #1f2937; }}
      .scope-view-panel {{ display: none; }}
      .scope-view-panel.is-active {{ display: block; }}
      .list-table-wrap {{ margin: .75rem 0 1rem; }}
      .view-link {{ margin: .2rem 0 .9rem; }}
      .lists-markdown-wrap {{ display: grid; gap: .75rem; }}
      .list-md {{ background: #1f2937; border: 1px solid #374151; border-radius: 10px; padding: .85rem; display: flex; flex-direction: column; gap: .5rem; }}
      .list-md-header {{ display: flex; justify-content: space-between; align-items: baseline; gap: .5rem; flex-wrap: wrap; }}
      .list-md-name {{ font-weight: 600; font-size: 1rem; line-height: 1.3; word-break: break-word; }}
      .list-md-tag {{ font-size: .8rem; color: #93c5fd; white-space: nowrap; }}
      .list-meta {{ font-size: .85rem; color: #9ca3af; margin: 0; }}
      .list-units-wrap {{ overflow-x: auto; }}
      .list-units-table {{ width: 100%; border-collapse: collapse; font-size: .85rem; margin-top: .25rem; min-width: 760px; }}
      .list-units-table th {{ color: #9ca3af; font-weight: 500; padding: .3rem .3rem; border-bottom: 1px solid #374151; text-align: left; }}
      .list-units-table td {{ padding: .28rem .3rem; border-bottom: 1px solid #1e2a3a; }}
      .list-units-table .unit-count {{ text-align: right; color: #d1d5db; width: 3rem; }}
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
      <p class="meta">Generated: {escape(generated_at)}</p>
      <nav class="nav" aria-label="Dataset navigation">{dataset_links}</nav>
      {dataset_sections}
    </main>
    <script>
      (() => {{
        const firstDatasetKey = {first_dataset_key!r};
        const scopeOrder = {list(SCOPES)!r};
        const hashPrefix = '#tab=';

        const parseHash = () => {{
          const value = window.location.hash || '';
          if (!value.startsWith(hashPrefix)) {{
            return null;
          }}

          const payload = value.slice(hashPrefix.length);
          const parts = payload.split('|');
          if (parts.length !== 2) {{
            return null;
          }}

          return {{ datasetKey: parts[0], scopeKey: parts[1] }};
        }};

        const updateHash = (datasetKey, scopeKey) => {{
          const next = `${{hashPrefix}}${{datasetKey}}|${{scopeKey}}`;
          if (window.location.hash !== next) {{
            window.location.hash = next;
          }}
        }};

        const buildHash = (datasetKey, scopeKey) => `${{hashPrefix}}${{datasetKey}}|${{scopeKey}}`;

        const copyLink = async (datasetKey, scopeKey, button) => {{
          const url = `${{window.location.origin}}${{window.location.pathname}}${{buildHash(datasetKey, scopeKey)}}`;

          try {{
            if (navigator.clipboard && navigator.clipboard.writeText) {{
              await navigator.clipboard.writeText(url);
            }} else {{
              window.prompt('Copy link:', url);
            }}

            const original = button.textContent;
            button.textContent = 'Copied';
            button.classList.add('copied');
            window.setTimeout(() => {{
              button.textContent = original;
              button.classList.remove('copied');
            }}, 1200);
          }} catch (_error) {{
            window.prompt('Copy link:', url);
          }}
        }};

        const setScopeView = (datasetKey, scopeKey, viewKey) => {{
          document.querySelectorAll('.scopeview-tab').forEach((button) => {{
            const isMatch =
              button.dataset.datasetKey === datasetKey &&
              button.dataset.scopeKey === scopeKey &&
              button.dataset.viewKey === viewKey;
            button.classList.toggle('is-active', isMatch);
          }});

          document.querySelectorAll('.scope-view-panel').forEach((panel) => {{
            const isMatch =
              panel.dataset.datasetKey === datasetKey &&
              panel.dataset.scopeKey === scopeKey &&
              panel.dataset.viewKey === viewKey;
            panel.classList.toggle('is-active', isMatch);
          }});
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

        const setScope = (datasetKey, scopeKey, skipHash = false) => {{
          document.querySelectorAll('.subtab').forEach((button) => {{
            const isMatch = button.dataset.datasetKey === datasetKey && button.dataset.scopeKey === scopeKey;
            button.classList.toggle('is-active', isMatch);
          }});

          document.querySelectorAll('.scope-panel').forEach((panel) => {{
            const isMatch = panel.dataset.datasetKey === datasetKey && panel.dataset.scopeKey === scopeKey;
            panel.classList.toggle('is-active', isMatch);
          }});

          setScopeView(datasetKey, scopeKey, 'stats');

          if (!skipHash) {{
            updateHash(datasetKey, scopeKey);
          }}
        }};

        const setDataset = (datasetKey, skipHash = false) => {{
          document.querySelectorAll('.tab').forEach((button) => {{
            button.classList.toggle('is-active', button.dataset.datasetKey === datasetKey);
          }});

          document.querySelectorAll('.dataset-panel').forEach((panel) => {{
            panel.classList.toggle('is-active', panel.dataset.datasetKey === datasetKey);
          }});

          const firstScope = getDefaultScope(datasetKey);
          setScope(datasetKey, firstScope, skipHash);
        }};

        document.querySelectorAll('.tab').forEach((button) => {{
          button.addEventListener('click', () => setDataset(button.dataset.datasetKey));
        }});

        document.querySelectorAll('.subtab').forEach((button) => {{
          button.addEventListener('click', () => setScope(button.dataset.datasetKey, button.dataset.scopeKey));
        }});

        document.querySelectorAll('.scopeview-tab').forEach((button) => {{
          button.addEventListener('click', () =>
            setScopeView(button.dataset.datasetKey, button.dataset.scopeKey, button.dataset.viewKey)
          );
        }});

        document.querySelectorAll('.copy-link').forEach((button) => {{
          button.addEventListener('click', () => copyLink(button.dataset.datasetKey, button.dataset.scopeKey, button));
        }});

        const initial = parseHash();
        if (initial && isValidDataset(initial.datasetKey)) {{
          const scopeKey = isValidScope(initial.datasetKey, initial.scopeKey)
            ? initial.scopeKey
            : getDefaultScope(initial.datasetKey);
          setDataset(initial.datasetKey, true);
          setScope(initial.datasetKey, scopeKey, true);
        }} else {{
          setDataset(firstDatasetKey);
        }}

        window.addEventListener('hashchange', () => {{
          const next = parseHash();
          if (!next || !isValidDataset(next.datasetKey)) {{
            return;
          }}

          const scopeKey = isValidScope(next.datasetKey, next.scopeKey)
            ? next.scopeKey
            : getDefaultScope(next.datasetKey);
          setDataset(next.datasetKey, true);
          setScope(next.datasetKey, scopeKey, true);
        }});
      }})();
    </script>
  </body>
</html>
"""
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
