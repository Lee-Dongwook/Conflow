import { type AxiosError, isAxiosError } from "axios";

const extractMessageFromResponseData = (data: unknown): string | undefined => {
  if (typeof data !== "object" || data === null) {
    return undefined;
  }
  if (!("message" in data)) {
    return undefined;
  }
  const message = (data as { message: unknown }).message;
  return typeof message === "string" ? message : undefined;
};

const resolveAxiosErrorCode = (error: AxiosError<unknown>): string => {
  const status = error.response?.status;
  if (status !== undefined) {
    return `HTTP_${String(status)}`;
  }
  const code = error.code;
  if (typeof code === "string" && code.length > 0) {
    return code;
  }
  return "NETWORK_ERROR";
};

export class APIError extends Error {
  readonly code: string;
  readonly details?: unknown;

  constructor(code: string, message: string, details?: unknown) {
    super(message);
    this.name = "APIError";
    this.code = code;
    if (details !== undefined) {
      this.details = details;
    }
  }
}

export const isAPIError = (error: unknown): error is APIError =>
  error instanceof APIError;

export const fromAxiosError = (error: AxiosError<unknown>): APIError => {
  const data = error.response?.data;
  const messageFromBody = extractMessageFromResponseData(data);
  const message = messageFromBody ?? (error.message || "Request failed");
  const code = resolveAxiosErrorCode(error);
  const details = {
    status: error.response?.status,
    axiosCode: error.code,
    data: error.response?.data,
  };
  return new APIError(code, message, details);
};

export const toAPIError = (error: unknown): APIError => {
  if (isAPIError(error)) {
    return error;
  }
  if (isAxiosError(error)) {
    return fromAxiosError(error);
  }
  if (error instanceof Error) {
    return new APIError("UNKNOWN", error.message, { cause: error });
  }
  return new APIError("UNKNOWN", "Unknown error", { original: error });
};
