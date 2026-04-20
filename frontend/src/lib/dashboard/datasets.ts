import type {
  DatasetPayload,
  ScopePayload,
  ScopeStory,
  ScopeStorySharedUnitPair,
  SiteDataPayload,
  SiteList,
  StatsTable,
} from '../../models/siteData';

export const aggregateDatasetKey = 'all';

type ScopedDataset = {
  dataset: DatasetPayload;
  scope: ScopePayload;
};

export function buildDashboardDatasets(payload: SiteDataPayload): DatasetPayload[] {
  const aggregateDataset = buildAggregateDataset(payload);

  if (!aggregateDataset) {
    return payload.datasets;
  }

  return [aggregateDataset, ...payload.datasets];
}

function buildAggregateDataset(payload: SiteDataPayload): DatasetPayload | null {
  if (payload.datasets.length === 0) {
    return null;
  }

  const scopes = payload.scopeOrder
    .map((scopeKey) => buildAggregateScope(scopeKey, payload))
    .filter((scope): scope is ScopePayload => scope !== null);

  if (scopes.length === 0) {
    return null;
  }

  return {
    key: aggregateDatasetKey,
    label: 'All',
    reportBasePath: '',
    scopes,
  };
}

function buildAggregateScope(scopeKey: string, payload: SiteDataPayload): ScopePayload | null {
  const sourceScopes = payload.datasets
    .map((dataset) => {
      const scope = dataset.scopes.find((candidate) => candidate.key === scopeKey);
      return scope ? { dataset, scope } : null;
    })
    .filter((entry): entry is ScopedDataset => entry !== null);

  if (sourceScopes.length === 0) {
    return null;
  }

  const label = payload.scopeLabels[scopeKey] ?? sourceScopes[0].scope.label;
  const lists = mergeLists(sourceScopes);
  const statsTables = buildAggregateStatsTables(lists);

  return {
    key: scopeKey,
    label,
    datasetKey: aggregateDatasetKey,
    listCount: lists.length,
    reportLinks: {
      stats: '',
      lists: '',
    },
    statsSummary: buildStatsSummary(statsTables, lists.length),
    filters: {
      results: Array.from(new Set(lists.map((list) => list.result))).sort((left, right) => left.localeCompare(right)),
      subfactions: Array.from(new Set(lists.map((list) => list.subfaction))).sort((left, right) => left.localeCompare(right)),
    },
    story: buildAggregateStory(lists),
    statsTables,
    lists,
  };
}

function mergeLists(sourceScopes: ScopedDataset[]): SiteList[] {
  const merged: SiteList[] = [];

  sourceScopes.forEach(({ dataset, scope }) => {
    scope.lists.forEach((list) => {
      merged.push({
        ...list,
        index: merged.length,
        source: `${dataset.label} / ${list.source}`,
      });
    });
  });

  return merged;
}

function buildAggregateStatsTables(lists: SiteList[]): StatsTable[] {
  const tables: StatsTable[] = [];
  const listCount = lists.length;

  const resultCounts = countBy(lists, (list) => list.result);
  const resultRows = buildSortedRows(resultCounts, 8, (count) => [String(count)]);
  if (resultRows.length > 0) {
    tables.push({
      key: 'resultBreakdown',
      title: 'Result breakdown',
      headers: ['Result', 'Lists'],
      rows: resultRows,
    });
  }

  const unitPresenceCounts = new Map<string, number>();
  lists.forEach((list) => {
    const seenUnits = new Set(list.units.map((unit) => unit.name));
    seenUnits.forEach((unitName) => {
      unitPresenceCounts.set(unitName, (unitPresenceCounts.get(unitName) ?? 0) + 1);
    });
  });

  const unitPresenceRows = buildSortedRows(unitPresenceCounts, 10, (count) => [String(count), formatShare(count, listCount)]);
  if (unitPresenceRows.length > 0) {
    tables.push({
      key: 'topUnitPresence',
      title: 'Top units by list presence',
      headers: ['Unit', 'Lists', '% of lists'],
      rows: unitPresenceRows,
    });
  }

  const unitEntryCounts = new Map<string, number>();
  lists.forEach((list) => {
    list.units.forEach((unit) => {
      unitEntryCounts.set(unit.name, (unitEntryCounts.get(unit.name) ?? 0) + 1);
    });
  });

  const unitEntryRows = buildSortedRows(unitEntryCounts, 10, (count) => [String(count)]);
  if (unitEntryRows.length > 0) {
    tables.push({
      key: 'topUnitEntries',
      title: 'Top unit entries',
      headers: ['Unit', 'Entries'],
      rows: unitEntryRows,
    });
  }

  const subfactionCounts = countBy(lists, (list) => list.subfaction);
  const subfactionRows = buildSortedRows(subfactionCounts, 8, (count) => [String(count)]);
  if (subfactionRows.length > 0) {
    tables.push({
      key: 'topSubfactions',
      title: 'Top subfactions',
      headers: ['Subfaction', 'Lists'],
      rows: subfactionRows,
    });
  }

  const loreCounts = countBy(lists, (list) => list.manifestationLore || 'Unknown');
  const loreRows = buildSortedRows(loreCounts, 8, (count) => [String(count)]);
  if (loreRows.length > 0) {
    tables.push({
      key: 'manifestationLores',
      title: 'Manifestation lores',
      headers: ['Lore', 'Lists'],
      rows: loreRows,
    });
  }

  return tables;
}

function buildAggregateStory(lists: SiteList[]): ScopeStory | undefined {
  if (lists.length === 0) {
    return undefined;
  }

  const listCount = lists.length;
  const topSubfaction = getLeader(countBy(lists, (list) => list.subfaction));
  const topLore = getLeader(countBy(lists, (list) => list.manifestationLore || 'Unknown'));
  const unitPresence = new Map<string, number>();
  const pairCounts = new Map<string, { units: string[]; count: number }>();

  lists.forEach((list) => {
    const uniqueUnits = Array.from(new Set(list.units.map((unit) => unit.name))).sort((left, right) => left.localeCompare(right));
    uniqueUnits.forEach((unitName) => {
      unitPresence.set(unitName, (unitPresence.get(unitName) ?? 0) + 1);
    });

    for (let leftIndex = 0; leftIndex < uniqueUnits.length; leftIndex += 1) {
      for (let rightIndex = leftIndex + 1; rightIndex < uniqueUnits.length; rightIndex += 1) {
        const units = [uniqueUnits[leftIndex], uniqueUnits[rightIndex]];
        const key = units.join('|');
        const current = pairCounts.get(key);
        if (current) {
          current.count += 1;
        } else {
          pairCounts.set(key, { units, count: 1 });
        }
      }
    }
  });

  const topUnit = getLeader(unitPresence);
  const coreSignals = [
    topSubfaction
      ? {
          label: 'Top subfaction',
          value: topSubfaction.label,
          detail: `${topSubfaction.count} of ${listCount} lists`,
        }
      : null,
    topLore
      ? {
          label: 'Top manifestation lore',
          value: topLore.label,
          detail: `${topLore.count} of ${listCount} lists`,
        }
      : null,
    topUnit
      ? {
          label: 'Most shared unit',
          value: topUnit.label,
          detail: `${topUnit.count} of ${listCount} lists (${formatShare(topUnit.count, listCount)})`,
        }
      : null,
  ].filter((signal): signal is NonNullable<typeof signal> => signal !== null);

  const sharedUnits = buildSortedRows(unitPresence, 5, (count) => [String(count)])
    .map(([name, count]) => ({
      name,
      listCount: Number(count),
      share: formatShare(Number(count), listCount),
    }))
    .filter((entry) => entry.listCount > 1);

  const sharedUnitPairs = Array.from(pairCounts.values())
    .sort((left, right) => {
      if (right.count !== left.count) {
        return right.count - left.count;
      }
      return left.units.join(' + ').localeCompare(right.units.join(' + '));
    })
    .slice(0, 5)
    .map<ScopeStorySharedUnitPair>((entry) => ({
      units: entry.units,
      listCount: entry.count,
      share: formatShare(entry.count, listCount),
    }))
    .filter((entry) => entry.listCount > 1);

  return {
    coreSignals,
    sharedUnits,
    sharedUnitPairs,
    snapshotTrends: [],
  };
}

function buildStatsSummary(statsTables: StatsTable[], listCount: number) {
  const resultLeader = statsTables.find((table) => table.key === 'resultBreakdown')?.rows[0];
  const unitLeader = statsTables.find((table) => table.key === 'topUnitPresence')?.rows[0];

  const summaryParts: string[] = [];

  if (resultLeader) {
    summaryParts.push(`Most common result is ${resultLeader[0]} (${resultLeader[1]} lists).`);
  }

  if (unitLeader) {
    summaryParts.push(`Top unit presence is ${unitLeader[0]} in ${unitLeader[1]} lists (${unitLeader[2]}).`);
  }

  if (summaryParts.length > 0) {
    return summaryParts.join(' ');
  }

  return `${listCount} winning lists are included in this combined view.`;
}

function countBy(items: SiteList[], selector: (item: SiteList) => string) {
  const counts = new Map<string, number>();

  items.forEach((item) => {
    const key = selector(item).trim() || 'Unknown';
    counts.set(key, (counts.get(key) ?? 0) + 1);
  });

  return counts;
}

function buildSortedRows(counts: Map<string, number>, limit: number, buildColumns: (count: number) => string[]) {
  return Array.from(counts.entries())
    .sort((left, right) => {
      if (right[1] !== left[1]) {
        return right[1] - left[1];
      }
      return left[0].localeCompare(right[0]);
    })
    .slice(0, limit)
    .map(([label, count]) => [label, ...buildColumns(count)]);
}

function getLeader(counts: Map<string, number>) {
  const [label, count] = Array.from(counts.entries()).sort((left, right) => {
    if (right[1] !== left[1]) {
      return right[1] - left[1];
    }
    return left[0].localeCompare(right[0]);
  })[0] ?? [];

  if (!label || typeof count !== 'number') {
    return null;
  }

  return { label, count };
}

function formatShare(count: number, total: number) {
  if (total <= 0) {
    return '0.0%';
  }

  return `${((count / total) * 100).toFixed(1)}%`;
}