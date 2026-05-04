const DELAY_SECONDS = /^\d+$/;

/**
 * Parses `Retry-After` (RFC 7231): delay-seconds **or** HTTP-date.
 * Returns **milliseconds** until the client may retry, relative to `nowMs`.
 * Use when scheduling retries from `429` / `503` (etc.) responses.
 */
export const parseRetryAfter = (
  value: string | null | undefined,
  nowMs: number = Date.now(),
): number | null => {
  if (value === null || value === undefined) {
    return null;
  }
  const trimmed = value.trim();
  if (trimmed.length === 0) {
    return null;
  }
  if (DELAY_SECONDS.test(trimmed)) {
    const seconds = Number(trimmed);
    return seconds * 1000;
  }
  const absoluteMs = Date.parse(trimmed);
  if (Number.isNaN(absoluteMs)) {
    return null;
  }
  return Math.max(0, absoluteMs - nowMs);
};
