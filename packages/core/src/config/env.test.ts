import { describe, expect, it } from "vitest";
import { envSchema } from "./env";

describe("Env Schema Test", () => {
  it("VITE_USE_MOCK", () => {
    const parsed = envSchema.parse({
      VITE_API_BASE_URL: "https://api.example.com",
      VITE_USE_MOCK: "false",
    });

    expect(parsed).toEqual({
      VITE_API_BASE_URL: "https://api.example.com",
      VITE_USE_MOCK: false,
    });
  });
});
