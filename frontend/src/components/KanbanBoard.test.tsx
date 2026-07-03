import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { KanbanBoard } from "@/components/KanbanBoard";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

vi.mock("@dnd-kit/core", () => ({
  DndContext: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  DragOverlay: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  PointerSensor: vi.fn(),
  useSensor: vi.fn(),
  useSensors: vi.fn().mockReturnValue([]),
  closestCorners: "closestCorners",
  useDroppable: () => ({ setNodeRef: vi.fn(), isOver: false }),
}));

vi.mock("@dnd-kit/sortable", () => ({
  SortableContext: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  verticalListSortingStrategy: "verticalListSortingStrategy",
  useSortable: () => ({
    attributes: {},
    listeners: {},
    setNodeRef: vi.fn(),
    transform: null,
    transition: null,
    isDragging: false,
  }),
}));

vi.mock("@/components/AuthGate", () => ({
  useCurrentUser: () => ({ username: "user" }),
}));

// Use vi.hoisted so the factory receives the actual fn references
const { apiFetch } = vi.hoisted(() => {
  const columns = [
    { id: "col-1", title: "Backlog", position: 0, card_ids: ["card-1", "card-2"] },
    { id: "col-2", title: "Discovery", position: 1, card_ids: ["card-3"] },
    { id: "col-3", title: "In Progress", position: 2, card_ids: [] },
    { id: "col-4", title: "Review", position: 3, card_ids: [] },
    { id: "col-5", title: "Done", position: 4, card_ids: [] },
  ];
  const cards = {
    "card-1": { id: "card-1", title: "Card One", details: "", position: 0, column_id: "col-1" },
    "card-2": { id: "card-2", title: "Card Two", details: "", position: 1, column_id: "col-1" },
    "card-3": { id: "card-3", title: "Card Three", details: "", position: 0, column_id: "col-2" },
  };
  const boardData = { columns, cards };
  const fetch = vi.fn<() => Promise<unknown>>().mockImplementation((url: string) => {
    if (String(url).includes("/api/board") && !String(url).includes("/cards")) return Promise.resolve(boardData);
    if (String(url).includes("/api/board/cards") && String(url).includes("/move")) return Promise.resolve({ id: "card-1", title: "Card One", details: "", position: 0, column_id: "col-2" });
    return Promise.resolve({ id: "new-card", title: "New Card", details: "", position: 0, column_id: "col-1" });
  });
  return { apiFetch: fetch };
});

vi.mock("@/lib/api", () => ({ apiFetch }));

const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

describe("KanbanBoard", () => {
  beforeEach(() => {
    apiFetch.mockReset();
    apiFetch.mockImplementation((url: string) => {
      if (String(url).includes("/api/board") && !String(url).includes("/cards")) {
        return Promise.resolve({
          columns: [
            { id: "col-1", title: "Backlog", position: 0, card_ids: ["card-1", "card-2"] },
            { id: "col-2", title: "Discovery", position: 1, card_ids: ["card-3"] },
            { id: "col-3", title: "In Progress", position: 2, card_ids: [] },
            { id: "col-4", title: "Review", position: 3, card_ids: [] },
            { id: "col-5", title: "Done", position: 4, card_ids: [] },
          ],
          cards: {
            "card-1": { id: "card-1", title: "Card One", details: "", position: 0, column_id: "col-1" },
            "card-2": { id: "card-2", title: "Card Two", details: "", position: 1, column_id: "col-1" },
            "card-3": { id: "card-3", title: "Card Three", details: "", position: 0, column_id: "col-2" },
          },
        });
      }
      if (String(url).includes("/api/board/cards") && String(url).includes("/move")) {
        return Promise.resolve({ id: "card-1", title: "Card One", details: "", position: 0, column_id: "col-2" });
      }
      return Promise.resolve({ id: "new-card", title: "New Card", details: "", position: 0, column_id: "col-1" });
    });
  });

  afterEach(() => {
    apiFetch.mockReset();
  });

  it("renders five columns from API", async () => {
    render(<KanbanBoard />);
    expect(await screen.findAllByTestId(/column-/i)).toHaveLength(5);
  });

  it("renames a column", async () => {
    apiFetch.mockImplementation((url: string) => {
      if (String(url).includes("/api/board") && !String(url).includes("/cards")) {
        return Promise.resolve({
          columns: [
            { id: "col-1", title: "Backlog", position: 0, card_ids: ["card-1", "card-2"] },
            { id: "col-2", title: "Discovery", position: 1, card_ids: ["card-3"] },
            { id: "col-3", title: "In Progress", position: 2, card_ids: [] },
            { id: "col-4", title: "Review", position: 3, card_ids: [] },
            { id: "col-5", title: "Done", position: 4, card_ids: [] },
          ],
          cards: {
            "card-1": { id: "card-1", title: "Card One", details: "", position: 0, column_id: "col-1" },
            "card-2": { id: "card-2", title: "Card Two", details: "", position: 1, column_id: "col-1" },
            "card-3": { id: "card-3", title: "Card Three", details: "", position: 0, column_id: "col-2" },
          },
        });
      }
      return Promise.resolve({ id: "new-card", title: "New Card", details: "", position: 0, column_id: "col-1" });
    });
    render(<KanbanBoard />);
    // Wait for board to load (async via useEffect)
    const columns = await screen.findAllByTestId(/column-/i);
    expect(columns).toHaveLength(5);
    const column = columns[0];
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name{Enter}");
    expect(apiFetch).toHaveBeenCalledWith("/api/board", expect.objectContaining({ method: "PATCH" }));
  });

  it("adds a card and deletes it", async () => {
    apiFetch.mockImplementation((url: string) => {
      if (String(url).includes("/api/board") && !String(url).includes("/cards")) {
        return Promise.resolve({
          columns: [
            { id: "col-1", title: "Backlog", position: 0, card_ids: ["card-1", "card-2"] },
            { id: "col-2", title: "Discovery", position: 1, card_ids: ["card-3"] },
            { id: "col-3", title: "In Progress", position: 2, card_ids: [] },
            { id: "col-4", title: "Review", position: 3, card_ids: [] },
            { id: "col-5", title: "Done", position: 4, card_ids: [] },
          ],
          cards: {
            "card-1": { id: "card-1", title: "Card One", details: "", position: 0, column_id: "col-1" },
            "card-2": { id: "card-2", title: "Card Two", details: "", position: 1, column_id: "col-1" },
            "card-3": { id: "card-3", title: "Card Three", details: "", position: 0, column_id: "col-2" },
          },
        });
      }
      if (String(url).includes("/move")) {
        return Promise.resolve({ id: "card-1", title: "Card One", details: "", position: 0, column_id: "col-2" });
      }
      return Promise.resolve({ id: "new-card", title: "New card", details: "", position: 0, column_id: "col-1" });
    });
    render(<KanbanBoard />);
    const columns = await screen.findAllByTestId(/column-/i);
    expect(columns).toHaveLength(5);
    const column = columns[0];

    const addButton = within(column).getByRole("button", { name: /add a card/i });
    await userEvent.click(addButton);

    const titleInput = within(column).getByPlaceholderText(/card title/i);
    await userEvent.type(titleInput, "New card");
    const detailsInput = within(column).getByPlaceholderText(/details/i);
    await userEvent.type(detailsInput, "Notes");

    await userEvent.click(within(column).getByRole("button", { name: /add card/i }));

    expect(apiFetch).toHaveBeenCalledWith(
      "/api/board/cards",
      expect.objectContaining({ method: "POST" })
    );
    expect(await screen.findByText("New card")).toBeInTheDocument();

    const deleteButton = within(column).getByRole("button", { name: /delete new card/i });
    await userEvent.click(deleteButton);
    expect(apiFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/board/cards/"),
      expect.objectContaining({ method: "DELETE" })
    );
  });

  it("shows loading state while fetching", () => {
    apiFetch.mockImplementation(() => new Promise(() => {}));
    render(<KanbanBoard />);
    expect(screen.getByText("Loading board…")).toBeInTheDocument();
  });

  it("shows error banner on load failure", async () => {
    apiFetch.mockRejectedValue(new Error("network"));
    render(<KanbanBoard />);
    expect(await screen.findByText(/Failed to load board/i)).toBeInTheDocument();
  });
});
