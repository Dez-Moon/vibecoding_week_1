from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

STATIC_DIR = Path("/app/static")


def create_app(static_dir: Path | None = None) -> FastAPI:
    app = FastAPI()

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    sd = static_dir if static_dir is not None else STATIC_DIR
    if sd.is_dir():
        app.mount("/", StaticFiles(directory=sd, html=True), name="static")

    return app


app = create_app()
