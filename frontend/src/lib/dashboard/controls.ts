import {
  defaultVisibleColumns,
  listColumns,
  type ListColumnKey,
  type ListSortKey,
} from './lists';

export type ListControlsSnapshot = {
  activeColumnCount: number;
  resultFilter: string;
  search: string;
  sortKey: ListSortKey;
  subfactionFilter: string;
  totalColumnCount: number;
  visibleColumns: Record<ListColumnKey, boolean>;
};

export function hasCustomVisibleColumns(visibleColumns: Record<ListColumnKey, boolean>) {
  return listColumns.some(
    (column) => visibleColumns[column.key] !== defaultVisibleColumns[column.key]
  );
}

export function hasCustomListControls(snapshot: ListControlsSnapshot) {
  return (
    snapshot.search.trim().length > 0 ||
    snapshot.resultFilter.length > 0 ||
    snapshot.subfactionFilter.length > 0 ||
    snapshot.sortKey !== 'default' ||
    hasCustomVisibleColumns(snapshot.visibleColumns)
  );
}

export function buildActiveControlTags(snapshot: ListControlsSnapshot) {
  return [
    snapshot.search.trim().length > 0 ? `Search: ${snapshot.search.trim()}` : null,
    snapshot.resultFilter ? `Result: ${snapshot.resultFilter}` : null,
    snapshot.subfactionFilter ? `Subfaction: ${snapshot.subfactionFilter}` : null,
    snapshot.sortKey !== 'default' ? `Sort: ${getSortLabel(snapshot.sortKey)}` : null,
    hasCustomVisibleColumns(snapshot.visibleColumns)
      ? `${snapshot.activeColumnCount}/${snapshot.totalColumnCount} columns visible`
      : null,
  ].filter((value): value is string => value !== null);
}

export function getSortLabel(sortKey: ListSortKey) {
  switch (sortKey) {
    case 'regiments-desc':
      return 'Regiments (high to low)';
    case 'regiments-asc':
      return 'Regiments (low to high)';
    case 'models-desc':
      return 'Models (high to low)';
    case 'models-asc':
      return 'Models (low to high)';
    case 'entries-desc':
      return 'Unit entries (high to low)';
    case 'entries-asc':
      return 'Unit entries (low to high)';
    case 'name-asc':
      return 'Name (A-Z)';
    default:
      return 'Original order';
  }
}