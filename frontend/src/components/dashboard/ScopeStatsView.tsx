import type { ScopePayload } from '../../models/siteData';

type ScopeStatsViewProps = {
  datasetKey: string;
  scope: ScopePayload;
};

export function ScopeStatsView({ datasetKey, scope }: ScopeStatsViewProps) {
  return (
    <section
      aria-labelledby={`scope-view-${datasetKey}-${scope.key}-stats`}
      className="scope-view"
      id={`scope-view-${datasetKey}-${scope.key}-stats`}
      role="tabpanel"
    >
      <p className="view-link-row">
        <a className="scope-link" href={scope.reportLinks.stats}>
          Open markdown report
        </a>
      </p>
      <p className="stats-summary">Summary: {scope.statsSummary}</p>

      <div className="stats-grid">
        {scope.statsTables.map((table) => (
          <section className="stats-card" key={table.key}>
            <h4 className="stats-card__title">{table.title}</h4>
            <div className="table-scroll-wrap">
              <table>
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
                        <td key={`${table.key}-${rowIndex}-${valueIndex}`}>{value}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ))}
      </div>
    </section>
  );
}