import { useEffect, useId, useRef, useState } from 'react';
import type { DatasetPayload, ScopePayload, SiteDataPayload } from '../../models/siteData';
import { buildHash, getInitialRoute, type DashboardRoute } from '../../lib/dashboard/routing';
import {
  buildActiveControlTags,
  hasCustomListControls,
} from '../../lib/dashboard/controls';
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
  const [actionFeedback, setActionFeedback] = useState<string>('');
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
  const datasetTone = dataset.key === 'current' ? 'Current dataset' : 'Archive snapshot';
  const listBatchSize = Number(payload.uiConfig.listRowsBatchSize);
  const listControlSnapshot = {
    activeColumnCount: activeColumns.length,
    resultFilter,
    search,
    sortKey,
    subfactionFilter,
    totalColumnCount: listColumns.length,
    visibleColumns,
  };
  const hasCustomListControlState = hasCustomListControls(listControlSnapshot);
  const activeControlTags = buildActiveControlTags(listControlSnapshot);

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
    setVisibleCount(listBatchSize);
    setSearch('');
    setResultFilter('');
    setSubfactionFilter('');
    setSortKey('default');
    setVisibleColumns(defaultVisibleColumns);
  }, [listBatchSize, payload.uiConfig, route.datasetKey, route.scopeKey]);

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
  const datasetTabId = `${datasetNavId}-tab-${dataset.key}`;
  const scopeTabId = `${scopeNavId}-tab-${scope.key}`;
  const statsViewTabId = `${viewNavId}-tab-stats`;
  const listsViewTabId = `${viewNavId}-tab-lists`;

  function updateRoute(nextRoute: DashboardRoute) {
    setRoute(nextRoute);
  }

  function focusElementById(elementId: string) {
    document.getElementById(elementId)?.focus();
  }

  function handleTabKeyDown<TItem>(
    event: React.KeyboardEvent<HTMLButtonElement>,
    items: readonly TItem[],
    currentIndex: number,
    getId: (item: TItem) => string,
    onSelect: (item: TItem) => void
  ) {
    let nextIndex = currentIndex;

    switch (event.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        nextIndex = (currentIndex + 1) % items.length;
        break;
      case 'ArrowLeft':
      case 'ArrowUp':
        nextIndex = (currentIndex - 1 + items.length) % items.length;
        break;
      case 'Home':
        nextIndex = 0;
        break;
      case 'End':
        nextIndex = items.length - 1;
        break;
      default:
        return;
    }

    event.preventDefault();
    const nextItem = items[nextIndex];
    focusElementById(getId(nextItem));
    onSelect(nextItem);
  }

  async function handleCopyLink() {
    const url = `${window.location.origin}${window.location.pathname}${buildHash(payload.uiConfig.hashPrefix as string, route)}`;
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setActionFeedback('Shareable view link copied.');
      if (copiedTimerRef.current !== null) {
        window.clearTimeout(copiedTimerRef.current);
      }
      copiedTimerRef.current = window.setTimeout(() => {
        setCopied(false);
        setActionFeedback('');
      }, 1200);
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
    setTheme((currentTheme) => {
      const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
      setActionFeedback(`Switched to ${nextTheme} theme.`);
      return nextTheme;
    });
  }

  function toggleColumn(columnKey: ListColumnKey) {
    setVisibleColumns((current) => ({
      ...current,
      [columnKey]: !current[columnKey],
    }));
    setActionFeedback('Updated visible table columns.');
  }

  function handleSearchChange(value: string) {
    setSearch(value);
    setVisibleCount(listBatchSize);
  }

  function handleResultFilterChange(value: string) {
    setResultFilter(value);
    setVisibleCount(listBatchSize);
  }

  function handleSubfactionFilterChange(value: string) {
    setSubfactionFilter(value);
    setVisibleCount(listBatchSize);
  }

  function handleSortChange(value: ListSortKey) {
    setSortKey(value);
    setVisibleCount(listBatchSize);
  }

  function resetListControls() {
    setSearch('');
    setResultFilter('');
    setSubfactionFilter('');
    setSortKey('default');
    setVisibleColumns(defaultVisibleColumns);
    setVisibleCount(listBatchSize);
    setActionFeedback('Reset list controls to their default state.');
  }

  return (
    <section className="dashboard" aria-label="Helsmith stats dashboard">
      <div className="dashboard-toolbar">
        <section className="control-group control-group--primary">
          <p className="control-group__label">Datasets</p>
          <nav aria-label="Dataset navigation" className="tab-row tab-row--primary" role="tablist" id={datasetNavId}>
            {payload.datasets.map((candidate) => {
              const isActive = candidate.key === dataset.key;
              return (
                <button
                  key={candidate.key}
                  aria-controls={`dataset-panel-${candidate.key}`}
                  aria-selected={isActive}
                  className={`tab-pill${isActive ? ' is-active' : ''}`}
                  id={`${datasetNavId}-tab-${candidate.key}`}
                  onKeyDown={(event) =>
                    handleTabKeyDown(
                      event,
                      payload.datasets,
                      payload.datasets.findIndex((item) => item.key === candidate.key),
                      (item) => `${datasetNavId}-tab-${item.key}`,
                      setDataset
                    )
                  }
                  onClick={() => setDataset(candidate)}
                  role="tab"
                  tabIndex={isActive ? 0 : -1}
                  type="button"
                >
                  {candidate.label}
                </button>
              );
            })}
          </nav>
        </section>

        <section className="control-group control-group--actions">
          <p className="control-group__label">Actions</p>
          <div className="dashboard-actions">
            <button className={`action-pill${copied ? ' is-copied' : ''}`} onClick={handleCopyLink} type="button">
              {copied ? 'Copied view link' : 'Copy view link'}
            </button>
            <button
              aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
              aria-pressed={theme === 'dark'}
              className="action-pill"
              onClick={toggleTheme}
              type="button"
            >
              Theme: {theme === 'dark' ? 'Dark' : 'Light'}
            </button>
          </div>
          <p aria-live="polite" className="toolbar-feedback" role="status">
            {actionFeedback || 'Route updates stay synced to the URL as you switch datasets, scopes, and views.'}
          </p>
        </section>
      </div>

      <p className="context-bar" aria-live="polite">
        <span className="context-bar__label">Viewing</span>
        <span className="context-bar__value">{contextLabel}</span>
      </p>

      <section aria-labelledby={datasetTabId} className="dataset-panel" id={`dataset-panel-${dataset.key}`} role="tabpanel">
        <header className="dataset-header">
          <div className="dataset-header__content">
            <p className="section-kicker">{datasetTone}</p>
            <h2 className="section-title">{dataset.label}</h2>
            <p className="dataset-meta">
              Generated: {payload.generatedAt} · {dataset.scopes.length} scope{dataset.scopes.length === 1 ? '' : 's'}
            </p>
          </div>
        </header>

        <section className="panel-control-group">
          <p className="panel-control-group__label">Scope</p>
          <nav aria-label={`${dataset.label} scope tabs`} className="tab-row tab-row--secondary" role="tablist" id={scopeNavId}>
            {dataset.scopes.map((candidate) => {
              const isActive = candidate.key === scope.key;
              return (
                <button
                  key={candidate.key}
                  aria-controls={`scope-panel-${dataset.key}-${candidate.key}`}
                  aria-selected={isActive}
                  className={`tab-pill${isActive ? ' is-active' : ''}`}
                  id={`${scopeNavId}-tab-${candidate.key}`}
                  onKeyDown={(event) =>
                    handleTabKeyDown(
                      event,
                      dataset.scopes,
                      dataset.scopes.findIndex((item) => item.key === candidate.key),
                      (item) => `${scopeNavId}-tab-${item.key}`,
                      setScope
                    )
                  }
                  onClick={() => setScope(candidate)}
                  role="tab"
                  tabIndex={isActive ? 0 : -1}
                  type="button"
                >
                  {candidate.label}
                </button>
              );
            })}
          </nav>
        </section>

        <section aria-labelledby={scopeTabId} className="scope-panel" id={`scope-panel-${dataset.key}-${scope.key}`} role="tabpanel">
          <header className="scope-header">
            <div className="scope-header__content">
              <p className="section-kicker">Scope</p>
              <h3 className="section-title section-title--scope">{scope.label}</h3>
              <p aria-label={`Lists parsed: ${scope.listCount}`} className="scope-meta">
                Lists parsed: <span className="count-badge">{scope.listCount}</span>
              </p>
            </div>
          </header>

          <section className="panel-control-group panel-control-group--view">
            <p className="panel-control-group__label">View</p>
            <nav aria-label={`${scope.label} view tabs`} className="tab-row tab-row--tertiary" role="tablist" id={viewNavId}>
              {(['stats', 'lists'] as const).map((viewKey) => {
                const isActive = route.viewKey === viewKey;
                const tabId = `${viewNavId}-tab-${viewKey}`;
                return (
                  <button
                    key={viewKey}
                    aria-controls={`scope-view-${dataset.key}-${scope.key}-${viewKey}`}
                    aria-selected={isActive}
                    className={`tab-pill${isActive ? ' is-active' : ''}`}
                    id={tabId}
                    onKeyDown={(event) =>
                      handleTabKeyDown(
                        event,
                        ['stats', 'lists'] as const,
                        (['stats', 'lists'] as const).findIndex((item) => item === viewKey),
                        (item) => `${viewNavId}-tab-${item}`,
                        setView
                      )
                    }
                    onClick={() => setView(viewKey)}
                    role="tab"
                    tabIndex={isActive ? 0 : -1}
                    type="button"
                  >
                    {viewKey === 'stats' ? 'Stats' : 'Lists'}
                  </button>
                );
              })}
            </nav>
          </section>

          {route.viewKey === 'stats' ? (
            <ScopeStatsView datasetKey={dataset.key} scope={scope} tabId={statsViewTabId} />
          ) : (
            <ScopeListsView
              datasetKey={dataset.key}
              controls={{
                activeControlTags,
                hasCustomListControls: hasCustomListControlState,
                resultFilter,
                search,
                sortKey,
                subfactionFilter,
                totalColumnCount: listColumns.length,
                visibleColumns,
                visibleColumnCount: activeColumns.length,
              }}
              controlActions={{
                onColumnToggle: toggleColumn,
                onResetListControls: resetListControls,
                onResultFilterChange: handleResultFilterChange,
                onSearchChange: handleSearchChange,
                onSortChange: handleSortChange,
                onSubfactionFilterChange: handleSubfactionFilterChange,
              }}
              results={{
                activeColumns,
                canLoadMore,
                numericColumnIndexes,
                onLoadMore: () => setVisibleCount((current) => current + listBatchSize),
                totalMatchingLists: filteredLists.length,
                visibleLists,
              }}
              scope={scope}
              tabId={listsViewTabId}
            />
          )}
        </section>
      </section>
    </section>
  );
}
