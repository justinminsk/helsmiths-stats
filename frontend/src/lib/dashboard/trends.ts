import type { DatasetPayload, ScopePayload, ScopeStoryTrend, ScopeStoryTrendPoint } from '../../models/siteData';
import { parseWeekLabel } from './weeks';

export type TrendMetricKey = 'unit' | 'subfaction' | 'lore' | 'result';

export type TrendRollupKey = 'weekly' | 'twoWeek' | 'monthly';

export type TrendOption = {
  label: string;
  latestValue: number;
  totalMentions: number;
};

type TrendListRecord = {
  datasetKey: string;
  datasetLabel: string;
  scopeKey: string;
  weekLabel: string;
  list: ScopePayload['lists'][number];
};

type WeekGroup = {
  key: string;
  label: string;
  sortKey: number;
  eraLabel?: string;
  lists: TrendListRecord[];
};

type TrendBucket = {
  key: string;
  label: string;
  eraLabel?: string;
  listCount: number;
  lists: TrendListRecord[];
};

const metricLabels: Record<TrendMetricKey, string> = {
  unit: 'Unit presence',
  subfaction: 'Subfaction share',
  lore: 'Lore share',
  result: 'Result share',
};

const rollupSizes: Record<TrendRollupKey, number> = {
  weekly: 1,
  twoWeek: 2,
  monthly: 4,
};

export function getTrendMetricLabel(metric: TrendMetricKey) {
  return metricLabels[metric];
}

export function buildTrendOptions(datasets: DatasetPayload[], scopeKey: string, metric: TrendMetricKey, rollup: TrendRollupKey) {
  const buckets = buildTrendBuckets(datasets, scopeKey, rollup);
  const optionMap = new Map<string, { latestValue: number; totalMentions: number }>();

  buckets.forEach((bucket) => {
    const listCount = bucket.listCount;
    const counts = countMetricValues(bucket.lists, metric);
    counts.forEach((count, label) => {
      optionMap.set(label, {
        latestValue: listCount > 0 ? (count / listCount) * 100 : 0,
        totalMentions: (optionMap.get(label)?.totalMentions ?? 0) + count,
      });
    });
  });

  return Array.from(optionMap.entries())
    .map(([label, summary]) => ({
      label,
      latestValue: summary.latestValue,
      totalMentions: summary.totalMentions,
    }))
    .sort((left, right) => {
      if (right.latestValue !== left.latestValue) {
        return right.latestValue - left.latestValue;
      }
      if (right.totalMentions !== left.totalMentions) {
        return right.totalMentions - left.totalMentions;
      }
      return left.label.localeCompare(right.label);
    });
}

export function buildDerivedTrendSeries(
  datasets: DatasetPayload[],
  scopeKey: string,
  metric: TrendMetricKey,
  rollup: TrendRollupKey,
  selectedLabels: string[]
): ScopeStoryTrend[] {
  const buckets = buildTrendBuckets(datasets, scopeKey, rollup);

  return selectedLabels
    .map((label) => buildSeriesForLabel(buckets, metric, label))
    .filter((series): series is ScopeStoryTrend => series !== null);
}

export function getTrendCoverage(datasets: DatasetPayload[], scopeKey: string, rollup: TrendRollupKey) {
  const weekGroups = buildWeekGroups(datasets, scopeKey);
  const buckets = buildTrendBuckets(datasets, scopeKey, rollup);
  const totalLists = buckets.reduce((sum, bucket) => sum + bucket.listCount, 0);

  return {
    bucketCount: buckets.length,
    totalLists,
    weekCount: weekGroups.length,
  };
}

function buildSeriesForLabel(buckets: TrendBucket[], metric: TrendMetricKey, label: string) {
  const points: ScopeStoryTrendPoint[] = buckets.map((bucket) => {
    const count = countMetricMatches(bucket.lists, metric, label);
    const share = bucket.listCount > 0 ? (count / bucket.listCount) * 100 : 0;

    return {
      datasetKey: bucket.key,
      datasetLabel: bucket.label,
      eraLabel: bucket.eraLabel,
      value: formatPercent(share),
    };
  });

  if (points.length < 2) {
    return null;
  }

  const currentValue = parsePercent(points[points.length - 1].value);
  const previousValue = parsePercent(points[points.length - 2].value);
  const delta = currentValue - previousValue;

  return {
    metric: metricLabels[metric],
    label,
    currentValue: formatPercent(currentValue),
    deltaLabel: formatDelta(delta, points[points.length - 2].datasetLabel),
    direction: delta > 0 ? 'up' : delta < 0 ? 'down' : 'flat',
    points,
  };
}

function buildTrendBuckets(datasets: DatasetPayload[], scopeKey: string, rollup: TrendRollupKey) {
  const groups = buildWeekGroups(datasets, scopeKey);
  const rollupSize = rollupSizes[rollup];
  const buckets: TrendBucket[] = [];

  for (let index = 0; index < groups.length; index += rollupSize) {
    const chunk = groups.slice(index, index + rollupSize);
    const lists = chunk.flatMap((group) => group.lists);
    const first = chunk[0];
    const last = chunk[chunk.length - 1];
    const eraLabels = Array.from(new Set(chunk.map((group) => group.eraLabel).filter(Boolean)));

    buckets.push({
      key: `${first.key}-${last.key}`,
      label: chunk.length === 1 ? first.label : `${compactLabel(first.label)} to ${compactLabel(last.label)}`,
      eraLabel: eraLabels.length === 1 ? eraLabels[0] : eraLabels.length > 1 ? 'Cross-era rollup' : undefined,
      listCount: lists.length,
      lists,
    });
  }

  return buckets;
}

function buildWeekGroups(datasets: DatasetPayload[], scopeKey: string) {
  const grouped = new Map<string, WeekGroup>();

  collectScopeLists(datasets, scopeKey).forEach((record) => {
    const parsed = parseWeekLabel(record.weekLabel);
    const key = parsed?.identity ?? record.weekLabel;
    const sortKey = parsed?.sortKey ?? Number.MAX_SAFE_INTEGER;
    const existing = grouped.get(key);
    const eraLabel = deriveEraLabel(record.datasetKey, record.datasetLabel);

    if (!existing) {
      grouped.set(key, {
        key,
        label: record.weekLabel,
        sortKey,
        eraLabel,
        lists: [record],
      });
      return;
    }

    existing.lists.push(record);
    if (record.weekLabel.length > existing.label.length) {
      existing.label = record.weekLabel;
    }
    if (!existing.eraLabel && eraLabel) {
      existing.eraLabel = eraLabel;
    }
  });

  return Array.from(grouped.values()).sort((left, right) => {
    if (left.sortKey !== right.sortKey) {
      return left.sortKey - right.sortKey;
    }
    return left.label.localeCompare(right.label);
  });
}

function collectScopeLists(datasets: DatasetPayload[], scopeKey: string): TrendListRecord[] {
  const records: TrendListRecord[] = [];

  datasets.forEach((dataset) => {
    const scope = dataset.scopes.find((candidate) => candidate.key === scopeKey);
    if (!scope) {
      return;
    }

    scope.lists.forEach((list) => {
      if (!list.weekLabel?.trim()) {
        return;
      }

      records.push({
        datasetKey: dataset.key,
        datasetLabel: dataset.label,
        scopeKey,
        weekLabel: list.weekLabel.trim(),
        list,
      });
    });
  });

  return records;
}

function countMetricValues(records: TrendListRecord[], metric: TrendMetricKey) {
  const counts = new Map<string, number>();

  records.forEach((record) => {
    getMetricValues(record, metric).forEach((value) => {
      counts.set(value, (counts.get(value) ?? 0) + 1);
    });
  });

  return counts;
}

function countMetricMatches(records: TrendListRecord[], metric: TrendMetricKey, label: string) {
  return records.reduce((count, record) => count + (getMetricValues(record, metric).includes(label) ? 1 : 0), 0);
}

function getMetricValues(record: TrendListRecord, metric: TrendMetricKey) {
  switch (metric) {
    case 'unit':
      return Array.from(new Set(record.list.units.map((unit) => unit.name)));
    case 'subfaction':
      return record.list.subfaction ? [record.list.subfaction] : [];
    case 'lore':
      return record.list.manifestationLore ? [record.list.manifestationLore] : [];
    case 'result':
      return record.list.result ? [record.list.result] : [];
    default:
      return [];
  }
}

function deriveEraLabel(datasetKey: string, datasetLabel: string) {
  const normalized = `${datasetKey} ${datasetLabel}`.toLowerCase();
  if (normalized.includes('pre-points')) {
    return 'Pre-points era';
  }
  if (normalized.includes('post-points') || normalized.includes('current')) {
    return 'Post-points era';
  }
  return undefined;
}

function compactLabel(label: string) {
  return label.replace(/^January\b/, 'Jan').replace(/^February\b/, 'Feb').replace(/^March\b/, 'Mar').replace(/^April\b/, 'Apr');
}

function parsePercent(value: string) {
  return Number(value.replace('%', '')) || 0;
}

function formatPercent(value: number) {
  return `${value.toFixed(1)}%`;
}

function formatDelta(delta: number, baselineLabel: string) {
  if (Math.abs(delta) < 0.05) {
    return `Flat versus ${compactLabel(baselineLabel)}`;
  }

  const prefix = delta > 0 ? '+' : '';
  return `${prefix}${delta.toFixed(1)} pts versus ${compactLabel(baselineLabel)}`;
}