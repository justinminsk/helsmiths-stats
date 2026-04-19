import type { ListColumn, ListColumnKey, ListSortKey } from '../../lib/dashboard/lists';
import type { ScopePayload, SiteList } from '../../models/siteData';

type WinnerOverviewStat = {
  eyebrow: string;
  value: string;
  title: string;
  detail: string;
};

type WinnerResultTierCount = {
  result: string;
  count: number;
  tone: 'strong' | 'supporting';
};

type ScopeListsViewProps = {
  controls: {
    activeControlTags: string[];
    hasCustomListControls: boolean;
    resultFilter: string;
    search: string;
    sortKey: ListSortKey;
    subfactionFilter: string;
    totalColumnCount: number;
    visibleColumns: Record<ListColumnKey, boolean>;
    visibleColumnCount: number;
  };
  controlActions: {
    onColumnToggle: (columnKey: ListColumnKey) => void;
    onResetListControls: () => void;
    onResultFilterChange: (value: string) => void;
    onSearchChange: (value: string) => void;
    onSortChange: (value: ListSortKey) => void;
    onSubfactionFilterChange: (value: string) => void;
  };
  datasetKey: string;
  results: {
    activeColumns: ListColumn[];
    canLoadMore: boolean;
    numericColumnIndexes: number[];
    onLoadMore: () => void;
    totalMatchingLists: number;
    visibleLists: SiteList[];
  };
  scope: ScopePayload;
  tabId: string;
};

export function ScopeListsView({
  controls,
  controlActions,
  datasetKey,
  results,
  scope,
  tabId,
}: ScopeListsViewProps) {
  const {
    activeControlTags,
    hasCustomListControls,
    resultFilter,
    search,
    sortKey,
    subfactionFilter,
    totalColumnCount,
    visibleColumns,
    visibleColumnCount,
  } = controls;
  const {
    activeColumns,
    canLoadMore,
    numericColumnIndexes,
    onLoadMore,
    totalMatchingLists,
    visibleLists,
  } = results;
  const {
    onColumnToggle,
    onResetListControls,
    onResultFilterChange,
    onSearchChange,
    onSortChange,
    onSubfactionFilterChange,
  } = controlActions;
  const hasResults = totalMatchingLists > 0;
  const winnerOverviewStats = buildWinnerOverviewStats(visibleLists);
  const resultTierCounts = buildResultTierCounts(visibleLists);
  const winnerCards = buildWinnerGlanceCards(visibleLists);
  const hasTierComparison = resultTierCounts.length > 1;

  return (
    <section
      aria-labelledby={tabId}
      className="scope-view scope-view--lists"
      id={`scope-view-${datasetKey}-${scope.key}-lists`}
      role="tabpanel"
    >
      <header className="view-header view-header--lists">
        <div>
          <p className="view-kicker">List explorer</p>
          <h4 className="view-title">Compare individual lists</h4>
          <p className="view-description">Filter the current scope, inspect composition, and keep the markdown list report close by.</p>
        </div>
        <p className="view-link-row">
          <a className="scope-link" href={scope.reportLinks.lists}>
            Open markdown report
          </a>
        </p>
      </header>

      <section className="lists-tools-panel">
        <header className="subsection-header subsection-header--compact">
          <div>
            <p className="subsection-kicker">Filters</p>
            <h5 className="subsection-title">Narrow the visible list pool</h5>
          </div>
          <p aria-live="polite" className="subsection-meta">
            {hasResults
              ? `Showing ${visibleLists.length} of ${totalMatchingLists} matching lists.`
              : 'No lists match the current filters.'}
          </p>
        </header>

        <div className="lists-toolbar">
          <label className="field field--search">
            <span>Search lists</span>
            <input
              className="field-control"
              onChange={(event) => onSearchChange(event.target.value)}
              placeholder="Search source, name, or unit"
              type="search"
              value={search}
            />
          </label>

          <label className="field">
            <span>Result</span>
            <select className="field-control" onChange={(event) => onResultFilterChange(event.target.value)} value={resultFilter}>
              <option value="">All results</option>
              {scope.filters.results.map((result) => (
                <option key={result} value={result}>
                  {result}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Subfaction</span>
            <select
              className="field-control"
              onChange={(event) => onSubfactionFilterChange(event.target.value)}
              value={subfactionFilter}
            >
              <option value="">All subfactions</option>
              {scope.filters.subfactions.map((subfaction) => (
                <option key={subfaction} value={subfaction}>
                  {subfaction}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Sort</span>
            <select className="field-control" onChange={(event) => onSortChange(event.target.value as ListSortKey)} value={sortKey}>
              <option value="default">Original order</option>
              <option value="regiments-desc">Regiments (high to low)</option>
              <option value="regiments-asc">Regiments (low to high)</option>
              <option value="models-desc">Models (high to low)</option>
              <option value="models-asc">Models (low to high)</option>
              <option value="entries-desc">Unit entries (high to low)</option>
              <option value="entries-asc">Unit entries (low to high)</option>
              <option value="name-asc">Name (A-Z)</option>
            </select>
          </label>

          <details className="field field--columns">
            <summary>Columns ({visibleColumnCount}/{totalColumnCount})</summary>
            <div className="column-toggle-list">
              {Object.entries(visibleColumns).map(([columnKey, visible]) => (
                <label className="column-toggle" key={columnKey}>
                  <input checked={visible} onChange={() => onColumnToggle(columnKey as ListColumnKey)} type="checkbox" />
                  <span>{activeColumns.find((column) => column.key === columnKey)?.label ?? columnKey}</span>
                </label>
              ))}
            </div>
          </details>
        </div>

        <div className="list-control-summary">
          <div className="list-control-summary__tags" aria-live="polite">
            {activeControlTags.length > 0 ? (
              activeControlTags.map((tag) => (
                <span className="filter-chip" key={tag}>
                  {tag}
                </span>
              ))
            ) : (
              <p className="list-control-summary__hint">Using default filters, sort order, and visible columns.</p>
            )}
          </div>

          {hasCustomListControls ? (
            <button className="action-pill action-pill--subtle" onClick={onResetListControls} type="button">
              Reset all list controls
            </button>
          ) : null}
        </div>
      </section>

      {hasResults ? (
        <>
          <section className="data-surface winners-overview-section">
            <header className="subsection-header subsection-header--compact">
              <div>
                <p className="subsection-kicker">Winning lists</p>
                <h5 className="subsection-title">Scan the current winner pool</h5>
              </div>
              <p className="subsection-meta">
                All lists here are winners. Use record tiers as a supporting lens, not the main story.
              </p>
            </header>

            <div className="winners-overview-layout">
              <div className="winner-overview-stat-grid">
                {winnerOverviewStats.map((stat) => (
                  <article className="winner-overview-stat" key={`${stat.eyebrow}-${stat.title}`}>
                    <p className="winner-overview-stat__eyebrow">{stat.eyebrow}</p>
                    <h5 className="winner-overview-stat__value">{stat.value}</h5>
                    <p className="winner-overview-stat__title">{stat.title}</p>
                    <p className="winner-overview-stat__detail">{stat.detail}</p>
                  </article>
                ))}
              </div>

              <section className="winner-result-tier-panel" aria-label="Winning record tiers">
                <header className="winner-result-tier-panel__header">
                  <p className="winner-result-tier-panel__eyebrow">Record tiers</p>
                  <h5 className="winner-result-tier-panel__title">How the current winner pool is split</h5>
                </header>

                <div className="winner-result-tier-strip">
                  {resultTierCounts.map((tier) => (
                    <article
                      className={`winner-result-tier-pill winner-result-tier-pill--${tier.tone}`}
                      key={`${tier.result}-${tier.count}`}
                    >
                      <p className="winner-result-tier-pill__result">{tier.result}</p>
                      <p className="winner-result-tier-pill__count">{tier.count} list{tier.count === 1 ? '' : 's'}</p>
                    </article>
                  ))}
                </div>

                <p className="winner-result-tier-panel__note">
                  {hasTierComparison
                    ? 'Keep 5-0 vs 4-1 as a small comparison, not the main story.'
                    : 'The current filtered pool is concentrated in one record tier.'}
                </p>
              </section>
            </div>

            <div className="winner-glance-grid">
              {winnerCards.map(({ definingUnits, list }) => (
                <article className="winner-glance-card" key={`winner-glance-${scope.key}-${list.index}`}>
                  <header className="winner-glance-card__header">
                    <div className="winner-glance-card__copy">
                      <h6 className="winner-glance-card__title">{list.name}</h6>
                      <p className="winner-glance-card__meta">{list.source}</p>
                    </div>
                    <span className={`winner-glance-card__result winner-glance-card__result--${getResultTone(list.result)}`}>
                      {list.result}
                    </span>
                  </header>

                  <p className="winner-glance-card__identity">
                    {list.subfaction} · {list.manifestationLore}
                  </p>

                  <dl className="winner-glance-card__metrics">
                    <div>
                      <dt>Regiments</dt>
                      <dd>{list.regiments}</dd>
                    </div>
                    <div>
                      <dt>Entries</dt>
                      <dd>{list.unitEntries}</dd>
                    </div>
                    <div>
                      <dt>Models</dt>
                      <dd>{list.models}</dd>
                    </div>
                  </dl>

                  <div className="winner-glance-card__units" aria-label={`Defining units for ${list.name}`}>
                    {definingUnits.map((unit) => (
                      <span className="winner-unit-chip" key={`${list.index}-${unit}`}>
                        {unit}
                      </span>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="data-surface lists-table-section">
            <header className="subsection-header">
              <div>
                <p className="subsection-kicker">Table scan</p>
                <h5 className="subsection-title">Compare matching lists quickly</h5>
              </div>
              <p className="subsection-meta">{activeColumns.length} visible columns in the current table view.</p>
            </header>

            <div className="table-scroll-wrap table-scroll-wrap--framed">
              <table className="lists-table">
                <caption className="sr-only">Lists in this scope</caption>
                <thead>
                  <tr>
                    {activeColumns.map((column, index) => (
                      <th className={numericColumnIndexes.includes(index) ? 'numeric-col' : ''} key={column.key} scope="col">
                        {column.label}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {visibleLists.map((list) => (
                    <tr key={`${scope.key}-${list.index}`}>
                      {activeColumns.map((column, index) => {
                        const value = column.render(list);
                        return (
                          <td
                            className={numericColumnIndexes.includes(index) ? 'numeric-col' : ''}
                            data-label={column.label}
                            key={column.key}
                          >
                            {value}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="data-surface lists-card-section">
            <header className="subsection-header">
              <div>
                <p className="subsection-kicker">Card detail</p>
                <h5 className="subsection-title">Inspect each list composition</h5>
              </div>
              {canLoadMore ? (
                <button className="action-pill" onClick={onLoadMore} type="button">
                  Load more lists
                </button>
              ) : (
                <p className="subsection-meta">Showing all currently matching lists.</p>
              )}
            </header>

            <div className="list-card-grid">
              {visibleLists.map((list) => (
                <article className="list-card" key={`card-${scope.key}-${list.index}`}>
                  <header className="list-card__header">
                    <h4 className="list-card__title">{list.name}</h4>
                    <span className="list-card__tag">
                      {list.source} · {list.result}
                    </span>
                  </header>

                  <dl className="list-card__meta-grid">
                    <div className="list-card__meta-item">
                      <dt className="list-card__meta-label">Subfaction</dt>
                      <dd className="list-card__meta-value">{list.subfaction}</dd>
                    </div>
                    <div className="list-card__meta-item">
                      <dt className="list-card__meta-label">Lore</dt>
                      <dd className="list-card__meta-value">{list.manifestationLore}</dd>
                    </div>
                    <div className="list-card__meta-item">
                      <dt className="list-card__meta-label">Regiments</dt>
                      <dd className="list-card__meta-value">{list.regiments}</dd>
                    </div>
                    <div className="list-card__meta-item">
                      <dt className="list-card__meta-label">Entries</dt>
                      <dd className="list-card__meta-value">{list.unitEntries}</dd>
                    </div>
                    <div className="list-card__meta-item">
                      <dt className="list-card__meta-label">Models</dt>
                      <dd className="list-card__meta-value">{list.models}</dd>
                    </div>
                  </dl>

                  <div className="table-scroll-wrap table-scroll-wrap--framed">
                    <table className="unit-table">
                      <caption className="sr-only">Units for {list.name}</caption>
                      <thead>
                        <tr>
                          <th scope="col">Regiment</th>
                          <th scope="col">Unit</th>
                          <th className="numeric-col" scope="col">
                            Pts
                          </th>
                          <th className="numeric-col" scope="col">
                            Models
                          </th>
                          <th scope="col">Reinforced</th>
                          <th scope="col">Notes</th>
                        </tr>
                      </thead>
                      <tbody>
                        {list.units.map((unit, unitIndex) => (
                          <tr key={`${list.index}-${unit.name}-${unitIndex}`}>
                            <td data-label="Regiment">{unit.regiment || '—'}</td>
                            <td data-label="Unit">{unit.name}</td>
                            <td className="numeric-col" data-label="Pts">{unit.points}</td>
                            <td className="numeric-col" data-label="Models">{unit.models}</td>
                            <td data-label="Reinforced">{unit.reinforced ? 'Yes' : 'No'}</td>
                            <td data-label="Notes">{unit.notes.length > 0 ? unit.notes.join(' · ') : '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="unit-mobile-list" aria-label={`Units for ${list.name}`}>
                    {list.units.map((unit, unitIndex) => (
                      <article className="unit-mobile-card" key={`mobile-${list.index}-${unit.name}-${unitIndex}`}>
                        <header className="unit-mobile-card__header">
                          <p className="unit-mobile-card__regiment">{unit.regiment || 'Unassigned regiment'}</p>
                          <h5 className="unit-mobile-card__title">{unit.name}</h5>
                        </header>

                        <dl className="unit-mobile-card__meta-grid">
                          <div className="unit-mobile-card__meta-item">
                            <dt className="unit-mobile-card__label">Pts</dt>
                            <dd className="unit-mobile-card__value">{unit.points}</dd>
                          </div>
                          <div className="unit-mobile-card__meta-item">
                            <dt className="unit-mobile-card__label">Models</dt>
                            <dd className="unit-mobile-card__value">{unit.models}</dd>
                          </div>
                          <div className="unit-mobile-card__meta-item">
                            <dt className="unit-mobile-card__label">Reinforced</dt>
                            <dd className="unit-mobile-card__value">{unit.reinforced ? 'Yes' : 'No'}</dd>
                          </div>
                        </dl>

                        <p className="unit-mobile-card__notes">
                          <span className="unit-mobile-card__label">Notes</span>
                          <span className="unit-mobile-card__notes-value">
                            {unit.notes.length > 0 ? unit.notes.join(' · ') : '—'}
                          </span>
                        </p>
                      </article>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          </section>
        </>
      ) : (
        <section className="empty-state">
          <p className="subsection-kicker">No matching lists</p>
          <h5 className="empty-state__title">Adjust the current filters</h5>
          <p className="empty-state__body">Try clearing the search, result, or subfaction filters to bring lists back into view.</p>
          {hasCustomListControls ? (
            <div className="empty-state__actions">
              <button className="action-pill" onClick={onResetListControls} type="button">
                Reset all list controls
              </button>
            </div>
          ) : null}
        </section>
      )}
    </section>
  );
}

function buildWinnerOverviewStats(lists: SiteList[]): WinnerOverviewStat[] {
  if (lists.length === 0) {
    return [];
  }

  const recordTiers = buildResultTierCounts(lists);
  const strongestTier = recordTiers[0];
  const topSubfaction = getMostCommonLabel(lists.map((list) => list.subfaction));
  const topLore = getMostCommonLabel(lists.map((list) => list.manifestationLore));
  const averageEntries = Math.round(lists.reduce((total, list) => total + list.unitEntries, 0) / lists.length);

  return [
    {
      eyebrow: 'Visible winners',
      value: `${lists.length}`,
      title: 'Lists in the current view',
      detail: 'Already winner-only data',
    },
    {
      eyebrow: 'Strongest finish',
      value: strongestTier?.result ?? '—',
      title: strongestTier ? `${strongestTier.count} list${strongestTier.count === 1 ? '' : 's'}` : 'No result data',
      detail: 'Best record in the current pool',
    },
    {
      eyebrow: 'Top subfaction',
      value: topSubfaction?.count ? `${topSubfaction.count}` : '—',
      title: topSubfaction?.label ?? 'No subfaction data',
      detail: 'Most common winning shell',
    },
    {
      eyebrow: 'Avg unit entries',
      value: `${averageEntries}`,
      title: topLore?.label ?? 'No lore data',
      detail: topLore ? 'Most common winning lore' : 'Filtered pool composition',
    },
  ];
}

function buildResultTierCounts(lists: SiteList[]): WinnerResultTierCount[] {
  const counts = new Map<string, number>();

  for (const list of lists) {
    counts.set(list.result, (counts.get(list.result) ?? 0) + 1);
  }

  return Array.from(counts.entries())
    .sort((left, right) => {
      const resultStrength = getResultRank(right[0]) - getResultRank(left[0]);
      if (resultStrength !== 0) {
        return resultStrength;
      }

      if (right[1] !== left[1]) {
        return right[1] - left[1];
      }

      return left[0].localeCompare(right[0]);
    })
    .map(([result, count], index) => ({
      count,
      result,
      tone: index === 0 ? 'strong' : 'supporting',
    }));
}

function buildWinnerGlanceCards(lists: SiteList[]) {
  return [...lists]
    .sort((left, right) => {
      const resultStrength = getResultRank(right.result) - getResultRank(left.result);
      if (resultStrength !== 0) {
        return resultStrength;
      }

      return left.name.localeCompare(right.name);
    })
    .map((list) => ({
      definingUnits: getDefiningUnits(list),
      list,
    }));
}

function getMostCommonLabel(values: string[]) {
  const counts = new Map<string, number>();

  for (const value of values) {
    counts.set(value, (counts.get(value) ?? 0) + 1);
  }

  return Array.from(counts.entries())
    .sort((left, right) => {
      if (right[1] !== left[1]) {
        return right[1] - left[1];
      }

      return left[0].localeCompare(right[0]);
    })
    .map(([label, count]) => ({ count, label }))[0] ?? null;
}

function getDefiningUnits(list: SiteList) {
  return Array.from(new Set(list.units.map((unit) => unit.name))).slice(0, 3);
}

function getResultRank(result: string) {
  const match = result.match(/^(\d+)-(\d+)$/);

  if (!match) {
    return -1;
  }

  const wins = Number(match[1]);
  const losses = Number(match[2]);
  return wins * 100 - losses;
}

function getResultTone(result: string) {
  return result === '5-0' ? 'strong' : 'supporting';
}
