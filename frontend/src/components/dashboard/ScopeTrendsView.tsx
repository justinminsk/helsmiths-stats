import { useEffect, useMemo, useState } from 'react';
import type { DatasetPayload, ScopePayload, ScopeStoryTrend } from '../../models/siteData';
import {
  buildDerivedTrendSeries,
  buildTrendOptions,
  getTrendCoverage,
  getTrendMetricLabel,
  type TrendMetricKey,
  type TrendRollupKey,
} from '../../lib/dashboard/trends';

type ScopeTrendsViewProps = {
  datasetKey: string;
  datasets: DatasetPayload[];
  scope: ScopePayload;
  tabId: string;
};

type TrendSeriesColor = {
  line: string;
  focus: string;
};

const metricOptions: Array<{ key: TrendMetricKey; label: string }> = [
  { key: 'unit', label: 'Units' },
  { key: 'subfaction', label: 'Subfactions' },
  { key: 'lore', label: 'Manifestation lores' },
  { key: 'result', label: 'Results' },
];

const rollupOptions: Array<{ key: TrendRollupKey; label: string }> = [
  { key: 'weekly', label: 'Weekly' },
  { key: 'twoWeek', label: '2 weeks' },
  { key: 'monthly', label: '4 weeks' },
];

const trendSeriesPalette: TrendSeriesColor[] = [
  { line: '#0f766e', focus: 'rgba(15, 118, 110, 0.28)' },
  { line: '#2563eb', focus: 'rgba(37, 99, 235, 0.28)' },
  { line: '#b45309', focus: 'rgba(180, 83, 9, 0.28)' },
  { line: '#b91c1c', focus: 'rgba(185, 28, 28, 0.28)' },
];

export function ScopeTrendsView({ datasetKey, datasets, scope, tabId }: ScopeTrendsViewProps) {
  const [metric, setMetric] = useState<TrendMetricKey>('unit');
  const [rollup, setRollup] = useState<TrendRollupKey>('weekly');
  const [search, setSearch] = useState('');
  const [selectedLabels, setSelectedLabels] = useState<string[]>([]);

  const options = useMemo(() => buildTrendOptions(datasets, scope.key, metric, rollup), [datasets, metric, rollup, scope.key]);
  const filteredOptions = options.filter((option) => option.label.toLowerCase().includes(search.trim().toLowerCase()));
  const visibleOptions = filteredOptions.slice(0, 18);
  const coverage = useMemo(() => getTrendCoverage(datasets, scope.key, rollup), [datasets, rollup, scope.key]);

  useEffect(() => {
    setSelectedLabels((current) => {
      const available = new Set(options.map((option) => option.label));
      const retained = current.filter((label) => available.has(label));
      if (retained.length > 0) {
        return retained.slice(0, 4);
      }
      return options.slice(0, 3).map((option) => option.label);
    });
  }, [options]);

  const visibleSeries = useMemo(
    () => buildDerivedTrendSeries(datasets, scope.key, metric, rollup, selectedLabels),
    [datasets, metric, rollup, scope.key, selectedLabels]
  );
  const seriesColorByLabel = useMemo(
    () => new Map(visibleSeries.map((trend, index) => [trend.label, trendSeriesPalette[index % trendSeriesPalette.length]])),
    [visibleSeries]
  );

  const hasTrendData = coverage.weekCount > 1 && options.length > 0;

  function toggleLabel(label: string) {
    setSelectedLabels((current) => {
      if (current.includes(label)) {
        return current.filter((item) => item !== label);
      }
      if (current.length >= 4) {
        return [...current.slice(1), label];
      }
      return [...current, label];
    });
  }

  return (
    <section
      aria-labelledby={tabId}
      className="scope-view scope-view--trends"
      id={`scope-view-${datasetKey}-${scope.key}-trends`}
      role="tabpanel"
    >
      <header className="view-header view-header--trends">
        <div>
          <p className="view-kicker">Trend explorer</p>
          <h4 className="view-title">Compare units and rollups over time</h4>
          <p className="view-description">
            Pick units, subfactions, lores, or results, then roll the visible scope up by week, 2 weeks, or 4 weeks.
          </p>
        </div>
        {scope.reportLinks.lists ? (
          <p className="view-link-row">
            <a className="scope-link" href={scope.reportLinks.lists}>
              Open markdown list report
            </a>
          </p>
        ) : null}
      </header>

      {hasTrendData ? (
        <>
          <section className="trends-tools-panel">
            <header className="subsection-header subsection-header--compact">
              <div>
                <p className="subsection-kicker">Controls</p>
                <h5 className="subsection-title">Shape the comparison surface</h5>
              </div>
              <p className="subsection-meta">
                {coverage.weekCount} recorded weeks rolled into {coverage.bucketCount} visible checkpoints from {coverage.totalLists} lists.
              </p>
            </header>

            <div className="trends-toolbar">
              <label className="field">
                <span>Metric</span>
                <select className="field-control" onChange={(event) => setMetric(event.target.value as TrendMetricKey)} value={metric}>
                  {metricOptions.map((option) => (
                    <option key={option.key} value={option.key}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="field">
                <span>Rollup</span>
                <select className="field-control" onChange={(event) => setRollup(event.target.value as TrendRollupKey)} value={rollup}>
                  {rollupOptions.map((option) => (
                    <option key={option.key} value={option.key}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="field field--search">
                <span>Find a signal</span>
                <input
                  className="field-control"
                  onChange={(event) => setSearch(event.target.value)}
                  placeholder="Search unit, subfaction, lore, or result"
                  type="search"
                  value={search}
                />
              </label>
            </div>

            <div className="trends-selection-summary">
              <div className="trends-selection-summary__tags" aria-live="polite">
                {selectedLabels.length > 0 ? (
                  selectedLabels.map((label) => {
                    const color = seriesColorByLabel.get(label);
                    return (
                      <span className="filter-chip filter-chip--trend" key={label}>
                        {color ? <span aria-hidden="true" className="trend-color-swatch" style={{ backgroundColor: color.line }} /> : null}
                        {label}
                      </span>
                    );
                  })
                ) : (
                  <p className="list-control-summary__hint">Pick up to 4 signals to compare in parallel.</p>
                )}
              </div>

              <button className="action-pill action-pill--subtle" onClick={() => setSelectedLabels(options.slice(0, 3).map((option) => option.label))} type="button">
                Reset picks
              </button>
            </div>

            <div className="trends-picker" role="list" aria-label={`${getTrendMetricLabel(metric)} options`}>
              {visibleOptions.map((option) => {
                const isSelected = selectedLabels.includes(option.label);
                const color = seriesColorByLabel.get(option.label);
                return (
                  <button
                    aria-label={`${option.label} ${option.latestValue.toFixed(1)}% latest share`}
                    aria-pressed={isSelected}
                    className={`trend-option-chip${isSelected ? ' is-selected' : ''}`}
                    key={option.label}
                    onClick={() => toggleLabel(option.label)}
                    role="listitem"
                    style={isSelected && color ? { borderColor: color.line } : undefined}
                    title={`${option.label} • ${option.latestValue.toFixed(1)}% latest share`}
                    type="button"
                  >
                    {isSelected && color ? <span aria-hidden="true" className="trend-color-swatch" style={{ backgroundColor: color.line }} /> : null}
                    <span className="trend-option-chip__label">{option.label}</span>
                  </button>
                );
              })}
            </div>
          </section>

          <section className="stats-grid-section">
            <header className="subsection-header">
              <div>
                <p className="subsection-kicker">Overlay comparison</p>
                <h5 className="subsection-title">{getTrendMetricLabel(metric)} across {rollupOptions.find((option) => option.key === rollup)?.label.toLowerCase()}</h5>
              </div>
              <p className="subsection-meta">Each colored line tracks one selected signal across the same checkpoints so the shifts read as one comparison.</p>
            </header>

            {visibleSeries.length > 0 ? (
              <CombinedTrendChart trends={visibleSeries} />
            ) : (
              <section className="empty-state">
                <p className="subsection-kicker">No comparisons selected</p>
                <h5 className="empty-state__title">Choose at least one signal to render a timeline</h5>
                <p className="empty-state__body">Use the picker above to choose units, subfactions, lores, or results for this scope.</p>
              </section>
            )}
          </section>
        </>
      ) : (
        <section className="empty-state">
          <p className="subsection-kicker">Trend explorer</p>
          <h5 className="empty-state__title">Not enough weekly metadata is available for this scope yet</h5>
          <p className="empty-state__body">Once at least two week-labelled checkpoints exist, this tab can roll them up and compare selected signals over time.</p>
        </section>
      )}
    </section>
  );
}

function CombinedTrendChart({ trends }: { trends: ScopeStoryTrend[] }) {
  const preparedSeries = trends
    .map((trend, index) => ({
      trend,
      color: trendSeriesPalette[index % trendSeriesPalette.length],
      points: trend.points
        .map((point, pointIndex) => ({
          ...point,
          index: pointIndex,
          magnitude: getStatMagnitude(point.value),
        }))
        .filter((point): point is typeof point & { magnitude: number } => point.magnitude !== null),
    }))
    .filter((series) => series.points.length > 1);

  const defaultActiveKey =
    preparedSeries.length > 0
      ? `${preparedSeries[0].trend.label}::${preparedSeries[0].points[preparedSeries[0].points.length - 1]?.datasetKey ?? ''}`
      : '';
  const [activeKey, setActiveKey] = useState(defaultActiveKey);

  useEffect(() => {
    setActiveKey(defaultActiveKey);
  }, [defaultActiveKey]);

  if (preparedSeries.length === 0) {
    return null;
  }

  const width = 720;
  const height = 240;
  const paddingX = 20;
  const paddingY = 20;
  const basePoints = preparedSeries[0].points;
  const allMagnitudes = preparedSeries.flatMap((series) => series.points.map((point) => point.magnitude));
  const minMagnitude = Math.min(...allMagnitudes);
  const maxMagnitude = Math.max(...allMagnitudes);
  const range = maxMagnitude - minMagnitude;

  const positionedSeries = preparedSeries.map((series) => ({
    ...series,
    points: series.points.map((point, index) => {
      const x = paddingX + (index * (width - paddingX * 2)) / Math.max(series.points.length - 1, 1);
      const normalized = range === 0 ? 0.5 : (point.magnitude - minMagnitude) / range;
      const y = height - paddingY - normalized * (height - paddingY * 2);

      return {
        ...point,
        x,
        y,
        xPercent: (x / width) * 100,
        yPercent: (y / height) * 100,
        hotspotKey: `${series.trend.label}::${point.datasetKey}`,
      };
    }),
  }));
  const eraSegments = buildTrendEraSegments(positionedSeries[0].points, width, paddingX);
  const visibleAxisIndices = getVisibleTrendAxisIndices(positionedSeries[0].points.length);

  const allPoints = positionedSeries.flatMap((series) =>
    series.points.map((point) => ({
      ...point,
      label: series.trend.label,
      deltaLabel: series.trend.deltaLabel,
      color: series.color,
    }))
  );
  const pointOffsetByKey = buildTrendPointOffsets(allPoints);
  const activePoint = allPoints.find((point) => point.hotspotKey === activeKey) ?? allPoints[allPoints.length - 1];

  return (
    <section aria-label="Trend comparison chart" className="stats-card stats-card--trend-board">
      <div aria-label="Selected trend series" className="trend-board__legend" role="list">
        {positionedSeries.map((series) => {
          const latestPoint = series.points[series.points.length - 1];
          const isActive = activePoint.label === series.trend.label;

          return (
            <button
              aria-pressed={isActive}
              className={`trend-board__legend-item${isActive ? ' is-active' : ''}`}
              key={series.trend.label}
              onClick={() => setActiveKey(`${series.trend.label}::${latestPoint.datasetKey}`)}
              role="listitem"
              style={isActive ? { borderColor: series.color.line } : undefined}
              type="button"
            >
              <span aria-hidden="true" className="trend-color-swatch trend-color-swatch--legend" style={{ backgroundColor: series.color.line }} />
              <span className="trend-board__legend-copy">
                <span className="trend-board__legend-label">{series.trend.label}</span>
                <span className="trend-board__legend-meta">{series.trend.currentValue} now • {series.trend.deltaLabel}</span>
              </span>
            </button>
          );
        })}
      </div>

      <div className="stats-trend-chart stats-trend-chart--overlay">
        {eraSegments.length > 1 ? (
          <div className="stats-trend-era-strip" aria-hidden="true">
            {eraSegments.map((segment) => (
              <span className="stats-trend-era-chip" key={segment.label}>
                {segment.label}
              </span>
            ))}
          </div>
        ) : null}

        <div className="stats-trend-chart__frame">
          <svg aria-hidden="true" className="stats-trend-chart__svg" viewBox={`0 0 ${width} ${height}`}>
            {eraSegments.map((segment, index) => (
              <rect
                className={`stats-trend-chart__era-band${index % 2 === 1 ? ' stats-trend-chart__era-band--alternate' : ''}`}
                height={height - paddingY}
                key={segment.label}
                width={segment.width}
                x={segment.x}
                y={0}
              />
            ))}
            {eraSegments.slice(1).map((segment) => (
              <line
                className="stats-trend-chart__divider"
                key={`${segment.label}-divider`}
                x1={segment.x}
                x2={segment.x}
                y1={paddingY / 2}
                y2={height - paddingY}
              />
            ))}
            {[0, 0.25, 0.5, 0.75, 1].map((ratio, index) => {
              const y = paddingY + ratio * (height - paddingY * 2);
              return <line className="stats-trend-chart__guide" key={`guide-${index}`} x1={paddingX} x2={width - paddingX} y1={y} y2={y} />;
            })}
            {positionedSeries.map((series) => (
              <polyline
                className="stats-trend-chart__line"
                key={`${series.trend.metric}-${series.trend.label}`}
                points={series.points.map((point) => `${point.x},${point.y}`).join(' ')}
                style={{ stroke: series.color.line }}
              />
            ))}
            {allPoints.map((point) => {
              const offsetX = pointOffsetByKey.get(point.hotspotKey) ?? 0;
              const isActive = point.hotspotKey === activePoint.hotspotKey;
              return (
                <circle
                  aria-hidden="true"
                  className={`stats-trend-chart__dot${isActive ? ' stats-trend-chart__dot--active' : ''}`}
                  cx={point.x + offsetX}
                  cy={point.y}
                  key={`${point.hotspotKey}-dot`}
                  r={isActive ? 7 : 5.5}
                  style={{ stroke: point.color.line }}
                />
              );
            })}
          </svg>

          {allPoints.map((point) => (
            <button
              aria-label={`${point.label} ${compactDatasetLabel(point.datasetLabel)} ${point.value}${point.eraLabel ? ` ${point.eraLabel}` : ''}`}
              className={`stats-trend-chart__hotspot${point.hotspotKey === activePoint.hotspotKey ? ' stats-trend-chart__hotspot--active' : ''}`}
              key={point.hotspotKey}
              onBlur={() => setActiveKey(defaultActiveKey || point.hotspotKey)}
              onFocus={() => setActiveKey(point.hotspotKey)}
              onMouseEnter={() => setActiveKey(point.hotspotKey)}
              style={{
                left: `${(((point.x + (pointOffsetByKey.get(point.hotspotKey) ?? 0)) / width) * 100).toFixed(4)}%`,
                top: `${point.yPercent}%`,
                borderColor: point.color.line,
                boxShadow: point.hotspotKey === activePoint.hotspotKey ? `0 0 0 3px ${point.color.focus}` : undefined,
              }}
              type="button"
            >
              <span className="sr-only">{point.label}</span>
            </button>
          ))}
        </div>

        <div className="stats-trend-axis" aria-hidden="true">
          {basePoints
            .filter((point) => visibleAxisIndices.has(point.index))
            .map((point, index) => {
              const x = paddingX + (point.index * (width - paddingX * 2)) / Math.max(basePoints.length - 1, 1);
              return (
                <div className="stats-trend-axis__tick" key={`${point.datasetKey}-axis-${index}`} style={{ left: `${(x / width) * 100}%` }}>
                  <span className="stats-trend-axis__label">{compactDatasetLabel(point.datasetLabel)}</span>
                </div>
              );
            })}
        </div>

        <div className="stats-trend-chart__detail">
          <div className="stats-trend-chart__detail-header">
            <span aria-hidden="true" className="trend-color-swatch trend-color-swatch--detail" style={{ backgroundColor: activePoint.color.line }} />
            <div className="stats-trend-chart__detail-copy">
              <p className="stats-trend-chart__detail-label">{activePoint.label}</p>
              <p className="stats-trend-chart__detail-meta">
                {compactDatasetLabel(activePoint.datasetLabel)}{activePoint.eraLabel ? ` • ${activePoint.eraLabel}` : ''}
              </p>
            </div>
          </div>

          <div className="stats-trend-chart__detail-summary">
            <p className="stats-trend-chart__detail-value">{activePoint.value}</p>
            <p className="stats-trend-chart__detail-delta">{activePoint.deltaLabel}</p>
          </div>
        </div>
      </div>
    </section>
  );
}

function getStatMagnitude(value: string) {
  const match = value.match(/-?\d+(?:\.\d+)?/);
  return match ? Number(match[0]) : null;
}

function compactDatasetLabel(label: string) {
  return label.replace(/^January\b/, 'Jan').replace(/^February\b/, 'Feb').replace(/^March\b/, 'Mar').replace(/^April\b/, 'Apr');
}

function buildTrendEraSegments(
  points: Array<{ x: number; eraLabel?: string }>,
  width: number,
  paddingX: number
) {
  const segments: Array<{ label: string; x: number; width: number }> = [];

  for (let index = 0; index < points.length; index += 1) {
    const point = points[index];
    const label = point.eraLabel?.trim() || 'Timeline';
    const previous = segments[segments.length - 1];

    if (!previous || previous.label !== label) {
      segments.push({ label, x: point.x, width: 0 });
    }
  }

  return segments.map((segment, index) => {
    const segmentPoints = points.filter((point) => (point.eraLabel?.trim() || 'Timeline') === segment.label);
    const firstPoint = segmentPoints[0];
    const lastPoint = segmentPoints[segmentPoints.length - 1];
    const previousSegment = index > 0 ? segments[index - 1] : null;
    const nextSegment = index < segments.length - 1 ? segments[index + 1] : null;
    const startX = previousSegment ? (previousSegment.x + firstPoint.x) / 2 : paddingX;
    const endX = nextSegment ? (lastPoint.x + nextSegment.x) / 2 : width - paddingX;

    return {
      label: segment.label,
      x: startX,
      width: Math.max(endX - startX, 0),
    };
  });
}

function getVisibleTrendAxisIndices(count: number) {
  const indices = new Set<number>();
  if (count <= 4) {
    for (let index = 0; index < count; index += 1) {
      indices.add(index);
    }
    return indices;
  }

  indices.add(0);
  indices.add(count - 1);

  const interiorTargets = 3;
  for (let step = 1; step <= interiorTargets; step += 1) {
    const index = Math.round((step * (count - 1)) / (interiorTargets + 1));
    indices.add(index);
  }

  return indices;
}

function buildTrendPointOffsets(
  points: Array<{ hotspotKey: string; index: number; value: string }>
) {
  const groupedPoints = new Map<string, Array<{ hotspotKey: string }>>();

  points.forEach((point) => {
    const groupKey = `${point.index}:${point.value}`;
    const group = groupedPoints.get(groupKey) ?? [];
    group.push({ hotspotKey: point.hotspotKey });
    groupedPoints.set(groupKey, group);
  });

  const offsets = new Map<string, number>();
  groupedPoints.forEach((group) => {
    if (group.length === 1) {
      offsets.set(group[0].hotspotKey, 0);
      return;
    }

    const spacing = 8;
    const midpoint = (group.length - 1) / 2;
    group.forEach((point, index) => {
      offsets.set(point.hotspotKey, (index - midpoint) * spacing);
    });
  });

  return offsets;
}