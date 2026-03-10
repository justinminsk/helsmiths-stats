from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import TypeAlias

from .constants import UNKNOWN

MetricCounter: TypeAlias = Counter[str]
UnitEntry: TypeAlias = tuple[str, int]


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
    result_bucket: str = UNKNOWN
    subfaction: str = UNKNOWN
    manifestation_lore: str = UNKNOWN
    units: list[UnitEntry] = field(default_factory=list)
    traits: list[str] = field(default_factory=list)
