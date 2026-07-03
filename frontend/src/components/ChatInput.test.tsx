import { render, screen, fireEvent } from "@testing-library/react";
import { ChatInput } from "./ChatInput";

describe("ChatInput", () => {
  it("renders input and send button", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);
    expect(screen.getByPlaceholderText("Ask me to manage your board...")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Send" })).toBeInTheDocument();
  });

  it("calls onSend when form is submitted", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    const input = screen.getByPlaceholderText("Ask me to manage your board...");
    fireEvent.change(input, { target: { value: "Test message" } });
    fireEvent.submit(screen.getByRole("button", { name: "Send" }));

    expect(onSend).toHaveBeenCalledWith("Test message");
  });

  it("clears input after submit", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    const input = screen.getByPlaceholderText("Ask me to manage your board...");
    fireEvent.change(input, { target: { value: "Test message" } });
    fireEvent.submit(screen.getByRole("button", { name: "Send" }));

    expect((input as HTMLInputElement).value).toBe("");
  });

  it("does not submit empty messages", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    fireEvent.submit(screen.getByRole("button", { name: "Send" }));
    expect(onSend).not.toHaveBeenCalled();
  });

  it("is disabled when disabled prop is true", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} disabled />);

    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
  });
});
