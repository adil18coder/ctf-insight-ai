import uuid
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin


class Flashcard(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "flashcards"
    __table_args__ = (
        CheckConstraint(
            "writeup_id IS NOT NULL OR learning_path_id IS NOT NULL",
            name="ck_flashcards_has_parent",
        ),
    )

    writeup_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("writeups.id", ondelete="CASCADE"), nullable=True, index=True
    )
    learning_path_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=True, index=True
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    writeup: Mapped[Optional["WriteUp"]] = relationship(back_populates="flashcards")
    learning_path: Mapped[Optional["LearningPath"]] = relationship(back_populates="flashcards")
    reviews: Mapped[list["FlashcardReview"]] = relationship(back_populates="flashcard", cascade="all, delete-orphan")
