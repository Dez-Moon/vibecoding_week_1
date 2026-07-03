from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import board, database, schemas
from app.auth import (
    clear_session_cookie,
    create_session_cookie,
    get_current_user,
    validate_credentials,
)
from app.seed import seed_if_empty

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

    @app.on_event("startup")
    def _startup() -> None:
        database.init_db()
        with database.SessionLocal() as db:
            seed_if_empty(db)

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

    @app.get("/api/board")
    def get_board_route(
        username: str = Depends(get_current_user),
        db: Session = Depends(database.get_db),
    ) -> dict:
        result = board.get_board(db, username)
        if result is None:
            raise HTTPException(status_code=404, detail="board not found")
        return result.model_dump()

    @app.patch("/api/board")
    def patch_board_route(
        payload: schemas.ColumnsRenameIn,
        username: str = Depends(get_current_user),
        db: Session = Depends(database.get_db),
    ) -> dict:
        board.rename_columns(db, username, payload)
        result = board.get_board(db, username)
        if result is None:
            raise HTTPException(status_code=404, detail="board not found")
        return result.model_dump()

    @app.post("/api/board/cards", status_code=201)
    def create_card_route(
        payload: schemas.CardCreateIn,
        username: str = Depends(get_current_user),
        db: Session = Depends(database.get_db),
    ) -> dict:
        try:
            card = board.create_card(db, username, payload)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return schemas.CardOut.model_validate(card).model_dump()

    @app.patch("/api/board/cards/{card_id}")
    def update_card_route(
        card_id: str,
        payload: schemas.CardUpdateIn,
        username: str = Depends(get_current_user),
        db: Session = Depends(database.get_db),
    ) -> dict:
        try:
            card = board.update_card(db, username, card_id, payload)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return schemas.CardOut.model_validate(card).model_dump()

    @app.delete("/api/board/cards/{card_id}", status_code=204)
    def delete_card_route(
        card_id: str,
        username: str = Depends(get_current_user),
        db: Session = Depends(database.get_db),
    ) -> Response:
        try:
            board.delete_card(db, username, card_id)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return Response(status_code=204)

    @app.post("/api/board/cards/{card_id}/move")
    def move_card_route(
        card_id: str,
        payload: schemas.CardMoveIn,
        username: str = Depends(get_current_user),
        db: Session = Depends(database.get_db),
    ) -> dict:
        try:
            card = board.move_card(db, username, card_id, payload)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return schemas.CardOut.model_validate(card).model_dump()

    sd = static_dir if static_dir is not None else STATIC_DIR
    if sd.is_dir():
        app.mount("/", StaticFiles(directory=sd, html=True), name="static")

    return app


app = create_app()
