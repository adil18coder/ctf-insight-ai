import enum
import uuid
from typing import List, Optional

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class FileType(str, enum.Enum):
    md = "md"
    pdf = "pdf"
    txt = "txt"
    docx = "docx"


class WriteUpStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Visibility(str, enum.Enum):
    private = "private"
    public = "public"


class WriteUp(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Visibility (decision #11): users choose private/public at upload time.
    Public write-ups are discoverable by other users via /search; private
    ones are only ever returned to their owner or an admin. Enforcement of
    this lives in the writeup repository/service layer (every read query
    filters by `visibility == public OR user_id == current_user.id`), not
    just in the API layer, so it can't be bypassed by calling the DB directly
    from a worker or admin script.
    """

    __tablename__ = "writeups"

    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    file_type: Mapped[FileType] = mapped_column(SAEnum(FileType, name="file_type"), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    raw_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[WriteUpStatus] = mapped_column(
        SAEnum(WriteUpStatus, name="writeup_status"), nullable=False, default=WriteUpStatus.pending, index=True
    )
    visibility: Mapped[Visibility] = mapped_column(
        SAEnum(Visibility, name="writeup_visibility"), nullable=False, default=Visibility.private, index=True
    )

    difficulty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    platform: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    project: Mapped[Optional["Project"]] = relationship(back_populates="writeups")
    user: Mapped["User"] = relationship(back_populates="writeups")
    summary: Mapped[Optional["Summary"]] = relationship(back_populates="writeup", cascade="all, delete-orphan", uselist=False)
    techniques: Mapped[List["Technique"]] = relationship(back_populates="writeup", cascade="all, delete-orphan")
    commands: Mapped[List["Command"]] = relationship(back_populates="writeup", cascade="all, delete-orphan")
    mitre_mappings: Mapped[List["MitreMapping"]] = relationship(back_populates="writeup", cascade="all, delete-orphan")
    flashcards: Mapped[List["Flashcard"]] = relationship(back_populates="writeup", cascade="all, delete-orphan")
    quizzes: Mapped[List["Quiz"]] = relationship(back_populates="writeup", cascade="all, delete-orphan")
    chat_messages: Mapped[List["ChatMessage"]] = relationship(back_populates="writeup", cascade="all, delete-orphan")
    cve_links: Mapped[List["WriteUpCVE"]] = relationship(back_populates="writeup", cascade="all, delete-orphan")
