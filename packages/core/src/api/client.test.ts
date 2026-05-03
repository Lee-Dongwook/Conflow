import http from "node:http";

import { describe, expect, it } from "vitest";

import { createBaseAPIClient } from "./client";
import { APIError } from "./errors";

describe("createBaseAPIClient", () => {
  it("normalizes failed HTTP responses to APIError", async () => {
    const server = http.createServer((_req, res) => {
      res.statusCode = 502;
      res.setHeader("Content-Type", "application/json");
      res.end(JSON.stringify({ message: "Bad gateway" }));
    });

    await new Promise<void>((resolve, reject) => {
      server.listen(0, "127.0.0.1", () => resolve());
      server.on("error", reject);
    });

    const address = server.address();
    if (address === null || typeof address === "string") {
      await new Promise<void>((resolve, reject) => {
        server.close((err) => (err ? reject(err) : resolve()));
      });
      throw new Error("expected socket address");
    }

    const client = createBaseAPIClient({
      baseURL: `http://127.0.0.1:${String(address.port)}`,
    });

    try {
      let caught: unknown;
      try {
        await client.get("/");
      } catch (e) {
        caught = e;
      }
      expect(caught).toBeInstanceOf(APIError);
      expect(caught).toMatchObject({
        name: "APIError",
        code: "HTTP_502",
        message: "Bad gateway",
      });
    } finally {
      await new Promise<void>((resolve, reject) => {
        server.close((err) => (err ? reject(err) : resolve()));
      });
    }
  });
});
