import { describe, expect, it } from "vitest";

import { isBlank, isNonBlank } from "./string";

describe("string utils", () => {
  it("isBlank", () => {
    expect(isBlank("")).toBe(true);
    expect(isBlank("   ")).toBe(true);
    expect(isBlank("\t\n")).toBe(true);
    expect(isBlank("a")).toBe(false);
    expect(isBlank(" a ")).toBe(false);
  });

  it("isNonBlank", () => {
    expect(isNonBlank("")).toBe(false);
    expect(isNonBlank("x")).toBe(true);
    expect(isNonBlank("  y  ")).toBe(true);
  });
});
