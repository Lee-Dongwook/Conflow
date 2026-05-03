export interface APIError extends Error {
  code: string;
  message: string;
  details?: unknown;
}
