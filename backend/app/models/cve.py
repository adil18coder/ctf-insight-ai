"""
Dedicated CVE table + writeup<->cve association (decision #10).

Rationale: storing CVEs as JSONB on `summaries` (the original spec's
implication) makes "show me every write-up referencing CVE-2023-1234" or
"what's the average CVSS severity across my uploads" impossible without a
full-table JSON scan. Breaking CVEs into their own first-class entity means:
  - CVE metadata (description, severity, published date) is stored once and
    reused across every write-up that references it, instead of duplicated.
  - The many-to-many relationship is indexed and joinable normally.
  - Future features (CVE trend dashboards, "similar write-ups by shared CVE")
    are cheap additions rather than a schema rewrite.
"""
import uuid
from datetime import date as date_type
from typing import List, Optional

from sqlalchemy import Date, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CVE(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "cves"

    cve_id: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)  # e.g. "CVE-2023-1234"
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    severity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # CVSS base score
    severity_label: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # low|medium|high|critical
    published_date: Mapped[Optional[date_type]] = mapped_column(Date, nullable=True)
    reference_urls: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    writeup_links: Mapped[List["WriteUpCVE"]] = relationship(back_populates="cve", cascade="all, delete-orphan")


class WriteUpCVE(Base):
    """Association table: many-to-many between writeups and cves."""

    __tablename__ = "writeup_cves"

    writeup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("writeups.id", ondelete="CASCADE"), primary_key=True
    )
    cve_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cves.id", ondelete="CASCADE"), primary_key=True
    )

    writeup: Mapped["WriteUp"] = relationship(back_populates="cve_links")
    cve: Mapped["CVE"] = relationship(back_populates="writeup_links")
