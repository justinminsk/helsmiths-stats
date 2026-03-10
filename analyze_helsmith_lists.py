from __future__ import annotations

import csv
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).parent
INPUT_FILE = ROOT / "Helsmiths 5-0s.md"


UNIT_MODEL_BASE_SIZE = {
    "Urak Taar, the First Daemonsmith": 1,
    "Daemonsmith": 1,
    "Daemonsmith on Infernal Taurus": 1,
    "Ashen Elder": 1,
    "War Despot": 1,
    "Scourge of Ghyran War Despot": 1,
    "Bull Centaurs": 3,
    "Deathshrieker Rocket Battery": 1,
    "Tormentor Bombard": 1,
    "Dominator Engine with Bane Maces": 1,
    "Dominator Engine with Immolation Cannons": 1,
    "Hobgrotz Vandalz": 10,
    "Infernal Cohort with Hashutite Spears": 10,
    "Infernal Cohort with Hashutite Blades": 10,
    "Infernal Razers with Blunderbusses": 10,
    "Infernal Razers with Flamehurlers": 10,
    "Scourge of Ghyran Infernal Cohort with Hashutite Blades": 10,
    "Scourge of Ghyran Infernal Cohort with Hashutite Spears": 10,
    "Anointed Sentinels": 3,
}

UNIT_NAME_ALIASES = {
    "Rocket battery because anointed suck": "Deathshrieker Rocket Battery",
    "Bull Centaur": "Bull Centaurs",
    "Hobgrot Vandals": "Hobgrotz Vandalz",
    "Scourge of Ghyran Cohort with Hashutite Spears": "Scourge of Ghyran Infernal Cohort with Hashutite Spears",
}

TRAIT_NAMES = {
    "Overdrive Switch",
    "Breath of Contempt",
    "Servile Automaton",
    "An Eye for Weakness",
    "Ruthless Overseer",
    "Scroll of Petrification",
    "Talisman of Obsidian",
    "Crucible of Spite",
    "Gauntlets of Punishment",
}

ARTIFACTS = {
    "Scroll of Petrification",
    "Talisman of Obsidian",
    "Crucible of Spite",
    "Gauntlets of Punishment",
}

COMMAND_TRAITS = {
    "An Eye for Weakness",
    "Ruthless Overseer",
}

WARMACHINE_TRAITS = {
    "Overdrive Switch",
    "Breath of Contempt",
    "Servile Automaton",
}

LIST_NAME_EXCLUSIONS = {
    "Helsmiths of Hashut",
    "Grand Alliance: Chaos",
    "Grand Alliance Chaos",
    "General's Handbook 2025-26",
}


@dataclass
class ListData:
    name: str = ""
    source: str = "Unknown"
    result_bucket: str = "Unknown"
    subfaction: str = "Unknown"
    manifestation_lore: str = "Unknown"
    units: list[tuple[str, int]] = field(default_factory=list)
    traits: list[str] = field(default_factory=list)


def clean_line(line: str) -> str:
    value = line.strip()
    value = value.replace("\\", "")
    value = value.strip('"')
    return value.strip()


def heading_text(raw: str) -> str:
    value = re.sub(r"^#+\s*", "", raw.strip())
    value = value.replace("**", "")
    return clean_line(value)


def normalize_subfaction(value: str) -> str:
    normalized = clean_line(value)
    normalized = re.sub(r"\s*\([^)]*\)\s*$", "", normalized).strip()
    return normalized or "Unknown"


def normalize_unit_name(name: str) -> str:
    normalized = clean_line(name)
    normalized = re.sub(r"^\d+\s*x?\s+", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    normalized = UNIT_NAME_ALIASES.get(normalized, normalized)
    if normalized.lower().startswith("rocket battery"):
        return "Deathshrieker Rocket Battery"
    return normalized


def normalize_trait_name(name: str) -> str:
    normalized = clean_line(name)
    normalized = re.sub(r"^\[[^\]]+\]\s*:\s*", "", normalized)
    normalized = re.sub(r"^[A-Za-z' ]+:\s*", "", normalized)
    normalized = re.sub(r"\s*\([^)]*\)\s*$", "", normalized).strip()
    normalized = re.sub(r"\s+", " ", normalized)

    trait_aliases = {
        "Ruthless Oversser": "Ruthless Overseer",
        "Scroll of petrification": "Scroll of Petrification",
    }
    normalized = trait_aliases.get(normalized, normalized)

    for canonical in TRAIT_NAMES:
        if normalized.lower().startswith(canonical.lower()):
            return canonical

    return normalized


def is_potential_list_name(text: str) -> bool:
    candidate = clean_line(text)
    if not candidate or candidate in LIST_NAME_EXCLUSIONS:
        return False

    excluded_prefixes = (
        "faction:",
        "battle formation:",
        "manifestation lore",
        "spell lore",
        "prayer lore",
        "drops:",
        "points:",
        "wounds:",
        "battle tactics",
    )
    return not candidate.lower().startswith(excluded_prefixes)


def infer_models(unit_name: str, points: int) -> int:
    base_size = UNIT_MODEL_BASE_SIZE.get(unit_name)
    if base_size is None or base_size == 1:
        return 1

    inferred_from_points = {
        ("Bull Centaurs", 190): 3,
        ("Bull Centaurs", 380): 6,
        ("Anointed Sentinels", 150): 3,
        ("Anointed Sentinels", 300): 6,
        ("Hobgrotz Vandalz", 70): 10,
        ("Hobgrotz Vandalz", 140): 20,
        ("Infernal Cohort with Hashutite Spears", 110): 10,
        ("Infernal Cohort with Hashutite Spears", 220): 20,
        ("Infernal Cohort with Hashutite Blades", 100): 10,
        ("Infernal Cohort with Hashutite Blades", 200): 20,
        ("Infernal Razers with Blunderbusses", 220): 20,
        ("Infernal Razers with Flamehurlers", 200): 20,
        ("Scourge of Ghyran Infernal Cohort with Hashutite Blades", 110): 10,
        ("Scourge of Ghyran Infernal Cohort with Hashutite Blades", 220): 20,
        ("Scourge of Ghyran Infernal Cohort with Hashutite Spears", 110): 10,
        ("Scourge of Ghyran Infernal Cohort with Hashutite Spears", 220): 20,
    }
    return inferred_from_points.get((unit_name, points), base_size)


def parse_lists(text: str) -> list[ListData]:
    lines = text.splitlines()
    lists: list[ListData] = []
    current_source = "Unknown"
    current_result = "Unknown"
    current_list: ListData | None = None
    pending_name = ""
    pending_subfaction = ""
    awaiting_subfaction = False

    points_trigger = re.compile(r"\b[\d,]{3,5}\s*/\s*[\d,]{3,5}\s*pts?\b", re.IGNORECASE)
    unit_pattern = re.compile(
        r"^(?:[-•~*]\s*)?(?:(\d+)\s*x?\s+)?(.+?)\s*\(([\d,]+)\s*(?:pts?|points)?\)$",
        re.IGNORECASE,
    )

    def close_current() -> None:
        nonlocal current_list, pending_name, pending_subfaction, awaiting_subfaction
        if current_list is not None and current_list.units:
            lists.append(current_list)
        current_list = None
        pending_name = ""
        pending_subfaction = ""
        awaiting_subfaction = False

    for raw in lines:
        line = clean_line(raw)
        if not line:
            continue

        if raw.lstrip().startswith("#"):
            title = heading_text(raw)
            if title in {"Singles", "Teams"}:
                close_current()
                current_source = title
                current_result = "Unknown"
                continue
            if title in {"5-0", "4-1"}:
                current_result = title
                continue

        if re.fullmatch(r"#+\s*5-0", line):
            current_result = "5-0"
            continue
        if re.fullmatch(r"#+\s*4-1", line):
            current_result = "4-1"
            continue

        stripped_raw = raw.strip()
        if stripped_raw.startswith("**") and stripped_raw.endswith("**"):
            candidate = clean_line(stripped_raw.replace("**", ""))
            if is_potential_list_name(candidate):
                pending_name = candidate
                if current_list is not None and not current_list.units:
                    current_list.name = candidate

        if points_trigger.search(line) or line.lower().startswith("points:"):
            if current_list is not None and current_list.units:
                close_current()
            if current_list is None:
                current_list = ListData(source=current_source, result_bucket=current_result)
                current_list.name = pending_name or line
                if pending_subfaction:
                    current_list.subfaction = pending_subfaction
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

        starters = (
            "Grand Alliance Chaos",
            "Grand Alliance:",
            "Helsmiths of Hashut",
            "Faction: Helsmiths of Hashut",
            "Battle Formation:",
        )
        if current_list is not None and current_list.units and line.startswith(starters):
            close_current()

        if current_list is None:
            if line.startswith(starters):
                current_list = ListData(source=current_source, result_bucket=current_result)
                if pending_name:
                    current_list.name = pending_name
                if pending_subfaction:
                    current_list.subfaction = pending_subfaction
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
            if line not in {"Army of Renown", "General's Handbook 2025-26"} and not line.startswith("Drops:"):
                current_list.subfaction = normalize_subfaction(line)
            awaiting_subfaction = False
            continue

        if line.startswith("Battle Formation:"):
            current_list.subfaction = normalize_subfaction(line.split(":", 1)[1])
            continue

        if line.startswith("Faction:"):
            continue

        if line.lower().startswith("manifestation lore"):
            value = line.split("-", 1)[-1] if "-" in line else line.split(":", 1)[-1]
            value = re.sub(r"\s*\([^)]*\)\s*$", "", value).strip()
            current_list.manifestation_lore = value
            continue

        unit_match = unit_pattern.match(line)
        if unit_match:
            unit_name = normalize_unit_name(unit_match.group(2))
            points = int(unit_match.group(3).replace(",", ""))
            if points < 50:
                continue
            current_list.units.append((unit_name, points))
            continue

        if line.startswith(("•", "~", "*", "-", "[")):
            trait = normalize_trait_name(re.sub(r"^[•~*\-]\s*", "", line))
            if trait in TRAIT_NAMES:
                current_list.traits.append(trait)
            continue

    if current_list is not None:
        close_current()

    for index, army_list in enumerate(lists, start=1):
        if not army_list.name:
            army_list.name = f"List {index}"

    return lists


def write_counter_csv(path: Path, counter: Counter, header_left: str, header_right: str) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([header_left, header_right])
        for key, value in counter.most_common():
            writer.writerow([key, value])


def write_presence_csv(path: Path, presence_counter: Counter, total_lists: int) -> None:
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


def build_report(scope_name: str, lists_for_scope: list[ListData]) -> str:
    unit_entries = Counter()
    unit_presence_lists = Counter()
    model_counts = Counter()
    subfactions = Counter()
    manifestation_lores = Counter()
    artifacts = Counter()
    command_traits = Counter()
    warmachine_traits = Counter()

    for army_list in lists_for_scope:
        subfactions[army_list.subfaction] += 1
        manifestation_lores[army_list.manifestation_lore] += 1

        units_in_this_list = set()
        for unit_name, points in army_list.units:
            unit_entries[unit_name] += 1
            units_in_this_list.add(unit_name)
            model_counts[unit_name] += infer_models(unit_name, points)

        for unit_name in units_in_this_list:
            unit_presence_lists[unit_name] += 1

        for trait in army_list.traits:
            if trait in ARTIFACTS:
                artifacts[trait] += 1
            if trait in COMMAND_TRAITS:
                command_traits[trait] += 1
            if trait in WARMACHINE_TRAITS:
                warmachine_traits[trait] += 1

    known_units = set(UNIT_MODEL_BASE_SIZE.keys())
    played_units = set(unit_presence_lists.keys())
    unplayed_units = sorted(
        [(unit_name, UNIT_MODEL_BASE_SIZE[unit_name]) for unit_name in known_units - played_units],
        key=lambda item: item[0],
    )

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
        f"- Total unit entries: {sum(unit_entries.values())}",
        f"- Total inferred models: {sum(model_counts.values())}",
        "",
        "## Top units by entries",
    ]
    report_lines.extend([f"- {name}: {count}" for name, count in unit_entries.most_common(10)])
    report_lines.append("")
    report_lines.append("## Top units by list presence")
    for name, list_count in unit_presence_lists.most_common(10):
        percent = (list_count / len(lists_for_scope) * 100) if lists_for_scope else 0.0
        report_lines.append(f"- {name}: {list_count}/{len(lists_for_scope)} lists ({percent:.1f}%)")
    report_lines.append("")
    report_lines.append("## Top units by model count")
    report_lines.extend([f"- {name}: {count}" for name, count in model_counts.most_common(10)])
    report_lines.append("")
    report_lines.append("## Unplayed units")
    if unplayed_units:
        report_lines.extend([f"- {name} (unit size {size})" for name, size in unplayed_units])
    else:
        report_lines.append("- None")
    report_lines.append("")
    report_lines.append("## Subfaction counts")
    report_lines.extend([f"- {name}: {count}" for name, count in subfactions.most_common()])
    report_lines.append("")
    report_lines.append("## Manifestation lore counts")
    report_lines.extend([f"- {name}: {count}" for name, count in manifestation_lores.most_common()])
    report_lines.append("")
    report_lines.append("## Artifact counts")
    report_lines.extend([f"- {name}: {count}" for name, count in artifacts.most_common()])
    report_lines.append("")
    report_lines.append("## Command trait counts")
    report_lines.extend([f"- {name}: {count}" for name, count in command_traits.most_common()])
    report_lines.append("")
    report_lines.append("## Warmachine trait counts")
    report_lines.extend([f"- {name}: {count}" for name, count in warmachine_traits.most_common()])
    report_lines.append("")
    report_lines.append("## Assumptions")
    report_lines.extend([f"- {line}" for line in assumptions])
    report_lines.append("")

    return "\n".join(report_lines)


def write_list_summary(path: Path, lists_for_scope: list[ListData]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["source", "name", "result", "subfaction", "manifestation_lore", "unit_entries", "models"],
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
                    "models": sum(infer_models(unit_name, points) for unit_name, points in army_list.units),
                }
            )


def write_combined_metric_files(all_lists: list[ListData]) -> None:
    unit_entries = Counter()
    unit_presence_lists = Counter()
    model_counts = Counter()
    subfactions = Counter()
    manifestation_lores = Counter()
    artifacts = Counter()
    command_traits = Counter()
    warmachine_traits = Counter()

    for army_list in all_lists:
        subfactions[army_list.subfaction] += 1
        manifestation_lores[army_list.manifestation_lore] += 1

        units_in_this_list = set()
        for unit_name, points in army_list.units:
            unit_entries[unit_name] += 1
            units_in_this_list.add(unit_name)
            model_counts[unit_name] += infer_models(unit_name, points)

        for unit_name in units_in_this_list:
            unit_presence_lists[unit_name] += 1

        for trait in army_list.traits:
            if trait in ARTIFACTS:
                artifacts[trait] += 1
            if trait in COMMAND_TRAITS:
                command_traits[trait] += 1
            if trait in WARMACHINE_TRAITS:
                warmachine_traits[trait] += 1

    known_units = set(UNIT_MODEL_BASE_SIZE.keys())
    played_units = set(unit_presence_lists.keys())
    unplayed_units = sorted(
        [(unit_name, UNIT_MODEL_BASE_SIZE[unit_name]) for unit_name in known_units - played_units],
        key=lambda item: item[0],
    )

    write_counter_csv(ROOT / "unit_entry_counts.csv", unit_entries, "unit_name", "unit_entries")
    write_counter_csv(ROOT / "unit_model_counts.csv", model_counts, "unit_name", "model_count")
    write_presence_csv(ROOT / "unit_presence_percent.csv", unit_presence_lists, len(all_lists))
    write_unplayed_csv(ROOT / "unplayed_units.csv", unplayed_units)
    write_counter_csv(ROOT / "subfaction_counts.csv", subfactions, "subfaction", "list_count")
    write_counter_csv(ROOT / "manifestation_lore_counts.csv", manifestation_lores, "manifestation_lore", "list_count")
    write_counter_csv(ROOT / "artifact_counts.csv", artifacts, "artifact", "count")
    write_counter_csv(ROOT / "command_trait_counts.csv", command_traits, "command_trait", "count")
    write_counter_csv(ROOT / "warmachine_trait_counts.csv", warmachine_traits, "warmachine_trait", "count")


def main() -> None:
    text = INPUT_FILE.read_text(encoding="utf-8")
    all_lists = parse_lists(text)

    singles_lists = [army_list for army_list in all_lists if army_list.source == "Singles"]
    teams_lists = [army_list for army_list in all_lists if army_list.source == "Teams"]

    reports = {
        "combined": build_report("Combined", all_lists),
        "singles": build_report("Singles", singles_lists),
        "teams": build_report("Teams", teams_lists),
    }

    (ROOT / "combined_helsmith_stats_report.md").write_text(reports["combined"] + "\n", encoding="utf-8")
    (ROOT / "singles_helsmith_stats_report.md").write_text(reports["singles"] + "\n", encoding="utf-8")
    (ROOT / "teams_helsmith_stats_report.md").write_text(reports["teams"] + "\n", encoding="utf-8")
    (ROOT / "helsmith_stats_report.md").write_text(reports["combined"] + "\n", encoding="utf-8")

    write_list_summary(ROOT / "combined_list_level_summary.csv", all_lists)
    write_list_summary(ROOT / "singles_list_level_summary.csv", singles_lists)
    write_list_summary(ROOT / "teams_list_level_summary.csv", teams_lists)
    write_list_summary(ROOT / "list_level_summary.csv", all_lists)

    write_combined_metric_files(all_lists)


if __name__ == "__main__":
    main()
