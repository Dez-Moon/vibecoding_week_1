import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/lib/api";
import { getCurrentUser, login, logout } from "@/lib/auth";

const fetchMock = vi.fn();

describe("auth helpers", () => {
  afterEach(() => {
    fetchMock.mockReset();
    vi.restoreAllMocks();
  });

  it("login posts credentials and returns the user", async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      status: 200,
      text: () => Promise.resolve(JSON.stringify({ username: "user" })),
    });
    vi.stubGlobal("fetch", fetchMock);

    const user = await login("user", "password");

    expect(user).toEqual({ username: "user" });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/login",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        body: JSON.stringify({ username: "user", password: "password" }),
      }),
    );
  });

  it("login throws Invalid credentials on 401", async () => {
    fetchMock.mockResolvedValueOnce({
      ok: false,
      status: 401,
      text: () => Promise.resolve(JSON.stringify({ detail: "Invalid credentials" })),
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(login("user", "wrong")).rejects.toThrow("Invalid credentials");
  });

  it("logout swallows failures", async () => {
    fetchMock.mockRejectedValueOnce(new Error("network"));
    vi.stubGlobal("fetch", fetchMock);

    await expect(logout()).resolves.toBeUndefined();
  });

  it("getCurrentUser returns null on 401", async () => {
    fetchMock.mockResolvedValueOnce({
      ok: false,
      status: 401,
      text: () => Promise.resolve(""),
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(getCurrentUser()).resolves.toBeNull();
  });

  it("getCurrentUser throws on non-401 errors", async () => {
    fetchMock.mockResolvedValueOnce({
      ok: false,
      status: 500,
      text: () => Promise.resolve("oops"),
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(getCurrentUser()).rejects.toBeInstanceOf(ApiError);
  });
});
