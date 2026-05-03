/** Joins Tailwind / conditional class fragments; skips empty or falsy entries. */
export const cn = (
  ...parts: readonly (string | undefined | false | null)[]
): string =>
  parts
    .filter((p): p is string => typeof p === "string" && p.trim().length > 0)
    .join(" ");
