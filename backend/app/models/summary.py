import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Summary(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """1:1 with WriteUp — the AI-generated analysis result (Milestone 7/8
    populate this). CVEs are intentionally NOT stored here as JSON (decision
    #10) — see models/cve.py and the writeup_cves association table instead,
    which allows efficient cross-writeup CVE queries."""

    __tablename__ = "summaries"

    writeup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("writeups.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    executive_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    vulnerability_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    exploitation_steps: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    detection_opportunities: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    blue_team_perspective: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    red_team_perspective: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prevention: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    technologies_used: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    owasp_mappings: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    similar_htb_machines: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    similar_thm_rooms: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    interview_questions: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    learning_roadmap: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    important_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    llm_provider_used: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    writeup: Mapped["WriteUp"] = relationship(back_populates="summary")
