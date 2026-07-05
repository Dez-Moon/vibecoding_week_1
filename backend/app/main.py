from pathlib import Path
import uuid

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import board, database, schemas
from app.services.ai import call_ai
from app.services.chat import apply_operations, build_system_prompt
from app.auth import (
    clear_session_cookie,
    create_session_cookie,
    get_current_user,
    hash_password,
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


class RegisterRequest(BaseModel):
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
        with database.get_session_factory()() as db:
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

    @app.post("/api/register")
    def register(
        payload: RegisterRequest,
        response: Response,
        db: Session = Depends(database.get_db),
    ) -> dict[str, str]:
        from sqlalchemy import select
        from app import models

        existing = db.execute(
            select(models.User).where(models.User.username == payload.username)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        user = models.User(
            id=str(uuid.uuid4()),
            username=payload.username,
            password_hash=hash_password(payload.password),
        )
        db.add(user)
        db.flush()

        board = models.Board(
            id=str(uuid.uuid4()),
            user_id=user.id,
            title="My Board",
        )
        db.add(board)
        db.flush()

        default_columns = ["Backlog", "In Progress", "Done"]
        for i, title in enumerate(default_columns):
            db.add(
                models.Column(
                    id=str(uuid.uuid4()),
                    board_id=board.id,
                    title=title,
                    position=i,
                )
            )
        db.commit()

        create_session_cookie(response, payload.username)
        return {"username": payload.username}

    @app.post("/api/logout", status_code=204)
    def logout(response: Response) -> None:
        clear_session_cookie(response)

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

    @app.post("/api/ai/test")
    def ai_test() -> dict[str, str]:
        messages = [{"role": "user", "content": "What is 2+2?"}]
        response = call_ai(messages)
        return {"response": response}

    @app.post("/api/ai/chat")
    def ai_chat(
        payload: schemas.AIChatRequest,
        username: str = Depends(get_current_user),
        db: Session = Depends(database.get_db),
    ) -> schemas.AIChatResponse:
        board_data = board.get_board(db, username)
        if board_data is None:
            raise HTTPException(status_code=404, detail="board not found")

        messages = [{"role": "system", "content": build_system_prompt(username, board_data)}]
        if payload.conversation_history:
            messages.extend([m.model_dump() for m in payload.conversation_history])
        messages.append({"role": "user", "content": payload.message})

        ai_response = call_ai(messages)

        import json
        try:
            parsed = json.loads(ai_response)
            update = schemas.BoardUpdate.model_validate(parsed.get("board_update") or {})
        except (json.JSONDecodeError, ValueError):
            return schemas.AIChatResponse(
                response=ai_response,
                board_update=None,
                board=board_data,
            )

        if update.operations:
            try:
                apply_operations(db, board_data, update)
            except ValueError:
                return schemas.AIChatResponse(
                    response=ai_response,
                    board_update=None,
                    board=board_data,
                )

        board_data = board.get_board(db, username)
        return schemas.AIChatResponse(
            response=parsed.get("response", ai_response),
            board_update=update if update.operations else None,
            board=board_data,
        )

    sd = static_dir if static_dir is not None else STATIC_DIR
    if sd.is_dir():
        app.mount("/", StaticFiles(directory=sd, html=True), name="static")

    return app


app = create_app()
