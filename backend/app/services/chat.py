"""Chat service for AI interactions with the Kanban board."""

from __future__ import annotations

import json

from app import board, schemas
from app.services.ai import call_ai


OPERATIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "response": {"type": "string", "description": "Your response to the user"},
        "board_update": {
            "type": "object",
            "nullable": True,
            "properties": {
                "operations": {
                    "type": "array",
                    "items": {
                        "oneOf": [
                            {
                                "type": "object",
                                "properties": {
                                    "op": {"const": "create_card"},
                                    "column_id": {"type": "string"},
                                    "title": {"type": "string"},
                                    "details": {"type": "string"},
                                },
                                "required": ["op", "column_id", "title"],
                                "additionalProperties": False,
                            },
                            {
                                "type": "object",
                                "properties": {
                                    "op": {"const": "update_card"},
                                    "card_id": {"type": "string"},
                                    "title": {"type": "string"},
                                    "details": {"type": "string"},
                                },
                                "required": ["op", "card_id"],
                                "additionalProperties": False,
                            },
                            {
                                "type": "object",
                                "properties": {
                                    "op": {"const": "delete_card"},
                                    "card_id": {"type": "string"},
                                },
                                "required": ["op", "card_id"],
                                "additionalProperties": False,
                            },
                            {
                                "type": "object",
                                "properties": {
                                    "op": {"const": "move_card"},
                                    "card_id": {"type": "string"},
                                    "column_id": {"type": "string"},
                                    "position": {"type": "integer", "minimum": 0},
                                },
                                "required": ["op", "card_id", "column_id", "position"],
                                "additionalProperties": False,
                            },
                            {
                                "type": "object",
                                "properties": {
                                    "op": {"const": "rename_column"},
                                    "column_id": {"type": "string"},
                                    "title": {"type": "string"},
                                },
                                "required": ["op", "column_id", "title"],
                                "additionalProperties": False,
                            },
                        ]
                    },
                }
            },
            "required": ["operations"],
        },
    },
    "required": ["response"],
}


def build_system_prompt(username: str, board_data: schemas.BoardOut) -> str:
    return f"""You are a helpful assistant for a project management Kanban board. The user is {username}.

Current board state:
{board_data.model_dump_json(indent=2)}

You can help the user manage their board. When they ask you to create, update, delete, or move cards, or rename columns, respond with JSON matching this schema:
{json.dumps(OPERATIONS_SCHEMA, indent=2)}

Only include board_update.operations when the user explicitly asks you to make changes. If they just ask questions, respond with just the "response" field and no board_update.

All operations are validated before being applied. Invalid operations (e.g., referencing non-existent cards or columns) will cause the entire update to be rejected."""


def apply_operations(db, board_data: schemas.BoardOut, update: schemas.BoardUpdate) -> None:
    """Apply board operations in a single transaction. Raises ValueError on invalid op."""
    column_ids = {col.id for col in board_data.columns}
    card_ids = set(board_data.cards.keys())

    for op in update.operations:
        match op:
            case schemas.OperationCreateCard():
                if op.column_id not in column_ids:
                    raise ValueError(f"Column {op.column_id} not found")
                board.create_card(db, "user", schemas.CardCreateIn(
                    column_id=op.column_id,
                    title=op.title,
                    details=op.details,
                ))
            case schemas.OperationUpdateCard():
                if op.card_id not in card_ids:
                    raise ValueError(f"Card {op.card_id} not found")
                board.update_card(db, "user", op.card_id, schemas.CardUpdateIn(
                    title=op.title,
                    details=op.details,
                ))
            case schemas.OperationDeleteCard():
                if op.card_id not in card_ids:
                    raise ValueError(f"Card {op.card_id} not found")
                board.delete_card(db, "user", op.card_id)
            case schemas.OperationMoveCard():
                if op.card_id not in card_ids:
                    raise ValueError(f"Card {op.card_id} not found")
                if op.column_id not in column_ids:
                    raise ValueError(f"Column {op.column_id} not found")
                board.move_card(db, "user", op.card_id, schemas.CardMoveIn(
                    column_id=op.column_id,
                    position=op.position,
                ))
            case schemas.OperationRenameColumn():
                if op.column_id not in column_ids:
                    raise ValueError(f"Column {op.column_id} not found")
                board.rename_columns(db, "user", schemas.ColumnsRenameIn(
                    columns=[schemas.ColumnRename(id=op.column_id, title=op.title)],
                ))
