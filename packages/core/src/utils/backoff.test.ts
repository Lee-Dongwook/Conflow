import { describe, expect, it } from "vitest";

import { computeBackoffMs } from "./backoff";

const opts = {
  baseMs: 100,
  maxMs: 10_000,
  jitter: 0.25,
} as const;

describe("computeBackoffMs", () => {
  it("doubles exponential base until max", () => {
    expect(computeBackoffMs(0, { ...opts, jitter: 0 }, 0)).toBe(100);
    expect(computeBackoffMs(1, { ...opts, jitter: 0 }, 0)).toBe(200);
    expect(computeBackoffMs(2, { ...opts, jitter: 0 }, 0)).toBe(400);
  });

  it("caps at maxMs", () => {
    expect(computeBackoffMs(20, { ...opts, jitter: 0 }, 0)).toBe(10_000);
  });

  it("applies jitter range with randomUnit", () => {
    const raw = computeBackoffMs(0, opts, 0);
    const low = computeBackoffMs(0, opts, 1);
    expect(low).toBeLessThan(raw);
    expect(low).toBeCloseTo(75, 5);
    expect(raw).toBe(100);
  });
});
