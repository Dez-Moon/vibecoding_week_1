from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated, Literal


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AIChatRequest(BaseModel):
    message: str
    conversation_history: list[Message] | None = None


class OperationCreateCard(BaseModel):
    op: Literal["create_card"] = "create_card"
    column_id: str
    title: str
    details: str = ""


class OperationUpdateCard(BaseModel):
    op: Literal["update_card"] = "update_card"
    card_id: str
    title: str | None = None
    details: str | None = None


class OperationDeleteCard(BaseModel):
    op: Literal["delete_card"] = "delete_card"
    card_id: str


class OperationMoveCard(BaseModel):
    op: Literal["move_card"] = "move_card"
    card_id: str
    column_id: str
    position: int


class OperationRenameColumn(BaseModel):
    op: Literal["rename_column"] = "rename_column"
    column_id: str
    title: str


Operation = Annotated[
    OperationCreateCard | OperationUpdateCard | OperationDeleteCard | OperationMoveCard | OperationRenameColumn,
    Field(discriminator="op"),
]


class BoardUpdate(BaseModel):
    operations: list[Operation] = []


class AIChatResponse(BaseModel):
    response: str
    board_update: BoardUpdate | None = None
    board: BoardOut


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
