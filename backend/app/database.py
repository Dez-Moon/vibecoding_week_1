import os
from collections.abc import Iterator
from pathlib import Path
from threading import Lock

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "pm.db"
DEFAULT_URL = f"sqlite:///{DEFAULT_DB_PATH}"

# Protected by a lock so concurrent fixture calls (unlikely, but safe) don't
# race during reconfiguration.
_lock = Lock()
_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def _resolve_url() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_URL)


def _ensure_data_dir(url: str) -> None:
    if not url.startswith("sqlite:///"):
        return
    db_path = url.removeprefix("sqlite:///")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)


def _build_engine(url: str) -> Engine:
    _ensure_data_dir(url)
    return create_engine(url, future=True, echo=False)


def _get_engine() -> Engine:
    if _engine is None:
        url = _resolve_url()
        configure(url)
    return _engine  # type: ignore[return-value]


def get_session_factory() -> sessionmaker[Session]:
    if _SessionLocal is None:
        _get_engine()
    return _SessionLocal  # type: ignore[return-value]


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
    global _engine, _SessionLocal
    with _lock:
        _engine = _build_engine(url)
        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)


def _get_engine() -> Engine:
    global _engine, _SessionLocal
    with _lock:
        if _engine is None:
            url = _resolve_url()
            _engine = _build_engine(url)
            _SessionLocal = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)
        return _engine


def get_db() -> Iterator[Session]:
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Models are imported at module load time, so Base.metadata is
    # already populated. Just issue the CREATE TABLE statements.
    Base.metadata.create_all(bind=_get_engine())
