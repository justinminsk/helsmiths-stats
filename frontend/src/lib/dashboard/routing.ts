import type { SiteDataPayload } from '../../models/siteData';

export type DashboardRoute = {
  datasetKey: string;
  scopeKey: string;
  viewKey: 'stats' | 'trends' | 'lists' | 'submit';
};

const dashboardViews = new Set<DashboardRoute['viewKey']>(['stats', 'trends', 'lists', 'submit']);

export function buildHash(hashPrefix: string, route: DashboardRoute) {
  return `${hashPrefix}${route.datasetKey}|${route.scopeKey}|${route.viewKey}`;
}

export function getInitialRoute(payload: SiteDataPayload): DashboardRoute {
  const fallbackDataset =
    payload.datasets.find((candidate) => candidate.key === payload.defaultDatasetKey) ?? payload.datasets[0];
  const fallbackScope = fallbackDataset?.scopes[0];
  const defaultRoute: DashboardRoute = {
    datasetKey: fallbackDataset?.key ?? payload.defaultDatasetKey,
    scopeKey: fallbackScope?.key ?? payload.scopeOrder[0],
    viewKey: 'stats',
  };

  const hashPrefix = String(payload.uiConfig.hashPrefix ?? '#tab=');
  const hash = window.location.hash;
  if (!hash.startsWith(hashPrefix)) {
    return defaultRoute;
  }

  const parts = hash.slice(hashPrefix.length).split('|');
  if (parts.length < 2 || parts.length > 3) {
    return defaultRoute;
  }

  const [datasetKey, scopeKey, rawViewKey] = parts;
  const viewKey = dashboardViews.has(rawViewKey as DashboardRoute['viewKey'])
    ? (rawViewKey as DashboardRoute['viewKey'])
    : 'stats';
  const dataset = payload.datasets.find((candidate) => candidate.key === datasetKey);
  if (!dataset) {
    return defaultRoute;
  }

  const scope = dataset.scopes.find((candidate) => candidate.key === scopeKey);
  if (!scope) {
    return {
      datasetKey: dataset.key,
      scopeKey: dataset.scopes[0]?.key ?? defaultRoute.scopeKey,
      viewKey,
    };
  }

  return {
    datasetKey: dataset.key,
    scopeKey: scope.key,
    viewKey,
  };
}
