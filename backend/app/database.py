import os
from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "pm.db"
DEFAULT_URL = f"sqlite:///{DEFAULT_DB_PATH}"


def _resolve_url() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_URL)


def _ensure_data_dir(url: str) -> None:
    if not url.startswith("sqlite:///"):
        return
    db_path = url.removeprefix("sqlite:///")
    parent = Path(db_path).parent
    parent.mkdir(parents=True, exist_ok=True)


def _build_engine(url: str) -> Engine:
    _ensure_data_dir(url)
    return create_engine(url, future=True, echo=False)


engine: Engine = _build_engine(_resolve_url())
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# Import models at module load time so Base.metadata is populated before
# init_db() runs and the model classes are reachable as `app.database.models`.
from app import models  # noqa: E402, F401


def configure(url: str) -> None:
    """Rebind the engine and session factory to a new URL.

    Used by tests to point at an ephemeral SQLite file. Idempotent: safe
    to call multiple times.
    """
    global engine, SessionLocal
    engine = _build_engine(url)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Models are imported at module load time, so Base.metadata is
    # already populated. Just issue the CREATE TABLE statements.
    Base.metadata.create_all(bind=engine)
