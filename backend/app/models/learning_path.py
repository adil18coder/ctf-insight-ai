import uuid
from typing import List, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class LearningPath(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "learning_paths"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ordered_topics: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    flashcards: Mapped[List["Flashcard"]] = relationship(back_populates="learning_path")
    quizzes: Mapped[List["Quiz"]] = relationship(back_populates="learning_path")
