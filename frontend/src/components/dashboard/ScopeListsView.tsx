import type { ListColumn, ListColumnKey, ListSortKey } from '../../lib/dashboard/lists';
import type { ScopePayload, SiteList } from '../../models/siteData';

type ScopeListsViewProps = {
  activeColumns: ListColumn[];
  canLoadMore: boolean;
  datasetKey: string;
  numericColumnIndexes: number[];
  onColumnToggle: (columnKey: ListColumnKey) => void;
  onLoadMore: () => void;
  onResultFilterChange: (value: string) => void;
  onSearchChange: (value: string) => void;
  onSortChange: (value: ListSortKey) => void;
  onSubfactionFilterChange: (value: string) => void;
  resultFilter: string;
  scope: ScopePayload;
  search: string;
  sortKey: ListSortKey;
  subfactionFilter: string;
  totalMatchingLists: number;
  visibleColumns: Record<ListColumnKey, boolean>;
  visibleLists: SiteList[];
};

export function ScopeListsView({
  activeColumns,
  canLoadMore,
  datasetKey,
  numericColumnIndexes,
  onColumnToggle,
  onLoadMore,
  onResultFilterChange,
  onSearchChange,
  onSortChange,
  onSubfactionFilterChange,
  resultFilter,
  scope,
  search,
  sortKey,
  subfactionFilter,
  totalMatchingLists,
  visibleColumns,
  visibleLists,
}: ScopeListsViewProps) {
  return (
    <section
      aria-labelledby={`scope-view-${datasetKey}-${scope.key}-lists`}
      className="scope-view"
      id={`scope-view-${datasetKey}-${scope.key}-lists`}
      role="tabpanel"
    >
      <p className="view-link-row">
        <a className="scope-link" href={scope.reportLinks.lists}>
          Open markdown report
        </a>
      </p>

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
          <summary>Columns</summary>
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

      <p aria-live="polite" className="list-meta-row">
        {totalMatchingLists > 0
          ? `Showing ${visibleLists.length} of ${totalMatchingLists} matching lists.`
          : 'No lists match the current filters.'}
      </p>

      <div className="table-scroll-wrap">
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
                    <td className={numericColumnIndexes.includes(index) ? 'numeric-col' : ''} key={column.key}>
                      {value}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {canLoadMore ? (
        <div className="load-more-row">
          <button className="action-pill" onClick={onLoadMore} type="button">
            Load more lists
          </button>
        </div>
      ) : null}

      <div className="list-card-grid">
        {visibleLists.map((list) => (
          <article className="list-card" key={`card-${scope.key}-${list.index}`}>
            <header className="list-card__header">
              <h4 className="list-card__title">{list.name}</h4>
              <span className="list-card__tag">
                {list.source} · {list.result}
              </span>
            </header>
            <p className="list-card__meta">
              Subfaction: {list.subfaction} · Lore: {list.manifestationLore} · Regiments: {list.regiments} · Unit entries: {list.unitEntries} · Models: {list.models}
            </p>

            <div className="table-scroll-wrap">
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
                      <td>{unit.regiment || '—'}</td>
                      <td>{unit.name}</td>
                      <td className="numeric-col">{unit.points}</td>
                      <td className="numeric-col">{unit.models}</td>
                      <td>{unit.reinforced ? 'Yes' : 'No'}</td>
                      <td>{unit.notes.length > 0 ? unit.notes.join(' · ') : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
