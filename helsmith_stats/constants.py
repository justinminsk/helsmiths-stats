from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "Helsmiths 5-0s.md"
README_FILE = ROOT / "README.md"
REPORTS_DIR = ROOT / "reports"
SUMMARIES_DIR = ROOT / "summaries"
DOCS_DIR = ROOT / "docs"

UNKNOWN = "Unknown"
SCOPE_NAMES = ("Singles", "Teams")
STARTER_PREFIXES = (
    "Grand Alliance Chaos",
    "Grand Alliance:",
    "Helsmiths of Hashut",
    "Faction: Helsmiths of Hashut",
    "Battle Formation:",
)
LIST_NAME_EXCLUDED_PREFIXES = (
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

POINTS_TRIGGER = re.compile(r"\b[\d,]{3,5}\s*/\s*[\d,]{3,5}\s*pts?\b", re.IGNORECASE)
UNIT_PATTERN = re.compile(
    r"^(?:[-•~*]\s*)?(?:(\d+)\s*x?\s+)?(.+?)\s*\(([\d,]+)\s*(?:pts?|points)?\)$",
    re.IGNORECASE,
)
HEADING_RESULT_PATTERN = re.compile(r"#+\s*(5-0|4-1)")
REPORT_SECTION_LIMIT = 10

POINT_INFERENCES = {
    ("Bull Centaurs", 190): 3,
    ("Bull Centaurs", 380): 6,
    ("Anointed Sentinels", 150): 3,
    ("Anointed Sentinels", 300): 6,
    ("Hobgrotz Vandalz", 70): 10,
    ("Hobgrotz Vandalz", 140): 20,
    ("Infernal Cohort with Hashutite Spears", 100): 10,
    ("Infernal Cohort with Hashutite Spears", 200): 20,
    ("Infernal Cohort with Hashutite Spears", 110): 10,
    ("Infernal Cohort with Hashutite Spears", 220): 20,
    ("Scourge of Ghyran Infernal Cohort with Hashutite Blades", 100): 10,
    ("Scourge of Ghyran Infernal Cohort with Hashutite Blades", 200): 20,
    ("Infernal Cohort with Hashutite Blades", 100): 10,
    ("Infernal Cohort with Hashutite Blades", 200): 20,
    ("Infernal Razers with Blunderbusses", 220): 10,
    ("Infernal Razers with Flamehurlers", 200): 10,
    ("Scourge of Ghyran Infernal Cohort with Hashutite Blades", 110): 10,
    ("Scourge of Ghyran Infernal Cohort with Hashutite Blades", 220): 20,
}

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
    "Infernal Razers with Blunderbusses": 5,
    "Infernal Razers with Flamehurlers": 5,
    "Scourge of Ghyran Infernal Cohort with Hashutite Blades": 10,
    "Anointed Sentinels": 3,
}

UNIT_NAME_ALIASES = {
    "Rocket battery because anointed suck": "Deathshrieker Rocket Battery",
    "Bull Centaur": "Bull Centaurs",
    "Hobgrot Vandals": "Hobgrotz Vandalz",
    "Scourge of Ghyran Cohort with Hashutite Spears": "Scourge of Ghyran Infernal Cohort with Hashutite Blades",
    "Scourge of Ghyran Infernal Cohort with Hashutite Spears": "Scourge of Ghyran Infernal Cohort with Hashutite Blades",
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
