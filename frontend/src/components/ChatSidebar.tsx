"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { sendChatMessage, type Message } from "@/lib/chat";
import { getBoard } from "@/lib/board";
import { apiToBoard } from "./KanbanBoard";

type Props = {
  isOpen: boolean;
  onClose: () => void;
  onBoardRefresh: () => void;
};

export const ChatSidebar = ({ isOpen, onClose, onBoardRefresh }: Props) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const handleSend = useCallback(
    async (message: string) => {
      const userMessage: Message = { role: "user", content: message };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        const response = await sendChatMessage(message, messages.length > 0 ? messages : null);

        const aiMessage: Message = { role: "assistant", content: response.response };
        setMessages((prev) => [...prev, aiMessage]);

        if (response.board_update) {
          onBoardRefresh();
        }
      } catch {
        setError("Failed to get response. Please try again.");
        setMessages((prev) => prev.slice(0, -1));
      } finally {
        setIsLoading(false);
      }
    },
    [messages, onBoardRefresh]
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 flex w-full max-w-md flex-col border-l border-[var(--stroke)] bg-[var(--surface-strong)] shadow-[-20px_0_60px_rgba(30,41,59,0.15)]">
      <header className="flex items-center justify-between border-b border-[var(--stroke)] px-6 py-4">
        <h2 className="font-display text-lg font-semibold text-[var(--dark-slate)]">
          AI Assistant
        </h2>
        <button
          onClick={onClose}
          className="rounded-lg p-2 text-[var(--gray-text)] transition hover:bg-[var(--surface)] hover:text-[var(--dark-slate)]"
          aria-label="Close chat"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </header>

      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <div className="mb-4 rounded-full bg-[var(--primary-indigo)]/10 p-4">
              <svg className="h-8 w-8 text-[var(--primary-indigo)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <p className="text-sm font-medium text-[var(--dark-slate)]">How can I help?</p>
            <p className="mt-1 text-xs text-[var(--gray-text)]">
              Ask me to create, update, move, or delete cards on your board.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {messages.map((msg, i) => (
              <ChatMessage key={i} message={msg} />
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="rounded-2xl rounded-bl-md bg-[var(--surface)] px-4 py-3">
                  <div className="flex gap-1">
                    <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--gray-text)] [animation-delay:0ms]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--gray-text)] [animation-delay:150ms]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--gray-text)] [animation-delay:300ms]" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {error && (
        <div className="border-t border-[var(--stroke)] px-4 py-2">
          <p className="text-xs text-red-600">{error}</p>
        </div>
      )}

      <div className="border-t border-[var(--stroke)] p-4">
        <ChatInput onSend={handleSend} disabled={isLoading} />
      </div>
    </div>
  );
};
