import { ApiError, apiFetch } from "@/lib/api";

export interface CurrentUser {
  username: string;
}

export async function login(username: string, password: string): Promise<CurrentUser> {
  try {
    return await apiFetch<CurrentUser>("/api/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      throw new Error("Invalid credentials");
    }
    throw error;
  }
}

export async function logout(): Promise<void> {
  try {
    await apiFetch<null>("/api/logout", { method: "POST" });
  } catch {
    // best-effort: cookie may already be gone
  }
}

export async function getCurrentUser(): Promise<CurrentUser | null> {
  try {
    return await apiFetch<CurrentUser>("/api/whoami");
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      return null;
    }
    throw error;
  }
}
