from __future__ import annotations

import re

from .models import ListData

WEEK_LABEL_PATTERN = re.compile(
    r"^([A-Za-z]+)\s+(\d{1,2})(?:\s*[-–]\s*(\d{1,2}))?$"
)

MONTH_LOOKUP = {
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


def parse_week_label(label: str) -> tuple[int, int, int] | None:
    match = WEEK_LABEL_PATTERN.match(label.strip())
    if not match:
        return None

    month_token = match.group(1).lower()[:3]
    month = MONTH_LOOKUP.get(month_token)
    if month is None:
        return None

    start_day = int(match.group(2))
    end_day = int(match.group(3) or match.group(2))
    return month, start_day, end_day


def week_label_identity(label: str) -> str:
    parts = parse_week_label(label)
    if parts is None:
        return label.strip().lower()

    month, start_day, end_day = parts
    return f"{month:02d}-{start_day:02d}-{end_day:02d}"


def week_label_sort_key(label: str) -> tuple[int, int, int, str]:
    parts = parse_week_label(label)
    if parts is None:
        return (99, 99, 99, label.lower())

    month, start_day, end_day = parts
    return (month, start_day, end_day, label.lower())


def sort_lists_by_week(lists_for_scope: list[ListData]) -> list[ListData]:
    return sorted(
        lists_for_scope,
        key=lambda army_list: (
            week_label_sort_key(army_list.week_label),
            army_list.name.casefold(),
            army_list.source.casefold(),
        ),
    )