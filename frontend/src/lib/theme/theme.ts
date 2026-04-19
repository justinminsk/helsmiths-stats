import type { SiteDataPayload, ThemeTokenMap } from '../../models/siteData';

export type ThemeMode = 'dark' | 'light';

function toCssVariableName(tokenName: string) {
  return `--${tokenName.replace(/[A-Z]/g, (character) => `-${character.toLowerCase()}`)}`;
}

function applyTokenMap(tokenMap: ThemeTokenMap) {
  const root = document.documentElement;
  for (const [tokenName, tokenValue] of Object.entries(tokenMap)) {
    root.style.setProperty(toCssVariableName(tokenName), tokenValue);
  }
}

export function getStoredTheme(storageKey: string): ThemeMode | null {
  const stored = window.localStorage.getItem(storageKey);
  if (stored === 'dark' || stored === 'light') {
    return stored;
  }
  return null;
}

export function getInitialTheme(storageKey: string): ThemeMode {
  return (
    getStoredTheme(storageKey) ??
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
  );
}

export function storeTheme(storageKey: string, theme: ThemeMode) {
  window.localStorage.setItem(storageKey, theme);
}

export function applyThemeTokens(payload: SiteDataPayload['themeTokens'], theme: ThemeMode) {
  applyTokenMap(payload[theme]);
}
