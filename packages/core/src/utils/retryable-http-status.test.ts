import { describe, expect, it } from "vitest";

import { isRetryableHttpStatus } from "./retryable-http-status";

describe("isRetryableHttpStatus", () => {
  it("is true for 408, 429, and 5xx", () => {
    expect(isRetryableHttpStatus(408)).toBe(true);
    expect(isRetryableHttpStatus(429)).toBe(true);
    expect(isRetryableHttpStatus(500)).toBe(true);
    expect(isRetryableHttpStatus(502)).toBe(true);
    expect(isRetryableHttpStatus(503)).toBe(true);
    expect(isRetryableHttpStatus(504)).toBe(true);
    expect(isRetryableHttpStatus(599)).toBe(true);
  });

  it("is false for typical client errors", () => {
    expect(isRetryableHttpStatus(400)).toBe(false);
    expect(isRetryableHttpStatus(401)).toBe(false);
    expect(isRetryableHttpStatus(404)).toBe(false);
    expect(isRetryableHttpStatus(422)).toBe(false);
  });

  it("is false for non-retryable success and redirects", () => {
    expect(isRetryableHttpStatus(200)).toBe(false);
    expect(isRetryableHttpStatus(301)).toBe(false);
  });
});
