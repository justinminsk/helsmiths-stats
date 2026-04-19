from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
from collections import Counter
from datetime import datetime
from itertools import combinations
from pathlib import Path
import re

from .constants import DOCS_DIR, REPORTS_DIR, ROOT, SUMMARIES_DIR

SCOPES = ("combined", "singles", "teams")
MAX_ARCHIVED_SNAPSHOTS = 3
STATS_TABLE_ROWS_DEFAULT = 12
SHARED_UNIT_ROWS_DEFAULT = 5
SHARED_PAIR_ROWS_DEFAULT = 4
SNAPSHOT_TREND_ROWS_DEFAULT = 3
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


def _format_share(count: int, total: int) -> str:
    if total <= 0:
        return "0.0%"
    return f"{(count / total) * 100:.1f}%"


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
        "weekLabel": row.get("week", "").strip(),
        "name": row.get("name", ""),
        "result": row.get("result", ""),
        "subfaction": row.get("subfaction", ""),
        "manifestationLore": row.get("manifestation_lore", ""),
        "regiments": len(regiments),
        "unitEntries": _int_from_text(row.get("unit_entries", "0")),
        "models": _int_from_text(row.get("models", "0")),
        "units": units,
    }


def _build_shared_units(list_payload: list[dict[str, object]]) -> list[dict[str, object]]:
    if not list_payload:
        return []

    unit_counts: Counter[str] = Counter()
    for army_list in list_payload:
        unit_counts.update(
            {
                str(unit.get("name", "")).strip()
                for unit in army_list.get("units", [])
                if str(unit.get("name", "")).strip()
            }
        )

    minimum_count = 2 if len(list_payload) >= 2 else 1
    shared_rows = [
        (name, count)
        for name, count in unit_counts.items()
        if count >= minimum_count
    ]
    if not shared_rows:
        shared_rows = unit_counts.most_common(SHARED_UNIT_ROWS_DEFAULT)
    else:
        shared_rows = sorted(shared_rows, key=lambda item: (-item[1], item[0]))

    return [
        {
            "name": name,
            "listCount": count,
            "share": _format_share(count, len(list_payload)),
        }
        for name, count in shared_rows[:SHARED_UNIT_ROWS_DEFAULT]
    ]


def _build_shared_unit_pairs(
    list_payload: list[dict[str, object]],
) -> list[dict[str, object]]:
    if len(list_payload) < 2:
        return []

    pair_counts: Counter[tuple[str, str]] = Counter()
    for army_list in list_payload:
        unit_names = sorted(
            {
                str(unit.get("name", "")).strip()
                for unit in army_list.get("units", [])
                if str(unit.get("name", "")).strip()
            }
        )
        for pair in combinations(unit_names, 2):
            pair_counts[pair] += 1

    shared_pairs = [
        (pair, count) for pair, count in pair_counts.items() if count >= 2
    ]
    shared_pairs.sort(key=lambda item: (-item[1], item[0]))

    return [
        {
            "units": list(pair),
            "listCount": count,
            "share": _format_share(count, len(list_payload)),
        }
        for pair, count in shared_pairs[:SHARED_PAIR_ROWS_DEFAULT]
    ]


def _build_story_core_signals(
    *,
    list_count: int,
    shared_units: list[dict[str, object]],
    shared_pairs: list[dict[str, object]],
    subfaction_rows: list[list[str]],
    manifestation_rows: list[list[str]],
) -> list[dict[str, str]]:
    signals: list[dict[str, str]] = []

    if subfaction_rows:
        label = subfaction_rows[0][0] if subfaction_rows[0] else ""
        count = subfaction_rows[0][1] if len(subfaction_rows[0]) > 1 else "0"
        if label:
            signals.append(
                {
                    "label": "Top subfaction",
                    "value": label,
                    "detail": f"{count} of {list_count} lists",
                }
            )

    if manifestation_rows:
        label = manifestation_rows[0][0] if manifestation_rows[0] else ""
        count = manifestation_rows[0][1] if len(manifestation_rows[0]) > 1 else "0"
        if label:
            signals.append(
                {
                    "label": "Top manifestation lore",
                    "value": label,
                    "detail": f"{count} of {list_count} lists",
                }
            )

    if shared_units:
        shared_unit = shared_units[0]
        signals.append(
            {
                "label": "Most shared unit",
                "value": str(shared_unit["name"]),
                "detail": (
                    f"{shared_unit['listCount']} of {list_count} lists"
                    f" ({shared_unit['share']})"
                ),
            }
        )

    if shared_pairs:
        shared_pair = shared_pairs[0]
        pair_label = " + ".join(str(unit) for unit in shared_pair["units"])
        signals.append(
            {
                "label": "Most repeated package",
                "value": pair_label,
                "detail": (
                    f"{shared_pair['listCount']} of {list_count} lists"
                    f" ({shared_pair['share']})"
                ),
            }
        )

    return signals[:4]


def _find_stats_table(
    scope_payload: dict[str, object], table_key: str
) -> dict[str, object] | None:
    for table in scope_payload.get("statsTables", []):
        if str(table.get("key", "")) == table_key:
            return table
    return None


def _metric_value_kind(table_key: str) -> tuple[int, str]:
    if table_key == "topUnitPresence":
        return 2, "percent"
    return 1, "count"


def _value_to_number(value: str, kind: str) -> float:
    cleaned = str(value).replace("%", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _format_delta_label(delta: float, kind: str, baseline_label: str) -> str:
    if abs(delta) < 0.05:
        return f"Flat versus {baseline_label}"
    if kind == "percent":
        return f"{delta:+.1f} pts versus {baseline_label}"
    unit_label = "list" if abs(delta) == 1 else "lists"
    return f"{delta:+.0f} {unit_label} versus {baseline_label}"


def _week_label_parts(label: str) -> tuple[int, int, int] | None:
    match = re.match(
        r"^([A-Za-z]+)\s+(\d{1,2})(?:\s*[-–]\s*(\d{1,2}))?$",
        label.strip(),
    )
    if not match:
        return None

    month_token = match.group(1).lower()[:3]
    month_lookup = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }
    month = month_lookup.get(month_token)
    if month is None:
        return None

    start_day = int(match.group(2))
    end_day = int(match.group(3) or match.group(2))
    return month, start_day, end_day


def _week_label_identity(label: str) -> str:
    parts = _week_label_parts(label)
    if parts is None:
        return label.strip().lower()
    month, start_day, end_day = parts
    return f"{month:02d}-{start_day:02d}-{end_day:02d}"


def _week_label_sort_key(label: str) -> tuple[int, int, int, str]:
    parts = _week_label_parts(label)
    if parts is None:
        return (99, 99, 99, label.lower())
    month, start_day, end_day = parts
    return (month, start_day, end_day, label.lower())


def _weekly_era_label(dataset_key: str) -> str:
    return "Post-points era" if dataset_key == "current" else "Pre-points era"


def _build_snapshot_trends(
    timeline: list[dict[str, object]],
) -> list[dict[str, object]]:
    if len(timeline) < 2:
        return []

    trend_specs = [
        ("topUnitPresence", "Unit presence"),
        ("topSubfactions", "Subfaction usage"),
        ("manifestationLores", "Lore usage"),
    ]
    trends: list[dict[str, object]] = []

    current_scope = timeline[0]["scope"]
    current_scope_payload = current_scope if isinstance(current_scope, dict) else {}

    for table_key, title in trend_specs:
        current_table = _find_stats_table(current_scope_payload, table_key)
        current_rows = current_table.get("rows", []) if current_table else []
        if not current_rows or not current_rows[0]:
            continue

        tracked_label = str(current_rows[0][0]).strip()
        if not tracked_label:
            continue

        value_index, kind = _metric_value_kind(table_key)
        points: list[dict[str, str]] = []
        for dataset in reversed(timeline):
            scope_payload = dataset["scope"]
            scope_payload_dict = scope_payload if isinstance(scope_payload, dict) else {}
            table = _find_stats_table(scope_payload_dict, table_key)
            value = "0%" if kind == "percent" else "0"
            if table:
                for row in table.get("rows", []):
                    if row and str(row[0]).strip() == tracked_label:
                        if len(row) > value_index:
                            value = str(row[value_index])
                        break
            points.append(
                {
                    "datasetKey": str(dataset["datasetKey"]),
                    "datasetLabel": str(dataset["datasetLabel"]),
                    "value": value,
                }
            )

        baseline_value = _value_to_number(points[0]["value"], kind)
        current_value = _value_to_number(points[-1]["value"], kind)
        delta = current_value - baseline_value
        if abs(delta) < 0.05:
            direction = "flat"
        elif delta > 0:
            direction = "up"
        else:
            direction = "down"

        trends.append(
            {
                "metric": title,
                "label": tracked_label,
                "currentValue": points[-1]["value"],
                "deltaLabel": _format_delta_label(
                    delta, kind, points[0]["datasetLabel"]
                ),
                "direction": direction,
                "points": points,
            }
        )

    return trends[:SNAPSHOT_TREND_ROWS_DEFAULT]


def _group_lists_by_week(
    list_payload: list[dict[str, object]],
    *,
    start_index: int = 1,
    era_label: str | None = None,
) -> list[dict[str, object]]:
    grouped: list[dict[str, object]] = []
    lookup: dict[str, dict[str, object]] = {}

    for army_list in list_payload:
        week_label = str(army_list.get("weekLabel", "")).strip()
        if not week_label:
            continue

        existing = lookup.get(week_label)
        if existing is None:
            existing = {
                "datasetKey": f"week-{start_index + len(grouped)}",
                "datasetLabel": week_label,
                "eraLabel": era_label or "",
                "lists": [],
            }
            lookup[week_label] = existing
            grouped.append(existing)

        existing_lists = existing.get("lists")
        if isinstance(existing_lists, list):
            existing_lists.append(army_list)

    return grouped


def _weekly_trend_value(
    table_key: str,
    tracked_label: str,
    grouped_lists: list[dict[str, object]],
) -> str:
    total_lists = len(grouped_lists)
    if total_lists <= 0:
        return "0.0%"

    if table_key == "topUnitPresence":
        matching_lists = sum(
            1
            for army_list in grouped_lists
            if tracked_label
            in {
                str(unit.get("name", "")).strip()
                for unit in army_list.get("units", [])
                if str(unit.get("name", "")).strip()
            }
        )
    elif table_key == "topSubfactions":
        matching_lists = sum(
            1
            for army_list in grouped_lists
            if str(army_list.get("subfaction", "")).strip() == tracked_label
        )
    else:
        matching_lists = sum(
            1
            for army_list in grouped_lists
            if str(army_list.get("manifestationLore", "")).strip() == tracked_label
        )

    return _format_share(matching_lists, total_lists)


def _build_weekly_trends(
    scope_payload: dict[str, object],
    timeline: list[dict[str, object]],
) -> list[dict[str, object]]:
    weekly_groups: list[dict[str, object]] = []
    seen_week_labels: set[str] = set()

    for timeline_scope in reversed(timeline):
        scope = timeline_scope.get("scope")
        scope_payload_dict = scope if isinstance(scope, dict) else {}
        scope_lists = scope_payload_dict.get("lists", [])
        if not isinstance(scope_lists, list):
            continue

        for group in _group_lists_by_week(
            scope_lists,
            start_index=len(weekly_groups) + 1,
            era_label=_weekly_era_label(str(timeline_scope.get("datasetKey", ""))),
        ):
            week_label = str(group.get("datasetLabel", "")).strip()
            week_identity = _week_label_identity(week_label)
            if not week_label or week_identity in seen_week_labels:
                continue
            seen_week_labels.add(week_identity)
            weekly_groups.append(group)

    weekly_groups.sort(
        key=lambda group: _week_label_sort_key(str(group.get("datasetLabel", "")))
    )
    for index, group in enumerate(weekly_groups, start=1):
        group["datasetKey"] = f"week-{index}"

    if len(weekly_groups) < 2:
        return []

    trend_specs = [
        ("topUnitPresence", "Unit presence"),
        ("topSubfactions", "Subfaction share"),
        ("manifestationLores", "Lore share"),
    ]
    trends: list[dict[str, object]] = []

    for table_key, title in trend_specs:
        current_table = _find_stats_table(scope_payload, table_key)
        current_rows = current_table.get("rows", []) if current_table else []
        if not current_rows or not current_rows[0]:
            continue

        tracked_label = str(current_rows[0][0]).strip()
        if not tracked_label:
            continue

        points = [
            {
                "datasetKey": str(group["datasetKey"]),
                "datasetLabel": str(group["datasetLabel"]),
                "eraLabel": str(group.get("eraLabel", "")).strip(),
                "value": _weekly_trend_value(
                    table_key,
                    tracked_label,
                    group.get("lists", []),
                ),
            }
            for group in weekly_groups
        ]

        baseline_value = _value_to_number(points[0]["value"], "percent")
        current_value = _value_to_number(points[-1]["value"], "percent")
        delta = current_value - baseline_value
        if abs(delta) < 0.05:
            direction = "flat"
        elif delta > 0:
            direction = "up"
        else:
            direction = "down"

        trends.append(
            {
                "metric": title,
                "label": tracked_label,
                "currentValue": points[-1]["value"],
                "deltaLabel": _format_delta_label(
                    delta, "percent", points[0]["datasetLabel"]
                ),
                "direction": direction,
                "points": points,
            }
        )

    return trends[:SNAPSHOT_TREND_ROWS_DEFAULT]


def _attach_story_trends(payload_datasets: list[dict[str, object]]) -> None:
    for dataset_index, dataset in enumerate(payload_datasets):
        scope_lookup = {
            str(scope.get("key", "")): scope for scope in dataset.get("scopes", [])
        }
        for scope_key, scope in scope_lookup.items():
            timeline: list[dict[str, object]] = []
            for timeline_dataset in payload_datasets[dataset_index:]:
                matching_scope = next(
                    (
                        item
                        for item in timeline_dataset.get("scopes", [])
                        if str(item.get("key", "")) == scope_key
                    ),
                    None,
                )
                if matching_scope is None:
                    continue
                timeline.append(
                    {
                        "datasetKey": str(timeline_dataset.get("key", "")),
                        "datasetLabel": str(timeline_dataset.get("label", "")),
                        "scope": matching_scope,
                    }
                )

            story = scope.get("story", {})
            if isinstance(story, dict):
                story["weeklyTrends"] = _build_weekly_trends(scope, timeline)
                story["snapshotTrends"] = _build_snapshot_trends(timeline)
                scope["story"] = story


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
    shared_units = _build_shared_units(list_payload)
    shared_pairs = _build_shared_unit_pairs(list_payload)

    scope_payload = {
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
        "story": {
            "coreSignals": _build_story_core_signals(
                list_count=len(list_payload),
                shared_units=shared_units,
                shared_pairs=shared_pairs,
                subfaction_rows=subfaction_rows,
                manifestation_rows=manifestation_rows,
            ),
            "sharedUnits": shared_units,
            "sharedUnitPairs": shared_pairs,
            "weeklyTrends": [],
            "snapshotTrends": [],
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

    story = scope_payload.get("story", {})
    if isinstance(story, dict):
        story["weeklyTrends"] = _build_weekly_trends(scope_payload, list_payload)
        scope_payload["story"] = story

    return scope_payload


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
    _attach_story_trends(payload_datasets)
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
