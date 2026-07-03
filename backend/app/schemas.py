from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    details: str
    position: int
    column_id: str


class ColumnOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    position: int
    card_ids: list[str]


class BoardOut(BaseModel):
    columns: list[ColumnOut]
    cards: dict[str, CardOut]


class ColumnRename(BaseModel):
    id: str
    title: str = Field(min_length=1, max_length=120)


class ColumnsRenameIn(BaseModel):
    columns: list[ColumnRename]


class CardCreateIn(BaseModel):
    column_id: str
    title: str = Field(min_length=1, max_length=200)
    details: str = Field(default="", max_length=10_000)


class CardUpdateIn(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    details: str | None = Field(default=None, max_length=10_000)


class CardMoveIn(BaseModel):
    column_id: str
    position: int = Field(ge=0)
