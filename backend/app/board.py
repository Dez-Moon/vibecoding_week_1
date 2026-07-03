"""Board service layer.

All write paths that change `position` go through `renumber_column`,
which compacts positions to 0..N-1 in a single transaction. This keeps
the tight-integer invariant from [docs/DATABASE.md](../docs/DATABASE.md) honest.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import models, schemas
from app.seed import new_id


def _load_user_board(db: Session, username: str) -> models.Board | None:
    stmt = (
        select(models.User)
        .where(models.User.username == username)
        .options(selectinload(models.User.board).selectinload(models.Board.columns).selectinload(models.Column.cards))
    )
    user = db.execute(stmt).scalar_one_or_none()
    return user.board if user else None


def get_board(db: Session, username: str) -> schemas.BoardOut | None:
    board = _load_user_board(db, username)
    if board is None:
        return None
    columns_out: list[schemas.ColumnOut] = []
    cards_out: dict[str, schemas.CardOut] = {}
    for column in board.columns:
        card_ids: list[str] = []
        for card in column.cards:
            cards_out[card.id] = schemas.CardOut(
                id=card.id,
                title=card.title,
                details=card.details,
                position=card.position,
                column_id=card.column_id,
            )
            card_ids.append(card.id)
        columns_out.append(
            schemas.ColumnOut(
                id=column.id,
                title=column.title,
                position=column.position,
                card_ids=card_ids,
            )
        )
    return schemas.BoardOut(columns=columns_out, cards=cards_out)


def _column_owned_by_board(db: Session, column_id: str, board: models.Board) -> models.Column:
    column = next((c for c in board.columns if c.id == column_id), None)
    if column is None:
        raise LookupError("column not found on this board")
    return column


def _card_owned_by_board(db: Session, card_id: str, board: models.Board) -> models.Card:
    for column in board.columns:
        card = next((c for c in column.cards if c.id == card_id), None)
        if card is not None:
            return card
    raise LookupError("card not found on this board")


def rename_columns(
    db: Session, username: str, payload: schemas.ColumnsRenameIn
) -> None:
    board = _load_user_board(db, username)
    if board is None:
        return
    requested = {item.id: item.title for item in payload.columns}
    for column in board.columns:
        if column.id in requested:
            column.title = requested[column.id]
    db.commit()


def create_card(db: Session, username: str, payload: schemas.CardCreateIn) -> models.Card:
    board = _load_user_board(db, username)
    if board is None:
        raise LookupError("board not found")
    column = _column_owned_by_board(db, payload.column_id, board)
    card = models.Card(
        id=new_id(),
        column_id=column.id,
        title=payload.title,
        details=payload.details,
        position=len(column.cards),
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def update_card(
    db: Session, username: str, card_id: str, payload: schemas.CardUpdateIn
) -> models.Card:
    board = _load_user_board(db, username)
    if board is None:
        raise LookupError("board not found")
    card = _card_owned_by_board(db, card_id, board)
    if payload.title is not None:
        card.title = payload.title
    if payload.details is not None:
        card.details = payload.details
    db.commit()
    db.refresh(card)
    return card


def delete_card(db: Session, username: str, card_id: str) -> None:
    board = _load_user_board(db, username)
    if board is None:
        raise LookupError("board not found")
    card = _card_owned_by_board(db, card_id, board)
    source_column = card.column
    db.delete(card)
    db.flush()
    db.refresh(source_column)
    _renumber_column(db, source_column)
    db.commit()


def move_card(
    db: Session, username: str, card_id: str, payload: schemas.CardMoveIn
) -> models.Card:
    board = _load_user_board(db, username)
    if board is None:
        raise LookupError("board not found")
    card = _card_owned_by_board(db, card_id, board)
    source_column = card.column
    target_column = _column_owned_by_board(db, payload.column_id, board)

    if source_column.id != target_column.id:
        # Park the card at a negative sentinel before changing column_id.
        # Without this, the UPDATE on column_id would collide with the card
        # that already occupies the target column at our current position.
        sentinel = -(len(source_column.cards) + 1)
        card.position = sentinel
        db.flush()
        card.column_id = target_column.id
        db.flush()
        db.refresh(source_column)
        db.refresh(target_column)

    db.refresh(target_column)

    # Move the card to its final in-column index. Use list.remove (not insert)
    # because the card is already in the collection after the refresh above —
    # insert would leave a duplicate entry that breaks renumbering.
    target_column.cards.remove(card)
    insert_at = min(max(payload.position, 0), len(target_column.cards))
    target_column.cards.insert(insert_at, card)

    _renumber_column(db, source_column)
    _renumber_column(db, target_column)
    db.commit()
    db.refresh(card)
    return card


def _renumber_column(db: Session, column: models.Column) -> None:
    """Renumber `column.cards` to 0..N-1 using two passes.

    SQLAlchemy flushes dirty rows in primary-key order, which means a
    tight negative range like -1..-N can collide with rows we haven't
    flushed yet — the first UPDATE writes -2 while the second card is
    still at its old position of -2 in the DB. We sidestep that by
    parking cards at large positive offsets that no existing row holds.
    """
    ordered_cards = list(column.cards)
    temp_base = 1_000_000
    for index, card in enumerate(ordered_cards):
        card.position = temp_base + index
    db.flush()
    for index, card in enumerate(ordered_cards):
        card.position = index
    db.flush()
