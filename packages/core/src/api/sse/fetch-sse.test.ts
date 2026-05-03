import { describe, expect, it } from "vitest";

import { consumeSSEStream } from "./fetch-sse";

describe("consumeSSEStream", () => {
  it("decodes a stream of SSE frames", async () => {
    const received: { event: string; data: string }[] = [];
    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        const enc = new TextEncoder();
        controller.enqueue(enc.encode("data: one\n\ndata: two\n\n"));
        controller.close();
      },
    });

    await consumeSSEStream(stream, (e) => {
      received.push({ event: e.event, data: e.data });
    });

    expect(received).toEqual([
      { event: "message", data: "one" },
      { event: "message", data: "two" },
    ]);
  });
});
