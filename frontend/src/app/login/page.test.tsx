import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

const login = vi.fn();
const replace = vi.fn();

vi.mock("@/lib/auth", () => ({
  login: (username: string, password: string) => login(username, password),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
}));

import LoginPage from "@/app/login/page";

afterEach(() => {
  login.mockReset();
  replace.mockReset();
});

describe("LoginPage", () => {
  it("submits credentials, navigates on success", async () => {
    login.mockResolvedValue({ username: "user" });
    render(<LoginPage />);

    await userEvent.type(screen.getByTestId("input-username"), "user");
    await userEvent.type(screen.getByTestId("input-password"), "password");
    await userEvent.click(screen.getByTestId("submit-login"));

    await waitFor(() => {
      expect(login).toHaveBeenCalledWith("user", "password");
    });
    await waitFor(() => {
      expect(replace).toHaveBeenCalledWith("/");
    });
  });

  it("shows an error on failed login", async () => {
    login.mockRejectedValue(new Error("Invalid credentials"));
    render(<LoginPage />);

    await userEvent.type(screen.getByTestId("input-username"), "user");
    await userEvent.type(screen.getByTestId("input-password"), "wrong");
    await userEvent.click(screen.getByTestId("submit-login"));

    expect(await screen.findByTestId("error-message")).toHaveTextContent(
      "Invalid credentials",
    );
    expect(replace).not.toHaveBeenCalled();
  });
});
