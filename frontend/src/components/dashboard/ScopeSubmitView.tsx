import { useState } from 'react';

type ScopeSubmitViewProps = {
  tabId: string;
};

export function ScopeSubmitView({ tabId }: ScopeSubmitViewProps) {
  const [tournamentLink, setTournamentLink] = useState('');
  const [wins, setWins] = useState<number | ''>('');
  const [losses, setLosses] = useState<number | ''>('');
  const [listText, setListText] = useState('');

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    const title = `List Submission: ${wins}-${losses}`;
    const body = `**Tournament Link**: ${tournamentLink}

**Wins**: ${wins}
**Losses**: ${losses}

### Army List

\`\`\`
${listText}
\`\`\`
`;

    const url = new URL('https://github.com/justinminsk/helsmiths-stats/issues/new');
    url.searchParams.set('title', title);
    url.searchParams.set('body', body);

    window.open(url.toString(), '_blank', 'noopener,noreferrer');
  }

  return (
    <section
      aria-labelledby={tabId}
      className="scope-view scope-view--submit"
      role="tabpanel"
    >
      <header className="view-header">
        <div>
          <p className="view-kicker">Submit List</p>
          <h4 className="view-title">Add your list to the database</h4>
        </div>
      </header>

      <section className="stats-summary-card">
        <p className="stats-summary" style={{ marginBottom: '1.5rem' }}>
          Fill out the form below to submit a tournament list. This will generate a pre-filled GitHub issue on our repository for review.
        </p>

        <form onSubmit={handleSubmit} className="submit-list-form">
          <div className="form-group">
            <label htmlFor="tournamentLink">Tournament Link (BCP, Ecksen, etc.)</label>
            <input
              id="tournamentLink"
              type="url"
              required
              value={tournamentLink}
              onChange={(e) => setTournamentLink(e.target.value)}
              placeholder="https://..."
              className="form-input"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="wins">Wins</label>
              <input
                id="wins"
                type="number"
                required
                min="0"
                value={wins}
                onChange={(e) => setWins(e.target.value ? Number(e.target.value) : '')}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label htmlFor="losses">Losses</label>
              <input
                id="losses"
                type="number"
                required
                min="0"
                value={losses}
                onChange={(e) => setLosses(e.target.value ? Number(e.target.value) : '')}
                className="form-input"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="listText">Plain Text Army List</label>
            <textarea
              id="listText"
              required
              rows={12}
              value={listText}
              onChange={(e) => setListText(e.target.value)}
              placeholder="Paste the raw text of the army list here..."
              className="form-input"
            />
          </div>

          <button type="submit" className="form-submit-button action-pill" style={{ marginTop: '1rem', background: 'var(--color-accent-strong)', color: 'white', fontWeight: 'bold' }}>
            Generate GitHub Issue
          </button>
        </form>
      </section>
    </section>
  );
}
