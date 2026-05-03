import type { SSEParsedEvent } from "./parse";
import { emptySSEParserState, pushSSEChunk } from "./parse";

export type ConsumeSSEStreamOptions = {
  readonly signal?: AbortSignal;
};

/**
 * Reads a `fetch` response body as Server-Sent Events and invokes `onEvent` for each parsed event.
 * Use when you need custom headers, POST bodies, or environments without `EventSource`.
 */
export const consumeSSEStream = async (
  body: ReadableStream<Uint8Array>,
  onEvent: (event: SSEParsedEvent) => void,
  options?: ConsumeSSEStreamOptions,
): Promise<void> => {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let parseState = emptySSEParserState;

  try {
    while (true) {
      if (options?.signal?.aborted) {
        throw options.signal.reason;
      }
      const { done, value } = await reader.read();
      if (options?.signal?.aborted) {
        throw options.signal.reason;
      }
      if (done) {
        const tail = decoder.decode();
        if (tail.length > 0) {
          const parsed = pushSSEChunk(parseState, tail);
          parseState = parsed.state;
          for (const ev of parsed.events) {
            onEvent(ev);
          }
        }
        return;
      }
      const chunk = decoder.decode(value, { stream: true });
      const parsed = pushSSEChunk(parseState, chunk);
      parseState = parsed.state;
      for (const ev of parsed.events) {
        onEvent(ev);
      }
    }
  } finally {
    reader.releaseLock();
  }
};

export type FetchSSEOptions = RequestInit & {
  readonly onEvent: (event: SSEParsedEvent) => void;
};

/**
 * `fetch` with `Accept: text/event-stream`, then parses the body as SSE.
 */
export const fetchSSE = async (
  input: string | URL | Request,
  init: FetchSSEOptions,
): Promise<void> => {
  const { onEvent, ...rest } = init;
  const headers = new Headers(rest.headers);
  if (!headers.has("Accept")) {
    headers.set("Accept", "text/event-stream");
  }

  const response = await fetch(input, {
    ...rest,
    headers,
  });

  if (!response.ok) {
    throw new Error(`SSE request failed: ${String(response.status)}`);
  }

  if (response.body === null) {
    throw new Error("SSE response has no body");
  }

  const consumeOptions =
    rest.signal != null ? { signal: rest.signal } : undefined;
  await consumeSSEStream(response.body, onEvent, consumeOptions);
};
