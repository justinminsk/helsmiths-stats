from helsmith_stats.models import ListData, UnitData
from helsmith_stats.reporting import build_lists_report


def test_build_lists_report_includes_unit_details() -> None:
    lists_for_scope = [
        ListData(
            name="List A",
            source="Singles",
            result_bucket="4-1",
            subfaction="Taar's Grand Forgehost",
            manifestation_lore="Forbidden Power",
            units=[
                UnitData(
                    name="Urak Taar, the First Daemonsmith",
                    points=350,
                    models=1,
                    regiment="General's Regiment",
                    notes=["General"],
                ),
                UnitData(
                    name="Bull Centaurs",
                    points=380,
                    models=6,
                    regiment="Regiment 1",
                    reinforced=True,
                ),
            ],
        )
    ]

    report = build_lists_report("Singles", lists_for_scope)

    assert "# Helsmith lists - Singles" in report
    assert "## List A" in report
    assert "### General's Regiment" in report
    assert "### Regiment 1" in report
    assert (
        "Urak Taar, the First Daemonsmith - 350 pts - 1 models - notes: General"
        in report
    )
    assert "Bull Centaurs - 380 pts - 6 models - reinforced" in report
