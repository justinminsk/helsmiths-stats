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
    expect(screen.getByRole('tab', { name: 'Trends' })).toBeInTheDocument();
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

    fireEvent.click(screen.getAllByRole('tab', { name: 'Lists' }).at(-1)!);
    const listsPanel = screen.getAllByRole('tabpanel', { name: 'Lists' }).at(-1)!;

    expect(within(listsPanel).getByPlaceholderText('Search source, name, or unit')).toBeInTheDocument();

    fireEvent.change(within(listsPanel).getByPlaceholderText('Search source, name, or unit'), {
      target: { value: 'Bull' },
    });

    expect(within(listsPanel).getAllByText('Sample List')).toHaveLength(2);
    expect(window.location.hash).toBe('#tab=current|combined|lists');
  });

  it('filters and sorts lists by week in lists view', () => {
    render(<Dashboard payload={sampleSiteData} />);

    fireEvent.click(screen.getAllByRole('tab', { name: 'Lists' }).at(-1)!);
    const listsPanel = screen.getAllByRole('tabpanel', { name: 'Lists' }).at(-1)!;

    fireEvent.change(within(listsPanel).getByRole('combobox', { name: 'Week' }), {
      target: { value: 'April 13-19' },
    });

    expect(within(listsPanel).getByText('Week: April 13-19')).toBeInTheDocument();
    expect(within(listsPanel).getByText('Showing 1 of 1 matching lists.')).toBeInTheDocument();
    expect(within(listsPanel).getAllByText('Ashen Pressure').length).toBeGreaterThan(0);
    expect(within(listsPanel).queryByText('Sample List')).not.toBeInTheDocument();

    fireEvent.change(within(listsPanel).getByRole('combobox', { name: 'Sort' }), {
      target: { value: 'week-asc' },
    });

    expect(within(listsPanel).getByText('Sort: Week (earliest first)')).toBeInTheDocument();
  });

  it('opens the trends view and lets you change rollups and picks', () => {
    render(<Dashboard payload={sampleSiteData} />);

    fireEvent.click(screen.getAllByRole('tab', { name: 'Trends' })[0]);

    expect(screen.getByRole('heading', { name: 'Compare units and rollups over time' })).toBeInTheDocument();
    expect(screen.getByLabelText('Trend comparison chart')).toBeInTheDocument();
    expect(screen.getAllByText('Bull Centaurs').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Jan 1-11').length).toBeGreaterThan(0);

    fireEvent.change(screen.getByRole('combobox', { name: 'Rollup' }), { target: { value: 'twoWeek' } });

    expect(screen.getAllByText('Jan 1-11 to Mar 23-29').length).toBeGreaterThan(0);

    fireEvent.change(screen.getByRole('combobox', { name: 'Metric' }), { target: { value: 'subfaction' } });

    expect(screen.getAllByText("Taar's Grand Forgehost").length).toBeGreaterThan(0);
    expect(window.location.hash).toBe('#tab=current|combined|trends');
  });

  it('shows a winners-at-a-glance section in lists view', () => {
    render(<Dashboard payload={sampleSiteData} />);

    fireEvent.click(screen.getAllByRole('tab', { name: 'Lists' }).at(-1)!);
    const listsPanel = screen.getAllByRole('tabpanel', { name: 'Lists' }).at(-1)!;

    const winnersHeading = within(listsPanel).getByRole('heading', { name: 'Scan the current winner pool' });
    const winnersSection = winnersHeading.closest('section');

    expect(winnersSection).not.toBeNull();
    expect(within(listsPanel).getByRole('heading', { name: 'Scan the current winner pool' })).toBeInTheDocument();
    expect(
      within(listsPanel).getByText('All lists here are winners. Lead with recurring units, subfactions, and lores, then use record tiers as a supporting lens.')
    ).toBeInTheDocument();
    expect(within(listsPanel).getByRole('heading', { name: 'Supporting result split' })).toBeInTheDocument();
    expect(within(listsPanel).getByLabelText('Winning record tiers')).toBeInTheDocument();
    expect(within(listsPanel).getAllByText('5-0').length).toBeGreaterThan(0);
    expect(within(listsPanel).getAllByText('4-1').length).toBeGreaterThan(0);
    expect(within(winnersSection!).getAllByRole('article').length).toBeGreaterThan(0);
  });

  it('resets list controls after a no-results filter state', () => {
    render(<Dashboard payload={sampleSiteData} />);

    fireEvent.click(screen.getAllByRole('tab', { name: 'Lists' }).at(-1)!);
    const listsPanel = screen.getAllByRole('tabpanel', { name: 'Lists' }).at(-1)!;

    fireEvent.change(within(listsPanel).getByPlaceholderText('Search source, name, or unit'), {
      target: { value: 'zzz' },
    });

    expect(within(listsPanel).getByRole('heading', { name: 'Adjust the current filters' })).toBeInTheDocument();
    fireEvent.click(within(listsPanel).getAllByRole('button', { name: 'Reset all list controls' }).at(-1)!);

    expect(within(listsPanel).getByPlaceholderText('Search source, name, or unit')).toHaveValue('');
    expect(within(listsPanel).getAllByText('Sample List')).toHaveLength(2);
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
    expect(screen.getAllByRole('heading', { name: 'Top rankings first' }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole('heading', { name: 'Compact distribution groups' }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole('heading', { name: 'Missing or inactive options' }).length).toBeGreaterThan(0);
    expect(screen.getAllByText('Shared winner units').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Most common lore').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Result mix').length).toBeGreaterThan(0);
    expect(screen.queryByRole('heading', { name: 'Result breakdown' })).not.toBeInTheDocument();
    expect(screen.getAllByText('Urak Taar, the First Daemonsmith').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Bull Centaurs').length).toBeGreaterThan(0);
    expect(screen.getAllByText("Taar's Grand Forgehost").length).toBeGreaterThan(0);
    expect(screen.getAllByText('Urak Taar, the First Daemonsmith').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Leader').length).toBeGreaterThan(0);
    expect(screen.getAllByText('% of lists').length).toBeGreaterThan(0);
    expect(screen.getAllByText('100.0%').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Forbidden Power').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Infernal Razers with Flamehurlers').length).toBeGreaterThan(0);
  });
});
