from __future__ import annotations

from .constants import REPORT_SECTION_LIMIT
from .models import ListData, MetricCounter, ScopeMetrics, UnitData
from .weeks import sort_lists_by_week


def append_counter_section(
    report_lines: list[str],
    title: str,
    counter: MetricCounter,
    limit: int | None = None,
) -> None:
    report_lines.append(title)
    items = counter.most_common(limit)
    report_lines.extend([f"- {name}: {count}" for name, count in items])
    report_lines.append("")


def build_report(
    scope_name: str, lists_for_scope: list[ListData], metrics: ScopeMetrics
) -> str:
    assumptions = [
        "Model counts are inferred from points where reinforced pricing is obvious in this dataset.",
        "Alias normalization is applied for known spelling and export differences.",
        "Trait categories are mapped by a fixed dictionary and count occurrences across lists.",
        "Subfaction is parsed from battle formation, pipe-delimited exports, or Army of Renown lines.",
    ]

    report_lines = [
        f"# Helsmith stats - {scope_name}",
        "",
        f"- Lists parsed: {len(lists_for_scope)}",
        f"- Total unit entries: {sum(metrics.unit_entries.values())}",
        f"- Total inferred models: {sum(metrics.model_counts.values())}",
        "",
    ]

    append_counter_section(
        report_lines,
        "## Top units by entries",
        metrics.unit_entries,
        REPORT_SECTION_LIMIT,
    )
    report_lines.append("## Top units by list presence")
    for name, list_count in metrics.unit_presence_lists.most_common(
        REPORT_SECTION_LIMIT
    ):
        percent = (list_count / len(lists_for_scope) * 100) if lists_for_scope else 0.0
        report_lines.append(
            f"- {name}: {list_count}/{len(lists_for_scope)} lists ({percent:.1f}%)"
        )
    report_lines.append("")
    append_counter_section(
        report_lines,
        "## Top units by model count",
        metrics.model_counts,
        REPORT_SECTION_LIMIT,
    )

    report_lines.append("## Unplayed units")
    if metrics.unplayed_units:
        report_lines.extend(
            [f"- {name} (unit size {size})" for name, size in metrics.unplayed_units]
        )
    else:
        report_lines.append("- None")
    report_lines.append("")

    append_counter_section(report_lines, "## Subfaction counts", metrics.subfactions)
    append_counter_section(
        report_lines, "## Manifestation lore counts", metrics.manifestation_lores
    )
    append_counter_section(report_lines, "## Artifact counts", metrics.artifacts)
    append_counter_section(
        report_lines, "## Command trait counts", metrics.command_traits
    )
    append_counter_section(
        report_lines, "## Warmachine trait counts", metrics.warmachine_traits
    )

    report_lines.append("## Assumptions")
    report_lines.extend([f"- {line}" for line in assumptions])
    report_lines.append("")

    return "\n".join(report_lines)


def _unit_line(unit: UnitData) -> str:
    parts = [f"{unit.name} - {unit.points} pts - {unit.models} models"]
    if unit.reinforced:
        parts.append("reinforced")
    if unit.notes:
        parts.append("notes: " + ", ".join(unit.notes))
    return " - ".join(parts)


def build_lists_report(scope_name: str, lists_for_scope: list[ListData]) -> str:
    ordered_lists = sort_lists_by_week(lists_for_scope)
    report_lines = [
        f"# Helsmith lists - {scope_name}",
        "",
        f"- Lists parsed: {len(ordered_lists)}",
        "",
    ]

    if not ordered_lists:
        report_lines.append("No lists parsed.")
        report_lines.append("")
        return "\n".join(report_lines)

    for army_list in ordered_lists:
        report_lines.extend(
            [
                f"## {army_list.name}",
                "",
                f"- Source: {army_list.source}",
                f"- Week: {army_list.week_label or 'Unspecified'}",
                f"- Result: {army_list.result_bucket}",
                f"- Subfaction: {army_list.subfaction}",
                f"- Manifestation lore: {army_list.manifestation_lore}",
                f"- Unit entries: {len(army_list.units)}",
                "",
            ]
        )

        current_regiment = None
        for unit in army_list.units:
            if unit.regiment != current_regiment:
                current_regiment = unit.regiment
                report_lines.append(f"### {current_regiment}")
            report_lines.append(f"- {_unit_line(unit)}")

        report_lines.append("")

    return "\n".join(report_lines)
