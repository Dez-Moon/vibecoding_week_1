import { apiFetch } from "@/lib/api";

export interface BoardApiCard {
  id: string;
  title: string;
  details: string;
  position: number;
  column_id: string;
}

export interface BoardApiColumn {
  id: string;
  title: string;
  position: number;
  card_ids: string[];
}

export interface BoardApiData {
  columns: BoardApiColumn[];
  cards: Record<string, BoardApiCard>;
}

export interface ColumnRenamePayload {
  id: string;
  title: string;
}

export async function getBoard(): Promise<BoardApiData> {
  return apiFetch<BoardApiData>("/api/board");
}

export async function renameColumns(
  columns: ColumnRenamePayload[]
): Promise<BoardApiData> {
  return apiFetch<BoardApiData>("/api/board", {
    method: "PATCH",
    body: JSON.stringify({ columns }),
  });
}

export async function createCard(
  columnId: string,
  title: string,
  details: string
): Promise<BoardApiCard> {
  return apiFetch<BoardApiCard>("/api/board/cards", {
    method: "POST",
    body: JSON.stringify({ column_id: columnId, title, details }),
  });
}

export async function updateCard(
  cardId: string,
  title?: string,
  details?: string
): Promise<BoardApiCard> {
  return apiFetch<BoardApiCard>(`/api/board/cards/${cardId}`, {
    method: "PATCH",
    body: JSON.stringify({ title, details }),
  });
}

export async function deleteCard(cardId: string): Promise<void> {
  return apiFetch<void>(`/api/board/cards/${cardId}`, {
    method: "DELETE",
  });
}

export async function moveCard(
  cardId: string,
  columnId: string,
  position: number
): Promise<BoardApiCard> {
  return apiFetch<BoardApiCard>(`/api/board/cards/${cardId}/move`, {
    method: "POST",
    body: JSON.stringify({ column_id: columnId, position }),
  });
}
