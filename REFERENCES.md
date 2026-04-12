# Helsmith Stats References

## Hashut Palette Research (2026 Batch 8)

Visual cues used for the current "fun but readable" faction palette:

- Obsidian/coal base for armor and industrial massing.
- Brass/bronze + ember highlights for forged-metal identity.
- Arcane teal/cyan for magical energy, weapon glows, and supernatural effects (prominent in all official artwork).
- Hashut Magenta for banners, cloth wrappings, and champion regalia.
- Fire/ash accents for heat, glow, and icon emphasis.
- Bone/ash neutrals for readable text against heavy warm surfaces.

Documented palette swatches (research-derived motif set):

- Obsidian: `#0F0B08`
- Soot: `#0C0807`
- Forge Bronze: `#5E4225`
- Brass Glow: `#C8921A`
- Bright Ember: `#DCAA32`
- Cinder Red-Brown: `#6B4A34`
- Arcane Teal (arcane effects / weapon glow): `#00C8A8`
- Hashut Magenta (banners / cloth): `#C84090`
- Ash Parchment (light bg family): `#F9F4EE`
- Scribed Bronze Ink (light text family): `#2E2118`

Dashboard token mapping now used in `helsmith_stats/web.py`:

- Dark mode core: `--color-bg #0f0b08`, `--color-surface #181009`, `--color-border #5e4225`, `--color-accent #c8921a`, `--color-text #fff7ef`, `--color-focus #00c8a8`
- Light mode core: `--color-bg #f9f4ee`, `--color-surface #ffffff`, `--color-border #ddc8b5`, `--color-accent #7a4e0e`, `--color-text #2e2118`, `--color-focus #006e5a`

Theme switching behavior:

- Toggle button in UI switches light/dark manually.
- Initial theme still follows system preference when no manual choice exists.

## Web References

- WCAG 2.2 Quick Reference: https://www.w3.org/WAI/WCAG22/quickref/
- Use of Color criterion: https://www.w3.org/WAI/WCAG22/quickref/#use-of-color
- Reflow criterion: https://www.w3.org/WAI/WCAG22/quickref/#reflow
- W3C ARIA Table pattern: https://www.w3.org/WAI/ARIA/apg/patterns/table/
- W3C ARIA Grid/Table properties: https://www.w3.org/WAI/ARIA/apg/practices/grid-and-table-properties/
- W3C complex images guidance: https://www.w3.org/WAI/tutorials/images/complex/