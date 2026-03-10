from datetime import datetime, timezone

from helsmith_stats import pipeline


class FixedDateTime:
    @classmethod
    def now(cls):
        return datetime(2026, 3, 10, 16, 30, 0, tzinfo=timezone.utc)


def test_update_readme_run_date_replaces_existing_marker(tmp_path, monkeypatch) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        "# Title\n\nIntro\n- Last run date: old\n\nBody\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(pipeline, "README_FILE", readme)
    monkeypatch.setattr(pipeline, "datetime", FixedDateTime)

    pipeline.update_readme_run_date()

    updated = readme.read_text(encoding="utf-8")
    assert "- Last run date: 2026-03-10" in updated
    assert "- Last run date: old" not in updated


def test_update_readme_run_date_inserts_marker_when_missing(
    tmp_path, monkeypatch
) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        "# Title\n\nIntro\n\nBody\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(pipeline, "README_FILE", readme)
    monkeypatch.setattr(pipeline, "datetime", FixedDateTime)

    pipeline.update_readme_run_date()

    lines = readme.read_text(encoding="utf-8").splitlines()
    assert lines[3].startswith("- Last run date: 2026-03-10")
