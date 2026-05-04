import { describe, expect, it } from "vitest";

import { joinBaseUrlAndPath } from "./base-url";

describe("joinBaseUrlAndPath", () => {
  it("merges base and path slashes", () => {
    expect(joinBaseUrlAndPath("https://api.example.com", "v1/users")).toBe(
      "https://api.example.com/v1/users",
    );
    expect(joinBaseUrlAndPath("https://api.example.com/", "/v1/users")).toBe(
      "https://api.example.com/v1/users",
    );
    expect(joinBaseUrlAndPath("https://api.example.com///", "///a")).toBe(
      "https://api.example.com/a",
    );
  });
});
