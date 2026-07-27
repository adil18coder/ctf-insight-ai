import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin


class MitreMapping(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "mitre_mappings"

    writeup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("writeups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    technique_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("techniques.id", ondelete="CASCADE"), nullable=True
    )
    mitre_technique_id: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    mitre_tactic: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    mitre_technique_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    writeup: Mapped["WriteUp"] = relationship(back_populates="mitre_mappings")
    technique: Mapped[Optional["Technique"]] = relationship(back_populates="mitre_mappings")
