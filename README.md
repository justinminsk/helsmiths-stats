# Helsmith stats

Small repo for parsing Helsmiths of Hashut event lists and generating readable summaries.

## What lives where

- [Helsmiths 5-0s.md](Helsmiths%205-0s.md): source document with Singles and Teams lists
- [analyze_helsmith_lists.py](analyze_helsmith_lists.py): parser and report generator
- [reports/combined.md](reports/combined.md): combined Markdown report
- [reports/singles.md](reports/singles.md): singles-only Markdown report
- [reports/teams.md](reports/teams.md): teams-only Markdown report
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

## Notes

- The script normalizes a few known naming/export quirks.
- Model counts are inferred from unit size and point-cost patterns in the source lists.
- The repo is organized so the root stays focused on the source file, the parser, and this README.
