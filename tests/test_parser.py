from helsmith_stats.parser import parse_lists


def test_parse_lists_handles_sources_aliases_and_traits() -> None:
    markdown = """
# **Singles**
### April 6-12
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
### April 13-19
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
    assert singles.week_label == "April 6-12"
    assert singles.result_bucket == "4-1"
    assert singles.subfaction == "Taar's Grand Forgehost"
    assert singles.manifestation_lore == "Forbidden Power"
    deathshrieker = next(
        unit for unit in singles.units if unit.name == "Deathshrieker Rocket Battery"
    )
    assert deathshrieker.points == 140
    assert deathshrieker.regiment == "General's Regiment"

    cohort = next(
        unit
        for unit in singles.units
        if unit.name == "Scourge of Ghyran Infernal Cohort with Hashutite Blades"
    )
    assert cohort.points == 220
    assert cohort.reinforced is True
    assert cohort.notes == ["Ruthless Overseer"]
    assert "Ruthless Overseer" in singles.traits

    teams = parsed[1]
    assert teams.source == "Teams"
    assert teams.week_label == "April 13-19"
    assert teams.result_bucket == "5-0"
    assert teams.subfaction == "Industrial Polluters"
    assert teams.manifestation_lore == "Aetherwrought Machineries"
    sentinels = next(unit for unit in teams.units if unit.name == "Anointed Sentinels")
    assert sentinels.points == 300
    assert sentinels.models == 6
