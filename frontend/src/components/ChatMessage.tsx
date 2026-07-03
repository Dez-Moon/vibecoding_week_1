"use client";

import type { Message } from "@/lib/chat";

type Props = {
  message: Message;
};

export const ChatMessage = ({ message }: Props) => {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
          isUser
            ? "rounded-br-md bg-[var(--primary-indigo)] text-white"
            : "rounded-bl-md bg-[var(--surface-strong)] text-[var(--dark-slate)] border border-[var(--stroke)]"
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
      </div>
    </div>
  );
};
