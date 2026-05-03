/** True when `value` is empty or contains only whitespace. */
export const isBlank = (value: string): boolean => value.trim() === "";

/** True when `value` has at least one non-whitespace character. */
export const isNonBlank = (value: string): boolean => !isBlank(value);
