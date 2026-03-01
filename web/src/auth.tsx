import { createContext, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  clearAuthStorage,
  getToken,
  getUserEmail,
  setToken as persistToken,
  setUserEmail as persistUserEmail,
} from "./api";

type AuthContextValue = {
  token: string | null;
  userEmail: string;
  isAuthenticated: boolean;
  login: (token: string, email: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getToken());
  const [userEmail, setUserEmail] = useState<string>(() => getUserEmail());

  function login(nextToken: string, email: string) {
    persistToken(nextToken);
    persistUserEmail(email);
    setToken(nextToken);
    setUserEmail(email);
  }

  function logout() {
    clearAuthStorage();
    setToken(null);
    setUserEmail("");
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      userEmail,
      isAuthenticated: Boolean(token),
      login,
      logout,
    }),
    [token, userEmail],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
