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
      <AppShell title="Helsmith Stats" subtitle="React dashboard migration in progress">
        <p className="status-message">Loading the Python-generated site contract…</p>
      </AppShell>
    );
  }

  if (state.status === 'error') {
    return (
      <AppShell
        title="Helsmith Stats"
        subtitle="React dashboard migration in progress"
        banner={`Live contract unavailable. Showing bundled sample data instead. ${state.message}`}
      >
        <Dashboard payload={state.fallback} />
      </AppShell>
    );
  }

  return (
    <AppShell
      title="Helsmith Stats"
      subtitle="React dashboard migration in progress"
      banner={
        state.source === 'sample'
          ? 'Showing bundled sample data.'
          : 'Loaded the Python-generated site contract successfully.'
      }
    >
      <Dashboard payload={state.payload} />
    </AppShell>
  );
}
