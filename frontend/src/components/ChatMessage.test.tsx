import { render, screen } from "@testing-library/react";
import { ChatMessage } from "./ChatMessage";

describe("ChatMessage", () => {
  it("renders user message correctly", () => {
    render(<ChatMessage message={{ role: "user", content: "Hello AI" }} />);
    expect(screen.getByText("Hello AI")).toBeInTheDocument();
  });

  it("renders AI message correctly", () => {
    render(<ChatMessage message={{ role: "assistant", content: "Hello human" }} />);
    expect(screen.getByText("Hello human")).toBeInTheDocument();
  });
});
