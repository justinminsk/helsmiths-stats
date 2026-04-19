import type { SiteDataPayload } from '../models/siteData';

export const sampleSiteData: SiteDataPayload = {
  generatedAt: '2026-04-19 12:00:00 UTC',
  defaultDatasetKey: 'current',
  scopeOrder: ['combined', 'singles', 'teams'],
  scopeLabels: {
    combined: 'Combined',
    singles: 'Singles',
    teams: 'Teams',
  },
  uiConfig: {
    hashPrefix: '#tab=',
    listRowsBatchSize: 20,
    listFilterInputDebounceMs: 140,
    themeStorageKey: 'helsmithTheme',
    maxArchivedSnapshots: 3,
  },
  themeTokens: {
    dark: {
      colorBg: '#0f0b08',
      colorAccent: '#c8921a',
      colorTeal: '#00c8a8',
      colorMagenta: '#c84090',
    },
    light: {
      colorBg: '#f9f4ee',
      colorAccent: '#7a4e0e',
      colorTeal: '#007a68',
      colorMagenta: '#a0306e',
    },
  },
  datasets: [
    {
      key: 'current',
      label: 'Current',
      reportBasePath: 'reports/current',
      scopes: [
        {
          key: 'combined',
          label: 'Combined',
          datasetKey: 'current',
          listCount: 12,
          reportLinks: {
            stats: 'reports/current/combined.md',
            lists: 'reports/current/combined-lists.md',
          },
          statsSummary:
            'Most common result is 5-0 (6 lists). Top unit presence is Bull Centaurs in 8 lists (66.7%).',
          filters: {
            results: ['4-1', '5-0'],
            subfactions: ['Industrial Polluters', "Taar's Grand Forgehost"],
          },
          statsTables: [
            {
              key: 'resultBreakdown',
              title: 'Result breakdown',
              headers: ['Result', 'Lists'],
              rows: [
                ['5-0', '6'],
                ['4-1', '6'],
              ],
            },
          ],
          lists: [
            {
              index: 0,
              source: 'Singles',
              name: 'Sample List',
              result: '5-0',
              subfaction: "Taar's Grand Forgehost",
              manifestationLore: 'Forbidden Power',
              regiments: 1,
              unitEntries: 3,
              models: 10,
              units: [
                {
                  regiment: "General's Regiment",
                  name: 'Bull Centaurs',
                  points: 380,
                  models: 6,
                  reinforced: true,
                  notes: ['General'],
                },
              ],
            },
          ],
        },
        {
          key: 'singles',
          label: 'Singles',
          datasetKey: 'current',
          listCount: 1,
          reportLinks: {
            stats: 'reports/current/singles.md',
            lists: 'reports/current/singles-lists.md',
          },
          statsSummary: 'Singles summary.',
          filters: {
            results: ['5-0'],
            subfactions: ["Taar's Grand Forgehost"],
          },
          statsTables: [],
          lists: [],
        },
        {
          key: 'teams',
          label: 'Teams',
          datasetKey: 'current',
          listCount: 0,
          reportLinks: {
            stats: 'reports/current/teams.md',
            lists: 'reports/current/teams-lists.md',
          },
          statsSummary: 'Teams summary.',
          filters: {
            results: [],
            subfactions: [],
          },
          statsTables: [],
          lists: [],
        },
      ],
    },
    {
      key: 'archive-2026-04-02-pre-points',
      label: 'Snapshot (2026-04-02-pre-points)',
      reportBasePath: 'reports/archive-2026-04-02-pre-points',
      scopes: [
        {
          key: 'combined',
          label: 'Combined',
          datasetKey: 'archive-2026-04-02-pre-points',
          listCount: 1,
          reportLinks: {
            stats: 'reports/archive-2026-04-02-pre-points/combined.md',
            lists: 'reports/archive-2026-04-02-pre-points/combined-lists.md',
          },
          statsSummary: 'Archived summary.',
          filters: {
            results: ['4-1'],
            subfactions: ['Industrial Polluters'],
          },
          statsTables: [],
          lists: [],
        },
        {
          key: 'singles',
          label: 'Singles',
          datasetKey: 'archive-2026-04-02-pre-points',
          listCount: 0,
          reportLinks: {
            stats: 'reports/archive-2026-04-02-pre-points/singles.md',
            lists: 'reports/archive-2026-04-02-pre-points/singles-lists.md',
          },
          statsSummary: 'Archived singles summary.',
          filters: {
            results: [],
            subfactions: [],
          },
          statsTables: [],
          lists: [],
        },
        {
          key: 'teams',
          label: 'Teams',
          datasetKey: 'archive-2026-04-02-pre-points',
          listCount: 0,
          reportLinks: {
            stats: 'reports/archive-2026-04-02-pre-points/teams.md',
            lists: 'reports/archive-2026-04-02-pre-points/teams-lists.md',
          },
          statsSummary: 'Archived teams summary.',
          filters: {
            results: [],
            subfactions: [],
          },
          statsTables: [],
          lists: [],
        },
      ],
    },
  ],
};