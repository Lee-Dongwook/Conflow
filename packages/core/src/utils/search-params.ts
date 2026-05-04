export type SearchParamScalar = string | number | boolean;

export type SearchParamValue =
  | SearchParamScalar
  | readonly SearchParamScalar[]
  | undefined;

/**
 * Applies key/value pairs to a `URLSearchParams`. Omits keys whose value is
 * `undefined`. Arrays append multiple entries with the same key.
 */
export const assignSearchParams = (
  target: URLSearchParams,
  record: Readonly<Record<string, SearchParamValue>>,
): URLSearchParams => {
  Object.entries(record).forEach(([key, value]) => {
    if (value === undefined) {
      return;
    }
    if (Array.isArray(value)) {
      value.forEach((item) => {
        target.append(key, String(item));
      });
      return;
    }
    target.set(key, String(value));
  });
  return target;
};

/**
 * Builds a new `URLSearchParams` from a plain record (stable key order follows
 * `Object.entries`).
 */
export const searchParamsFromRecord = (
  record: Readonly<Record<string, SearchParamValue>>,
): URLSearchParams => {
  const params = new URLSearchParams();
  return assignSearchParams(params, record);
};
