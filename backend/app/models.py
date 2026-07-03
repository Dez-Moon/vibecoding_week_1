from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    board: Mapped["Board"] = relationship(
        "Board", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class Board(Base):
    __tablename__ = "boards"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), unique=True
    )
    title: Mapped[str] = mapped_column(String, default="Kanban Studio")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    user: Mapped["User"] = relationship("User", back_populates="board")
    columns: Mapped[list["Column"]] = relationship(
        "Column",
        back_populates="board",
        cascade="all, save-update, merge",
        order_by="Column.position",
    )


class Column(Base):
    __tablename__ = "columns"
    __table_args__ = (UniqueConstraint("board_id", "position"),)

    id: Mapped[str] = mapped_column(String, primary_key=True)
    board_id: Mapped[str] = mapped_column(ForeignKey("boards.id"), index=True)
    title: Mapped[str] = mapped_column(String)
    position: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    board: Mapped["Board"] = relationship("Board", back_populates="columns")
    cards: Mapped[list["Card"]] = relationship(
        "Card",
        back_populates="column",
        cascade="all, save-update, merge",
        order_by="Card.position",
    )


class Card(Base):
    __tablename__ = "cards"
    __table_args__ = (UniqueConstraint("column_id", "position"),)

    id: Mapped[str] = mapped_column(String, primary_key=True)
    column_id: Mapped[str] = mapped_column(ForeignKey("columns.id"), index=True)
    title: Mapped[str] = mapped_column(String)
    details: Mapped[str] = mapped_column(String, default="")
    position: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    column: Mapped["Column"] = relationship("Column", back_populates="cards")
