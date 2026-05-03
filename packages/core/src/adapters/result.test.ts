import { describe, expect, it } from "vitest";

import { err, ok } from "./result";

describe("Result", () => {
  it("ok and err", () => {
    expect(ok(42)).toEqual({ ok: true, data: 42 });
    expect(err("x")).toEqual({ ok: false, error: "x" });
  });
});
