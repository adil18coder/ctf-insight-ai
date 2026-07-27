"""
Shared FastAPI dependencies.

`get_db` is re-exported from app.db.session so every router imports
dependencies from this one module instead of reaching into app.db directly.

get_current_user / require_role guards are added in Milestone 3 once JWT
auth exists — routes built in this milestone (health check) don't need them.
"""
from app.db.session import get_db

__all__ = ["get_db"]
