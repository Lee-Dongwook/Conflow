import { describe, expect, it } from "vitest";

import { parseJsonUnknown } from "./json";

describe("parseJsonUnknown", () => {
  it("returns ok for valid JSON", () => {
    const r = parseJsonUnknown('{"a":1}');
    expect(r.ok).toBe(true);
    if (r.ok) {
      expect(r.data).toEqual({ a: 1 });
    }
  });

  it("returns err for invalid JSON", () => {
    const r = parseJsonUnknown("{");
    expect(r.ok).toBe(false);
    if (!r.ok) {
      expect(r.error.startsWith("invalid_json:")).toBe(true);
    }
  });
});
