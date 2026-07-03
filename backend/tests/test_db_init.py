import pytest
from sqlalchemy import inspect

from app import database


@pytest.fixture
def db(tmp_path):
    url = f"sqlite:///{tmp_path / 'init.db'}"
    database.configure(url)
    return url, tmp_path


def test_db_init_creates_file_when_missing(db):
    _, tmp_path = db
    db_path = tmp_path / "init.db"
    assert not db_path.exists()

    database.init_db()
    assert db_path.exists()


def test_db_init_creates_expected_tables(db):
    database.init_db()
    inspector = inspect(database.engine)
    table_names = set(inspector.get_table_names())
    assert {"users", "boards", "columns", "cards"}.issubset(table_names)


def test_seed_creates_demo_workspace(db):
    from app.seed import DEFAULT_COLUMNS, seed_if_empty

    database.init_db()
    with database.SessionLocal() as session:
        seed_if_empty(session)
    with database.SessionLocal() as session:
        users = session.query(database.models.User).all()
        assert len(users) == 1
        assert users[0].username == "user"
        board = users[0].board
        assert board is not None
        assert board.title == "Kanban Studio"
        assert [c.title for c in board.columns] == DEFAULT_COLUMNS
        assert sum(len(c.cards) for c in board.columns) == 8


def test_seed_is_idempotent(db):
    from app.seed import seed_if_empty

    database.init_db()
    with database.SessionLocal() as session:
        seed_if_empty(session)
    with database.SessionLocal() as session:
        first_count = session.query(database.models.User).count()
        assert first_count == 1

    with database.SessionLocal() as session:
        seed_if_empty(session)
    with database.SessionLocal() as session:
        second_count = session.query(database.models.User).count()
        assert second_count == 1
