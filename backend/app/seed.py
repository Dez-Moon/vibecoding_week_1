import logging
import uuid

from sqlalchemy.orm import Session

from app import models

logger = logging.getLogger(__name__)

DEMO_USER_ID = "user-demo-id"
DEMO_USERNAME = "user"

DEFAULT_COLUMNS = [
    "Backlog",
    "Discovery",
    "In Progress",
    "Review",
    "Done",
]

DEFAULT_CARDS_BY_COLUMN = {
    "Backlog": [
        ("Audit the existing API", "Document every endpoint before changing it."),
    ],
    "Discovery": [
        ("Spike: in-app chat", "How would a sidebar chat integrate with the board?"),
        ("Spike: card labels", "Color-coded labels on cards."),
    ],
    "In Progress": [
        ("Wire board to API", "Replace frontend initialData with /api/board."),
        ("Column rename UI polish", "Make rename feel less sticky."),
    ],
    "Review": [
        ("Add card details pane", "Inline expand to read/edit details."),
    ],
    "Done": [
        ("Decide spec color scheme", "Locked in green / indigo / cyan / slate / gray."),
        ("Ship the demo", "First end-to-end clickable board."),
    ],
}


def seed_if_empty(db: Session) -> None:
    """Seed the demo workspace on a fresh database.

    Creates the demo `user` plus one board, the five default columns,
    and the eight seed cards. The seed mirrors the demo data the
    frontend carried in [frontend/src/lib/kanban.ts](../frontend/src/lib/kanban.ts)
    in earlier parts. Idempotent: a no-op when any user already exists.
    """
    if db.query(models.User).count() > 0:
        return
    user = models.User(id=DEMO_USER_ID, username=DEMO_USERNAME)
    board = models.Board(id=new_id(), user_id=user.id, title="Kanban Studio")
    db.add_all([user, board])
    db.flush()

    columns_by_title: dict[str, models.Column] = {}
    for position, title in enumerate(DEFAULT_COLUMNS):
        column = models.Column(
            id=new_id(), board_id=board.id, title=title, position=position
        )
        columns_by_title[title] = column
        db.add(column)
    db.flush()

    card_count = 0
    for title, cards in DEFAULT_CARDS_BY_COLUMN.items():
        column = columns_by_title[title]
        for position, (card_title, card_details) in enumerate(cards):
            db.add(
                models.Card(
                    id=new_id(),
                    column_id=column.id,
                    title=card_title,
                    details=card_details,
                    position=position,
                )
            )
            card_count += 1
    db.commit()
    logger.info(
        "Seeded demo workspace: user=%s, board=%s, %d columns, %d cards",
        DEMO_USERNAME,
        board.id,
        len(DEFAULT_COLUMNS),
        card_count,
    )


def new_id() -> str:
    return str(uuid.uuid4())
