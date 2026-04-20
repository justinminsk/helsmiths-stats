import { useEffect, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { Dashboard } from '../components/dashboard/Dashboard';
import { loadSiteData } from '../lib/data/loadSiteData';
import { sampleSiteData } from '../testing/sampleSiteData';
import type { SiteDataPayload } from '../models/siteData';

type LoadState =
  | { status: 'loading' }
  | { status: 'ready'; payload: SiteDataPayload; source: 'live' | 'sample' }
  | { status: 'error'; message: string; fallback: SiteDataPayload };

type StatusPanelProps = {
  title: string;
  detail: string;
  tone?: 'neutral' | 'warning';
};

function StatusPanel({ title, detail, tone = 'neutral' }: StatusPanelProps) {
  return (
    <section aria-live="polite" className={`status-panel status-panel--${tone}`} role="status">
      <p className="status-panel__eyebrow">Dashboard state</p>
      <h2 className="status-panel__title">{title}</h2>
      <p className="status-panel__detail">{detail}</p>
    </section>
  );
}

export function App() {
  const [state, setState] = useState<LoadState>({ status: 'loading' });

  useEffect(() => {
    let active = true;

    async function bootstrap() {
      try {
        const payload = await loadSiteData();
        if (!active) {
          return;
        }
        setState({ status: 'ready', payload, source: 'live' });
      } catch (error) {
        if (!active) {
          return;
        }

        setState({
          status: 'error',
          message:
            error instanceof Error
              ? error.message
              : 'Unknown error while loading site data.',
          fallback: sampleSiteData,
        });
      }
    }

    void bootstrap();
    return () => {
      active = false;
    };
  }, []);

  if (state.status === 'loading') {
    return (
      <AppShell title="Helsmith Stats" subtitle="Play rates of winning lists">
        <StatusPanel
          detail="Loading the latest Helsmith list data and summary views."
          title="Preparing dashboard"
        />
      </AppShell>
    );
  }

  if (state.status === 'error') {
    return (
      <AppShell
        title="Helsmith Stats"
        subtitle="Play rates of winning lists"
        banner="Latest data unavailable. Showing bundled sample data instead."
        bannerTone="warning"
      >
        <StatusPanel detail={state.message} title="Sample data fallback active" tone="warning" />
        <Dashboard payload={state.fallback} />
      </AppShell>
    );
  }

  return (
    <AppShell
      title="Helsmith Stats"
      subtitle="Play rates of winning lists"
      bannerTone={state.source === 'sample' ? 'sample' : 'success'}
      banner={
        state.source === 'sample'
          ? 'Showing bundled sample data.'
          : 'Loaded Helsmith list data successfully.'
      }
    >
      <Dashboard payload={state.payload} />
    </AppShell>
  );
}
