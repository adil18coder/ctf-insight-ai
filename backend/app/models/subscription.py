import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SubscriptionPlan(str, enum.Enum):
    free = "free"
    premium = "premium"


class SubscriptionStatus(str, enum.Enum):
    active = "active"
    canceled = "canceled"
    past_due = "past_due"


class Subscription(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Stripe is the payment provider (decision #12). Kept future-ready for v1:
    the table and API surface exist now, but the actual Stripe checkout/webhook
    wiring is deferred to when billing goes live — `stripe_customer_id` /
    `stripe_subscription_id` are nullable so a free-tier row can exist with no
    Stripe object behind it yet.

    Premium plan = unlimited AI usage under a fair-use policy (not a hard
    numeric cap) — enforced via abuse-detection in the AI service layer
    (Milestone 7+) rather than a `ai_credits` deduction like free-tier users.
    """

    __tablename__ = "subscriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    plan: Mapped[SubscriptionPlan] = mapped_column(
        SAEnum(SubscriptionPlan, name="subscription_plan"), nullable=False, default=SubscriptionPlan.free
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        SAEnum(SubscriptionStatus, name="subscription_status"), nullable=False, default=SubscriptionStatus.active
    )
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="subscription")
