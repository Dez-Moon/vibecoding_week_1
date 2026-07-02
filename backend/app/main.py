from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.auth import (
    clear_session_cookie,
    create_session_cookie,
    get_current_user,
    validate_credentials,
)

STATIC_DIR = Path("/app/static")
DEV_ORIGINS = [
    "http://127.0.0.1:3100",
    "http://localhost:3100",
]


class LoginRequest(BaseModel):
    username: str
    password: str


def create_app(static_dir: Path | None = None) -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=DEV_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/login")
    def login(payload: LoginRequest, response: Response) -> dict[str, str]:
        if not validate_credentials(payload.username, payload.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        create_session_cookie(response, payload.username)
        return {"username": payload.username}

    @app.post("/api/logout", status_code=204)
    def logout(response: Response) -> Response:
        clear_session_cookie(response)
        return Response(status_code=204)

    @app.get("/api/whoami")
    def whoami(username: str = Depends(get_current_user)) -> dict[str, str]:
        return {"username": username}

    sd = static_dir if static_dir is not None else STATIC_DIR
    if sd.is_dir():
        app.mount("/", StaticFiles(directory=sd, html=True), name="static")

    return app


app = create_app()
