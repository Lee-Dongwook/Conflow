import { describe, expect, it } from "vitest";

import { clampInt } from "./clamp";

describe("clampInt", () => {
  it("truncates toward zero then clamps", () => {
    expect(clampInt(3.9, 0, 10)).toBe(3);
    expect(clampInt(-2.9, -5, 5)).toBe(-2);
    expect(clampInt(100, 0, 10)).toBe(10);
    expect(clampInt(-1, 0, 10)).toBe(0);
  });
});
