import { useEffect, useId, useRef, useState } from 'react';
import type { DatasetPayload, ScopePayload, SiteDataPayload } from '../../models/siteData';
import { buildHash, getInitialRoute, type DashboardRoute } from '../../lib/dashboard/routing';
import {
  compareLists,
  defaultVisibleColumns,
  filterLists,
  getNumericColumnIndexes,
  listColumns,
  type ListColumnKey,
  type ListSortKey,
} from '../../lib/dashboard/lists';
import { applyThemeTokens, getInitialTheme, storeTheme, type ThemeMode } from '../../lib/theme/theme';
import { ScopeStatsView } from './ScopeStatsView';
import { ScopeListsView } from './ScopeListsView';

type DashboardProps = {
  payload: SiteDataPayload;
};

export function Dashboard({ payload }: DashboardProps) {
  const [route, setRoute] = useState<DashboardRoute>(() => getInitialRoute(payload));
  const [theme, setTheme] = useState<ThemeMode>(() => getInitialTheme(payload.uiConfig.themeStorageKey as string));
  const [search, setSearch] = useState('');
  const [resultFilter, setResultFilter] = useState('');
  const [subfactionFilter, setSubfactionFilter] = useState('');
  const [sortKey, setSortKey] = useState<ListSortKey>('default');
  const [visibleCount, setVisibleCount] = useState(Number(payload.uiConfig.listRowsBatchSize));
  const [visibleColumns, setVisibleColumns] = useState<Record<ListColumnKey, boolean>>(defaultVisibleColumns);
  const [copied, setCopied] = useState(false);
  const datasetNavId = useId();
  const scopeNavId = useId();
  const viewNavId = useId();
  const copiedTimerRef = useRef<number | null>(null);

  const dataset =
    payload.datasets.find((candidate) => candidate.key === route.datasetKey) ?? payload.datasets[0];
  const scope =
    dataset.scopes.find((candidate) => candidate.key === route.scopeKey) ?? dataset.scopes[0];

  const filteredLists = filterLists(scope.lists, {
    search,
    result: resultFilter,
    subfaction: subfactionFilter,
  }).sort((left, right) => compareLists(left, right, sortKey));

  const visibleLists = filteredLists.slice(0, visibleCount);
  const canLoadMore = filteredLists.length > visibleLists.length;
  const activeColumns = listColumns.filter((column) => visibleColumns[column.key]);
  const contextLabel = `${dataset.label} > ${scope.label} > ${route.viewKey === 'lists' ? 'Lists' : 'Stats'}`;

  useEffect(() => {
    applyThemeTokens(payload.themeTokens, theme);
    document.documentElement.setAttribute('data-theme', theme);
    storeTheme(payload.uiConfig.themeStorageKey as string, theme);
  }, [payload.themeTokens, payload.uiConfig, theme]);

  useEffect(() => {
    const onHashChange = () => {
      setRoute(getInitialRoute(payload));
    };

    window.addEventListener('hashchange', onHashChange);
    return () => {
      window.removeEventListener('hashchange', onHashChange);
    };
  }, [payload]);

  useEffect(() => {
    setVisibleCount(Number(payload.uiConfig.listRowsBatchSize));
    setSearch('');
    setResultFilter('');
    setSubfactionFilter('');
    setSortKey('default');
    setVisibleColumns(defaultVisibleColumns);
  }, [payload.uiConfig, route.datasetKey, route.scopeKey]);

  useEffect(() => {
    const nextHash = buildHash(payload.uiConfig.hashPrefix as string, route);
    if (window.location.hash !== nextHash) {
      window.location.hash = nextHash;
    }
  }, [payload.uiConfig, route]);

  useEffect(() => {
    return () => {
      if (copiedTimerRef.current !== null) {
        window.clearTimeout(copiedTimerRef.current);
      }
    };
  }, []);

  const numericColumnIndexes = getNumericColumnIndexes(activeColumns);

  function updateRoute(nextRoute: DashboardRoute) {
    setRoute(nextRoute);
  }

  async function handleCopyLink() {
    const url = `${window.location.origin}${window.location.pathname}${buildHash(payload.uiConfig.hashPrefix as string, route)}`;
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      if (copiedTimerRef.current !== null) {
        window.clearTimeout(copiedTimerRef.current);
      }
      copiedTimerRef.current = window.setTimeout(() => setCopied(false), 1200);
    } catch {
      window.prompt('Copy this link:', url);
    }
  }

  function setDataset(nextDataset: DatasetPayload) {
    updateRoute({
      datasetKey: nextDataset.key,
      scopeKey: nextDataset.scopes[0]?.key ?? payload.scopeOrder[0],
      viewKey: route.viewKey,
    });
  }

  function setScope(nextScope: ScopePayload) {
    updateRoute({
      datasetKey: dataset.key,
      scopeKey: nextScope.key,
      viewKey: route.viewKey,
    });
  }

  function setView(viewKey: DashboardRoute['viewKey']) {
    updateRoute({
      datasetKey: dataset.key,
      scopeKey: scope.key,
      viewKey,
    });
  }

  function toggleTheme() {
    setTheme((currentTheme) => (currentTheme === 'dark' ? 'light' : 'dark'));
  }

  function toggleColumn(columnKey: ListColumnKey) {
    setVisibleColumns((current) => ({
      ...current,
      [columnKey]: !current[columnKey],
    }));
  }

  return (
    <section className="dashboard" aria-label="Helsmith stats dashboard">
      <div className="dashboard-toolbar">
        <nav aria-label="Dataset navigation" className="tab-row" role="tablist" id={datasetNavId}>
          {payload.datasets.map((candidate) => {
            const isActive = candidate.key === dataset.key;
            return (
              <button
                key={candidate.key}
                aria-controls={`dataset-panel-${candidate.key}`}
                aria-selected={isActive}
                className={`tab-pill${isActive ? ' is-active' : ''}`}
                onClick={() => setDataset(candidate)}
                role="tab"
                type="button"
              >
                {candidate.label}
              </button>
            );
          })}
        </nav>

        <div className="dashboard-actions">
          <button className={`action-pill${copied ? ' is-copied' : ''}`} onClick={handleCopyLink} type="button">
            {copied ? 'Copied' : 'Copy view link'}
          </button>
          <button className="action-pill" onClick={toggleTheme} type="button">
            Theme: {theme === 'dark' ? 'Dark' : 'Light'}
          </button>
        </div>
      </div>

      <p className="context-bar" aria-live="polite">
        {contextLabel}
      </p>

      <section className="dataset-panel" id={`dataset-panel-${dataset.key}`} role="tabpanel">
        <header className="dataset-header">
          <div>
            <h2 className="section-title">{dataset.label}</h2>
            <p className="dataset-meta">Generated: {payload.generatedAt}</p>
          </div>
        </header>

        <nav aria-label={`${dataset.label} scope tabs`} className="tab-row tab-row--secondary" role="tablist" id={scopeNavId}>
          {dataset.scopes.map((candidate) => {
            const isActive = candidate.key === scope.key;
            return (
              <button
                key={candidate.key}
                aria-controls={`scope-panel-${dataset.key}-${candidate.key}`}
                aria-selected={isActive}
                className={`tab-pill${isActive ? ' is-active' : ''}`}
                onClick={() => setScope(candidate)}
                role="tab"
                type="button"
              >
                {candidate.label}
              </button>
            );
          })}
        </nav>

        <section className="scope-panel" id={`scope-panel-${dataset.key}-${scope.key}`} role="tabpanel">
          <header className="scope-header">
            <div>
              <h3 className="section-title section-title--scope">{scope.label}</h3>
              <p className="scope-meta">Lists parsed: {scope.listCount}</p>
            </div>
          </header>

          <nav aria-label={`${scope.label} view tabs`} className="tab-row tab-row--tertiary" role="tablist" id={viewNavId}>
            {(['stats', 'lists'] as const).map((viewKey) => {
              const isActive = route.viewKey === viewKey;
              return (
                <button
                  key={viewKey}
                  aria-controls={`scope-view-${dataset.key}-${scope.key}-${viewKey}`}
                  aria-selected={isActive}
                  className={`tab-pill${isActive ? ' is-active' : ''}`}
                  onClick={() => setView(viewKey)}
                  role="tab"
                  type="button"
                >
                  {viewKey === 'stats' ? 'Stats' : 'Lists'}
                </button>
              );
            })}
          </nav>

          {route.viewKey === 'stats' ? (
            <ScopeStatsView datasetKey={dataset.key} scope={scope} />
          ) : (
            <ScopeListsView
              activeColumns={activeColumns}
              canLoadMore={canLoadMore}
              datasetKey={dataset.key}
              numericColumnIndexes={numericColumnIndexes}
              onColumnToggle={toggleColumn}
              onLoadMore={() =>
                setVisibleCount((current) => current + Number(payload.uiConfig.listRowsBatchSize))
              }
              onResultFilterChange={setResultFilter}
              onSearchChange={setSearch}
              onSortChange={setSortKey}
              onSubfactionFilterChange={setSubfactionFilter}
              resultFilter={resultFilter}
              scope={scope}
              search={search}
              sortKey={sortKey}
              subfactionFilter={subfactionFilter}
              visibleColumns={visibleColumns}
              visibleLists={visibleLists}
              totalMatchingLists={filteredLists.length}
            />
          )}
        </section>
      </section>
    </section>
  );
}