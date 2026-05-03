import type { InternalAxiosRequestConfig } from "axios";
import { AxiosError } from "axios";
import { describe, expect, it } from "vitest";

import { APIError, fromAxiosError, isAPIError, toAPIError } from "./errors";

const minimalConfig = {} as InternalAxiosRequestConfig;

describe("APIError", () => {
  it("fromAxiosError uses HTTP code and body message", () => {
    const axiosError = new AxiosError(
      "Request failed with status 422",
      "ERR_BAD_RESPONSE",
      undefined,
      undefined,
      {
        data: { message: "Invalid payload" },
        status: 422,
        statusText: "Unprocessable Entity",
        headers: {},
        config: minimalConfig,
      },
    );

    const api = fromAxiosError(axiosError);
    expect(api).toBeInstanceOf(APIError);
    expect(api.code).toBe("HTTP_422");
    expect(api.message).toBe("Invalid payload");
    expect(api.details).toEqual({
      status: 422,
      axiosCode: "ERR_BAD_RESPONSE",
      data: { message: "Invalid payload" },
    });
  });

  it("fromAxiosError falls back when no response", () => {
    const axiosError = new AxiosError(
      "Network Error",
      "ERR_NETWORK",
      undefined,
      undefined,
      undefined,
    );

    const api = fromAxiosError(axiosError);
    expect(api.code).toBe("ERR_NETWORK");
    expect(api.message).toBe("Network Error");
  });

  it("toAPIError normalizes unknown", () => {
    const axiosError = new AxiosError(
      "fail",
      "ERR_BAD_REQUEST",
      undefined,
      undefined,
      {
        data: {},
        status: 400,
        statusText: "Bad Request",
        headers: {},
        config: minimalConfig,
      },
    );
    expect(toAPIError(axiosError).code).toBe("HTTP_400");
    expect(toAPIError(new APIError("X", "msg")).code).toBe("X");
    expect(toAPIError(new Error("boom")).code).toBe("UNKNOWN");
    expect(toAPIError("literal").message).toBe("Unknown error");
    expect(isAPIError(toAPIError(new Error("e")))).toBe(true);
  });
});
