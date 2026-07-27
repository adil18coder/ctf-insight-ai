"""
Aggregates all v1 routers into one. Each feature area gets its own router
module (auth.py, users.py, writeups.py, ...) added here as its milestone
lands — health.py is the only one that exists as of Milestone 2.
"""
from fastapi import APIRouter

from app.api.v1 import health

api_router = APIRouter()
api_router.include_router(health.router)

# Milestone 3+: api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# Milestone 4+: api_router.include_router(users.router, prefix="/users", tags=["users"])
# Milestone 5+: api_router.include_router(writeups.router, prefix="/writeups", tags=["writeups"])
# ... etc., one line added per milestone rather than pre-declared as dead stubs.
