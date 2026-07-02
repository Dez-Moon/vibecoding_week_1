# Frontend

Next.js Kanban board. Built as a static export and served by the backend at `/`. Currently no persistence — board state lives in React state and resets on reload (auth + persistence land in Parts 4 and 7).

## Stack

- Next.js (App Router, TypeScript)
- React 19
- Tailwind CSS 4 (via `@tailwindcss/postcss`)
- `@dnd-kit/core`, `@dnd-kit/sortable` for drag and drop
- Vitest + Testing Library for unit tests (jsdom environment)
- Playwright for E2E tests
- ESLint with `eslint-config-next`

## Directory layout

```
src/
  app/
    layout.tsx        # Root layout, font setup, metadata
    page.tsx          # Home page, renders <KanbanBoard />
    globals.css       # Tailwind import + global styles
  components/
    KanbanBoard.tsx           # Top-level board, owns state and DnD context
    KanbanBoard.test.tsx      # Unit tests for board behavior
    KanbanColumn.tsx          # Droppable column, hosts cards and rename input
    KanbanCard.tsx            # Sortable card with delete button
    KanbanCardPreview.tsx     # Stateless card for the drag overlay
    NewCardForm.tsx           # Inline form to add a card to a column
  lib/
    kanban.ts         # Types (Card, Column, BoardData), seed data, pure moveCard helper
    kanban.test.ts    # Unit tests for moveCard
  test/
    setup.ts          # Imports @testing-library/jest-dom matchers
    vitest.d.ts       # Vitest type references
tests/
  kanban.spec.ts      # Playwright E2E tests (board loads, add card, move card)
public/
  file.svg, globe.svg, next.svg, vercel.svg, window.svg   # Default Next.js assets (unused)
```

## State model

`src/lib/kanban.ts` defines the data shapes:

- `Card` — `{ id, title, details }`
- `Column` — `{ id, title, cardIds: string[] }` (cards are stored by ID so order is explicit)
- `BoardData` — `{ columns: Column[], cards: Record<string, Card> }`

`initialData` provides 5 columns (`Backlog`, `Discovery`, `In Progress`, `Review`, `Done`) and 8 seed cards spread across them.

`moveCard(columns, activeId, overId)` is a pure function that returns a new `Column[]` reflecting the move. It handles same-column reorder, cross-column move, and dropping onto an empty column.

`createId(prefix)` generates a random ID using `Math.random` + `Date.now`.

## Component behavior

- `KanbanBoard` owns the board state via `useState` initialized from `initialData`. It also tracks the currently-dragging card ID for the `DragOverlay`.
- DnD uses `DndContext` with `PointerSensor` (6px activation distance) and `closestCorners` collision detection. `onDragEnd` calls `moveCard` and updates state.
- Column rename is a controlled `<input>` that calls `onRename(columnId, title)` on every keystroke.
- `NewCardForm` is collapsed by default ("Add a card" button) and expands into a title input, details textarea, and Add/Cancel buttons. Empty title submits are rejected.
- `KanbanCard` uses `useSortable` for drag, and the delete button calls `onDelete(card.id)`.
- `KanbanCardPreview` is rendered inside `DragOverlay` so the user sees a card while dragging without losing the original card position.

## Test IDs

Tests rely on these `data-testid` attributes — keep them stable:

- `column-${column.id}` on each column section (e.g. `column-col-backlog`)
- `card-${card.id}` on each card (e.g. `card-card-1`)

## Tests

- Unit: `npm run test:unit` (Vitest).
  - `kanban.test.ts` covers `moveCard` (same-column reorder, cross-column move, drop to empty column).
  - `KanbanBoard.test.tsx` covers rendering 5 columns, renaming, and add+delete card.
- E2E: `npm run test:e2e` (Playwright against `npm run dev`). Loads the board, adds a card, and drags a card between columns.

## Dev and build

- Dev: `npm run dev` (Next dev server, default port 3000).
- Build: `npm run build` — produces `frontend/out/` as the static export.
- Start: `npm run start` (production server; not used by the Docker setup).
- Lint: `npm run lint`

## Known discrepancies

- The current frontend uses its own color palette (yellow / blue / purple), which differs from the spec at the project root (green / indigo / cyan). The color scheme will be migrated in Part 3.
- No static export is configured yet — `next.config.ts` still defaults to an SSR build. Static export is added in Part 3.
- No backend serving: today the dev server is the only way to run the frontend. The backend + multi-stage Docker build is added in Part 3.
