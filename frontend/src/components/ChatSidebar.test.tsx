import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import { ChatSidebar } from "./ChatSidebar";

const mockSendChatMessage = vi.fn();

vi.mock("@/lib/chat", () => ({
  sendChatMessage: (...args: unknown[]) => mockSendChatMessage(...args),
}));

describe("ChatSidebar", () => {
  const onBoardRefresh = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock scrollIntoView which isn't implemented in jsdom
    Element.prototype.scrollIntoView = vi.fn();
  });

  it("renders empty state when no messages", () => {
    render(<ChatSidebar isOpen={true} onClose={vi.fn()} onBoardRefresh={onBoardRefresh} />);
    expect(screen.getByText("How can I help?")).toBeInTheDocument();
  });

  it("does not render when isOpen is false", () => {
    render(<ChatSidebar isOpen={false} onClose={vi.fn()} onBoardRefresh={onBoardRefresh} />);
    expect(screen.queryByText("AI Assistant")).not.toBeInTheDocument();
  });

  it("has a close button", () => {
    const onClose = vi.fn();
    render(<ChatSidebar isOpen={true} onClose={onClose} onBoardRefresh={onBoardRefresh} />);
    fireEvent.click(screen.getByLabelText("Close chat"));
    expect(onClose).toHaveBeenCalled();
  });

  it("shows typing indicator while loading", async () => {
    mockSendChatMessage.mockImplementation(() => new Promise(() => {}));
    render(<ChatSidebar isOpen={true} onClose={vi.fn()} onBoardRefresh={onBoardRefresh} />);

    const input = screen.getByPlaceholderText("Ask me to manage your board...");
    fireEvent.change(input, { target: { value: "Hello" } });
    fireEvent.submit(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(screen.queryByText("How can I help?")).not.toBeInTheDocument();
    });
  });

  it("displays error message on failure", async () => {
    mockSendChatMessage.mockRejectedValue(new Error("Network error"));
    render(<ChatSidebar isOpen={true} onClose={vi.fn()} onBoardRefresh={onBoardRefresh} />);

    const input = screen.getByPlaceholderText("Ask me to manage your board...");
    fireEvent.change(input, { target: { value: "Hello" } });
    fireEvent.submit(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(screen.getByText("Failed to get response. Please try again.")).toBeInTheDocument();
    });
  });

  it("displays user and AI messages", async () => {
    mockSendChatMessage.mockResolvedValue({
      response: "I can help with that!",
      board_update: null,
      board: { columns: [], cards: {} },
    });
    render(<ChatSidebar isOpen={true} onClose={vi.fn()} onBoardRefresh={onBoardRefresh} />);

    const input = screen.getByPlaceholderText("Ask me to manage your board...");
    fireEvent.change(input, { target: { value: "Create a card" } });
    fireEvent.submit(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(screen.getByText("Create a card")).toBeInTheDocument();
      expect(screen.getByText("I can help with that!")).toBeInTheDocument();
    });
  });
});
