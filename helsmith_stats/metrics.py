from __future__ import annotations

from .constants import (
    ARTIFACTS,
    COMMAND_TRAITS,
    POINT_INFERENCES,
    UNIT_MODEL_BASE_SIZE,
    WARMACHINE_TRAITS,
)
from .models import ListData, ScopeMetrics, UnitEntry


def infer_models(unit_name: str, points: int) -> int:
    base_size = UNIT_MODEL_BASE_SIZE.get(unit_name)
    if base_size is None or base_size == 1:
        return 1
    return POINT_INFERENCES.get((unit_name, points), base_size)


def total_models(units: list[UnitEntry]) -> int:
    return sum(infer_models(unit_name, points) for unit_name, points in units)


def compute_unplayed_units(played_units: set[str]) -> list[tuple[str, int]]:
    known_units = set(UNIT_MODEL_BASE_SIZE.keys())
    return sorted(
        [
            (unit_name, UNIT_MODEL_BASE_SIZE[unit_name])
            for unit_name in known_units - played_units
        ],
        key=lambda item: item[0],
    )


def collect_scope_metrics(lists_for_scope: list[ListData]) -> ScopeMetrics:
    metrics = ScopeMetrics()

    for army_list in lists_for_scope:
        metrics.subfactions[army_list.subfaction] += 1
        metrics.manifestation_lores[army_list.manifestation_lore] += 1

        units_in_this_list = set()
        for unit_name, points in army_list.units:
            metrics.unit_entries[unit_name] += 1
            units_in_this_list.add(unit_name)
            metrics.model_counts[unit_name] += infer_models(unit_name, points)

        for unit_name in units_in_this_list:
            metrics.unit_presence_lists[unit_name] += 1

        for trait in army_list.traits:
            if trait in ARTIFACTS:
                metrics.artifacts[trait] += 1
            if trait in COMMAND_TRAITS:
                metrics.command_traits[trait] += 1
            if trait in WARMACHINE_TRAITS:
                metrics.warmachine_traits[trait] += 1

    metrics.unplayed_units = compute_unplayed_units(
        set(metrics.unit_presence_lists.keys())
    )
    return metrics
