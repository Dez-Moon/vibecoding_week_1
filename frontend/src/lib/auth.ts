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

export async function register(username: string, password: string): Promise<CurrentUser> {
  if (!username.trim()) {
    throw new Error("Username is required");
  }
  if (password.length < 4) {
    throw new Error("Password must be at least 4 characters");
  }

  try {
    return await apiFetch<CurrentUser>("/api/register", {
      method: "POST",
      body: JSON.stringify({ username: username.trim(), password }),
    });
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.status === 409) {
        throw new Error("Username already taken");
      }
      if (error.status >= 500) {
        throw new Error("Server error. Please try again later.");
      }
      if (error.status === 422) {
        throw new Error("Invalid input. Please check your username and password.");
      }
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
