import type { SiteList } from '../../models/siteData';
import { compareWeekLabels, getWeekIdentity } from './weeks';

export type ListSortKey =
  | 'default'
  | 'week-desc'
  | 'week-asc'
  | 'regiments-desc'
  | 'regiments-asc'
  | 'models-desc'
  | 'models-asc'
  | 'entries-desc'
  | 'entries-asc'
  | 'name-asc';

export type ListColumnKey =
  | 'weekLabel'
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
  { key: 'weekLabel', label: 'Week', render: (list) => list.weekLabel || 'Unspecified' },
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
  weekLabel: true,
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
  filters: { search: string; result: string; subfaction: string; week: string }
) {
  const query = filters.search.trim().toLowerCase();
  const result = filters.result.trim().toLowerCase();
  const subfaction = filters.subfaction.trim().toLowerCase();
  const week = getWeekIdentity(filters.week);

  return lists.filter((list) => {
    const searchHaystack = [
      list.weekLabel,
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
      (week.length === 0 || getWeekIdentity(list.weekLabel) === week) &&
      (result.length === 0 || list.result.toLowerCase() === result) &&
      (subfaction.length === 0 || list.subfaction.toLowerCase() === subfaction)
    );
  });
}

export function compareLists(left: SiteList, right: SiteList, sortKey: ListSortKey) {
  switch (sortKey) {
    case 'week-desc':
      return compareWeekLabels(right.weekLabel, left.weekLabel) || left.index - right.index;
    case 'week-asc':
      return compareWeekLabels(left.weekLabel, right.weekLabel) || left.index - right.index;
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

export function getListWeekOptions(lists: SiteList[]) {
  const labelsByIdentity = new Map<string, string>();

  lists.forEach((list) => {
    if (!list.weekLabel) {
      return;
    }

    const identity = getWeekIdentity(list.weekLabel);
    const existing = labelsByIdentity.get(identity);
    if (!existing || list.weekLabel.length > existing.length) {
      labelsByIdentity.set(identity, list.weekLabel);
    }
  });

  return Array.from(labelsByIdentity.values()).sort((left, right) => compareWeekLabels(left, right));
}
