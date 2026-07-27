import enum
import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class BookmarkEntityType(str, enum.Enum):
    writeup = "writeup"
    flashcard = "flashcard"
    learning_path = "learning_path"


class Bookmark(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "bookmarks"
    __table_args__ = (
        UniqueConstraint("user_id", "entity_type", "entity_id", name="uq_bookmark_per_entity"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    entity_type: Mapped[BookmarkEntityType] = mapped_column(
        SAEnum(BookmarkEntityType, name="bookmark_entity_type"), nullable=False
    )
    # Polymorphic reference — no physical FK since it can point at three different
    # tables. Integrity is enforced in the service layer on write (existence check
    # against the right table based on entity_type) rather than at the DB level.
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
