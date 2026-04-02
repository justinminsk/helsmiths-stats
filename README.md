# Helsmith stats

[![Python tests](https://github.com/justinminsk/helsmiths-stats/actions/workflows/tests.yml/badge.svg)](https://github.com/justinminsk/helsmiths-stats/actions/workflows/tests.yml)

Small repo for parsing Helsmiths of Hashut event lists and generating readable summaries.

- Last run date: 2026-04-02 17:58:16 Mountain Daylight Time

## What lives where

- [Helsmiths 5-0s.md](Helsmiths%205-0s.md): source document with Singles and Teams lists
- [analyze_helsmith_lists.py](analyze_helsmith_lists.py): thin runner entrypoint
- [helsmith_stats](helsmith_stats): modular parsing/stats package
- [reports/combined.md](reports/combined.md): combined Markdown report
- [reports/singles.md](reports/singles.md): singles-only Markdown report
- [reports/teams.md](reports/teams.md): teams-only Markdown report
- [docs/index.html](docs/index.html): generated static dashboard for GitHub Pages
- [summaries/combined](summaries/combined): combined CSV outputs
- [summaries/singles](summaries/singles): singles-only CSV outputs
- [summaries/teams](summaries/teams): teams-only CSV outputs

## Generated outputs per scope

Each scope folder under [summaries](summaries) contains:

- `list_level_summary.csv`
- `unit_entry_counts.csv`
- `unit_model_counts.csv`
- `unit_presence_percent.csv`
- `unplayed_units.csv`
- `subfaction_counts.csv`
- `manifestation_lore_counts.csv`
- `artifact_counts.csv`
- `command_trait_counts.csv`
- `warmachine_trait_counts.csv`

## Workflow

1. Update [Helsmiths 5-0s.md](Helsmiths%205-0s.md)
2. Run the parser:
	- `python analyze_helsmith_lists.py`
3. Read the outputs in [reports](reports) and [summaries](summaries)

## Historical snapshots

- Pre-points-change data has been archived at [history/2026-04-02-pre-points](history/2026-04-02-pre-points).
- The active source file [Helsmiths 5-0s.md](Helsmiths%205-0s.md) is reset for the new points era starting 2026-04-06.
- Future runs will overwrite root [reports](reports), [summaries](summaries), and [docs](docs), while archived snapshots remain unchanged.

For future points rollovers, use the helper script:

- `python rollover_snapshot.py --label 2026-07-01-pre-points --start-date 2026-07-07`
- Preview first (no file changes): `python rollover_snapshot.py --label 2026-07-01-pre-points --start-date 2026-07-07 --dry-run`

This command archives the current [Helsmiths 5-0s.md](Helsmiths%205-0s.md), [reports](reports), [summaries](summaries), and [docs](docs) into `history/<label>/`, then resets [Helsmiths 5-0s.md](Helsmiths%205-0s.md) to a clean template.

## Web dashboard + hosting

- Running `python analyze_helsmith_lists.py` also rebuilds [docs/index.html](docs/index.html).
- The dashboard shows **Current** plus up to the 3 newest archived snapshots from [history](history).
- Local preview: open [docs/index.html](docs/index.html) in a browser.
- GitHub Pages deploy is handled by [.github/workflows/pages.yml](.github/workflows/pages.yml).
- In GitHub repo settings, set **Pages** source to **GitHub Actions** (one-time).
- After push to `main`, your site will be available at:
	- `https://<your-github-username>.github.io/helsmiths-stats/`

## Linting (pre-commit)

1. Install dev dependencies:
	- `python -m pip install -r requirements-dev.txt`
2. Install git hooks:
	- `pre-commit install`
3. Run linting on all files anytime:
	- `pre-commit run --all-files`

The same pre-commit checks run in GitHub Actions before tests.

## Python modules

- [helsmith_stats/constants.py](helsmith_stats/constants.py): regexes, paths, and lookup tables
- [helsmith_stats/models.py](helsmith_stats/models.py): typed dataclasses
- [helsmith_stats/normalization.py](helsmith_stats/normalization.py): text normalization helpers
- [helsmith_stats/parser.py](helsmith_stats/parser.py): Markdown list parsing
- [helsmith_stats/metrics.py](helsmith_stats/metrics.py): metric calculations and model inference
- [helsmith_stats/reporting.py](helsmith_stats/reporting.py): Markdown report generation
- [helsmith_stats/writers.py](helsmith_stats/writers.py): CSV/report output writers
- [helsmith_stats/pipeline.py](helsmith_stats/pipeline.py): end-to-end orchestration

## Notes

- The script normalizes a few known naming/export quirks.
- Model counts are inferred from unit size and point-cost patterns in the source lists.
- The repo is organized so the root stays focused on the source file, the parser, and this README.
