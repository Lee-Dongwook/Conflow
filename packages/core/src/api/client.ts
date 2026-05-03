import axios, { type AxiosInstance } from "axios";

import { DEFAULT_REQUEST_TIMEOUT_MS } from "../constants/http";

import { toAPIError } from "./errors";

export interface APIClientOptions {
  baseURL: string;
  timeout?: number;
  withCredentials?: boolean;
}

export const createBaseAPIClient = (
  config: APIClientOptions,
): AxiosInstance => {
  const instance = axios.create({
    baseURL: config.baseURL,
    withCredentials: config.withCredentials ?? true,
    timeout: config.timeout ?? DEFAULT_REQUEST_TIMEOUT_MS,
  });

  instance.interceptors.response.use(
    (response) => response,
    (error: unknown) => Promise.reject(toAPIError(error)),
  );

  return instance;
};
