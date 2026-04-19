export type ThemeTokenMap = Record<string, string>;

export type SiteUnit = {
  regiment: string;
  name: string;
  points: number;
  models: number;
  reinforced: boolean;
  notes: string[];
};

export type SiteList = {
  index: number;
  source: string;
  name: string;
  result: string;
  subfaction: string;
  manifestationLore: string;
  regiments: number;
  unitEntries: number;
  models: number;
  units: SiteUnit[];
};

export type StatsTable = {
  key: string;
  title: string;
  headers: string[];
  rows: string[][];
};

export type ScopePayload = {
  key: string;
  label: string;
  datasetKey: string;
  listCount: number;
  reportLinks: {
    stats: string;
    lists: string;
  };
  statsSummary: string;
  filters: {
    results: string[];
    subfactions: string[];
  };
  statsTables: StatsTable[];
  lists: SiteList[];
};

export type DatasetPayload = {
  key: string;
  label: string;
  reportBasePath: string;
  scopes: ScopePayload[];
};

export type SiteDataPayload = {
  generatedAt: string;
  defaultDatasetKey: string;
  scopeOrder: string[];
  scopeLabels: Record<string, string>;
  uiConfig: Record<string, string | number>;
  themeTokens: {
    dark: ThemeTokenMap;
    light: ThemeTokenMap;
  };
  datasets: DatasetPayload[];
};

function invariant(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new Error(message);
  }
}

export function assertSiteDataPayload(payload: unknown): SiteDataPayload {
  invariant(payload && typeof payload === 'object', 'Site data payload must be an object.');

  const candidate = payload as Partial<SiteDataPayload>;
  invariant(typeof candidate.generatedAt === 'string', 'Site data payload must include generatedAt.');
  invariant(
    typeof candidate.defaultDatasetKey === 'string',
    'Site data payload must include defaultDatasetKey.'
  );
  invariant(Array.isArray(candidate.scopeOrder), 'Site data payload must include scopeOrder.');
  invariant(candidate.scopeLabels && typeof candidate.scopeLabels === 'object', 'Site data payload must include scopeLabels.');
  invariant(candidate.uiConfig && typeof candidate.uiConfig === 'object', 'Site data payload must include uiConfig.');
  invariant(
    candidate.themeTokens &&
      typeof candidate.themeTokens === 'object' &&
      typeof candidate.themeTokens.dark === 'object' &&
      typeof candidate.themeTokens.light === 'object',
    'Site data payload must include dark and light theme tokens.'
  );
  invariant(Array.isArray(candidate.datasets), 'Site data payload must include datasets.');

  return candidate as SiteDataPayload;
}
