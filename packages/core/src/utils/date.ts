/** True when `value` is a `Date` with a finite time value. */
export const isValidDate = (value: unknown): value is Date =>
  value instanceof Date && !Number.isNaN(value.getTime());

const ISO_DATE_ONLY = /^(\d{4})-(\d{2})-(\d{2})$/;

/**
 * Parses a `YYYY-MM-DD` string as UTC midnight. Returns `null` if the string
 * is malformed or not a real calendar date (e.g. `2024-02-30`).
 */
export const parseISODateOnlyUTC = (iso: string): Date | null => {
  const match = ISO_DATE_ONLY.exec(iso);
  if (match === null) {
    return null;
  }
  const year = Number(match[1]);
  const monthIndex = Number(match[2]) - 1;
  const day = Number(match[3]);
  const candidate = new Date(Date.UTC(year, monthIndex, day));
  if (!isValidDate(candidate)) {
    return null;
  }
  if (
    candidate.getUTCFullYear() !== year ||
    candidate.getUTCMonth() !== monthIndex ||
    candidate.getUTCDate() !== day
  ) {
    return null;
  }
  return candidate;
};

/** UTC calendar date as `YYYY-MM-DD` (ISO 8601 date-only). */
export const formatISODateUTC = (d: Date): string => {
  const y = d.getUTCFullYear();
  const m = String(d.getUTCMonth() + 1).padStart(2, "0");
  const day = String(d.getUTCDate()).padStart(2, "0");
  return `${String(y)}-${m}-${day}`;
};

/** Same UTC calendar day at `00:00:00.000` UTC. */
export const startOfDayUTC = (d: Date): Date =>
  new Date(
    Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate(), 0, 0, 0, 0),
  );

/**
 * Adds whole UTC calendar days. Non-integers are truncated toward zero
 * (same direction as `Math.trunc`).
 */
export const addDaysUTC = (d: Date, days: number): Date => {
  const next = new Date(d.getTime());
  next.setUTCDate(next.getUTCDate() + Math.trunc(days));
  return next;
};
