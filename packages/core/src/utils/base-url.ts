/**
 * Joins an API-style `baseURL` (with or without trailing slash) and a path
 * (with or without leading slash). Pure string normalization — no URL parsing.
 */
export const joinBaseUrlAndPath = (baseURL: string, path: string): string => {
  const base = baseURL.replace(/\/+$/, "");
  const segment = path.replace(/^\/+/, "");
  return `${base}/${segment}`;
};
