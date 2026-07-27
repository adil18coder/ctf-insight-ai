"""
Rate limiting scaffold.

Wired here so every route added from Milestone 3 onward is rate-limit-aware
from the start, rather than bolting it on retroactively in Milestone 15.
Milestone 15 will tune the actual limits per-route and add Redis-backed
distributed limiting (this default uses in-memory storage, fine for a single
Railway instance but not for horizontal scaling — flagged for revisit).
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_default_per_minute}/minute"],
)

# Stricter bucket applied explicitly to auth routes via @limiter.limit(AUTH_RATE_LIMIT)
AUTH_RATE_LIMIT = f"{settings.rate_limit_auth_per_minute}/minute"
