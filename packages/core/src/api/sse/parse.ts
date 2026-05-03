export type SSEParsedEvent = {
  readonly event: string;
  readonly data: string;
  readonly id?: string;
};

export type SSEParserState = {
  readonly lineBuffer: string;
  readonly dataLines: readonly string[];
  readonly pendingEvent: string;
  readonly pendingId: string | undefined;
};

export const emptySSEParserState: SSEParserState = {
  lineBuffer: "",
  dataLines: [],
  pendingEvent: "message",
  pendingId: undefined,
};

const flushEvent = (
  state: SSEParserState,
): { state: SSEParserState; event: SSEParsedEvent | undefined } => {
  if (state.dataLines.length === 0) {
    return {
      state: {
        ...state,
        dataLines: [],
        pendingEvent: "message",
        pendingId: undefined,
      },
      event: undefined,
    };
  }
  const data = state.dataLines.join("\n");
  const event: SSEParsedEvent =
    state.pendingId !== undefined
      ? { event: state.pendingEvent, data, id: state.pendingId }
      : { event: state.pendingEvent, data };
  return {
    state: {
      ...state,
      dataLines: [],
      pendingEvent: "message",
      pendingId: undefined,
    },
    event,
  };
};

const processLine = (
  state: SSEParserState,
  line: string,
): { state: SSEParserState; events: readonly SSEParsedEvent[] } => {
  if (line === "") {
    const { state: next, event } = flushEvent(state);
    return { state: next, events: event !== undefined ? [event] : [] };
  }
  if (line.startsWith(":")) {
    return { state, events: [] };
  }
  const colon = line.indexOf(":");
  const field = colon === -1 ? line : line.slice(0, colon);
  const value = colon === -1 ? "" : line.slice(colon + 1).trimStart();

  if (field === "data") {
    return {
      state: { ...state, dataLines: [...state.dataLines, value] },
      events: [],
    };
  }
  if (field === "event") {
    return { state: { ...state, pendingEvent: value }, events: [] };
  }
  if (field === "id") {
    return { state: { ...state, pendingId: value }, events: [] };
  }
  return { state, events: [] };
};

/**
 * Incrementally parses SSE wire format from decoded UTF-8 chunks.
 * Pass `emptySSEParserState` as the initial state, then thread the returned state for each chunk.
 */
export const pushSSEChunk = (
  state: SSEParserState,
  chunk: string,
): { state: SSEParserState; events: readonly SSEParsedEvent[] } => {
  const combined = state.lineBuffer + chunk;
  const normalized = combined.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  const parts = normalized.split("\n");
  const newLineBuffer = parts.length > 0 ? (parts.pop() ?? "") : "";
  const fullLines = parts;

  const head: SSEParserState = {
    lineBuffer: "",
    dataLines: state.dataLines,
    pendingEvent: state.pendingEvent,
    pendingId: state.pendingId,
  };

  const outEvents: SSEParsedEvent[] = [];
  const finalState = fullLines.reduce((current, line) => {
    const { state: next, events: lineEvents } = processLine(current, line);
    outEvents.push(...lineEvents);
    return next;
  }, head);

  return {
    state: {
      ...finalState,
      lineBuffer: newLineBuffer,
    },
    events: outEvents,
  };
};
