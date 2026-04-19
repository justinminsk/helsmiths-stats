import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Dashboard } from '../components/dashboard/Dashboard';
import { sampleSiteData } from '../testing/sampleSiteData';

describe('Dashboard', () => {
  it('renders dataset and scope metadata from the typed contract', () => {
    render(<Dashboard payload={sampleSiteData} />);

    expect(screen.getByRole('tab', { name: 'Current' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Combined' })).toBeInTheDocument();
    expect(screen.getByText(/Lists parsed: 12/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Open markdown report' })).toHaveAttribute(
      'href',
      'reports/current/combined.md'
    );
  });

  it('switches into lists view and filters lists by text', () => {
    render(<Dashboard payload={sampleSiteData} />);

    fireEvent.click(screen.getAllByRole('tab', { name: 'Lists' })[0]);
    expect(screen.getByPlaceholderText('Search source, name, or unit')).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText('Search source, name, or unit'), {
      target: { value: 'Bull' },
    });

    expect(screen.getAllByText('Sample List')).toHaveLength(2);
  });
});