import axios, { type AxiosInstance } from "axios";

import { DEFAULT_REQUEST_TIMEOUT_MS } from "../constants/http";

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

  return instance;
};
