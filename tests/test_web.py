from helsmith_stats import web


# ---------------------------------------------------------------------------
# _render_table
# ---------------------------------------------------------------------------


def test_render_table_escapes_html_content() -> None:
    rows = [["<script>alert(1)</script>", "99"]]
    html = web._render_table("Title", ["Name", "Count"], rows)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_render_table_shows_placeholder_when_empty() -> None:
    html = web._render_table("Title", ["Name", "Count"], [])
    assert "—" in html


def test_render_table_has_sr_only_caption() -> None:
    html = web._render_table("My Table", ["A", "B"], [["x", "1"]])
    assert 'class="sr-only"' in html
    assert "My Table" in html


# ---------------------------------------------------------------------------
# _stats_summary_text
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# build_web_page — integration / regression
# ---------------------------------------------------------------------------


def test_build_web_page_dark_mode_color_tokens(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(web, "DOCS_DIR", tmp_path / "docs")
    web.build_web_page()
    html = (tmp_path / "docs" / "index.html").read_text(encoding="utf-8")

    assert "--color-bg: #0f0b08" in html
    assert "--color-surface: #181009" in html
    assert "--color-border: #5e4225" in html
    assert "--color-accent: #c8921a" in html
    assert "--color-accent-strong: #dcaa32" in html
    assert "--color-focus: #00c8a8" in html
    assert "--color-teal: #00c8a8" in html
    assert "--color-magenta: #c84090" in html


def test_build_web_page_light_mode_color_tokens(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(web, "DOCS_DIR", tmp_path / "docs")
    web.build_web_page()
    html = (tmp_path / "docs" / "index.html").read_text(encoding="utf-8")

    assert "--color-bg: #f9f4ee" in html
    assert "--color-accent: #7a4e0e" in html
    assert "--color-focus: #006e5a" in html
    assert "--color-teal: #007a68" in html
    assert "--color-magenta: #a0306e" in html


def test_build_web_page_html_structure(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(web, "DOCS_DIR", tmp_path / "docs")
    web.build_web_page()
    html = (tmp_path / "docs" / "index.html").read_text(encoding="utf-8")

    assert "<!doctype html>" in html
    assert "<main" in html
    assert 'role="tab"' in html
    assert 'role="tabpanel"' in html
    assert 'class="sr-only"' in html
    assert "aria-controls=" in html
