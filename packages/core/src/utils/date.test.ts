import { describe, expect, it } from "vitest";

import {
  addDaysUTC,
  formatISODateUTC,
  isValidDate,
  parseISODateOnlyUTC,
  startOfDayUTC,
} from "./date";

describe("date utils", () => {
  it("isValidDate", () => {
    expect(isValidDate(new Date(NaN))).toBe(false);
    expect(isValidDate(new Date(0))).toBe(true);
    expect(isValidDate({})).toBe(false);
  });

  it("parseISODateOnlyUTC", () => {
    expect(parseISODateOnlyUTC("2024-03-15")).toEqual(
      new Date(Date.UTC(2024, 2, 15)),
    );
    expect(parseISODateOnlyUTC("2024-02-30")).toBe(null);
    expect(parseISODateOnlyUTC("24-01-01")).toBe(null);
    expect(parseISODateOnlyUTC("not-a-date")).toBe(null);
  });

  it("formatISODateUTC", () => {
    expect(formatISODateUTC(new Date(Date.UTC(2025, 0, 7)))).toBe("2025-01-07");
  });

  it("startOfDayUTC", () => {
    const d = new Date(Date.UTC(2025, 4, 3, 14, 30, 0));
    expect(startOfDayUTC(d)).toEqual(
      new Date(Date.UTC(2025, 4, 3, 0, 0, 0, 0)),
    );
  });

  it("addDaysUTC", () => {
    const base = new Date(Date.UTC(2025, 0, 31, 12, 0, 0));
    expect(addDaysUTC(base, 1)).toEqual(
      new Date(Date.UTC(2025, 1, 1, 12, 0, 0)),
    );
    expect(addDaysUTC(base, -1)).toEqual(
      new Date(Date.UTC(2025, 0, 30, 12, 0, 0)),
    );
    expect(addDaysUTC(base, 1.9)).toEqual(addDaysUTC(base, 1));
  });
});
