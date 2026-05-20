import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { getAccessToken, setAccessToken } from "@/lib/authToken";

type RetriableRequestConfig = InternalAxiosRequestConfig & {
  _retry?: boolean;
};

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshPromise: Promise<string | null> | null = null;

export async function refreshAccessToken(): Promise<string | null> {
  try {
    const response = await api.post<{ access_token: string }>("/auth/refresh");
    const nextToken = response.data?.access_token;
    if (!nextToken) return null;
    setAccessToken(nextToken);
    return nextToken;
  } catch {
    setAccessToken(null);
    return null;
  }
}

function isAuthEndpoint(url?: string): boolean {
  if (!url) return false;
  return (
    url.includes("/auth/challenge") ||
    url.includes("/auth/verify") ||
    url.includes("/auth/refresh")
  );
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetriableRequestConfig | undefined;
    const status = error.response?.status;

    if (
      status !== 401 ||
      !originalRequest ||
      originalRequest._retry ||
      isAuthEndpoint(originalRequest.url)
    ) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    if (!refreshPromise) {
      refreshPromise = refreshAccessToken().finally(() => {
        refreshPromise = null;
      });
    }

    const refreshedToken = await refreshPromise;
    if (!refreshedToken) {
      if (typeof window !== "undefined") {
        window.dispatchEvent(new Event("auth:logout"));
      }
      return Promise.reject(error);
    }

    originalRequest.headers = originalRequest.headers ?? {};
    originalRequest.headers.Authorization = `Bearer ${refreshedToken}`;
    return api.request(originalRequest);
  }
);
