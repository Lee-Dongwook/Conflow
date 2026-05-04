const clampUnit = (value: number): number => {
  if (!Number.isFinite(value)) {
    return 0;
  }
  return Math.min(1, Math.max(0, value));
};

export type BackoffOptions = {
  readonly baseMs: number;
  readonly maxMs: number;
  /** 0–1: scales random spread (see `randomUnit`). */
  readonly jitter: number;
};

/**
 * Exponential backoff capped at `maxMs`, with multiplicative jitter (pure).
 * Pass `randomUnit` from `Math.random()` at the call site when needed.
 *
 * - `attempt` 0 → factor `2^0`, after each failure increment (0-based).
 * - With positive `jitter`, delay is `raw * (1 - randomUnit * jitter)` in `[raw*(1-jitter), raw]`.
 */
export const computeBackoffMs = (
  attempt: number,
  options: BackoffOptions,
  randomUnit: number,
): number => {
  const { baseMs, maxMs, jitter } = options;
  const base = Math.max(0, baseMs);
  const max = Math.max(base, maxMs);
  const a = Math.max(0, Math.trunc(attempt));
  const raw = Math.min(max, base * 2 ** a);
  const j = clampUnit(jitter);
  const u = clampUnit(randomUnit);
  return raw * (1 - u * j);
};
