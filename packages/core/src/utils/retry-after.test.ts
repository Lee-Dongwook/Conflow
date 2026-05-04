import { describe, expect, it } from "vitest";

import { parseRetryAfter } from "./retry-after";

describe("parseRetryAfter", () => {
  it("parses delay-seconds as milliseconds", () => {
    expect(parseRetryAfter("120", 0)).toBe(120_000);
    expect(parseRetryAfter("  30 ", 0)).toBe(30_000);
  });

  it("parses HTTP-date as ms until that instant", () => {
    const abs = Date.parse("Wed, 21 Oct 2015 07:28:00 GMT");
    const tenSecBefore = abs - 10_000;
    expect(parseRetryAfter("Wed, 21 Oct 2015 07:28:00 GMT", tenSecBefore)).toBe(
      10_000,
    );
    expect(parseRetryAfter("Wed, 21 Oct 2015 07:28:00 GMT", abs)).toBe(0);
  });

  it("returns null for empty or invalid", () => {
    expect(parseRetryAfter(null, 0)).toBe(null);
    expect(parseRetryAfter(undefined, 0)).toBe(null);
    expect(parseRetryAfter("", 0)).toBe(null);
    expect(parseRetryAfter("   ", 0)).toBe(null);
    expect(parseRetryAfter("not-a-date", 0)).toBe(null);
  });
});
