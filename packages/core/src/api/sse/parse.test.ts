import { describe, expect, it } from "vitest";

import { emptySSEParserState, pushSSEChunk } from "./parse";

describe("pushSSEChunk", () => {
  it("parses a single data event", () => {
    const a = pushSSEChunk(emptySSEParserState, "data: hello\n\n");
    expect(a.events).toEqual([{ event: "message", data: "hello" }]);
    expect(a.state.lineBuffer).toBe("");
  });

  it("joins multiline data and custom event", () => {
    const a = pushSSEChunk(
      emptySSEParserState,
      "event: tick\ndata: a\ndata: b\n\n",
    );
    expect(a.events).toEqual([{ event: "tick", data: "a\nb" }]);
  });

  it("carries incomplete lines across chunks", () => {
    const a = pushSSEChunk(emptySSEParserState, "data: he");
    expect(a.events).toEqual([]);
    const b = pushSSEChunk(a.state, "llo\n\n");
    expect(b.events).toEqual([{ event: "message", data: "hello" }]);
  });

  it("includes id when present", () => {
    const a = pushSSEChunk(emptySSEParserState, "id: 1\ndata: x\n\n");
    expect(a.events).toEqual([{ event: "message", data: "x", id: "1" }]);
  });
});
