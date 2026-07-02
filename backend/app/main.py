from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return "<h1>Hello from Kanban</h1>"


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
