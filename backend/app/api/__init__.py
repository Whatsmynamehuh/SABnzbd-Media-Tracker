"""
API routes.
"""
from backend.app.api.downloads import router as downloads_router
from backend.app.api.stats import router as stats_router

__all__ = ["downloads_router", "stats_router"]
