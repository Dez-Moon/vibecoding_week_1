# Kanban Studio

A modern project management application with AI-powered kanban boards, built with Next.js and FastAPI.

**Live Demo:** https://frontend-54r4k6lc7-dezmoons-projects.vercel.app

**Frontend:** https://frontend-54r4k6lc7-dezmoons-projects.vercel.app
**Backend:** https://kanban-api-production-0683.up.railway.app

## Default Credentials

- Username: `user`
- Password: `password`

## Features

- **Kanban Board** — Drag-and-drop task management with columns
- **AI Chat Assistant** — Natural language commands to manage your board
- **User Authentication** — Secure session-based login system
- **Real-time Updates** — Optimistic UI with server sync

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16, React 19, Tailwind CSS 4, dnd-kit |
| Backend | FastAPI, SQLAlchemy, SQLite |
| AI | OpenRouter API |

## Project Structure

```
pm/
├── frontend/          # Next.js frontend (deployed to Vercel)
│   ├── src/app/      # App Router pages
│   ├── src/components/  # React components
│   └── src/lib/      # API clients and utilities
├── backend/          # FastAPI backend
│   ├── app/          # Application code
│   │   ├── main.py   # API routes
│   │   ├── auth.py   # Authentication
│   │   └── models.py # Database models
│   └── data/         # SQLite database
└── docs/             # Architecture documentation
```

## Local Development

### Prerequisites

- Node.js 18+
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (Python package manager)

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:3000`.

### Backend Setup

```bash
cd backend
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The backend runs at `http://localhost:8000`.

**Environment Variables (Backend):**

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Session signing key | Yes (production) |
| `DATABASE_URL` | SQLite database path | No (defaults to `data/pm.db`) |
| `OPENROUTER_API_KEY` | OpenRouter API key for AI | Yes (for AI features) |

### Environment Configuration

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Deployment

### Frontend (Vercel)

The frontend is deployed to Vercel: https://frontend-6vjbzi68l-dezmoons-projects.vercel.app

To redeploy:

```bash
cd frontend
vercel deploy --prod
```

Set `NEXT_PUBLIC_API_BASE_URL` to your backend URL.

### Backend Deployment

The backend needs to be deployed separately. Recommended platforms:

**Railway** (Recommended - free tier available):
1. Go to [railway.app](https://railway.app)
2. Create a new project from your GitHub repo
3. Add the backend directory
4. Set environment variables:
   - `SECRET_KEY` — Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
   - `OPENROUTER_API_KEY` — Get from [OpenRouter](https://openrouter.ai)

**Docker** (Any platform):
```bash
cd pm
docker build -t kanban-backend .
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret \
  -e OPENROUTER_API_KEY=your-key \
  kanban-backend
```

### Connecting Frontend to Backend

Once your backend is deployed, update the Vercel frontend environment variable:

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add: `NEXT_PUBLIC_API_BASE_URL` = your deployed backend URL

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/login` | Authenticate user |
| POST | `/api/register` | Create new account |
| POST | `/api/logout` | End session |
| GET | `/api/whoami` | Get current user |
| GET | `/api/board` | Get user's kanban board |
| PATCH | `/api/board` | Rename columns |
| POST | `/api/board/cards` | Create card |
| PATCH | `/api/board/cards/{id}` | Update card |
| DELETE | `/api/board/cards/{id}` | Delete card |
| POST | `/api/board/cards/{id}/move` | Move card |
| POST | `/api/ai/chat` | AI chat (modifies board) |

## Testing

```bash
# Frontend unit tests
cd frontend && npm run test:unit

# Backend tests
cd backend && uv run pytest
```

## License

MIT
