"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
  type DragEndEvent,
  type DragOverEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { KanbanColumn } from "@/components/KanbanColumn";
import { KanbanCardPreview } from "@/components/KanbanCardPreview";
import { useCurrentUser } from "@/components/AuthGate";
import { logout } from "@/lib/auth";
import {
  createCard as apiCreateCard,
  deleteCard as apiDeleteCard,
  getBoard,
  moveCard as apiMoveCard,
  renameColumns as apiRenameColumns,
  type BoardApiCard,
  type BoardApiColumn,
} from "@/lib/board";
import { moveCard } from "@/lib/kanban";

type KanbanCard = {
  id: string;
  title: string;
  details: string;
};

type KanbanColumn = {
  id: string;
  title: string;
  cardIds: string[];
};

type KanbanBoardData = {
  columns: KanbanColumn[];
  cards: Record<string, KanbanCard>;
};

function apiToBoard(
  apiColumns: BoardApiColumn[],
  apiCards: Record<string, BoardApiCard>
): KanbanBoardData {
  return {
    columns: apiColumns.map((c) => ({
      id: c.id,
      title: c.title,
      cardIds: c.card_ids,
    })),
    cards: Object.fromEntries(
      Object.entries(apiCards).map(([id, c]) => [id, { id, title: c.title, details: c.details }])
    ),
  };
}

export const KanbanBoard = () => {
  const { username } = useCurrentUser() ?? {};

  const [board, setBoard] = useState<KanbanBoardData | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [activeCardId, setActiveCardId] = useState<string | null>(null);
  const [overId, setOverId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 6 } })
  );

  useEffect(() => {
    getBoard()
      .then((data) => setBoard(apiToBoard(data.columns, data.cards)))
      .catch(() => setLoadError("Failed to load board. Please refresh."));
  }, []);

  const cardsById = useMemo(() => board?.cards ?? {}, [board?.cards]);

  const handleDragStart = (event: DragStartEvent) => {
    setActiveCardId(event.active.id as string);
  };

  const handleDragOver = (event: DragOverEvent) => {
    setOverId((event.over?.id as string) ?? null);
  };

  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      const { active, over } = event;
      setActiveCardId(null);
      setOverId(null);

      if (!over || !board || active.id === over.id) return;

      const prevBoard = board;

      // Optimistic update: run moveCard locally
      const updatedColumns = moveCard(board.columns, active.id as string, over.id as string);

      // Find the target column and the card's new position in it
      const targetColumnId = updatedColumns.find((col) =>
        col.cardIds.includes(active.id as string)
      )?.id;
      const targetColumn = updatedColumns.find((col) => col.id === targetColumnId);
      const targetPosition = targetColumn?.cardIds.indexOf(active.id as string) ?? 0;

      if (!targetColumnId) return;

      // Apply optimistic update
      setBoard((prev) =>
        prev ? { ...prev, columns: updatedColumns } : prev
      );
      setError(null);

      apiMoveCard(active.id as string, targetColumnId, targetPosition)
        .then(() => {
          // Refresh board to sync server state (positions may differ slightly)
          return getBoard().then((data) =>
            setBoard((prev) =>
              prev ? apiToBoard(data.columns, data.cards) : prev
            )
          );
        })
        .catch(() => {
          setBoard(prevBoard);
          setError("Move failed. Board restored.");
        });
    },
    [board]
  );

  const handleRenameColumn = useCallback(
    (columnId: string, title: string) => {
      if (!board) return;
      const prevBoard = board;
      setBoard((prev) =>
        prev
          ? {
              ...prev,
              columns: prev.columns.map((col) =>
                col.id === columnId ? { ...col, title } : col
              ),
            }
          : prev
      );
      setError(null);

      apiRenameColumns([{ id: columnId, title }])
        .then((data) =>
          setBoard((prev) =>
            prev ? apiToBoard(data.columns, data.cards) : prev
          )
        )
        .catch(() => {
          setBoard(prevBoard);
          setError("Rename failed. Board restored.");
        });
    },
    [board]
  );

  const handleAddCard = useCallback(
    (columnId: string, title: string, details: string) => {
      if (!board) return;
      const tempId = `temp-${Date.now()}`;
      const optimisticCard: KanbanCard = {
        id: tempId,
        title,
        details: details || "No details yet.",
      };
      const prevBoard = board;

      setBoard((prev) =>
        prev
          ? {
              ...prev,
              cards: { ...prev.cards, [tempId]: optimisticCard },
              columns: prev.columns.map((col) =>
                col.id === columnId
                  ? { ...col, cardIds: [...col.cardIds, tempId] }
                  : col
              ),
            }
          : prev
      );
      setError(null);

      apiCreateCard(columnId, title, details)
        .then((card) => {
          setBoard((prev) => {
            if (!prev) return prev;
            const { [tempId]: _, ...restCards } = prev.cards;
            return {
              ...prev,
              cards: { ...restCards, [card.id]: { id: card.id, title: card.title, details: card.details } },
              columns: prev.columns.map((col) =>
                col.id === columnId
                  ? { ...col, cardIds: col.cardIds.map((id) => (id === tempId ? card.id : id)) }
                  : col
              ),
            };
          });
        })
        .catch(() => {
          setBoard(prevBoard);
          setError("Failed to add card. Please try again.");
        });
    },
    [board]
  );

  const handleDeleteCard = useCallback(
    (columnId: string, cardId: string) => {
      if (!board) return;
      const prevBoard = board;

      setBoard((prev) =>
        prev
          ? {
              ...prev,
              cards: Object.fromEntries(
                Object.entries(prev.cards).filter(([id]) => id !== cardId)
              ),
              columns: prev.columns.map((col) =>
                col.id === columnId
                  ? { ...col, cardIds: col.cardIds.filter((id) => id !== cardId) }
                  : col
              ),
            }
          : prev
      );
      setError(null);

      apiDeleteCard(cardId).catch(() => {
        setBoard(prevBoard);
        setError("Failed to delete card. Please try again.");
      });
    },
    [board]
  );

  const activeCard = activeCardId ? cardsById[activeCardId] : null;

  if (loadError) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="rounded-xl border border-red-300 bg-red-50 px-6 py-4 text-red-700">
          <p className="font-semibold">{loadError}</p>
        </div>
      </div>
    );
  }

  if (!board) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-[var(--primary-indigo)] border-t-transparent" />
          <p className="text-sm text-[var(--gray-text)]">Loading board…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden">
      <div className="pointer-events-none absolute left-0 top-0 h-[420px] w-[420px] -translate-x-1/3 -translate-y-1/3 rounded-full bg-[radial-gradient(circle,_rgba(79,70,229,0.25)_0%,_rgba(79,70,229,0.05)_55%,_transparent_70%)]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-[520px] w-[520px] translate-x-1/4 translate-y-1/4 rounded-full bg-[radial-gradient(circle,_rgba(6,182,212,0.18)_0%,_rgba(6,182,212,0.05)_55%,_transparent_75%)]" />

      <main className="relative mx-auto flex min-h-screen max-w-[1500px] flex-col gap-10 px-6 pb-16 pt-12">
        <header className="flex flex-col gap-6 rounded-[32px] border border-[var(--stroke)] bg-white/80 p-8 shadow-[var(--shadow)] backdrop-blur">
          {error && (
            <div className="rounded-lg border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700">
              {error}
            </div>
          )}
          <div className="flex flex-wrap items-start justify-between gap-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
                Single Board Kanban
              </p>
              <h1 className="mt-3 font-display text-4xl font-semibold text-[var(--dark-slate)]">
                Kanban Studio
              </h1>
              <p className="mt-3 max-w-xl text-sm leading-6 text-[var(--gray-text)]">
                Keep momentum visible. Rename columns, drag cards between stages,
                and capture quick notes without getting buried in settings.
              </p>
            </div>
            <div className="flex flex-col items-end gap-3">
              {username ? (
                <p
                  data-testid="current-user"
                  className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--gray-text)]"
                >
                  Signed in as <span className="text-[var(--primary-indigo)]">{username}</span>
                </p>
              ) : null}
              <div className="rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-5 py-4">
                <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--gray-text)]">
                  Focus
                </p>
                <p className="mt-2 text-lg font-semibold text-[var(--primary-indigo)]">
                  One board. Five columns. Zero clutter.
                </p>
              </div>
              {username ? <LogoutButton /> : null}
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-4">
            {board.columns.map((column) => (
              <div
                key={column.id}
                className="flex items-center gap-2 rounded-full border border-[var(--stroke)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--dark-slate)]"
              >
                <span className="h-2 w-2 rounded-full bg-[var(--accent-green)]" />
                {column.title}
              </div>
            ))}
          </div>
        </header>

        <DndContext
          sensors={sensors}
          collisionDetection={closestCorners}
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDragEnd={handleDragEnd}
        >
          <section className="grid gap-6 lg:grid-cols-5">
            {board.columns.map((column) => (
              <KanbanColumn
                key={column.id}
                column={column}
                cards={column.cardIds.map((cardId) => board.cards[cardId])}
                onRename={handleRenameColumn}
                onAddCard={handleAddCard}
                onDeleteCard={handleDeleteCard}
              />
            ))}
          </section>
          <DragOverlay>
            {activeCard ? (
              <div className="w-[260px]">
                <KanbanCardPreview card={activeCard} />
              </div>
            ) : null}
          </DragOverlay>
        </DndContext>
      </main>
    </div>
  );
};

const LogoutButton = () => {
  const router = useRouter();
  const handleClick = async () => {
    await logout();
    router.push("/login");
  };
  return (
    <button
      data-testid="logout-button"
      type="button"
      onClick={handleClick}
      className="rounded-lg border border-[var(--stroke)] bg-[var(--surface)] px-4 py-2 text-sm font-semibold text-[var(--dark-slate)] transition hover:border-[var(--primary-indigo)] hover:text-[var(--primary-indigo)]"
    >
      Sign out
    </button>
  );
};
