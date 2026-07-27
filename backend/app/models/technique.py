import uuid
from typing import List, Optional

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Technique(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "techniques"

    writeup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("writeups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    evidence_snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    writeup: Mapped["WriteUp"] = relationship(back_populates="techniques")
    mitre_mappings: Mapped[List["MitreMapping"]] = relationship(back_populates="technique")
