import { describe, expect, it } from "vitest";

import { assignSearchParams, searchParamsFromRecord } from "./search-params";

describe("searchParamsFromRecord", () => {
  it("omits undefined and stringifies values", () => {
    const p = searchParamsFromRecord({
      a: 1,
      b: true,
      c: "x",
      d: undefined,
    });
    expect(p.get("a")).toBe("1");
    expect(p.get("b")).toBe("true");
    expect(p.get("c")).toBe("x");
    expect(p.has("d")).toBe(false);
  });

  it("appends array values", () => {
    const p = searchParamsFromRecord({ tag: ["a", "b"] });
    expect(p.getAll("tag")).toEqual(["a", "b"]);
  });
});

describe("assignSearchParams", () => {
  it("mutates the target params instance", () => {
    const target = new URLSearchParams("x=1");
    assignSearchParams(target, { y: 2 });
    expect(target.get("x")).toBe("1");
    expect(target.get("y")).toBe("2");
  });
});
