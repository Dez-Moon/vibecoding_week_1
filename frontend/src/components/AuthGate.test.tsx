import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

const getCurrentUser = vi.fn();
const replace = vi.fn();

vi.mock("@/lib/auth", () => ({
  getCurrentUser: () => getCurrentUser(),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
}));

import { AuthGate, useCurrentUser } from "@/components/AuthGate";

const Consumer = () => {
  const user = useCurrentUser();
  return <div>{user ? `hello ${user.username}` : "no user"}</div>;
};

afterEach(() => {
  getCurrentUser.mockReset();
  replace.mockReset();
});

describe("AuthGate", () => {
  it("redirects to /login when unauthenticated and hides children", async () => {
    getCurrentUser.mockResolvedValue(null);
    render(
      <AuthGate>
        <Consumer />
      </AuthGate>,
    );

    await waitFor(() => {
      expect(replace).toHaveBeenCalledWith("/login");
    });
    expect(screen.queryByText(/^hello /)).not.toBeInTheDocument();
  });

  it("renders children with the current user when authenticated", async () => {
    getCurrentUser.mockResolvedValue({ username: "user" });
    render(
      <AuthGate>
        <Consumer />
      </AuthGate>,
    );

    expect(await screen.findByText("hello user")).toBeInTheDocument();
    expect(replace).not.toHaveBeenCalled();
  });
});
