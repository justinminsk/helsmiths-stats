import type { PropsWithChildren } from 'react';

type AppShellProps = PropsWithChildren<{
  title: string;
  subtitle: string;
  banner?: string;
  bannerTone?: 'neutral' | 'success' | 'sample' | 'warning';
}>;

export function AppShell({ title, subtitle, banner, bannerTone = 'neutral', children }: AppShellProps) {
  return (
    <main className="app-shell">
      <header className="app-shell__hero">
        <div className="app-shell__hero-grid">
          <div className="app-shell__hero-copy">
            <div className="app-shell__eyebrow-row">
              <p className="eyebrow">Helsmiths of Hashut</p>
              <p className="hero-kicker">Python data pipeline · React interface</p>
            </div>
            <div className="app-shell__title-block">
              <h1 className="app-title">{title}</h1>
              <p className="app-subtitle">{subtitle}</p>
            </div>
          </div>

          <dl className="hero-facts" aria-label="Dashboard summary">
            <div className="hero-fact">
              <dt>Source</dt>
              <dd>Python-generated site contract</dd>
            </div>
            <div className="hero-fact">
              <dt>Views</dt>
              <dd>Summary tables and list explorer</dd>
            </div>
            <div className="hero-fact">
              <dt>Output</dt>
              <dd>Static reports plus routeable React UI</dd>
            </div>
          </dl>
        </div>
        {banner ? (
          <p aria-atomic="true" aria-live="polite" className={`banner banner--${bannerTone}`} role="status">
            {banner}
          </p>
        ) : null}
      </header>
      {children}
    </main>
  );
}
