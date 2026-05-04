/**
 * HTTP statuses where repeating the **same** request later may succeed
 * (timeouts, rate limits, server/gateway failures). Not domain-specific.
 */
export const isRetryableHttpStatus = (status: number): boolean => {
  if (!Number.isFinite(status)) {
    return false;
  }
  const code = Math.trunc(status);
  if (code === 408 || code === 429) {
    return true;
  }
  return code >= 500 && code <= 599;
};
