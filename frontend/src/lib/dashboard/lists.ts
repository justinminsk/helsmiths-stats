import type { SiteList } from '../../models/siteData';

export type ListSortKey =
  | 'default'
  | 'regiments-desc'
  | 'regiments-asc'
  | 'models-desc'
  | 'models-asc'
  | 'entries-desc'
  | 'entries-asc'
  | 'name-asc';

export type ListColumnKey =
  | 'source'
  | 'name'
  | 'result'
  | 'subfaction'
  | 'manifestationLore'
  | 'regiments'
  | 'unitEntries'
  | 'models';

export type ListColumn = {
  key: ListColumnKey;
  label: string;
  render: (list: SiteList) => string | number;
};

export const listColumns: ListColumn[] = [
  { key: 'source', label: 'Source', render: (list) => list.source },
  { key: 'name', label: 'Name', render: (list) => list.name },
  { key: 'result', label: 'Result', render: (list) => list.result },
  { key: 'subfaction', label: 'Subfaction', render: (list) => list.subfaction },
  {
    key: 'manifestationLore',
    label: 'Manifestation lore',
    render: (list) => list.manifestationLore,
  },
  { key: 'regiments', label: 'Regiments', render: (list) => list.regiments },
  { key: 'unitEntries', label: 'Unit entries', render: (list) => list.unitEntries },
  { key: 'models', label: 'Models', render: (list) => list.models },
];

export const defaultVisibleColumns: Record<ListColumnKey, boolean> = {
  source: true,
  name: true,
  result: true,
  subfaction: true,
  manifestationLore: true,
  regiments: true,
  unitEntries: true,
  models: true,
};

export function filterLists(
  lists: SiteList[],
  filters: { search: string; result: string; subfaction: string }
) {
  const query = filters.search.trim().toLowerCase();
  const result = filters.result.trim().toLowerCase();
  const subfaction = filters.subfaction.trim().toLowerCase();

  return lists.filter((list) => {
    const searchHaystack = [
      list.source,
      list.name,
      list.result,
      list.subfaction,
      list.manifestationLore,
      ...list.units.flatMap((unit) => [unit.name, unit.regiment, ...unit.notes]),
    ]
      .join(' ')
      .toLowerCase();

    return (
      (query.length === 0 || searchHaystack.includes(query)) &&
      (result.length === 0 || list.result.toLowerCase() === result) &&
      (subfaction.length === 0 || list.subfaction.toLowerCase() === subfaction)
    );
  });
}

export function compareLists(left: SiteList, right: SiteList, sortKey: ListSortKey) {
  switch (sortKey) {
    case 'models-desc':
      return right.models - left.models;
    case 'models-asc':
      return left.models - right.models;
    case 'entries-desc':
      return right.unitEntries - left.unitEntries;
    case 'entries-asc':
      return left.unitEntries - right.unitEntries;
    case 'regiments-desc':
      return right.regiments - left.regiments;
    case 'regiments-asc':
      return left.regiments - right.regiments;
    case 'name-asc':
      return left.name.localeCompare(right.name);
    default:
      return left.index - right.index;
  }
}

export function getNumericColumnIndexes(columns: ListColumn[]) {
  return columns.flatMap((column, index) =>
    column.key === 'regiments' || column.key === 'unitEntries' || column.key === 'models'
      ? [index]
      : []
  );
}
