import { err, ok, type Result } from "../adapters/result";

/**
 * Parses a JSON string into `unknown`. Use Zod (or similar) in the business
 * layer to refine to domain types.
 */
export const parseJsonUnknown = (text: string): Result<unknown, string> => {
  try {
    const parsed: unknown = JSON.parse(text);
    return ok(parsed);
  } catch (e: unknown) {
    const message = e instanceof Error ? e.message : String(e);
    return err(`invalid_json:${message}`);
  }
};
