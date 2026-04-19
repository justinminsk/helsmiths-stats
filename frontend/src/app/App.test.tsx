import { fireEvent, render, screen, within } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { Dashboard } from '../components/dashboard/Dashboard';
import { sampleSiteData } from '../testing/sampleSiteData';

describe('Dashboard', () => {
  beforeEach(() => {
    window.location.hash = '';
    window.localStorage.clear();
  });

  it('renders dataset and scope metadata from the typed contract', () => {
    render(<Dashboard payload={sampleSiteData} />);

    expect(screen.getByRole('tab', { name: 'Current' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Combined' })).toBeInTheDocument();
    expect(screen.getByRole('tabpanel', { name: 'Current' })).toBeInTheDocument();
    expect(screen.getByRole('tabpanel', { name: 'Combined' })).toBeInTheDocument();
    expect(screen.getByRole('tabpanel', { name: 'Stats' })).toBeInTheDocument();
    expect(screen.getByLabelText('Lists parsed: 12')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Open markdown report' })).toHaveAttribute(
      'href',
      'reports/current/combined.md'
    );
  });

  it('supports keyboard navigation across scope tabs', () => {
    render(<Dashboard payload={sampleSiteData} />);

    const combinedTab = screen.getAllByRole('tab', { name: 'Combined' }).at(-1);
    expect(combinedTab).toBeDefined();

    fireEvent.keyDown(combinedTab!, { key: 'ArrowRight' });

    const singlesTab = screen.getAllByRole('tab', { name: 'Singles' }).at(-1);
    expect(singlesTab).toBeDefined();

    expect(singlesTab!).toHaveAttribute('aria-selected', 'true');
    expect(singlesTab!).toHaveFocus();
    expect(screen.getByRole('tabpanel', { name: 'Singles' })).toBeInTheDocument();
  });

  it('switches into lists view and filters lists by text', () => {
    render(<Dashboard payload={sampleSiteData} />);

    fireEvent.click(screen.getAllByRole('tab', { name: 'Lists' })[0]);
    expect(screen.getByPlaceholderText('Search source, name, or unit')).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText('Search source, name, or unit'), {
      target: { value: 'Bull' },
    });

    expect(screen.getAllByText('Sample List')).toHaveLength(3);
    expect(window.location.hash).toBe('#tab=current|combined|lists');
  });

  it('shows a winners-at-a-glance section in lists view', () => {
    render(<Dashboard payload={sampleSiteData} />);

    fireEvent.click(screen.getAllByRole('tab', { name: 'Lists' })[0]);

    const winnersHeading = screen.getByRole('heading', { name: 'Scan the current winner pool' });
    const winnersSection = winnersHeading.closest('section');

    expect(winnersSection).not.toBeNull();
    expect(screen.getByRole('heading', { name: 'Scan the current winner pool' })).toBeInTheDocument();
    expect(
      screen.getByText('All lists here are winners. Use record tiers as a supporting lens, not the main story.')
    ).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'How the current winner pool is split' })).toBeInTheDocument();
    expect(screen.getByLabelText('Winning record tiers')).toBeInTheDocument();
    expect(screen.getAllByText('5-0').length).toBeGreaterThan(0);
    expect(screen.getAllByText('4-1').length).toBeGreaterThan(0);
    expect(within(winnersSection!).getAllByRole('heading', { level: 6 }).length).toBeGreaterThan(0);
  });

  it('resets list controls after a no-results filter state', () => {
    render(<Dashboard payload={sampleSiteData} />);

    fireEvent.click(screen.getAllByRole('tab', { name: 'Lists' })[0]);
    fireEvent.change(screen.getByPlaceholderText('Search source, name, or unit'), {
      target: { value: 'zzz' },
    });

    expect(screen.getByRole('heading', { name: 'Adjust the current filters' })).toBeInTheDocument();
    fireEvent.click(screen.getAllByRole('button', { name: 'Reset all list controls' })[0]);

    expect(screen.getByPlaceholderText('Search source, name, or unit')).toHaveValue('');
    expect(screen.getAllByText('Sample List')).toHaveLength(3);
  });

  it('announces theme toggles in the action area', () => {
    render(<Dashboard payload={sampleSiteData} />);

    const themeToggle = screen.getAllByRole('button', { name: 'Switch to light theme' }).at(-1);
    expect(themeToggle).toBeDefined();

    fireEvent.click(themeToggle!);

    expect(screen.getAllByRole('status').at(-1)).toHaveTextContent('Switched to light theme.');
  });

  it('groups stats into rankings, compact breakdowns, and watchlists', () => {
    render(<Dashboard payload={sampleSiteData} />);

    expect(screen.getAllByRole('heading', { name: 'Fast read before the full breakdowns' }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole('heading', { name: 'What winners share' }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole('heading', { name: 'How the winner profile shifts each week' }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole('heading', { name: 'Top rankings first' }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole('heading', { name: 'Compact distribution groups' }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole('heading', { name: 'Missing or inactive options' }).length).toBeGreaterThan(0);
    expect(screen.getAllByText('Shared winner units').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Weekly winner trendlines').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Most common result').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Most common lore').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Result mix').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Pre-points era').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Post-points era').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Urak Taar, the First Daemonsmith').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Bull Centaurs').length).toBeGreaterThan(0);
    expect(screen.getAllByText('+50.0 pts versus April 6-12').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Start').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Peak').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Net change').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Started at 50.0% in April 6-12 and sits at 100.0% in April 20-26.').length).toBeGreaterThan(0);
    expect(screen.getAllByText('April 20-26').length).toBeGreaterThan(0);
    expect(screen.getAllByText('6 · 50.0%').length).toBeGreaterThan(0);
    expect(screen.getAllByText("Taar's Grand Forgehost").length).toBeGreaterThan(0);
    expect(screen.getAllByText('Urak Taar, the First Daemonsmith').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Leader').length).toBeGreaterThan(0);
    expect(screen.getAllByText('% of lists').length).toBeGreaterThan(0);
    expect(screen.getAllByText('100.0%').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Forbidden Power').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Infernal Razers with Flamehurlers').length).toBeGreaterThan(0);
  });
});
