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
          story: {
            coreSignals: [
              {
                label: 'Top subfaction',
                value: "Taar's Grand Forgehost",
                detail: '7 of 12 lists',
              },
              {
                label: 'Top manifestation lore',
                value: 'Forbidden Power',
                detail: '5 of 12 lists',
              },
              {
                label: 'Most shared unit',
                value: 'Urak Taar, the First Daemonsmith',
                detail: '12 of 12 lists (100.0%)',
              },
            ],
            sharedUnits: [
              {
                name: 'Urak Taar, the First Daemonsmith',
                listCount: 12,
                share: '100.0%',
              },
              {
                name: 'Bull Centaurs',
                listCount: 8,
                share: '66.7%',
              },
            ],
            sharedUnitPairs: [
              {
                units: ['Urak Taar, the First Daemonsmith', 'Bull Centaurs'],
                listCount: 8,
                share: '66.7%',
              },
            ],
            weeklyTrends: [
              {
                metric: 'Unit presence',
                label: 'Bull Centaurs',
                currentValue: '100.0%',
                deltaLabel: '+50.0 pts versus April 6-12',
                direction: 'up',
                points: [
                  {
                    datasetKey: 'week-1',
                    datasetLabel: 'April 6-12',
                    eraLabel: 'Pre-points era',
                    value: '50.0%',
                  },
                  {
                    datasetKey: 'week-2',
                    datasetLabel: 'April 13-19',
                    eraLabel: 'Pre-points era',
                    value: '75.0%',
                  },
                  {
                    datasetKey: 'week-3',
                    datasetLabel: 'April 20-26',
                    eraLabel: 'Post-points era',
                    value: '100.0%',
                  },
                ],
              },
            ],
            snapshotTrends: [
              {
                metric: 'Unit presence',
                label: 'Bull Centaurs',
                currentValue: '66.7%',
                deltaLabel: '+16.7 pts versus Snapshot (2026-04-03-pre-points)',
                direction: 'up',
                points: [
                  {
                    datasetKey: 'archive-2026-04-03-pre-points',
                    datasetLabel: 'Snapshot (2026-04-03-pre-points)',
                    value: '50.0%',
                  },
                  {
                    datasetKey: 'archive-2026-04-10-pre-points',
                    datasetLabel: 'Snapshot (2026-04-10-pre-points)',
                    value: '58.3%',
                  },
                  {
                    datasetKey: 'archive-2026-04-17-pre-points',
                    datasetLabel: 'Snapshot (2026-04-17-pre-points)',
                    value: '66.7%',
                  },
                  {
                    datasetKey: 'current',
                    datasetLabel: 'Current',
                    value: '66.7%',
                  },
                ],
              },
            ],
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
            {
              key: 'topUnitsByPresence',
              title: 'Top units by list presence',
              headers: ['Unit', 'Lists', '% of lists'],
              rows: [
                ['Urak Taar, the First Daemonsmith', '12', '100.0%'],
                ['Bull Centaurs', '8', '66.7%'],
                ['Deathshrieker Rocket Battery', '7', '58.3%'],
              ],
            },
            {
              key: 'manifestationLoreCounts',
              title: 'Manifestation lore counts',
              headers: ['Lore', 'Lists'],
              rows: [
                ['Forbidden Power', '5'],
                ['Aetherwrought Machineries', '4'],
                ['Primal Energy', '3'],
              ],
            },
            {
              key: 'topUnitEntries',
              title: 'Top unit entries',
              headers: ['Unit', 'Entries'],
              rows: [
                ['Infernal Cohort with Hashutite Spears', '15'],
                ['Bull Centaurs', '8'],
                ['Deathshrieker Rocket Battery', '7'],
              ],
            },
            {
              key: 'topModelCounts',
              title: 'Top model counts',
              headers: ['Unit', 'Models'],
              rows: [
                ['Infernal Cohort with Hashutite Spears', '220'],
                ['Bull Centaurs', '48'],
                ['Deathshrieker Rocket Battery', '7'],
              ],
            },
            {
              key: 'topSubfactions',
              title: 'Top subfactions',
              headers: ['Subfaction', 'Lists'],
              rows: [
                ["Taar's Grand Forgehost", '7'],
                ['Industrial Polluters', '5'],
              ],
            },
            {
              key: 'unplayedUnits',
              title: 'Unplayed units',
              headers: ['Unit'],
              rows: [
                ['Infernal Razers with Flamehurlers'],
                ['War Despot'],
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
                {
                  regiment: "General's Regiment",
                  name: 'Urak Taar, the First Daemonsmith',
                  points: 320,
                  models: 1,
                  reinforced: false,
                  notes: ['General'],
                },
                {
                  regiment: 'Auxiliary',
                  name: 'Deathshrieker Rocket Battery',
                  points: 140,
                  models: 1,
                  reinforced: false,
                  notes: [],
                },
              ],
            },
            {
              index: 1,
              source: 'Singles',
              name: 'Ashen Pressure',
              result: '5-0',
              subfaction: "Taar's Grand Forgehost",
              manifestationLore: 'Forbidden Power',
              regiments: 2,
              unitEntries: 5,
              models: 24,
              units: [
                {
                  regiment: "General's Regiment",
                  name: 'Urak Taar, the First Daemonsmith',
                  points: 320,
                  models: 1,
                  reinforced: false,
                  notes: ['General'],
                },
                {
                  regiment: "General's Regiment",
                  name: 'Infernal Cohort with Hashutite Spears',
                  points: 200,
                  models: 20,
                  reinforced: true,
                  notes: [],
                },
                {
                  regiment: 'Artillery',
                  name: 'Deathshrieker Rocket Battery',
                  points: 140,
                  models: 1,
                  reinforced: false,
                  notes: [],
                },
              ],
            },
            {
              index: 2,
              source: 'Teams',
              name: 'Industrial Anvils',
              result: '4-1',
              subfaction: 'Industrial Polluters',
              manifestationLore: 'Aetherwrought Machineries',
              regiments: 2,
              unitEntries: 6,
              models: 28,
              units: [
                {
                  regiment: "General's Regiment",
                  name: 'Daemonsmith',
                  points: 150,
                  models: 1,
                  reinforced: false,
                  notes: ['General'],
                },
                {
                  regiment: "General's Regiment",
                  name: 'Infernal Cohort with Hashutite Blades',
                  points: 180,
                  models: 10,
                  reinforced: true,
                  notes: [],
                },
                {
                  regiment: 'Support',
                  name: 'Hobgrotz Vandalz',
                  points: 90,
                  models: 10,
                  reinforced: false,
                  notes: [],
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
