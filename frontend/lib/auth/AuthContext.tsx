"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode
} from "react";

import {
  getCurrentUser,
  login as loginRequest,
  register as registerRequest,
  type AuthUser,
  type LoginPayload,
  type RegisterPayload
} from "@/lib/api/auth";

const TOKEN_STORAGE_KEY = "careeros_ai_access_token";

type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
  loadCurrentUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setToken(null);
    setUser(null);
  }, []);

  const loadCurrentUser = useCallback(async () => {
    const storedToken = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (!storedToken) {
      setUser(null);
      setToken(null);
      return;
    }

    const currentUser = await getCurrentUser(storedToken);
    setToken(storedToken);
    setUser(currentUser);
  }, []);

  useEffect(() => {
    let isMounted = true;

    async function hydrateSession() {
      try {
        const storedToken = localStorage.getItem(TOKEN_STORAGE_KEY);
        if (!storedToken) {
          return;
        }

        const currentUser = await getCurrentUser(storedToken);
        if (isMounted) {
          setToken(storedToken);
          setUser(currentUser);
        }
      } catch {
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        if (isMounted) {
          setToken(null);
          setUser(null);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void hydrateSession();

    return () => {
      isMounted = false;
    };
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    const tokenResponse = await loginRequest(payload);
    localStorage.setItem(TOKEN_STORAGE_KEY, tokenResponse.access_token);
    setToken(tokenResponse.access_token);
    const currentUser = await getCurrentUser(tokenResponse.access_token);
    setUser(currentUser);
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    await registerRequest(payload);
    const tokenResponse = await loginRequest({
      email: payload.email,
      password: payload.password
    });
    localStorage.setItem(TOKEN_STORAGE_KEY, tokenResponse.access_token);
    setToken(tokenResponse.access_token);
    const currentUser = await getCurrentUser(tokenResponse.access_token);
    setUser(currentUser);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(user && token),
      isLoading,
      login,
      register,
      logout,
      loadCurrentUser
    }),
    [isLoading, loadCurrentUser, login, logout, register, token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
