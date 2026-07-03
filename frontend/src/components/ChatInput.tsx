"use client";

import { useState } from "react";

type Props = {
  onSend: (message: string) => void;
  disabled?: boolean;
};

export const ChatInput = ({ onSend, disabled }: Props) => {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;
    onSend(input.trim());
    setInput("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
          }
        }}
        placeholder="Ask me to manage your board..."
        disabled={disabled}
        rows={1}
        className="flex-1 resize-none rounded-xl border border-[var(--stroke)] bg-[var(--surface-strong)] px-4 py-3 text-sm text-[var(--dark-slate)] placeholder-[var(--gray-text)] focus:border-[var(--primary-indigo)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-indigo)]/20 disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled || !input.trim()}
        className="self-end rounded-xl bg-[var(--secondary-cyan)] px-4 py-3 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
      >
        Send
      </button>
    </form>
  );
};
