import csv
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from helsmith_stats import web


def _write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)


def _write_scope_fixture(base_dir: Path, scope: str) -> None:
    scope_dir = base_dir / scope
    _write_csv(
        scope_dir / "list_level_summary.csv",
        [
            "source",
            "name",
            "result",
            "subfaction",
            "manifestation_lore",
            "unit_entries",
            "models",
            "units",
        ],
        [
            [
                "Singles",
                f"{scope.title()} List A",
                "5-0",
                "Taar's Grand Forgehost",
                "Forbidden Power",
                "3",
                "10",
                '[{"regiment":"General\'s Regiment","name":"Bull Centaurs","points":380,"models":6,"reinforced":true,"notes":["General"]}]',
            ],
            [
                "Teams",
                f"{scope.title()} List B",
                "4-1",
                "Industrial Polluters",
                "Aetherwrought Machineries",
                "2",
                "7",
                '[{"regiment":"Regiment 1","name":"Deathshrieker Rocket Battery","points":140,"models":1,"reinforced":false,"notes":[]}]',
            ],
        ],
    )
    _write_csv(
        scope_dir / "unit_presence_percent.csv",
        ["unit_name", "lists_with_unit", "percent_of_lists"],
        [["Bull Centaurs", "1", "50.0"]],
    )
    _write_csv(
        scope_dir / "subfaction_counts.csv",
        ["subfaction", "list_count"],
        [["Taar's Grand Forgehost", "1"]],
    )
    _write_csv(
        scope_dir / "manifestation_lore_counts.csv",
        ["manifestation_lore", "list_count"],
        [["Forbidden Power", "1"]],
    )
    _write_csv(
        scope_dir / "artifact_counts.csv",
        ["artifact", "count"],
        [["Scroll of Petrification", "1"]],
    )
    _write_csv(
        scope_dir / "command_trait_counts.csv",
        ["command_trait", "count"],
        [["An Eye for Weakness", "1"]],
    )
    _write_csv(
        scope_dir / "warmachine_trait_counts.csv",
        ["warmachine_trait", "count"],
        [["Overdrive Switch", "1"]],
    )
    _write_csv(
        scope_dir / "unit_entry_counts.csv",
        ["unit_name", "unit_entries"],
        [["Bull Centaurs", "1"]],
    )
    _write_csv(
        scope_dir / "unit_model_counts.csv",
        ["unit_name", "model_count"],
        [["Bull Centaurs", "6"]],
    )
    _write_csv(
        scope_dir / "unplayed_units.csv",
        ["unit_name", "unit_size"],
        [["Anointed Sentinels", "3"]],
    )


def _write_reports_fixture(base_dir: Path) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    for scope in web.SCOPES:
        (base_dir / f"{scope}.md").write_text(
            f"# {scope} report\n",
            encoding="utf-8",
        )
        (base_dir / f"{scope}-lists.md").write_text(
            f"# {scope} lists report\n",
            encoding="utf-8",
        )


def _configure_test_workspace(tmp_path: Path, monkeypatch) -> Path:
    root = tmp_path / "repo"
    docs_dir = root / "docs"
    summaries_dir = root / "summaries"
    reports_dir = root / "reports"
    history_root = root / "history"
    frontend_dir = root / "frontend"

    for scope in web.SCOPES:
        _write_scope_fixture(summaries_dir, scope)
    _write_reports_fixture(reports_dir)

    for snapshot_name in (
        "2026-04-17-pre-points",
        "2026-04-10-pre-points",
        "2026-04-03-pre-points",
        "2026-03-27-pre-points",
    ):
        snapshot_dir = history_root / snapshot_name
        for scope in web.SCOPES:
            _write_scope_fixture(snapshot_dir / "summaries", scope)
        _write_reports_fixture(snapshot_dir / "reports")

    monkeypatch.setattr(web, "ROOT", root)
    monkeypatch.setattr(web, "DOCS_DIR", docs_dir)
    monkeypatch.setattr(web, "SUMMARIES_DIR", summaries_dir)
    monkeypatch.setattr(web, "REPORTS_DIR", reports_dir)
    monkeypatch.setattr(web, "FRONTEND_DIR", frontend_dir)
    monkeypatch.setattr(web, "FRONTEND_DIST_DIR", frontend_dir / "dist")

    return root


def _stub_frontend_build(monkeypatch, root: Path) -> None:
    def fake_build_frontend_site() -> None:
        dist_dir = root / "frontend" / "dist"
        (dist_dir / "assets").mkdir(parents=True, exist_ok=True)
        (dist_dir / "index.html").write_text(
            '<!doctype html><html><body><div id="root"></div></body></html>\n',
            encoding="utf-8",
        )
        (dist_dir / "assets" / "bundle.js").write_text(
            "console.log('react');\n",
            encoding="utf-8",
        )
        web._publish_frontend_dist(dist_dir)

    monkeypatch.setattr(web, "_build_frontend_site", fake_build_frontend_site)


def _build_test_site(tmp_path: Path, monkeypatch) -> tuple[Path, str]:
    root = _configure_test_workspace(tmp_path, monkeypatch)
    _stub_frontend_build(monkeypatch, root)
    web.build_web_page()
    return root, (root / "docs" / "index.html").read_text(encoding="utf-8")


def _build_test_payload(tmp_path: Path, monkeypatch) -> dict[str, object]:
    _configure_test_workspace(tmp_path, monkeypatch)
    return web.build_site_payload("2026-04-19 12:00:00 UTC")


def test_stats_summary_text_surfaces_all_top_fields() -> None:
    text = web._stats_summary_text(
        result_rows=[["5-0", "10"]],
        presence_rows=[["Bull Centaurs", "8", "80.0%"]],
        subfaction_rows=[["Taar's Grand Forgehost", "6"]],
        unit_model_rows=[["Infernal Cohort with Hashutite Spears", "40"]],
    )
    assert "5-0" in text
    assert "Bull Centaurs" in text
    assert "Taar's Grand Forgehost" in text
    assert "Infernal Cohort with Hashutite Spears" in text


def test_stats_summary_text_empty_returns_fallback() -> None:
    text = web._stats_summary_text(
        result_rows=[],
        presence_rows=[],
        subfaction_rows=[],
        unit_model_rows=[],
    )
    assert "No summary insights" in text


def test_discover_datasets_includes_current_plus_three_newest_snapshots(
    tmp_path, monkeypatch
) -> None:
    root = tmp_path / "repo"
    history_root = root / "history"
    history_root.mkdir(parents=True)
    for name in (
        "2026-04-17-pre-points",
        "2026-04-10-pre-points",
        "2026-04-03-pre-points",
        "2026-03-27-pre-points",
    ):
        (history_root / name).mkdir()

    monkeypatch.setattr(web, "ROOT", root)
    monkeypatch.setattr(web, "SUMMARIES_DIR", root / "summaries")
    monkeypatch.setattr(web, "REPORTS_DIR", root / "reports")

    datasets = web._discover_datasets()

    assert [dataset["key"] for dataset in datasets] == [
        "current",
        "archive-2026-04-17-pre-points",
        "archive-2026-04-10-pre-points",
        "archive-2026-04-03-pre-points",
    ]


def test_build_site_payload_contains_frontend_contract_metadata(
    tmp_path, monkeypatch
) -> None:
    payload = _build_test_payload(tmp_path, monkeypatch)

    assert payload["generatedAt"] == "2026-04-19 12:00:00 UTC"
    assert payload["defaultDatasetKey"] == "current"
    assert payload["scopeOrder"] == ["combined", "singles", "teams"]
    assert payload["scopeLabels"] == web.SCOPE_LABELS
    assert payload["uiConfig"] == web.UI_CONFIG
    assert payload["themeTokens"] == web.THEME_TOKENS


def test_build_site_payload_contains_dataset_scope_and_list_details(
    tmp_path, monkeypatch
) -> None:
    payload = _build_test_payload(tmp_path, monkeypatch)

    assert len(payload["datasets"]) == 4
    current_dataset = payload["datasets"][0]
    assert current_dataset["key"] == "current"
    assert current_dataset["label"] == "Current"
    assert current_dataset["reportBasePath"] == "reports/current"

    combined_scope = current_dataset["scopes"][0]
    assert combined_scope["key"] == "combined"
    assert combined_scope["label"] == "Combined"
    assert combined_scope["datasetKey"] == "current"
    assert combined_scope["reportLinks"] == {
        "stats": "reports/current/combined.md",
        "lists": "reports/current/combined-lists.md",
    }
    assert combined_scope["filters"] == {
        "results": ["4-1", "5-0"],
        "subfactions": ["Industrial Polluters", "Taar's Grand Forgehost"],
    }
    assert combined_scope["statsTables"][0]["key"] == "resultBreakdown"
    assert combined_scope["statsTables"][0]["rows"] == [["4-1", "1"], ["5-0", "1"]]

    first_list = combined_scope["lists"][0]
    assert first_list["name"] == "Combined List A"
    assert first_list["regiments"] == 1
    assert first_list["unitEntries"] == 3
    assert first_list["models"] == 10
    assert first_list["units"][0]["name"] == "Bull Centaurs"
    assert first_list["units"][0]["reinforced"] is True
    assert first_list["units"][0]["notes"] == ["General"]


def test_publish_frontend_dist_preserves_reports_and_site_data(
    tmp_path, monkeypatch
) -> None:
    docs_dir = tmp_path / "docs"
    reports_path = docs_dir / "reports" / "current" / "combined.md"
    site_data_path = docs_dir / "data" / "site-data.json"
    dist_dir = tmp_path / "frontend" / "dist"

    reports_path.parent.mkdir(parents=True, exist_ok=True)
    reports_path.write_text("# report\n", encoding="utf-8")
    site_data_path.parent.mkdir(parents=True, exist_ok=True)
    site_data_path.write_text('{"ok": true}\n', encoding="utf-8")
    dist_dir.mkdir(parents=True, exist_ok=True)
    (dist_dir / "index.html").write_text(
        "<html><body><div id='root'></div></body></html>\n", encoding="utf-8"
    )
    (dist_dir / "assets").mkdir(parents=True, exist_ok=True)
    (dist_dir / "assets" / "app.js").write_text(
        "console.log('frontend');\n", encoding="utf-8"
    )

    monkeypatch.setattr(web, "DOCS_DIR", docs_dir)

    web._publish_frontend_dist(dist_dir)

    assert (docs_dir / "index.html").exists()
    assert (docs_dir / "assets" / "app.js").exists()
    assert reports_path.exists()
    assert site_data_path.exists()


def test_build_frontend_site_raises_on_failed_build(tmp_path, monkeypatch) -> None:
    root = _configure_test_workspace(tmp_path, monkeypatch)
    (root / "frontend").mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(web, "_resolve_npm_command", lambda: ["npm"])
    monkeypatch.setattr(
        web.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=1, stderr="boom", stdout=""),
    )

    with pytest.raises(
        RuntimeError, match="Frontend build failed while publishing docs: boom"
    ):
        web._build_frontend_site()


def test_build_web_page_requires_frontend_build_tooling(tmp_path, monkeypatch) -> None:
    root = _configure_test_workspace(tmp_path, monkeypatch)
    monkeypatch.setattr(web, "_resolve_npm_command", lambda: None)

    with pytest.raises(RuntimeError, match="Frontend publishing requires npm"):
        web.build_web_page()

    assert (root / "docs" / "reports" / "current" / "combined.md").exists()
    assert (root / "docs" / "data" / "site-data.json").exists()


def test_build_web_page_publishes_frontend_output_and_supporting_files(
    tmp_path, monkeypatch
) -> None:
    root, html = _build_test_site(tmp_path, monkeypatch)

    assert '<div id="root"></div>' in html
    assert (root / "docs" / "assets" / "bundle.js").exists()
    assert (root / "docs" / "reports" / "current" / "combined.md").exists()
    assert (
        root / "docs" / "reports" / "archive-2026-04-17-pre-points" / "teams.md"
    ).exists()
    assert (root / "docs" / "data" / "site-data.json").exists()

    payload = json.loads(
        (root / "docs" / "data" / "site-data.json").read_text(encoding="utf-8")
    )
    assert (
        payload["datasets"][0]["scopes"][0]["reportLinks"]["stats"]
        == "reports/current/combined.md"
    )
