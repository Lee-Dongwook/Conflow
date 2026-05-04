/**
 * Truncates toward zero then clamps to `[min, max]`. All arguments must be finite.
 */
export const clampInt = (value: number, min: number, max: number): number => {
  const t = Math.trunc(value);
  return Math.min(Math.max(t, min), max);
};
