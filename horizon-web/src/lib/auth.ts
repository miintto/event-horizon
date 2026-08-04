const TOKEN_KEY = "horizon.token";

export const LOGIN_PATH = "/login";

/** 정적 프리렌더 중에는 localStorage 가 없으므로 항상 null */
export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  window.localStorage.removeItem(TOKEN_KEY);
}

/** 토큰을 버리고 로그인 화면으로. 이미 로그인 화면이면 아무것도 하지 않는다 */
export function redirectToLogin(): void {
  if (typeof window === "undefined") return;
  clearToken();
  if (window.location.pathname !== LOGIN_PATH) {
    window.location.href = LOGIN_PATH;
  }
}
