const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const TOKEN_KEY = "ebbvocab_token";
const USER_EMAIL_KEY = "ebbvocab_user_email";
const AUTH_ERROR_KEY = "ebbvocab_auth_error";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function getUserEmail(): string {
  return localStorage.getItem(USER_EMAIL_KEY) ?? "";
}

export function setUserEmail(email: string): void {
  localStorage.setItem(USER_EMAIL_KEY, email);
}

export function clearUserEmail(): void {
  localStorage.removeItem(USER_EMAIL_KEY);
}

export function clearAuthStorage(): void {
  clearToken();
  clearUserEmail();
}

export function consumeAuthError(): string {
  const msg = localStorage.getItem(AUTH_ERROR_KEY) ?? "";
  if (msg) {
    localStorage.removeItem(AUTH_ERROR_KEY);
  }
  return msg;
}

function handleUnauthorized() {
  clearAuthStorage();
  localStorage.setItem(AUTH_ERROR_KEY, "Token 已失效，请重新登录。");
  window.location.assign("/login");
}

function isPublicAuthPath(path: string): boolean {
  return path.startsWith("/auth/");
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit & { bodyJson?: unknown } = {},
): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers ?? {});
  const isAuthPath = isPublicAuthPath(path);
  const shouldSendAuthHeader = Boolean(token) && !isAuthPath;

  if (options.bodyJson !== undefined) {
    headers.set("Content-Type", "application/json");
  }
  if (shouldSendAuthHeader && token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    body: options.bodyJson !== undefined ? JSON.stringify(options.bodyJson) : options.body,
  });

  const contentType = response.headers.get("content-type") ?? "";
  const rawBody = await response.text();
  const isJson = contentType.includes("application/json");
  const data = isJson && rawBody ? JSON.parse(rawBody) : null;

  if (response.status === 401 && shouldSendAuthHeader) {
    handleUnauthorized();
    throw new Error("Unauthorized");
  }

  if (!response.ok) {
    const detail =
      typeof data?.detail === "string"
        ? data.detail
        : rawBody || `请求失败 (${response.status})`;
    throw new Error(detail);
  }

  return data as T;
}
