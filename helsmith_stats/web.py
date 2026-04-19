from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
from collections import Counter
from datetime import datetime
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
UI_CONFIG = {
    "hashPrefix": "#tab=",
    "listRowsBatchSize": 20,
    "listFilterInputDebounceMs": 140,
    "themeStorageKey": "helsmithTheme",
    "maxArchivedSnapshots": MAX_ARCHIVED_SNAPSHOTS,
}
THEME_TOKENS = {
    "dark": {
        "colorBg": "#0f0b08",
        "colorBgElevated": "#1e1409",
        "colorBgMuted": "#0c0807",
        "colorBgInput": "#17100a",
        "colorBgInputHover": "#1e1409",
        "colorText": "#fff7ef",
        "colorTextSoft": "#f1e6da",
        "colorMuted": "#d2beab",
        "colorAccent": "#c8921a",
        "colorAccentStrong": "#dcaa32",
        "colorAccentRgb": "200, 146, 26",
        "colorSurface": "#181009",
        "colorBorder": "#5e4225",
        "colorFocus": "#00c8a8",
        "colorOverlay": "rgba(12, 8, 5, .93)",
        "colorTeal": "#00c8a8",
        "colorMagenta": "#c84090",
    },
    "light": {
        "colorBg": "#f9f4ee",
        "colorBgElevated": "#ffffff",
        "colorBgMuted": "#f2ebe2",
        "colorBgInput": "#ffffff",
        "colorBgInputHover": "#fcf8f3",
        "colorText": "#2e2118",
        "colorTextSoft": "#3f2d21",
        "colorMuted": "#5a4333",
        "colorAccent": "#7a4e0e",
        "colorAccentStrong": "#63400b",
        "colorAccentRgb": "122, 78, 14",
        "colorSurface": "#ffffff",
        "colorBorder": "#ddc8b5",
        "colorFocus": "#006e5a",
        "colorOverlay": "rgba(249, 244, 238, .95)",
        "colorTeal": "#007a68",
        "colorMagenta": "#a0306e",
    },
}
FRONTEND_DIR = ROOT / "frontend"
FRONTEND_DIST_DIR = FRONTEND_DIR / "dist"


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


def _top_rows(path: Path, limit: int) -> list[dict[str, str]]:
    return _read_csv(path)[:limit]


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


def _int_from_text(value: str) -> int:
    cleaned = str(value).replace(",", "").strip()
    try:
        return int(cleaned)
    except ValueError:
        return 0


def _deserialize_units(raw_units: str) -> list[dict[str, object]]:
    try:
        units = json.loads(raw_units) if raw_units else []
    except Exception:
        units = []

    normalized: list[dict[str, object]] = []
    for unit in units:
        if isinstance(unit, dict):
            notes = unit.get("notes") or []
            normalized.append(
                {
                    "regiment": str(unit.get("regiment", "")).strip(),
                    "name": str(unit.get("name", "")).strip(),
                    "points": _int_from_text(str(unit.get("points", "0"))),
                    "models": _int_from_text(str(unit.get("models", "0"))),
                    "reinforced": bool(unit.get("reinforced", False)),
                    "notes": [str(note) for note in notes],
                }
            )
            continue

        if isinstance(unit, (list, tuple)):
            normalized.append(
                {
                    "regiment": "",
                    "name": str(unit[0]) if len(unit) > 0 else "",
                    "points": _int_from_text(str(unit[1])) if len(unit) > 1 else 0,
                    "models": 0,
                    "reinforced": False,
                    "notes": [],
                }
            )

    return normalized


def _report_links(report_base_link: str, scope: str) -> dict[str, str]:
    return {
        "stats": f"{report_base_link}/{scope}.md",
        "lists": f"{report_base_link}/{scope}-lists.md",
    }


def _serialize_list_payload(row: dict[str, str], list_index: int) -> dict[str, object]:
    units = _deserialize_units(row.get("units", ""))
    regiments = {
        str(unit.get("regiment", "")).strip()
        for unit in units
        if str(unit.get("regiment", "")).strip()
    }
    return {
        "index": list_index,
        "source": row.get("source", ""),
        "name": row.get("name", ""),
        "result": row.get("result", ""),
        "subfaction": row.get("subfaction", ""),
        "manifestationLore": row.get("manifestation_lore", ""),
        "regiments": len(regiments),
        "unitEntries": _int_from_text(row.get("unit_entries", "0")),
        "models": _int_from_text(row.get("models", "0")),
        "units": units,
    }


def _build_scope_payload(
    scope: str,
    label: str,
    summaries_dir: Path,
    report_base_link: str,
    dataset_key: str,
) -> dict[str, object]:
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
    report_links = _report_links(report_base_link, scope)
    list_payload = [
        _serialize_list_payload(row, list_index)
        for list_index, row in enumerate(list_rows)
    ]
    result_options = sorted(
        {str(item["result"]) for item in list_payload if str(item["result"]).strip()},
        key=str.lower,
    )
    subfaction_options = sorted(
        {
            str(item["subfaction"])
            for item in list_payload
            if str(item["subfaction"]).strip()
        },
        key=str.lower,
    )

    return {
        "key": scope,
        "label": label,
        "datasetKey": dataset_key,
        "listCount": len(list_rows),
        "reportLinks": report_links,
        "statsSummary": _stats_summary_text(
            result_rows=result_rows,
            presence_rows=presence_rows,
            subfaction_rows=subfaction_rows,
            unit_model_rows=unit_model_rows,
        ),
        "filters": {
            "results": result_options,
            "subfactions": subfaction_options,
        },
        "statsTables": [
            {
                "key": "resultBreakdown",
                "title": "Result breakdown",
                "headers": ["Result", "Lists"],
                "rows": result_rows,
            },
            {
                "key": "topUnitPresence",
                "title": "Top unit presence",
                "headers": ["Unit", "Lists", "% of lists"],
                "rows": presence_rows,
            },
            {
                "key": "topUnitEntries",
                "title": "Top unit entries",
                "headers": ["Unit", "Entries"],
                "rows": unit_entry_rows,
            },
            {
                "key": "topModelCounts",
                "title": "Top model counts",
                "headers": ["Unit", "Models"],
                "rows": unit_model_rows,
            },
            {
                "key": "topSubfactions",
                "title": "Top subfactions",
                "headers": ["Subfaction", "Count"],
                "rows": subfaction_rows,
            },
            {
                "key": "manifestationLores",
                "title": "Manifestation lores",
                "headers": ["Manifestation lore", "Count"],
                "rows": manifestation_rows,
            },
            {
                "key": "artifacts",
                "title": "Artifacts",
                "headers": ["Artifact", "Count"],
                "rows": artifact_rows,
            },
            {
                "key": "commandTraits",
                "title": "Command traits",
                "headers": ["Command trait", "Count"],
                "rows": command_trait_rows,
            },
            {
                "key": "warmachineTraits",
                "title": "Warmachine traits",
                "headers": ["Warmachine trait", "Count"],
                "rows": warmachine_trait_rows,
            },
            {
                "key": "unplayedKnownUnits",
                "title": "Unplayed known units",
                "headers": ["Unit", "Unit size"],
                "rows": unplayed_rows,
            },
        ],
        "lists": list_payload,
    }


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


def build_site_payload(generated_at: str | None = None) -> dict[str, object]:
    if generated_at is None:
        generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

    datasets = _discover_datasets()
    payload_datasets: list[dict[str, object]] = []
    for dataset in datasets:
        dataset_key = str(dataset["key"])
        dataset_label = str(dataset["label"])
        summaries_dir = Path(dataset["summaries_dir"])
        report_base_path = f"reports/{dataset_key}"
        payload_datasets.append(
            {
                "key": dataset_key,
                "label": dataset_label,
                "reportBasePath": report_base_path,
                "scopes": [
                    _build_scope_payload(
                        scope=scope,
                        label=SCOPE_LABELS[scope],
                        summaries_dir=summaries_dir,
                        report_base_link=report_base_path,
                        dataset_key=dataset_key,
                    )
                    for scope in SCOPES
                ],
            }
        )

    default_dataset_key = (
        str(payload_datasets[0]["key"]) if payload_datasets else "current"
    )
    return {
        "generatedAt": generated_at,
        "defaultDatasetKey": default_dataset_key,
        "scopeOrder": list(SCOPES),
        "scopeLabels": SCOPE_LABELS,
        "uiConfig": UI_CONFIG,
        "themeTokens": THEME_TOKENS,
        "datasets": payload_datasets,
    }


def _write_site_payload(payload: dict[str, object]) -> None:
    data_dir = DOCS_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "site-data.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _resolve_npm_command() -> list[str] | None:
    if not FRONTEND_DIR.exists():
        return None

    def _node_npm_cli_command(npm_like_path: Path) -> list[str] | None:
        node_executable = npm_like_path.parent / "node.exe"
        npm_cli = npm_like_path.parent / "node_modules" / "npm" / "bin" / "npm-cli.js"
        if node_executable.exists() and npm_cli.exists():
            return [str(node_executable), str(npm_cli)]
        return None

    npm_path = shutil.which("npm") or shutil.which("npm.cmd") or shutil.which("npm.exe")
    if npm_path is not None:
        npm_path_obj = Path(npm_path)
        node_cli_command = _node_npm_cli_command(npm_path_obj)
        if node_cli_command is not None:
            return node_cli_command
        return (
            ["cmd", "/c", npm_path] if npm_path.lower().endswith(".cmd") else [npm_path]
        )

    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    windows_candidates = [
        Path(program_files) / "nodejs" / "npm.cmd",
        Path(program_files) / "nodejs" / "npm",
    ]
    for candidate in windows_candidates:
        if candidate.exists():
            node_cli_command = _node_npm_cli_command(candidate)
            if node_cli_command is not None:
                return node_cli_command
            candidate_str = str(candidate)
            return (
                ["cmd", "/c", candidate_str]
                if candidate_str.lower().endswith(".cmd")
                else [candidate_str]
            )

    return None


def _publish_frontend_dist(dist_dir: Path) -> None:
    assets_dir = DOCS_DIR / "assets"
    if assets_dir.exists():
        shutil.rmtree(assets_dir)

    index_path = DOCS_DIR / "index.html"
    if index_path.exists():
        index_path.unlink()

    for child in dist_dir.iterdir():
        destination = DOCS_DIR / child.name
        if child.is_dir():
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(child, destination)
        else:
            shutil.copy2(child, destination)


def _build_frontend_site() -> None:
    npm_command = _resolve_npm_command()
    if npm_command is None:
        raise RuntimeError(
            "Frontend publishing requires npm and the frontend workspace. "
            "Run `npm ci --prefix frontend` before `python analyze_helsmith_lists.py`."
        )

    env = os.environ.copy()
    command_path = Path(npm_command[0])
    if command_path.exists():
        env["PATH"] = str(command_path.parent) + os.pathsep + env.get("PATH", "")

    result = subprocess.run(
        npm_command + ["run", "build"],
        cwd=FRONTEND_DIR,
        check=False,
        capture_output=True,
        env=env,
        text=True,
    )
    if result.returncode != 0:
        detail = (
            result.stderr.strip()
            or result.stdout.strip()
            or "Unknown frontend build failure."
        )
        raise RuntimeError(f"Frontend build failed while publishing docs: {detail}")

    if not FRONTEND_DIST_DIR.exists():
        raise RuntimeError(
            f"Frontend build completed without producing {FRONTEND_DIST_DIR}."
        )

    _publish_frontend_dist(FRONTEND_DIST_DIR)


def _copy_dataset_reports(dataset_key: str, reports_dir: Path) -> None:
    destination = DOCS_DIR / "reports" / dataset_key
    destination.mkdir(parents=True, exist_ok=True)
    for scope in SCOPES:
        for report_name in (f"{scope}.md", f"{scope}-lists.md"):
            source_report = reports_dir / report_name
            if source_report.exists():
                shutil.copy2(source_report, destination / source_report.name)


def build_web_page() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    docs_reports_root = DOCS_DIR / "reports"
    if docs_reports_root.exists():
        shutil.rmtree(docs_reports_root)
    docs_reports_root.mkdir(parents=True, exist_ok=True)

    datasets = _discover_datasets()
    for dataset in datasets:
        _copy_dataset_reports(str(dataset["key"]), Path(dataset["reports_dir"]))

    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    _write_site_payload(build_site_payload(generated_at))
    _build_frontend_site()
