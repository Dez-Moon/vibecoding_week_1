import { apiFetch } from "./api";
import type { BoardApiColumn, BoardApiCard } from "./board";

export type Message = {
  role: "user" | "assistant";
  content: string;
};

export type Operation =
  | { op: "create_card"; column_id: string; title: string; details: string }
  | { op: "update_card"; card_id: string; title?: string; details?: string }
  | { op: "delete_card"; card_id: string }
  | { op: "move_card"; card_id: string; column_id: string; position: number }
  | { op: "rename_column"; column_id: string; title: string };

export type BoardUpdate = {
  operations: Operation[];
};

export type ChatResponse = {
  response: string;
  board_update: BoardUpdate | null;
  board: {
    columns: BoardApiColumn[];
    cards: Record<string, BoardApiCard>;
  };
};

export async function sendChatMessage(
  message: string,
  conversationHistory: Message[] | null
): Promise<ChatResponse> {
  return apiFetch<ChatResponse>("/api/ai/chat", {
    method: "POST",
    body: JSON.stringify({
      message,
      conversation_history: conversationHistory,
    }),
  });
}
