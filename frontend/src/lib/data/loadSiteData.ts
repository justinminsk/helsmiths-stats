import type { SiteDataPayload } from '../../models/siteData';
import { assertSiteDataPayload } from '../../models/siteData';

const SITE_DATA_PATH = `${import.meta.env.BASE_URL}data/site-data.json`;

export async function loadSiteData(
  fetchImpl: typeof fetch = fetch
): Promise<SiteDataPayload> {
  const response = await fetchImpl(SITE_DATA_PATH, {
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to load site data: ${response.status} ${response.statusText}`);
  }

  const payload = (await response.json()) as unknown;
  return assertSiteDataPayload(payload);
}

export { SITE_DATA_PATH };