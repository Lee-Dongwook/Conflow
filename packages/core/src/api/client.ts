import axios, {
  type AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
} from "axios";

export interface APIClientOptions {
  baseURL: string;
  timeout?: number;
  withCredentials?: boolean;
}

type TokenAccessor = () => string | null;
type TokenSetter = (token: string | null) => void;
type OnRefreshToken = () => Promise<string | null>;
type OnUnauthorized = () => void;

export const createBaseAPIClient = (
  config: APIClientOptions,
): AxiosInstance => {
  const instance = axios.create({
    baseURL: config.baseURL,
    withCredentials: config.withCredentials ?? true,
    timeout: config.timeout ?? 10000,
  });

  return instance;
};
