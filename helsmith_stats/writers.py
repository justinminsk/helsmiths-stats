from __future__ import annotations

import csv
from pathlib import Path

from .constants import REPORTS_DIR, SUMMARIES_DIR
from .metrics import collect_scope_metrics, total_models
from .models import ListData, MetricCounter, ScopeMetrics
from .reporting import build_report


def write_counter_csv(
    path: Path, counter: MetricCounter, header_left: str, header_right: str
) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([header_left, header_right])
        for key, value in counter.most_common():
            writer.writerow([key, value])


def write_presence_csv(
    path: Path, presence_counter: MetricCounter, total_lists: int
) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["unit_name", "lists_with_unit", "percent_of_lists"])
        for unit_name, list_count in presence_counter.most_common():
            percent = (list_count / total_lists * 100) if total_lists else 0.0
            writer.writerow([unit_name, list_count, f"{percent:.1f}"])


def write_unplayed_csv(path: Path, unplayed_units: list[tuple[str, int]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["unit_name", "unit_size"])
        for unit_name, unit_size in unplayed_units:
            writer.writerow([unit_name, unit_size])


def write_list_summary(path: Path, lists_for_scope: list[ListData]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "source",
                "name",
                "result",
                "subfaction",
                "manifestation_lore",
                "unit_entries",
                "models",
            ],
        )
        writer.writeheader()
        for army_list in lists_for_scope:
            writer.writerow(
                {
                    "source": army_list.source,
                    "name": army_list.name,
                    "result": army_list.result_bucket,
                    "subfaction": army_list.subfaction,
                    "manifestation_lore": army_list.manifestation_lore,
                    "unit_entries": len(army_list.units),
                    "models": total_models(army_list.units),
                }
            )


def write_scope_outputs(
    scope_slug: str, scope_name: str, lists_for_scope: list[ListData]
) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    scope_dir = SUMMARIES_DIR / scope_slug
    scope_dir.mkdir(parents=True, exist_ok=True)

    metrics: ScopeMetrics = collect_scope_metrics(lists_for_scope)
    report_text = build_report(scope_name, lists_for_scope, metrics)

    write_counter_csv(
        scope_dir / "unit_entry_counts.csv",
        metrics.unit_entries,
        "unit_name",
        "unit_entries",
    )
    write_counter_csv(
        scope_dir / "unit_model_counts.csv",
        metrics.model_counts,
        "unit_name",
        "model_count",
    )
    write_presence_csv(
        scope_dir / "unit_presence_percent.csv",
        metrics.unit_presence_lists,
        len(lists_for_scope),
    )
    write_unplayed_csv(scope_dir / "unplayed_units.csv", metrics.unplayed_units)
    write_counter_csv(
        scope_dir / "subfaction_counts.csv",
        metrics.subfactions,
        "subfaction",
        "list_count",
    )
    write_counter_csv(
        scope_dir / "manifestation_lore_counts.csv",
        metrics.manifestation_lores,
        "manifestation_lore",
        "list_count",
    )
    write_counter_csv(
        scope_dir / "artifact_counts.csv", metrics.artifacts, "artifact", "count"
    )
    write_counter_csv(
        scope_dir / "command_trait_counts.csv",
        metrics.command_traits,
        "command_trait",
        "count",
    )
    write_counter_csv(
        scope_dir / "warmachine_trait_counts.csv",
        metrics.warmachine_traits,
        "warmachine_trait",
        "count",
    )
    write_list_summary(scope_dir / "list_level_summary.csv", lists_for_scope)

    (REPORTS_DIR / f"{scope_slug}.md").write_text(report_text + "\n", encoding="utf-8")
