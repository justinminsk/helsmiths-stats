from helsmith_stats.parser import parse_lists


def test_parse_lists_handles_sources_aliases_and_traits() -> None:
    markdown = """
# **Singles**
##### 4-1

**List A 2000/2000 pts**
Helsmiths of Hashut | Taar's Grand Forgehost
Manifestation Lore - Forbidden Power (20 Points)
General's Regiment
Urak Taar, the First Daemonsmith (350)
• General
Rocket battery because anointed suck (140)
Scourge of Ghyran Cohort with Hashutite Spears (220)
• Ruthless Oversser
Created with Warhammer Age of Sigmar: The App

# **Teams**
##### 5-0

**List B 2000/2000 pts**
Grand Alliance Chaos | Helsmiths of Hashut | Industrial Polluters
Manifestation Lore - Aetherwrought Machineries
General's Regiment
Daemonsmith on Infernal Taurus (290)
Anointed Sentinels (300)
Created with Warhammer Age of Sigmar: The App
"""

    parsed = parse_lists(markdown)

    assert len(parsed) == 2

    singles = parsed[0]
    assert singles.source == "Singles"
    assert singles.result_bucket == "4-1"
    assert singles.subfaction == "Taar's Grand Forgehost"
    assert singles.manifestation_lore == "Forbidden Power"
    assert ("Deathshrieker Rocket Battery", 140) in singles.units
    assert (
        "Scourge of Ghyran Infernal Cohort with Hashutite Blades",
        220,
    ) in singles.units
    assert "Ruthless Overseer" in singles.traits

    teams = parsed[1]
    assert teams.source == "Teams"
    assert teams.result_bucket == "5-0"
    assert teams.subfaction == "Industrial Polluters"
    assert teams.manifestation_lore == "Aetherwrought Machineries"
    assert ("Anointed Sentinels", 300) in teams.units
