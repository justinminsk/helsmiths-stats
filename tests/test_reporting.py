from helsmith_stats.models import ListData, UnitData
from helsmith_stats.reporting import build_lists_report
from helsmith_stats.weeks import (
    parse_week_label,
    week_label_identity,
    week_label_sort_key,
)


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
    assert "- Week: Unspecified" in report
    assert "### General's Regiment" in report
    assert "### Regiment 1" in report
    assert (
        "Urak Taar, the First Daemonsmith - 350 pts - 1 models - notes: General"
        in report
    )
    assert "Bull Centaurs - 380 pts - 6 models - reinforced" in report


def test_build_lists_report_orders_lists_by_week_label() -> None:
    lists_for_scope = [
        ListData(name="Late", source="Singles", week_label="April 20-26"),
        ListData(name="Early", source="Singles", week_label="April 6-12"),
        ListData(name="Unknown", source="Singles", week_label=""),
    ]

    report = build_lists_report("Combined", lists_for_scope)

    assert report.index("## Early") < report.index("## Late")
    assert report.index("## Late") < report.index("## Unknown")
    assert "- Week: April 6-12" in report
    assert "- Week: Unspecified" in report


def test_week_helpers_parse_identity_and_sort_key() -> None:
    assert parse_week_label("April 6-12") == (4, 6, 12)
    assert parse_week_label("Jan 1") == (1, 1, 1)
    assert week_label_identity("April 6-12") == "04-06-12"
    assert week_label_identity("Custom") == "custom"
    assert week_label_sort_key("April 6-12") < week_label_sort_key("April 20-26")
    assert week_label_sort_key("April 20-26") < week_label_sort_key("")
