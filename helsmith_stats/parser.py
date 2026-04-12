from __future__ import annotations

import re

from .constants import (
    HEADING_RESULT_PATTERN,
    POINTS_TRIGGER,
    SCOPE_NAMES,
    STARTER_PREFIXES,
    TRAIT_NAMES,
    UNIT_PATTERN,
    UNIT_MODEL_BASE_SIZE,
    UNKNOWN,
)
from .metrics import infer_models
from .models import ListData, UnitData
from .normalization import (
    clean_line,
    heading_text,
    is_potential_list_name,
    normalize_subfaction,
    normalize_trait_name,
    normalize_unit_name,
)


def _normalize_regiment_name(line: str) -> str | None:
    normalized = clean_line(line).replace("’", "'")
    normalized = re.sub(r"^[\-*~ ]+|[\-*~ ]+$", "", normalized).strip()
    lowered = normalized.lower()

    if not normalized or normalized == "REGIMENTS":
        return None
    if "general's regiment" in lowered:
        return "General's Regiment"

    regiment_match = re.search(r"regiment\s*#?\s*(\d+)", lowered)
    if regiment_match:
        label = f"Regiment {regiment_match.group(1)}"
        if "general" in lowered:
            return f"{label} (General's)"
        return label

    return None


def parse_lists(text: str) -> list[ListData]:
    lines = text.splitlines()
    lists: list[ListData] = []
    current_source = UNKNOWN
    current_result = UNKNOWN
    current_list: ListData | None = None
    current_unit: UnitData | None = None
    current_regiment = UNKNOWN
    pending_name = ""
    pending_subfaction = ""
    awaiting_subfaction = False

    def close_current() -> None:
        nonlocal \
            current_list, \
            current_unit, \
            current_regiment, \
            pending_name, \
            pending_subfaction, \
            awaiting_subfaction
        if current_list is not None and current_list.units:
            lists.append(current_list)
        current_list = None
        current_unit = None
        current_regiment = UNKNOWN
        pending_name = ""
        pending_subfaction = ""
        awaiting_subfaction = False

    for raw in lines:
        line = clean_line(raw)
        if not line:
            continue
        if re.fullmatch(r"[-~*]{3,}", line):
            continue

        if raw.lstrip().startswith("#"):
            title = heading_text(raw)
            if title in SCOPE_NAMES:
                close_current()
                current_source = title
                current_result = UNKNOWN
                continue
            if title in {"5-0", "4-1"}:
                current_result = title
                continue

        heading_result_match = HEADING_RESULT_PATTERN.fullmatch(line)
        if heading_result_match:
            current_result = heading_result_match.group(1)
            continue

        stripped_raw = raw.strip()
        if stripped_raw.startswith("**") and stripped_raw.endswith("**"):
            candidate = clean_line(stripped_raw.replace("**", ""))
            if is_potential_list_name(candidate):
                pending_name = candidate
                if current_list is not None and not current_list.units:
                    current_list.name = candidate

        if POINTS_TRIGGER.search(line) or line.lower().startswith("points:"):
            if current_list is not None and current_list.units:
                close_current()
            if current_list is None:
                current_list = ListData(
                    source=current_source, result_bucket=current_result
                )
                current_list.name = pending_name or line
                if pending_subfaction:
                    current_list.subfaction = pending_subfaction
                current_unit = None
                current_regiment = UNKNOWN
            continue

        if line.lower().startswith("created with"):
            close_current()
            continue

        if line.startswith("Army of Renown:") and "-" in line:
            parsed_subfaction = normalize_subfaction(line.split("-", 1)[1])
            pending_subfaction = parsed_subfaction
            if current_list is not None:
                current_list.subfaction = parsed_subfaction
            continue

        if (
            current_list is not None
            and current_list.units
            and line.startswith(STARTER_PREFIXES)
        ):
            close_current()

        if current_list is None:
            if line.startswith(STARTER_PREFIXES):
                current_list = ListData(
                    source=current_source, result_bucket=current_result
                )
                if pending_name:
                    current_list.name = pending_name
                if pending_subfaction:
                    current_list.subfaction = pending_subfaction
                current_unit = None
                current_regiment = UNKNOWN
            else:
                continue

        if not current_list.name and pending_name:
            current_list.name = pending_name

        if line.startswith("Grand Alliance Chaos"):
            parts = [normalize_subfaction(part) for part in line.split("|")]
            if len(parts) >= 3:
                current_list.subfaction = parts[2]
            continue

        if line.startswith("Helsmiths of Hashut") and "|" in line:
            parts = [normalize_subfaction(part) for part in line.split("|")]
            if len(parts) >= 2:
                current_list.subfaction = parts[1]
            continue

        if line == "Helsmiths of Hashut":
            awaiting_subfaction = True
            continue

        if awaiting_subfaction:
            if line not in {
                "Army of Renown",
                "General's Handbook 2025-26",
            } and not line.startswith("Drops:"):
                current_list.subfaction = normalize_subfaction(line)
            awaiting_subfaction = False
            continue

        if line.startswith("Battle Formation:"):
            current_list.subfaction = normalize_subfaction(line.split(":", 1)[1])
            continue

        if line.startswith("Faction:"):
            continue

        regiment_name = _normalize_regiment_name(line)
        if regiment_name is not None:
            current_regiment = regiment_name
            current_unit = None
            continue

        if line.lower().startswith("manifestation lore"):
            value = line.split("-", 1)[-1] if "-" in line else line.split(":", 1)[-1]
            value = re.sub(r"\s*\([^)]*\)\s*$", "", value).strip()
            current_list.manifestation_lore = value
            continue

        unit_match = UNIT_PATTERN.match(line)
        if unit_match:
            unit_name = normalize_unit_name(unit_match.group(2))
            points = int(unit_match.group(3).replace(",", ""))
            explicit_models = int(unit_match.group(1)) if unit_match.group(1) else None
            if points < 50:
                continue
            inferred_models = explicit_models or infer_models(unit_name, points)
            base_size = UNIT_MODEL_BASE_SIZE.get(unit_name, 1)
            current_unit = UnitData(
                name=unit_name,
                points=points,
                models=inferred_models,
                regiment=current_regiment,
                reinforced=inferred_models > base_size,
            )
            current_list.units.append(current_unit)
            continue

        if line.startswith(("•", "~", "*", "-", "[")):
            trait = normalize_trait_name(re.sub(r"^[•~*\-]\s*", "", line))
            if not trait:
                continue
            if current_unit is not None:
                if trait.lower() == "reinforced":
                    current_unit.reinforced = True
                else:
                    current_unit.notes.append(trait)
            if trait in TRAIT_NAMES:
                current_list.traits.append(trait)
            continue

    if current_list is not None:
        close_current()

    for index, army_list in enumerate(lists, start=1):
        if not army_list.name:
            army_list.name = f"List {index}"

    return lists
