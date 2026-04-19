import type { PropsWithChildren } from 'react';

type AppShellProps = PropsWithChildren<{
  title: string;
  subtitle: string;
  banner?: string;
}>;

export function AppShell({ title, subtitle, banner, children }: AppShellProps) {
  return (
    <main className="app-shell">
      <header className="app-shell__hero">
        <p className="eyebrow">Helsmiths of Hashut</p>
        <h1 className="app-title">{title}</h1>
        <p className="app-subtitle">{subtitle}</p>
        {banner ? <p className="banner">{banner}</p> : null}
      </header>
      {children}
    </main>
  );
}
