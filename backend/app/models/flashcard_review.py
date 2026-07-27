import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin


class FlashcardReview(Base, UUIDPrimaryKeyMixin):
    """Per-user SM-2 spaced-repetition scheduling state for a given flashcard."""

    __tablename__ = "flashcard_reviews"
    __table_args__ = (
        UniqueConstraint("flashcard_id", "user_id", name="uq_flashcard_review_per_user"),
    )

    flashcard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("flashcards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ease_factor: Mapped[int] = mapped_column(Integer, nullable=False, default=250)  # SM-2 stored as *100
    interval_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    next_review_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    flashcard: Mapped["Flashcard"] = relationship(back_populates="reviews")
