import enum
import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin


class QuizMode(str, enum.Enum):
    quiz = "quiz"
    exam = "exam"


class Quiz(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "quizzes"

    writeup_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("writeups.id", ondelete="CASCADE"), nullable=True, index=True
    )
    learning_path_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    mode: Mapped[QuizMode] = mapped_column(SAEnum(QuizMode, name="quiz_mode"), nullable=False, default=QuizMode.quiz)
    questions: Mapped[list] = mapped_column(JSONB, nullable=False)  # [{question, options[], correct_index, explanation}]

    writeup: Mapped[Optional["WriteUp"]] = relationship(back_populates="quizzes")
    learning_path: Mapped[Optional["LearningPath"]] = relationship(back_populates="quizzes")
    attempts: Mapped[list["QuizAttempt"]] = relationship(back_populates="quiz", cascade="all, delete-orphan")
