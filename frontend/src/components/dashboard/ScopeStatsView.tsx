import { useEffect, useRef, useState } from 'react';
import type {
  ScopePayload,
  ScopeStorySignal,
  ScopeStorySharedUnit,
  ScopeStorySharedUnitPair,
  ScopeStoryTrend,
  StatsTable,
} from '../../models/siteData';

type ScopeStatsViewProps = {
  datasetKey: string;
  scope: ScopePayload;
  tabId: string;
};

export function ScopeStatsView({ datasetKey, scope, tabId }: ScopeStatsViewProps) {
  const groupedTables = groupStatsTables(scope.statsTables);
  const hasStatsTables = scope.statsTables.length > 0;
  const resultBreakdownTable = getStatsTable(scope.statsTables, 'resultBreakdown');
  const statsHighlights = buildStatsHighlights(scope);
  const hasStorySignals = Boolean(
    scope.story &&
      (scope.story.coreSignals.length > 0 ||
        scope.story.sharedUnits.length > 0 ||
        scope.story.sharedUnitPairs.length > 0)
  );
  const trendMode = scope.story?.weeklyTrends?.length ? 'weekly' : scope.story?.snapshotTrends.length ? 'snapshot' : null;
  const visibleTrends = trendMode === 'weekly' ? scope.story?.weeklyTrends ?? [] : scope.story?.snapshotTrends ?? [];
  const hasSnapshotTrends = visibleTrends.length > 0;

  return (
    <section
      aria-labelledby={tabId}
      className="scope-view scope-view--stats"
      id={`scope-view-${datasetKey}-${scope.key}-stats`}
      role="tabpanel"
    >
      <header className="view-header view-header--stats">
        <div>
          <p className="view-kicker">Stats overview</p>
          <h4 className="view-title">Summary patterns</h4>
        </div>
        <p className="view-link-row">
          <a className="scope-link" href={scope.reportLinks.stats}>
            Open markdown report
          </a>
        </p>
      </header>

      <section className="stats-summary-card">
        <div>
          <p className="subsection-kicker">Scope summary</p>
          <h5 className="subsection-title">{scope.statsTables.length} summary blocks ready</h5>
        </div>
        <p className="stats-summary">Summary: {scope.statsSummary}</p>
      </section>

      {hasStatsTables && (statsHighlights.length > 0 || resultBreakdownTable) ? (
        <section className="stats-grid-section stats-grid-section--highlights">
          <header className="subsection-header">
            <div>
              <p className="subsection-kicker">Key takeaways</p>
              <h5 className="subsection-title">Fast read before the full breakdowns</h5>
            </div>
            <p className="subsection-meta">Lead with the strongest outcomes, then drop into rankings and detailed tables below.</p>
          </header>

          <div className="stats-highlights-layout">
            {statsHighlights.length > 0 ? (
              <div className="stats-highlight-grid">
                {statsHighlights.map((highlight) => (
                  <article className="stats-highlight-card" key={`${highlight.eyebrow}-${highlight.title}`}>
                    <p className="stats-highlight-card__eyebrow">{highlight.eyebrow}</p>
                    <h5 className="stats-highlight-card__value">{highlight.value}</h5>
                    <p className="stats-highlight-card__title">{highlight.title}</p>
                    <p className="stats-highlight-card__detail">{highlight.detail}</p>
                  </article>
                ))}
              </div>
            ) : null}

            {resultBreakdownTable ? <StatsResultBreakdownChart scope={scope} table={resultBreakdownTable} /> : null}
          </div>
        </section>
      ) : null}

      {hasStorySignals ? (
        <section className="stats-grid-section">
          <header className="subsection-header">
            <div>
              <p className="subsection-kicker">Winner signals</p>
              <h5 className="subsection-title">What winners share</h5>
            </div>
            <p className="subsection-meta">Lead with the recurring identity pieces first, then use the raw tables underneath as reference.</p>
          </header>

          <div className="stats-grid stats-grid--story">
            {scope.story?.coreSignals.length ? <StatsStorySignalsCard signals={scope.story.coreSignals} /> : null}
            {scope.story?.sharedUnits.length ? <StatsSharedUnitsCard units={scope.story.sharedUnits} /> : null}
            {scope.story?.sharedUnitPairs.length ? <StatsSharedPairsCard pairs={scope.story.sharedUnitPairs} /> : null}
          </div>
        </section>
      ) : null}

      {hasSnapshotTrends ? (
        <section className="stats-grid-section">
          <header className="subsection-header">
            <div>
              <p className="subsection-kicker">{trendMode === 'weekly' ? 'Week to week' : 'Over time'}</p>
              <h5 className="subsection-title">{trendMode === 'weekly' ? 'How the winner profile shifts each week' : 'How the winner profile evolves'}</h5>
            </div>
            <p className="subsection-meta">
              {trendMode === 'weekly'
                ? 'Use the source-file week buckets to track whether each winning signal is accelerating, flattening, or slipping week by week.'
                : 'Read the whole arc for each current leader so you can see where momentum held, flattened, or reversed across the timeline.'}
            </p>
          </header>

          <div className="stats-grid stats-grid--story">
            <StatsSnapshotTrendsCard mode={trendMode ?? 'snapshot'} trends={visibleTrends} />
          </div>
        </section>
      ) : null}

      {hasStatsTables ? (
        <>
          {groupedTables.ranking.length > 0 ? (
            <section className="stats-grid-section">
              <header className="subsection-header">
                <div>
                  <p className="subsection-kicker">Leading signals</p>
                  <h5 className="subsection-title">Top rankings first</h5>
                </div>
                <p className="subsection-meta">Surface the strongest usage and presence patterns before detailed reference tables.</p>
              </header>

              <div className="stats-grid stats-grid--ranking">
                {groupedTables.ranking.map((table) => (
                  <StatsRankingCard key={table.key} table={table} />
                ))}
              </div>
            </section>
          ) : null}

          {groupedTables.metrics.length > 0 ? (
            <section className="stats-grid-section">
              <header className="subsection-header">
                <div>
                  <p className="subsection-kicker">Field patterns</p>
                  <h5 className="subsection-title">Compact distribution groups</h5>
                </div>
                <p className="subsection-meta">Smaller count breakdowns read faster as metric tiles than as full tables.</p>
              </header>

              <div className="stats-grid stats-grid--metrics">
                {groupedTables.metrics.map((table) => (
                  <StatsMetricsCard key={table.key} table={table} />
                ))}
              </div>
            </section>
          ) : null}

          {groupedTables.watchlist.length > 0 ? (
            <section className="stats-grid-section">
              <header className="subsection-header">
                <div>
                  <p className="subsection-kicker">Watchlist</p>
                  <h5 className="subsection-title">Missing or inactive options</h5>
                </div>
                <p className="subsection-meta">Separate non-played or notable omissions from the ranked summaries.</p>
              </header>

              <div className="stats-grid stats-grid--watchlist">
                {groupedTables.watchlist.map((table) => (
                  <StatsWatchlistCard key={table.key} table={table} />
                ))}
              </div>
            </section>
          ) : null}

          {groupedTables.table.length > 0 ? (
            <section className="stats-grid-section">
              <header className="subsection-header">
                <div>
                  <p className="subsection-kicker">Reference tables</p>
                  <h5 className="subsection-title">Detailed breakdowns</h5>
                </div>
                <p className="subsection-meta">Keep true tables only for content that still benefits from a full grid view.</p>
              </header>

              <div className="stats-grid">
                {groupedTables.table.map((table) => (
                  <StatsTableCard key={table.key} table={table} />
                ))}
              </div>
            </section>
          ) : null}
        </>
      ) : (
        <section className="empty-state">
          <p className="subsection-kicker">Stats overview</p>
          <h5 className="empty-state__title">No summary tables are available for this scope yet</h5>
          <p className="empty-state__body">Open the markdown report for the raw output or switch scopes to inspect populated summaries.</p>
        </section>
      )}
    </section>
  );
}

type StatsPresentation = 'ranking' | 'metrics' | 'watchlist' | 'table';

type GroupedStatsTables = Record<StatsPresentation, StatsTable[]>;

type StatsMetric = {
  label: string;
  value: string;
};

type StatsHighlight = {
  eyebrow: string;
  title: string;
  value: string;
  detail: string;
};

type StatsStorySignalsCardProps = {
  signals: ScopeStorySignal[];
};

type StatsSharedUnitsCardProps = {
  units: ScopeStorySharedUnit[];
};

type StatsSharedPairsCardProps = {
  pairs: ScopeStorySharedUnitPair[];
};

type StatsSnapshotTrendsCardProps = {
  trends: ScopeStoryTrend[];
  mode: 'weekly' | 'snapshot';
};

function groupStatsTables(tables: StatsTable[]): GroupedStatsTables {
  return tables.reduce<GroupedStatsTables>(
    (grouped, table) => {
      grouped[categorizeStatsTable(table)].push(table);
      return grouped;
    },
    {
      ranking: [],
      metrics: [],
      watchlist: [],
      table: [],
    }
  );
}

function categorizeStatsTable(table: StatsTable): StatsPresentation {
  const normalizedTitle = table.title.toLowerCase();
  const normalizedKey = table.key.toLowerCase();
  const hasSingleValueRows = table.rows.every((row) => row.filter(Boolean).length <= 1);
  const hasCompactRows = table.headers.length <= 3 && table.rows.every((row) => row.filter(Boolean).length >= 2);
  const looksRanked =
    normalizedTitle.includes('top ') ||
    normalizedTitle.includes('top-') ||
    normalizedTitle.includes('presence') ||
    normalizedKey.startsWith('top') ||
    normalizedKey.includes('presence');

  if (normalizedTitle.includes('unplayed') || hasSingleValueRows) {
    return 'watchlist';
  }

  if (hasCompactRows) {
    if (looksRanked) {
      return 'ranking';
    }

    if (table.rows.length <= 6) {
      return 'metrics';
    }
  }

  return 'table';
}

function getStatsTable(tables: StatsTable[], key: string) {
  return tables.find((table) => table.key === key) ?? null;
}

function buildStatsHighlights(scope: ScopePayload): StatsHighlight[] {
  const highlights: StatsHighlight[] = [];
  const resultBreakdown = getStatsTable(scope.statsTables, 'resultBreakdown');
  const topUnitPresence = getStatsTable(scope.statsTables, 'topUnitPresence') ?? getStatsTable(scope.statsTables, 'topUnitsByPresence');
  const topUnitEntries = getStatsTable(scope.statsTables, 'topUnitEntries');
  const manifestationLores = getStatsTable(scope.statsTables, 'manifestationLores') ?? getStatsTable(scope.statsTables, 'manifestationLoreCounts');
  const topSubfactions = getStatsTable(scope.statsTables, 'topSubfactions');

  const resultLeader = resultBreakdown?.rows[0];
  if (resultLeader) {
    const count = resultLeader[1] ?? '0';
    const ratio = scope.listCount > 0 ? `${((Number(count) / scope.listCount) * 100).toFixed(1)}% of lists` : `${count} lists`;
    highlights.push({
      eyebrow: 'Most common result',
      title: resultLeader[0] ?? 'Unknown result',
      value: count,
      detail: ratio,
    });
  }

  const presenceLeader = topUnitPresence?.rows[0];
  if (presenceLeader) {
    highlights.push({
      eyebrow: 'Top unit presence',
      title: presenceLeader[0] ?? 'Unknown unit',
      value: presenceLeader[2] ?? presenceLeader[1] ?? '0',
      detail: `${presenceLeader[1] ?? '0'} lists`,
    });
  }

  const entriesLeader = topUnitEntries?.rows[0];
  if (entriesLeader) {
    highlights.push({
      eyebrow: 'Most repeated unit',
      title: entriesLeader[0] ?? 'Unknown unit',
      value: entriesLeader[1] ?? '0',
      detail: 'Entries across lists',
    });
  }

  const loreLeader = manifestationLores?.rows[0];
  if (loreLeader) {
    highlights.push({
      eyebrow: 'Most common lore',
      title: loreLeader[0] ?? 'Unknown lore',
      value: loreLeader[1] ?? '0',
      detail: 'Lists using this lore',
    });
  }

  const subfactionLeader = topSubfactions?.rows[0];
  if (subfactionLeader) {
    highlights.push({
      eyebrow: 'Top subfaction',
      title: subfactionLeader[0] ?? 'Unknown subfaction',
      value: subfactionLeader[1] ?? '0',
      detail: 'Lists using this build',
    });
  }

  return highlights.slice(0, 4);
}

type StatsTableCardProps = {
  table: StatsTable;
};

function StatsRankingCard({ table }: StatsTableCardProps) {
  const maxMagnitude = table.rows.reduce((currentMax, row) => {
    const magnitude = getPrimaryRankingMetric(table, row)?.magnitude ?? null;
    return magnitude === null ? currentMax : Math.max(currentMax, magnitude);
  }, 0);

  return (
    <section className="stats-card stats-card--ranking">
      <header className="stats-card__header">
        <h4 className="stats-card__title">{table.title}</h4>
        <p className="stats-card__meta">Ranked summary</p>
      </header>

      <ol className="stats-ranking-list" aria-label={`${table.title} ranking`}>
        {table.rows.map((row, rowIndex) => {
          const label = row[0] ?? `Row ${rowIndex + 1}`;
          const metrics = getRankingMetrics(table, row);
          const primaryMetric = getPrimaryRankingMetric(table, row);
          const supportingMetrics = primaryMetric
            ? metrics.filter((metric) => metric.label !== primaryMetric.label)
            : metrics;
          const magnitude = primaryMetric?.magnitude ?? null;
          const progress = maxMagnitude > 0 && magnitude !== null ? (magnitude / maxMagnitude) * 100 : null;

          return (
            <li className={`stats-ranking-item${rowIndex === 0 ? ' stats-ranking-item--leader' : ''}`} key={`ranking-${table.key}-${rowIndex}`}>
              <div className="stats-ranking-item__main">
                <span className="stats-ranking-item__rank" aria-hidden="true">
                  {rowIndex + 1}
                </span>
                <div className="stats-ranking-item__copy">
                  <p className="stats-ranking-item__label">{table.headers[0] ?? 'Item'}</p>
                  <h5 className="stats-ranking-item__title">{label}</h5>
                  {rowIndex === 0 ? <p className="stats-ranking-item__badge">Leader</p> : null}
                </div>
              </div>
              <div className="stats-ranking-item__trend">
                {primaryMetric ? (
                  <div className="stats-ranking-item__metric-callout">
                    <p className="stats-ranking-item__metric-label">{primaryMetric.label}</p>
                    <p className="stats-ranking-item__value">{primaryMetric.value}</p>
                  </div>
                ) : null}

                {supportingMetrics.length > 0 ? (
                  <dl className="stats-ranking-item__metrics">
                    {supportingMetrics.map((metric) => (
                      <div className="stats-ranking-item__metric" key={`${table.key}-${rowIndex}-${metric.label}`}>
                        <dt className="stats-ranking-item__metric-label">{metric.label}</dt>
                        <dd className="stats-ranking-item__metric-value">{metric.value}</dd>
                      </div>
                    ))}
                  </dl>
                ) : null}

                {progress !== null ? (
                  <div aria-hidden="true" className="stats-ranking-item__bar">
                    <span className="stats-ranking-item__fill" style={{ width: `${progress}%` }} />
                  </div>
                ) : null}
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

function StatsMetricsCard({ table }: StatsTableCardProps) {
  return (
    <section className="stats-card stats-card--metrics">
      <header className="stats-card__header">
        <h4 className="stats-card__title">{table.title}</h4>
        <p className="stats-card__meta">Compact breakdown</p>
      </header>

      <div className="stats-metric-grid">
        {table.rows.map((row, rowIndex) => {
          const label = row[0] ?? `Row ${rowIndex + 1}`;
          const value = row[1] ?? row.slice(1).join(' · ');

          return (
            <article className="stats-metric-tile" key={`metric-${table.key}-${rowIndex}`}>
              <p className="stats-metric-tile__label">{table.headers[0] ?? 'Item'}</p>
              <h5 className="stats-metric-tile__title">{label}</h5>
              <p className="stats-metric-tile__value">{value}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function getRankingMetrics(table: StatsTable, row: string[]): StatsMetric[] {
  return row.slice(1).map((value, valueIndex) => ({
    label: table.headers[valueIndex + 1] ?? `Column ${valueIndex + 2}`,
    value,
  }));
}

function getPrimaryRankingMetric(table: StatsTable, row: string[]) {
  const metrics = getRankingMetrics(table, row);
  const percentageMetric = metrics.find((metric) => metric.label.includes('%') || metric.value.includes('%'));
  const fallbackMetric = metrics.find((metric) => getStatMagnitude(metric.value) !== null) ?? metrics[0];
  const selectedMetric = percentageMetric ?? fallbackMetric;

  if (!selectedMetric) {
    return null;
  }

  return {
    ...selectedMetric,
    magnitude: getStatMagnitude(selectedMetric.value),
  };
}

function StatsStorySignalsCard({ signals }: StatsStorySignalsCardProps) {
  return (
    <section className="stats-card stats-card--metrics">
      <header className="stats-card__header">
        <h4 className="stats-card__title">Shared identity</h4>
        <p className="stats-card__meta">Quick read</p>
      </header>

      <div className="stats-metric-grid">
        {signals.map((signal) => (
          <article className="stats-metric-tile" key={`${signal.label}-${signal.value}`}>
            <p className="stats-metric-tile__label">{signal.label}</p>
            <h5 className="stats-metric-tile__title">{signal.value}</h5>
            <p className="stats-metric-tile__value stats-metric-tile__value--detail">{signal.detail}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function StatsSharedUnitsCard({ units }: StatsSharedUnitsCardProps) {
  return (
    <section className="stats-card stats-card--watchlist">
      <header className="stats-card__header">
        <h4 className="stats-card__title">Shared winner units</h4>
        <p className="stats-card__meta">Repeated across lists</p>
      </header>

      <ul className="stats-watchlist" aria-label="Shared winner units">
        {units.map((unit) => (
          <li className="stats-watchlist__item" key={unit.name}>
            <div>
              <h5 className="stats-watchlist__title">{unit.name}</h5>
              <p className="stats-watchlist__detail">
                {unit.listCount} lists · {unit.share}
              </p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

function StatsSharedPairsCard({ pairs }: StatsSharedPairsCardProps) {
  return (
    <section className="stats-card stats-card--watchlist">
      <header className="stats-card__header">
        <h4 className="stats-card__title">Recurring packages</h4>
        <p className="stats-card__meta">Pairs that keep returning</p>
      </header>

      <ul className="stats-watchlist" aria-label="Recurring winner packages">
        {pairs.map((pair) => (
          <li className="stats-watchlist__item" key={pair.units.join('|')}>
            <div>
              <h5 className="stats-watchlist__title">{pair.units.join(' + ')}</h5>
              <p className="stats-watchlist__detail">
                {pair.listCount} lists · {pair.share}
              </p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

function StatsSnapshotTrendsCard({ trends, mode }: StatsSnapshotTrendsCardProps) {
  return (
    <section className="stats-card stats-card--ranking stats-card--trend">
      <header className="stats-card__header">
        <h4 className="stats-card__title">{mode === 'weekly' ? 'Weekly winner trendlines' : 'Winner trendlines'}</h4>
        <p className="stats-card__meta">{mode === 'weekly' ? 'Current leaders across each visible week' : 'Current leaders across every visible checkpoint'}</p>
      </header>

      <ul className="stats-trend-list" aria-label={mode === 'weekly' ? 'Weekly trends' : 'Snapshot trends'}>
        {trends.map((trend) => {
          const summary = summarizeTrend(trend);

          return (
            <li className={`stats-trend-item stats-trend-item--${trend.direction}`} key={`${trend.metric}-${trend.label}`}>
              <div className="stats-trend-item__header">
                <div>
                  <p className="stats-trend-item__eyebrow">{trend.metric}</p>
                  <h5 className="stats-trend-item__title">{trend.label}</h5>
                </div>
                <div className="stats-trend-item__value-group">
                  <p className="stats-trend-item__value">{trend.currentValue}</p>
                  <p className="stats-trend-item__value-caption">Current</p>
                </div>
              </div>

              <p className="stats-trend-item__summary">{summary.narrative}</p>

              <dl className="stats-trend-metrics">
                <div className="stats-trend-metric">
                  <dt className="stats-trend-metric__label">Start</dt>
                  <dd className="stats-trend-metric__value">{summary.startValue}</dd>
                  <p className="stats-trend-metric__detail">{summary.startLabel}</p>
                </div>
                <div className="stats-trend-metric">
                  <dt className="stats-trend-metric__label">Peak</dt>
                  <dd className="stats-trend-metric__value">{summary.peakValue}</dd>
                  <p className="stats-trend-metric__detail">{summary.peakLabel}</p>
                </div>
                <div className="stats-trend-metric">
                  <dt className="stats-trend-metric__label">Net change</dt>
                  <dd className="stats-trend-metric__value">{trend.deltaLabel}</dd>
                  <p className="stats-trend-metric__detail">{summary.momentum}</p>
                </div>
              </dl>

              <StatsTrendSparkline trend={trend} />
            </li>
          );
        })}
      </ul>
    </section>
  );
}

type StatsTrendSparklineProps = {
  trend: ScopeStoryTrend;
};

function StatsTrendSparkline({ trend }: StatsTrendSparklineProps) {
  const points = trend.points
    .map((point, index) => ({
      ...point,
      index,
      magnitude: getStatMagnitude(point.value),
    }))
    .filter((point): point is typeof point & { magnitude: number } => point.magnitude !== null);

  const [activeDatasetKey, setActiveDatasetKey] = useState<string>(points[points.length - 1]?.datasetKey ?? '');

  useEffect(() => {
    setActiveDatasetKey(points[points.length - 1]?.datasetKey ?? '');
  }, [trend]);

  if (points.length < 2) {
    return null;
  }

  const width = 320;
  const height = 88;
  const paddingX = 12;
  const paddingY = 12;
  const minMagnitude = Math.min(...points.map((point) => point.magnitude));
  const maxMagnitude = Math.max(...points.map((point) => point.magnitude));
  const range = maxMagnitude - minMagnitude;
  const chartPoints = points.map((point, index) => {
    const x = paddingX + (index * (width - paddingX * 2)) / Math.max(points.length - 1, 1);
    const normalized = range === 0 ? 0.5 : (point.magnitude - minMagnitude) / range;
    const y = height - paddingY - normalized * (height - paddingY * 2);
    return {
      ...point,
      x,
      y,
      xPercent: (x / width) * 100,
      yPercent: (y / height) * 100,
    };
  });
  const polylinePoints = chartPoints.map((point) => `${point.x},${point.y}`).join(' ');
  const eraSegments = buildTrendEraSegments(chartPoints, width, paddingX);
  const activePoint = chartPoints.find((point) => point.datasetKey === activeDatasetKey) ?? chartPoints[chartPoints.length - 1];
  const visibleAxisIndices = getVisibleTrendAxisIndices(chartPoints.length);

  return (
    <div className="stats-trend-chart">
      {eraSegments.length > 1 ? (
        <div className="stats-trend-era-strip" aria-hidden="true">
          {eraSegments.map((segment) => (
            <span className="stats-trend-era-chip" key={`${trend.label}-${segment.label}`}>{segment.label}</span>
          ))}
        </div>
      ) : null}

      <div className="stats-trend-chart__frame">
        <svg aria-hidden="true" className="stats-trend-chart__svg" viewBox={`0 0 ${width} ${height}`}>
          {eraSegments.map((segment, index) => (
            <rect
              className={`stats-trend-chart__era-band${index % 2 === 1 ? ' stats-trend-chart__era-band--alternate' : ''}`}
              height={height - paddingY}
              key={`${trend.label}-${segment.label}`}
              width={segment.width}
              x={segment.x}
              y={0}
            />
          ))}
          {eraSegments.slice(1).map((segment) => (
            <line
              className="stats-trend-chart__divider"
              key={`${trend.label}-${segment.label}-divider`}
              x1={segment.x}
              x2={segment.x}
              y1={paddingY / 2}
              y2={height - paddingY}
            />
          ))}
          <line className="stats-trend-chart__guide" x1={paddingX} x2={width - paddingX} y1={height - paddingY} y2={height - paddingY} />
          <polyline className="stats-trend-chart__line" points={polylinePoints} />
        </svg>

        {chartPoints.map((point) => (
          <button
            aria-label={`${compactDatasetLabel(point.datasetLabel)} ${point.value}${point.eraLabel ? ` ${point.eraLabel}` : ''}`}
            className={`stats-trend-chart__hotspot${point.datasetKey === activePoint.datasetKey ? ' stats-trend-chart__hotspot--active' : ''}`}
            key={`${trend.label}-${point.datasetKey}`}
            onBlur={() => setActiveDatasetKey(chartPoints[chartPoints.length - 1]?.datasetKey ?? point.datasetKey)}
            onFocus={() => setActiveDatasetKey(point.datasetKey)}
            onMouseEnter={() => setActiveDatasetKey(point.datasetKey)}
            style={{ left: `${point.xPercent}%`, top: `${point.yPercent}%` }}
            type="button"
          >
            <span className="sr-only">{compactDatasetLabel(point.datasetLabel)}</span>
          </button>
        ))}
      </div>

      <div className="stats-trend-chart__detail">
        <p className="stats-trend-chart__detail-label">{compactDatasetLabel(activePoint.datasetLabel)}</p>
        <p className="stats-trend-chart__detail-value">{activePoint.value}</p>
        <p className="stats-trend-chart__detail-meta">{activePoint.eraLabel || 'Visible checkpoint'}</p>
      </div>

      <div className="stats-trend-axis" aria-hidden="true">
        {chartPoints
          .filter((point) => visibleAxisIndices.has(point.index))
          .map((point) => (
            <div className="stats-trend-axis__tick" key={`${trend.label}-${point.datasetKey}-axis`} style={{ left: `${point.xPercent}%` }}>
              <span className="stats-trend-axis__label">{compactDatasetLabel(point.datasetLabel)}</span>
              <span className="stats-trend-axis__value">{point.value}</span>
            </div>
          ))}
      </div>
    </div>
  );
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

function StatsWatchlistCard({ table }: StatsTableCardProps) {
  return (
    <section className="stats-card stats-card--watchlist">
      <header className="stats-card__header">
        <h4 className="stats-card__title">{table.title}</h4>
        <p className="stats-card__meta">Watchlist view</p>
      </header>

      <ul className="stats-watchlist" aria-label={`${table.title} watchlist`}>
        {table.rows.map((row, rowIndex) => {
          const label = row[0] ?? `Row ${rowIndex + 1}`;
          const detail = row.slice(1).filter(Boolean).join(' · ');

          return (
            <li className="stats-watchlist__item" key={`watch-${table.key}-${rowIndex}`}>
              <div>
                <h5 className="stats-watchlist__title">{label}</h5>
                {detail ? <p className="stats-watchlist__detail">{detail}</p> : null}
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}

type StatsResultBreakdownChartProps = {
  scope: ScopePayload;
  table: StatsTable;
};

function StatsResultBreakdownChart({ scope, table }: StatsResultBreakdownChartProps) {
  const maxMagnitude = table.rows.reduce((currentMax, row) => {
    const magnitude = getStatMagnitude(row[1] ?? '');
    return magnitude === null ? currentMax : Math.max(currentMax, magnitude);
  }, 0);

  return (
    <section className="stats-chart-card">
      <header className="stats-card__header">
        <h4 className="stats-card__title">Result mix</h4>
        <p className="stats-card__meta">Quick chart</p>
      </header>

      <div aria-label={`${table.title} chart`} className="stats-chart-list" role="list">
        {table.rows.map((row, rowIndex) => {
          const label = row[0] ?? `Row ${rowIndex + 1}`;
          const value = row[1] ?? '0';
          const magnitude = getStatMagnitude(value) ?? 0;
          const width = maxMagnitude > 0 ? (magnitude / maxMagnitude) * 100 : 0;
          const percentOfLists = scope.listCount > 0 ? `${((magnitude / scope.listCount) * 100).toFixed(1)}%` : null;

          return (
            <div className="stats-chart-row" key={`${table.key}-${rowIndex}`} role="listitem">
              <div className="stats-chart-row__header">
                <p className="stats-chart-row__label">{label}</p>
                <p className="stats-chart-row__value">
                  {value}
                  {percentOfLists ? ` · ${percentOfLists}` : ''}
                </p>
              </div>
              <div aria-hidden="true" className="stats-chart-row__track">
                <span className="stats-chart-row__fill" style={{ width: `${width}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function StatsTableCard({ table }: StatsTableCardProps) {
  const cardRef = useRef<HTMLElement | null>(null);
  const [isCondensed, setIsCondensed] = useState(false);

  useEffect(() => {
    const node = cardRef.current;
    if (!node || typeof ResizeObserver !== 'function') {
      return;
    }

    const observer = new ResizeObserver(([entry]) => {
      setIsCondensed(entry.contentRect.width < 420);
    });

    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return (
    <section className="stats-card" ref={cardRef}>
      <header className="stats-card__header">
        <h4 className="stats-card__title">{table.title}</h4>
        <p className="stats-card__meta">
          {table.rows.length} row{table.rows.length === 1 ? '' : 's'} · {table.headers.length} column{table.headers.length === 1 ? '' : 's'}
        </p>
      </header>

      {isCondensed ? <StatsCompactList table={table} /> : <StatsTableView table={table} />}
    </section>
  );
}

type StatsTableViewProps = {
  table: StatsTable;
};

function StatsTableView({ table }: StatsTableViewProps) {
  return (
    <div className="table-scroll-wrap table-scroll-wrap--framed">
      <table className="stats-table">
        <caption className="sr-only">{table.title}</caption>
        <thead>
          <tr>
            {table.headers.map((header) => (
              <th key={header} scope="col">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {table.rows.map((row, rowIndex) => (
            <tr key={`${table.key}-${rowIndex}`}>
              {row.map((value, valueIndex) => (
                <td
                  data-label={table.headers[valueIndex] ?? `Column ${valueIndex + 1}`}
                  key={`${table.key}-${rowIndex}-${valueIndex}`}
                >
                  {value}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

type StatsCompactListProps = {
  table: StatsTable;
};

function StatsCompactList({ table }: StatsCompactListProps) {
  const [primaryHeader, ...secondaryHeaders] = table.headers;

  return (
    <ol className="stats-compact-list" aria-label={`${table.title} condensed summary`}>
      {table.rows.map((row, rowIndex) => {
        const [primaryValue, ...secondaryValues] = row;

        return (
          <li className="stats-compact-item" key={`compact-${table.key}-${rowIndex}`}>
            <div className="stats-compact-item__main">
              <span className="stats-compact-item__rank" aria-hidden="true">
                {rowIndex + 1}
              </span>
              <div className="stats-compact-item__copy">
                <p className="stats-compact-item__eyebrow">{primaryHeader ?? 'Item'}</p>
                <h5 className="stats-compact-item__title">{primaryValue}</h5>
              </div>
            </div>

            <dl className="stats-compact-item__metrics">
              {secondaryValues.map((value, valueIndex) => (
                <div className="stats-compact-item__metric" key={`compact-${table.key}-${rowIndex}-${valueIndex}`}>
                  <dt className="stats-compact-item__label">
                    {secondaryHeaders[valueIndex] ?? `Column ${valueIndex + 2}`}
                  </dt>
                  <dd className="stats-compact-item__value">{value}</dd>
                </div>
              ))}
            </dl>
          </li>
        );
      })}
    </ol>
  );
}

function getStatMagnitude(value: string): number | null {
  const percentageMatch = value.match(/(\d+(?:\.\d+)?)%/);

  if (percentageMatch) {
    return Number(percentageMatch[1]);
  }

  const numericMatch = value.match(/-?\d+(?:\.\d+)?/);
  return numericMatch ? Number(numericMatch[0]) : null;
}

function summarizeTrend(trend: ScopeStoryTrend) {
  const firstPoint = trend.points[0];
  const lastPoint = trend.points[trend.points.length - 1];
  const pointsWithMagnitude = trend.points
    .map((point, index) => ({
      ...point,
      index,
      magnitude: getStatMagnitude(point.value),
    }))
    .filter((point): point is typeof point & { magnitude: number } => point.magnitude !== null);

  const peakPoint =
    pointsWithMagnitude.reduce<(typeof pointsWithMagnitude)[number] | null>((peak, point) => {
      if (!peak || point.magnitude > peak.magnitude) {
        return point;
      }
      return peak;
    }, null) ?? null;

  let rises = 0;
  let drops = 0;
  for (let index = 1; index < pointsWithMagnitude.length; index += 1) {
    const previous = pointsWithMagnitude[index - 1];
    const current = pointsWithMagnitude[index];
    if (current.magnitude > previous.magnitude) {
      rises += 1;
    } else if (current.magnitude < previous.magnitude) {
      drops += 1;
    }
  }

  let momentum = 'Held flat across the visible checkpoints.';
  if (rises > 0 && drops === 0) {
    momentum = 'Climbed without a visible drop.';
  } else if (drops > 0 && rises === 0) {
    momentum = 'Slid without a rebound.';
  } else if (rises > 0 && drops > 0) {
    momentum = 'Shifted in both directions before landing here.';
  }

  const startLabel = compactDatasetLabel(firstPoint?.datasetLabel ?? 'Current');
  const peakLabel = peakPoint ? compactDatasetLabel(peakPoint.datasetLabel) : startLabel;
  const startValue = firstPoint?.value ?? trend.currentValue;
  const peakValue = peakPoint?.value ?? trend.currentValue;
  const lastLabel = compactDatasetLabel(lastPoint?.datasetLabel ?? 'Current');
  const narrative = `Started at ${startValue} in ${startLabel} and sits at ${trend.currentValue} in ${lastLabel}.`;

  return {
    startLabel,
    startValue,
    peakLabel,
    peakValue,
    momentum,
    narrative,
  };
}

function compactDatasetLabel(label: string) {
  return label.startsWith('Snapshot (') ? label.slice(10, -1) : label;
}
