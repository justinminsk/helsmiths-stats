from helsmith_stats.metrics import collect_scope_metrics, infer_models, total_models
from helsmith_stats.models import ListData, UnitData


def test_infer_models_handles_reinforced_and_default_sizes() -> None:
    assert infer_models("Bull Centaurs", 380) == 6
    assert infer_models("Bull Centaurs", 190) == 3
    assert infer_models("Anointed Sentinels", 300) == 6
    assert infer_models("Deathshrieker Rocket Battery", 140) == 1


def test_collect_scope_metrics_counts_presence_and_traits() -> None:
    lists_for_scope = [
        ListData(
            name="List 1",
            source="Singles",
            units=[
                UnitData(name="Bull Centaurs", points=380, models=6),
                UnitData(name="Deathshrieker Rocket Battery", points=140, models=1),
                UnitData(
                    name="Infernal Cohort with Hashutite Spears",
                    points=220,
                    models=20,
                    reinforced=True,
                ),
            ],
            traits=[
                "Scroll of Petrification",
                "An Eye for Weakness",
                "Overdrive Switch",
            ],
            subfaction="Industrial Polluters",
            manifestation_lore="Forbidden Power",
        ),
        ListData(
            name="List 2",
            source="Singles",
            units=[
                UnitData(name="Bull Centaurs", points=190, models=3),
                UnitData(name="Anointed Sentinels", points=150, models=3),
            ],
            traits=["An Eye for Weakness"],
            subfaction="Taar's Grand Forgehost",
            manifestation_lore="Aetherwrought Machineries",
        ),
    ]

    metrics = collect_scope_metrics(lists_for_scope)

    assert metrics.unit_entries["Bull Centaurs"] == 2
    assert metrics.unit_presence_lists["Bull Centaurs"] == 2
    assert metrics.model_counts["Bull Centaurs"] == 9
    assert metrics.artifacts["Scroll of Petrification"] == 1
    assert metrics.command_traits["An Eye for Weakness"] == 2
    assert metrics.warmachine_traits["Overdrive Switch"] == 1
    assert metrics.subfactions["Industrial Polluters"] == 1
    assert metrics.manifestation_lores["Forbidden Power"] == 1

    assert total_models(lists_for_scope[0].units) == 27
