from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from .constants import UNKNOWN

MetricCounter = Counter[str]


@dataclass
class UnitData:
    name: str
    points: int
    models: int = 1
    regiment: str = UNKNOWN
    reinforced: bool = False
    notes: list[str] = field(default_factory=list)


@dataclass
class ScopeMetrics:
    unit_entries: MetricCounter = field(default_factory=Counter)
    unit_presence_lists: MetricCounter = field(default_factory=Counter)
    model_counts: MetricCounter = field(default_factory=Counter)
    subfactions: MetricCounter = field(default_factory=Counter)
    manifestation_lores: MetricCounter = field(default_factory=Counter)
    artifacts: MetricCounter = field(default_factory=Counter)
    command_traits: MetricCounter = field(default_factory=Counter)
    warmachine_traits: MetricCounter = field(default_factory=Counter)
    unplayed_units: list[tuple[str, int]] = field(default_factory=list)


@dataclass
class ListData:
    name: str = ""
    source: str = UNKNOWN
    week_label: str = ""
    result_bucket: str = UNKNOWN
    subfaction: str = UNKNOWN
    manifestation_lore: str = UNKNOWN
    units: list[UnitData] = field(default_factory=list)
    traits: list[str] = field(default_factory=list)
