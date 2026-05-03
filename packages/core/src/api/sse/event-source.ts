export type ConnectEventSourceOptions = {
  readonly withCredentials?: boolean;
  readonly signal?: AbortSignal;
  readonly onMessage: (payload: {
    readonly data: string;
    readonly lastEventId: string;
  }) => void;
  readonly onError?: (event: Event) => void;
};

/**
 * Browser `EventSource` wrapper with optional `AbortSignal` (calls `close()` on abort).
 * For named events (`event:`), use the returned `EventSource` and `addEventListener`.
 */
export const connectEventSource = (
  url: string | URL,
  options: ConnectEventSourceOptions,
): EventSource => {
  if (typeof EventSource === "undefined") {
    throw new Error("EventSource is not available in this environment");
  }

  const es = new EventSource(url, {
    withCredentials: options.withCredentials ?? false,
  });

  const onAbort = () => {
    es.close();
  };
  options.signal?.addEventListener("abort", onAbort, { once: true });

  es.onmessage = (event: MessageEvent<string>) => {
    options.onMessage({
      data: event.data,
      lastEventId: event.lastEventId,
    });
  };

  if (options.onError !== undefined) {
    es.onerror = options.onError;
  }

  return es;
};
